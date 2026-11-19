#!/usr/bin/env python3
"""One-time: get the GOOGLE_REFRESH_TOKEN that lets price_title.py edit your video's title.

Run it on a computer with a browser (or over `ssh -L 8765:127.0.0.1:8765 vps` with --port 8765), sign in as the
channel that owns the video, and put the printed token in the service's environment. Standard library only.

  GOOGLE_CLIENT_ID=... GOOGLE_CLIENT_SECRET=... python3 authorize.py [--port 8765]

The OAuth client must be of type "Desktop app" (Google Cloud console > APIs & services > Credentials), in a project
with the YouTube Data API v3 enabled. Set the OAuth consent screen to "In production": while it is in "Testing",
Google expires refresh tokens after 7 days. Unverified is fine for your own channel (click through the warning).
"""
import base64
import hashlib
import http.server
import json
import os
import secrets
import sys
import urllib.parse
import urllib.request

SCOPE = "https://www.googleapis.com/auth/youtube"


def main():
    cid, csec = os.environ.get("GOOGLE_CLIENT_ID"), os.environ.get("GOOGLE_CLIENT_SECRET")
    if not cid or not csec:
        sys.exit("set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET")
    port = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else 0
    state = secrets.token_urlsafe(16)
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    got = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(self.path).query))
            if "code" not in q and "error" not in q:
                self.send_response(404)
                self.end_headers()
                return
            got.update(q)
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"Done. You can close this tab and go back to the terminal.\n")

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(("127.0.0.1", port), Handler)
    redirect = f"http://127.0.0.1:{srv.server_port}"
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        "client_id": cid, "redirect_uri": redirect, "response_type": "code", "scope": SCOPE,
        "access_type": "offline", "prompt": "consent", "state": state,
        "code_challenge": challenge, "code_challenge_method": "S256"})
    print("Open this in a browser and sign in as the channel that owns the video:\n\n" + url + "\n", flush=True)
    while not got:
        srv.handle_request()
    if got.get("error"):
        sys.exit(f"Google said: {got['error']}")
    if got.get("state") != state:
        sys.exit("state mismatch; try again")
    body = urllib.parse.urlencode({
        "code": got["code"], "client_id": cid, "client_secret": csec, "redirect_uri": redirect,
        "grant_type": "authorization_code", "code_verifier": verifier}).encode()
    with urllib.request.urlopen(urllib.request.Request("https://oauth2.googleapis.com/token", data=body)) as r:
        tok = json.load(r)
    if "refresh_token" not in tok:
        sys.exit(f"no refresh token in the reply: {sorted(tok)}")
    print("GOOGLE_REFRESH_TOKEN=" + tok["refresh_token"])


if __name__ == "__main__":
    main()
