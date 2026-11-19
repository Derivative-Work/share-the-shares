"""Tests against a local stand-in for Alpaca, Google's token endpoint and the YouTube API: python3 test_price_title.py"""
import json
import os
import threading
import http.server
import unittest
import urllib.parse

state = {"price": 83.2, "title": "A benefit single for a $83 stock", "puts": [], "snippet_extra": {
    "description": "AI-generated satire...", "tags": ["satire"], "categoryId": "10", "channelId": "UCx",
    "thumbnails": {}, "localized": {}}}


class Mock(http.server.BaseHTTPRequestHandler):
    def reply(self, obj, code=200):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == "/v2/stocks/ANT/trades/latest":
            assert self.headers["APCA-API-KEY-ID"] == "kid"
            return self.reply({"symbol": "ANT", "trade": {"p": state["price"], "t": "2026-11-19T15:00:00Z"}})
        if u.path == "/yt/videos":
            assert self.headers["Authorization"] == "Bearer at"
            return self.reply({"items": [{"snippet": {"title": state["title"], **state["snippet_extra"]}}]})
        self.reply({}, 404)

    def do_POST(self):
        self.rfile.read(int(self.headers["Content-Length"]))
        self.reply({"access_token": "at", "expires_in": 3599})

    def do_PUT(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        state["puts"].append(body)
        state["title"] = body["snippet"]["title"]
        self.reply(body)

    def log_message(self, *a):
        pass


srv = http.server.HTTPServer(("127.0.0.1", 0), Mock)
threading.Thread(target=srv.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{srv.server_port}"
os.environ.update(ALPACA_DATA_URL=base, YOUTUBE_URL=base + "/yt", GOOGLE_TOKEN_URL=base + "/token",
                  ALPACA_KEY_ID="kid", ALPACA_SECRET_KEY="ks", YOUTUBE_VIDEO_ID="YpJn6DwTLlk",
                  GOOGLE_CLIENT_ID="c", GOOGLE_CLIENT_SECRET="s", GOOGLE_REFRESH_TOKEN="r", MIN_UPDATE_SECONDS="0")
import price_title as pt  # noqa: E402


class T(unittest.TestCase):
    def setUp(self):
        state.update(price=83.2, title="A benefit single for a $83 stock", puts=[])
        self.w = pt.Watcher(pt.Config())

    def test_format(self):
        self.assertEqual(pt.fmt_price(83.5, 0), "$84")
        self.assertEqual(pt.fmt_price(1234.4, 0), "$1,234")
        self.assertEqual(pt.fmt_price(83.165, 2), "$83.17")
        self.assertEqual(pt.title_regex("A benefit single for a {price} stock").match(
            "A benefit single for a $1,234 stock").group(1), "$1,234")

    def test_no_change(self):
        self.w.check()
        self.assertEqual(state["puts"], [])

    def test_hysteresis(self):
        state["price"] = 83.55  # rounds to 84, but within 0.6 of 83
        self.w.check()
        self.assertEqual(state["puts"], [])
        state["price"] = 83.7
        self.w.check()
        self.assertEqual(state["title"], "A benefit single for a $84 stock")
        state["price"] = 83.45  # back under 83.5, within 0.6 of 84
        self.w.check()
        self.assertEqual(len(state["puts"]), 1)

    def test_keeps_the_rest_of_the_snippet(self):
        state["price"] = 91.0
        self.w.check()
        sn = state["puts"][0]["snippet"]
        self.assertEqual(sn, {"title": "A benefit single for a $91 stock", "description": "AI-generated satire...",
                              "tags": ["satire"], "categoryId": "10"})
        self.assertEqual(state["puts"][0]["id"], "YpJn6DwTLlk")

    def test_guard(self):
        state["title"] = "Share the Shares — an all-star benefit single (sort of)"
        state["price"] = 91.0
        self.w.check()
        self.assertEqual(state["puts"], [])

    def test_hand_edit_between_checks(self):
        self.w.check()
        state["title"] = "Something else"
        state["price"] = 91.0
        self.w.check()
        self.assertEqual(state["puts"], [])

    def test_min_interval(self):
        self.w.cfg.min_update = 900
        state["price"] = 91.0
        self.w.check()
        state["price"] = 95.0
        self.w.check()
        self.assertEqual([p["snippet"]["title"] for p in state["puts"]], ["A benefit single for a $91 stock"])

    def test_dry_run(self):
        self.w.cfg.dry_run = True
        state["price"] = 91.0
        self.w.check()
        self.assertEqual(state["puts"], [])


if __name__ == "__main__":
    unittest.main()
