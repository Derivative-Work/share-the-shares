"""The phone's screen for S45-S46 (config/phone_dialer.json): an invented dialer types the pledge number on the
post-roll's DTMF timing (config/postroll.json), each key lighting as its tone plays; the call screen shows 'Calling'
over the ring, then 'On hold' with a timer through the hold music; 'Call ended' at the hang-up. Portrait, H.264 with
the post-roll's sound to the hang-up, to play full screen on the human's phone.

Usage: .venv/bin/python -I scripts/phone_dialer.py  ->  deliverables/phone/S45_S46_dialer.mp4
"""
import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "config/phone_dialer.json").read_text())
POST = json.loads((ROOT / "config/postroll.json").read_text())
OUT = ROOT / "deliverables/phone/S45_S46_dialer.mp4"
SS = 2  # drawn at twice the size, then reduced, for smooth edges
FONT = ROOT / "assets/fonts/NotoSans-Regular.ttf"
BOLD = ROOT / "assets/fonts/NotoSans-Bold.ttf"
BG, KEY, KEY_LIT, INK, DIM = (0, 0, 0), (38, 38, 42), (120, 120, 128), (245, 245, 245), (150, 150, 158)
GREEN, RED = (52, 178, 90), (226, 64, 56)
KEYS = [("1", ""), ("2", "ABC"), ("3", "DEF"), ("4", "GHI"), ("5", "JKL"), ("6", "MNO"),
        ("7", "PQRS"), ("8", "TUV"), ("9", "WXYZ"), ("*", ""), ("0", "+"), ("#", "")]


def font(path, px):
    return ImageFont.truetype(str(path), px * SS)


def pretty(digits):
    return digits if len(digits) <= 3 else f"{digits[:3]}-{digits[3:]}"


def phone_icon(d, cx, cy, r, down=False):
    """A handset: two rounded ends on a curved grip; tipped down for hanging up."""
    s = r * 0.42
    a, b = (-0.62, 0.55), (0.62, -0.55)
    if down:
        a, b = (-0.75, 0.15), (0.75, 0.15)
    d.line([(cx + a[0] * s, cy + a[1] * s), (cx + b[0] * s, cy + b[1] * s)], fill=INK, width=int(s * 0.55))
    for x, y in (a, b):
        e = s * 0.42
        d.ellipse([cx + x * s - e, cy + y * s - e, cx + x * s + e, cy + y * s + e], fill=INK)


class Screen:
    def __init__(self):
        self.w, self.h = (v * SS for v in CFG["size"])
        self.r = int(self.w * 0.105)  # key radius
        self.cols = [self.w * x for x in (0.24, 0.5, 0.76)]
        self.row0, self.dy = self.h * 0.40, self.r * 2.45
        self.call_y = self.row0 + 4 * self.dy + self.r * 0.4

    def keypad(self, digits, lit, light):
        im = Image.new("RGB", (self.w, self.h), BG)
        d = ImageDraw.Draw(im)
        f = font(FONT, 92 if len(digits) < 8 else 84)
        d.text((self.w / 2, self.h * 0.25), pretty(digits), font=f, fill=INK, anchor="mm")
        big, small = font(FONT, 74), font(BOLD, 22)
        for i, (k, letters) in enumerate(KEYS):
            cx, cy = self.cols[i % 3], self.row0 + (i // 3) * self.dy
            c = tuple(int(KEY[j] + (KEY_LIT[j] - KEY[j]) * light) for j in range(3)) if k == lit else KEY
            d.ellipse([cx - self.r, cy - self.r, cx + self.r, cy + self.r], fill=c)
            d.text((cx, cy - (self.r * 0.12 if letters else 0)), k, font=big, fill=INK, anchor="mm")
            if letters:
                d.text((cx, cy + self.r * 0.5), letters, font=small, fill=DIM, anchor="mm")
        cx = self.w / 2
        d.ellipse([cx - self.r, self.call_y - self.r, cx + self.r, self.call_y + self.r], fill=GREEN)
        phone_icon(d, cx, self.call_y, self.r)
        return im

    def call(self, digits, status, ended=False):
        im = Image.new("RGB", (self.w, self.h), BG)
        d = ImageDraw.Draw(im)
        d.text((self.w / 2, self.h * 0.22), pretty(digits), font=font(FONT, 104), fill=INK, anchor="mm")
        d.text((self.w / 2, self.h * 0.22 + 120 * SS), status, font=font(FONT, 48), fill=RED if ended else DIM,
               anchor="mm")
        if not ended:
            cx = self.w / 2
            d.ellipse([cx - self.r, self.call_y - self.r, cx + self.r, self.call_y + self.r], fill=RED)
            phone_icon(d, cx, self.call_y, self.r, down=True)
        return im


def main():
    fps, lead = CFG["fps"], CFG["lead_in"]
    dl, number = POST["dial"], POST["number"]
    step = dl["tone"] + dl["gap"]
    dial_end = dl["start"] + len(number) * step
    ring_at = dial_end + POST["ring"]["after_dial"]
    connected = ring_at + POST["ring"]["length"]
    call_at = dial_end + CFG["call_after_dial"]
    hang = CFG["hang_up"]
    end = hang + CFG["ended_hold"] + CFG["tail"]
    n = int(round((lead + end) * fps))
    scr, cache = Screen(), {}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        for i in range(n):
            t = i / fps - lead  # post-roll time
            if t < call_at:
                typed = sum(1 for k in range(len(number)) if t >= dl["start"] + k * step)
                lit, light = None, 0.0
                if typed and t < dl["start"] + (typed - 1) * step + dl["tone"] + 0.12:
                    since = t - (dl["start"] + (typed - 1) * step)
                    lit, light = number[typed - 1], round(max(0.0, 1 - max(0.0, since - dl["tone"]) / 0.12), 2)
                key = ("pad", typed, lit, light)
                make = lambda: scr.keypad(number[:typed], lit, light)  # noqa: E731
            elif t < connected:
                key = ("calling", int((t - call_at) * 2) % 4)
                make = lambda: scr.call(number, "Calling" + "." * key[1])  # noqa: E731
            elif t < hang:
                s = int(t - connected)
                key = ("hold", s)
                make = lambda: scr.call(number, f"On hold  {s // 60}:{s % 60:02d}")  # noqa: E731
            elif t < hang + CFG["ended_hold"]:
                key = ("ended",)
                make = lambda: scr.call(number, "Call ended", ended=True)  # noqa: E731
            else:
                key = ("black",)
                make = lambda: Image.new("RGB", (scr.w, scr.h), BG)  # noqa: E731
            if key not in cache:
                cache[key] = make().resize(tuple(CFG["size"]), Image.LANCZOS)
            cache[key].save(f"{td}/f_{i:05d}.png")
        # the post-roll's sound from its start, cut at the hang-up, after the lead-in's silence
        af = (f"[1:a]atrim=0:{hang},afade=t=out:st={hang - 0.05}:d=0.05,adelay={int(lead * 1000)}:all=1,"
              f"apad=whole_dur={lead + end}[a]")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(fps), "-i", f"{td}/f_%05d.png",
                        "-i", str(ROOT / "audio/postroll/postroll.wav"), "-filter_complex", af, "-map", "0:v",
                        "-map", "[a]", "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(OUT)], check=True)
    print(f"{OUT.relative_to(ROOT)}: {n} frames ({lead + end:.2f} s); first digit at {lead + dl['start']:.2f} s, "
          f"call {lead + call_at:.2f} s, on hold {lead + connected:.2f} s, hang-up {lead + hang:.2f} s")


if __name__ == "__main__":
    main()
