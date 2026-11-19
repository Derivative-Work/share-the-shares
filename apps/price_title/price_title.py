#!/usr/bin/env python3
"""Keep the video's title on the stock's price: "A benefit single for a $83 stock".

Polls Alpaca for the latest trade in SYMBOL (default ANT) and, when the whole-dollar price changes, rewrites the
YouTube video's title from TITLE_TEMPLATE. Standard library only (Python 3.9+).

Every setting comes from the environment (see price_title.env.example):
  ALPACA_KEY_ID, ALPACA_SECRET_KEY        Alpaca API key (market data; a free paper-trading key works)
  ALPACA_FEED          iex                iex (free) or sip (paid subscription)
  SYMBOL               ANT
  TRADES_SINCE         2026-11-19         ignore trades before this date (UTC), so an older listing under the same
                                          ticker can't set the title; until the first trade, the service just waits
  YOUTUBE_VIDEO_ID                        e.g. YpJn6DwTLlk
  GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN
                                          OAuth for the channel that owns the video (authorize.py makes the token;
                                          an API key alone can't edit a video)
  TITLE_TEMPLATE       A benefit single for a {price} stock      ({price} becomes "$83")
  PRICE_DECIMALS       0                  0 -> "$83", 2 -> "$83.17"
  HYSTERESIS           0.6                how far past the rounding boundary the price must go, in units of the last
                                          shown digit, before the title changes (stops flapping around $83.50)
  POLL_SECONDS         60
  MIN_UPDATE_SECONDS   900                at most one title change per 15 min (each costs 50 of the 10,000 daily
                                          quota units)
  TITLE_GUARD          1                  only rewrite a title that still matches the template, so a title changed by
                                          hand isn't overwritten (set 0 to always write)
  STATE_DIR                               where to remember the last change's time across restarts (optional)
  DRY_RUN              0                  1: log the change instead of making it

Usage: price_title.py [--once] [--dry-run]   (--once: one check, then exit; --dry-run: as DRY_RUN=1)
"""
import json
import logging
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ALPACA_DATA_URL = os.environ.get("ALPACA_DATA_URL", "https://data.alpaca.markets")
YOUTUBE_URL = os.environ.get("YOUTUBE_URL", "https://www.googleapis.com/youtube/v3")
TOKEN_URL = os.environ.get("GOOGLE_TOKEN_URL", "https://oauth2.googleapis.com/token")
UA = "price-title/1.0"
WRITABLE = ("title", "description", "tags", "categoryId", "defaultLanguage", "defaultAudioLanguage")

log = logging.getLogger("price_title")


class NotTrading(Exception):
    """No usable trade yet: the symbol isn't listed on the feed, has no trades, or only has trades from before
    TRADES_SINCE. Not an error; the service keeps polling and touches nothing on YouTube."""


class ApiError(Exception):
    def __init__(self, status, body):
        super().__init__(f"HTTP {status}: {body[:500]}")
        self.status, self.body = status, body


def env(name, default=None):
    v = os.environ.get(name, default)
    if v is None or v == "":
        sys.exit(f"price_title: {name} is not set")
    return v


def request(url, *, method="GET", headers=None, data=None, form=None):
    h = {"User-Agent": UA, "Accept": "application/json", **(headers or {})}
    body = None
    if form is not None:
        body = urllib.parse.urlencode(form).encode()
        h["Content-Type"] = "application/x-www-form-urlencoded"
    elif data is not None:
        body = json.dumps(data).encode()
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        raise ApiError(e.code, e.read().decode("utf-8", "replace")) from None


class Config:
    def __init__(self):
        self.alpaca_id = env("ALPACA_KEY_ID")
        self.alpaca_secret = env("ALPACA_SECRET_KEY")
        self.feed = env("ALPACA_FEED", "iex")
        self.symbol = env("SYMBOL", "ANT").upper()
        self.since = env("TRADES_SINCE", "2026-11-19")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", self.since):
            sys.exit("price_title: TRADES_SINCE must be YYYY-MM-DD")
        self.video = env("YOUTUBE_VIDEO_ID")
        self.client_id = env("GOOGLE_CLIENT_ID")
        self.client_secret = env("GOOGLE_CLIENT_SECRET")
        self.refresh_token = env("GOOGLE_REFRESH_TOKEN")
        self.template = env("TITLE_TEMPLATE", "A benefit single for a {price} stock")
        if self.template.count("{price}") != 1:
            sys.exit("price_title: TITLE_TEMPLATE needs exactly one {price}")
        self.decimals = int(env("PRICE_DECIMALS", "0"))
        self.hysteresis = float(env("HYSTERESIS", "0.6"))
        self.poll = float(env("POLL_SECONDS", "60"))
        self.min_update = float(env("MIN_UPDATE_SECONDS", "900"))
        self.guard = env("TITLE_GUARD", "1") != "0"
        self.state_dir = os.environ.get("STATE_DIR") or None
        self.dry_run = env("DRY_RUN", "0") != "0" or "--dry-run" in sys.argv[1:]


