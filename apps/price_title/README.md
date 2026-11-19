# price_title

Keeps the video's title on Anthropic's share price: **A benefit single for a $83 stock**. The service polls Alpaca for ANT's latest trade once a minute. When the whole-dollar price changes, it rewrites the YouTube title and leaves the description, tags and category as they are. It uses only the Python standard library (3.9+) and has no dependencies.

## What it needs

1. **An Alpaca API key** (key ID and secret). A free paper-trading account's key reads market data from the IEX feed. A paid data plan can use `ALPACA_FEED=sip` for consolidated prices.
2. **OAuth for the channel, not a YouTube API key.** An API key can only read public data, and editing a video needs the owner's authorization. Set it up once:
   1. In the Google Cloud console, choose a project and enable **YouTube Data API v3**.
   2. Under **APIs & services → OAuth consent screen**: user type External, add yourself, then **publish it ("In production")**. While the screen is in Testing, refresh tokens expire after 7 days. You don't need verification for your own channel; click through the "unverified app" warning.
   3. Under **Credentials → Create credentials → OAuth client ID**, choose type **Desktop app**. Note the client ID and secret.
   4. On a computer with a browser, run `GOOGLE_CLIENT_ID=… GOOGLE_CLIENT_SECRET=… python3 authorize.py` and sign in as the channel that owns the video. It prints `GOOGLE_REFRESH_TOKEN=…`. To run it on a VPS instead, use `ssh -L 8765:127.0.0.1:8765 vps` and `python3 authorize.py --port 8765`.
3. **The title set once by hand** to match the template, e.g. `A benefit single for a $83 stock`. With `TITLE_GUARD=1` (the default), the service only rewrites a title that matches the template. If you retitle the video by hand to anything else, it leaves the title alone until you set it back.

## Deploy (systemd)

```sh
sudo mkdir -p /opt/price-title && sudo cp price_title.py /opt/price-title/
sudo install -m 600 price_title.env.example /etc/price-title.env   # then fill it in
sudo cp price-title.service /etc/systemd/system/
# first, a dry run: one check that logs the change it would make
sudo systemd-run --pty --wait -p EnvironmentFile=/etc/price-title.env -p DynamicUser=yes \
  python3 /opt/price-title/price_title.py --once --dry-run
sudo systemctl daemon-reload && sudo systemctl enable --now price-title
journalctl -u price-title -f
```

Or with Docker:

```sh
docker build -t price-title .
docker run -d --name price-title --restart unless-stopped --env-file /etc/price-title.env -v price-title:/state price-title
```

## Behaviour

- **Rounding and flapping.** The price is rounded half up to `PRICE_DECIMALS` (default 0, so `$83`). The title only changes once the price is `HYSTERESIS` (default 0.6) of a dollar from the shown price. At `$83`, it moves to `$84` at 83.60, not 83.50, and back at 83.40, so a price hovering around 83.50 doesn't flap.
- **Quota.** Each title change costs 50 of YouTube's 10,000 daily quota units, and each read of the title costs 1. `MIN_UPDATE_SECONDS` (default 900) allows at most 96 changes a day, under half the quota. The service reads the title only at start and right before each change.
- **Outside market hours** the latest trade stays the same, so nothing changes. Alpaca's IEX feed includes extended-hours trades.
- **Errors** are logged and retried with backoff (up to 30 minutes), and the title is re-read after any failure. If the quota runs out, or Google refuses the refresh token, the service waits an hour; for a refused token, run `authorize.py` again.
- **`STATE_DIR`** keeps the last change's time, so a restart doesn't skip `MIN_UPDATE_SECONDS`.

All settings are listed in `price_title.env.example` and documented at the top of `price_title.py`.

## Tests

`python3 test_price_title.py` runs the watcher against a local stand-in for Alpaca, Google's token endpoint and the YouTube API. It covers rounding, hysteresis, the guard, a hand edit between checks, the minimum interval, dry runs, and the request body, which must keep the description, tags and category.