def fmt_price(p, decimals):
    step = 10 ** -decimals
    v = int(p / step + 0.5) * step  # half up
    return f"${v:,.{decimals}f}"


def parse_price(s):
    return float(s.lstrip("$").replace(",", ""))


def title_regex(template):
    a, b = template.split("{price}")
    return re.compile(re.escape(a) + r"(\$[\d,]+(?:\.\d+)?)" + re.escape(b) + r"\Z")


def should_change(price, shown, decimals, hysteresis):
    """The new price text, if the title should change from `shown` (a float, or None if unknown)."""
    new = fmt_price(price, decimals)
    if shown is None:
        return new
    if new == fmt_price(shown, decimals):
        return None
    step = 10 ** -decimals
    # the price must be past the boundary between `shown` and its neighbour by (hysteresis - 0.5) steps
    if abs(price - shown) < hysteresis * step:
        return None
    return new


class Google:
    def __init__(self, cfg):
        self.cfg, self.token, self.expires = cfg, None, 0.0

    def auth(self):
        if not self.token or time.time() > self.expires - 60:
            r = request(TOKEN_URL, method="POST", form={
                "client_id": self.cfg.client_id, "client_secret": self.cfg.client_secret,
                "refresh_token": self.cfg.refresh_token, "grant_type": "refresh_token"})
            self.token, self.expires = r["access_token"], time.time() + float(r.get("expires_in", 3600))
        return {"Authorization": f"Bearer {self.token}"}

    def snippet(self):
        q = urllib.parse.urlencode({"part": "snippet", "id": self.cfg.video})
        items = request(f"{YOUTUBE_URL}/videos?{q}", headers=self.auth()).get("items") or []
        if not items:
            raise RuntimeError(f"video {self.cfg.video} not found (or not visible to this account)")
        return items[0]["snippet"]

    def set_title(self, snippet, title):
        body = {"id": self.cfg.video, "snippet": {k: snippet[k] for k in WRITABLE if k in snippet}}
        body["snippet"]["title"] = title
        q = urllib.parse.urlencode({"part": "snippet"})
        return request(f"{YOUTUBE_URL}/videos?{q}", method="PUT", headers=self.auth(), data=body)


def latest_trade(cfg):
    q = urllib.parse.urlencode({"feed": cfg.feed})
    try:
        r = request(f"{ALPACA_DATA_URL}/v2/stocks/{urllib.parse.quote(cfg.symbol)}/trades/latest?{q}",
                    headers={"APCA-API-KEY-ID": cfg.alpaca_id, "APCA-API-SECRET-KEY": cfg.alpaca_secret})
    except ApiError as e:
        # an unknown symbol is a 404 or 422 (or a 400 naming the symbol); a bad key (401/403) stays an error
        if e.status in (404, 422) or (e.status == 400 and "symbol" in e.body.lower()):
            raise NotTrading(f"{cfg.symbol} isn't on the {cfg.feed} feed yet ({e})") from None
        raise
    t = r.get("trade") or {}
    if "p" not in t or not t.get("p"):
        raise NotTrading(f"no trades for {cfg.symbol} on the {cfg.feed} feed yet")
    if str(t.get("t", ""))[:10] < cfg.since:
        raise NotTrading(f"{cfg.symbol}'s latest trade on the {cfg.feed} feed ({t.get('t')}, ${t['p']}) is from "
                         f"before TRADES_SINCE ({cfg.since})")
    return float(t["p"]), t.get("t")


class Watcher:
    def __init__(self, cfg):
        self.cfg, self.google = cfg, Google(cfg)
        self.rx = title_regex(cfg.template)
        self.shown = None        # the price in the title, as last read or written
        self.title_known = False
        self.last_update = self.load_state()

    def state_path(self):
        return os.path.join(self.cfg.state_dir, "state.json") if self.cfg.state_dir else None

    def load_state(self):
        p = self.state_path()
        try:
            with open(p) as f:
                return float(json.load(f).get("last_update", 0))
        except (TypeError, OSError, ValueError):
            return 0.0

    def save_state(self):
        p = self.state_path()
        if p:
            os.makedirs(self.cfg.state_dir, exist_ok=True)
            with open(p + ".tmp", "w") as f:
                json.dump({"last_update": self.last_update, "shown": self.shown}, f)
            os.replace(p + ".tmp", p)

    def read_title(self):
        snip = self.google.snippet()
        m = self.rx.match(snip["title"])
        self.title_known = True
        if m:
            self.shown = parse_price(m.group(1))
        elif self.cfg.guard:
            self.shown = None
        return snip, m

    def check(self):
        price, at = latest_trade(self.cfg)
        if not getattr(self, "trading", False):
            self.trading = True
            log.info("%s is trading: %.2f at %s", self.cfg.symbol, price, at)
        if not self.title_known:
            snip, m = self.read_title()
            log.info("title now: %r%s", snip["title"], "" if m or not self.cfg.guard else " (doesn't match the template)")
        new = should_change(price, self.shown, self.cfg.decimals, self.cfg.hysteresis)
        log.debug("%s %.4f at %s; shown %s; change to %s", self.cfg.symbol, price, at, self.shown, new)
        if new is None:
            return
        wait = self.last_update + self.cfg.min_update - time.time()
        if wait > 0:
            log.debug("%s %.2f: change held for %.0f s more (MIN_UPDATE_SECONDS)", self.cfg.symbol, price, wait)
            return
        snip, m = self.read_title()  # re-read right before writing: the title may have been edited by hand
        if self.cfg.guard and not m:
            log.warning("title %r doesn't match TITLE_GUARD's template; leaving it alone", snip["title"])
            return
        new = should_change(price, self.shown, self.cfg.decimals, self.cfg.hysteresis)
        if new is None:
            return
        title = self.cfg.template.replace("{price}", new)
        if len(title) > 100 or "<" in title or ">" in title:
            raise RuntimeError(f"YouTube won't take this title: {title!r}")
        if self.cfg.dry_run:
            log.info("DRY RUN: %s %.2f (trade at %s): would retitle %r -> %r", self.cfg.symbol, price, at,
                     snip["title"], title)
        else:
            self.google.set_title(snip, title)
            log.info("%s %.2f (trade at %s): retitled %r -> %r", self.cfg.symbol, price, at, snip["title"], title)
        self.shown = parse_price(new)
        self.last_update = time.time()
        self.save_state()


def main():
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO").upper(),
                        format="%(asctime)s %(levelname)s %(message)s")
    cfg = Config()
    w = Watcher(cfg)
    log.info("watching %s (%s feed) for video %s; template %r%s", cfg.symbol, cfg.feed, cfg.video, cfg.template,
             "; DRY RUN" if cfg.dry_run else "")
    if "--once" in sys.argv[1:]:
        try:
            w.check()
        except NotTrading as e:
            log.info("waiting: %s", e)
        return
    backoff = cfg.poll
    waiting_logged = 0.0
    while True:
        try:
            w.check()
            backoff = cfg.poll
        except NotTrading as e:
            backoff = cfg.poll
            if time.time() - waiting_logged >= 3600:  # say so at start, then hourly
                log.info("waiting: %s; checking every %.0f s", e, cfg.poll)
                waiting_logged = time.time()
        except ApiError as e:
            if e.status == 403 and "quotaExceeded" in e.body:
                backoff = 3600
                log.error("YouTube quota exceeded; next try in an hour")
            elif e.status in (400, 401, 403) and ("invalid_grant" in e.body or "unauthorized_client" in e.body):
                log.error("Google refused the refresh token (revoked, or expired: a consent screen still in "
                          "Testing expires tokens after 7 days). Run authorize.py again. %s", e)
                backoff = 3600
            else:
                backoff = min(max(backoff * 2, cfg.poll), 1800)
                log.error("%s; next try in %.0f s", e, backoff)
            w.title_known = False
        except Exception as e:  # network errors, timeouts, odd responses
            backoff = min(max(backoff * 2, cfg.poll), 1800)
            log.error("%s: %s; next try in %.0f s", type(e).__name__, e, backoff)
            w.title_known = False
        time.sleep(backoff)


if __name__ == "__main__":
    main()
