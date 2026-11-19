"""The five Shorts (the human, 2026-11-19: "Make all of them, then I'll release as appropriate"), 1080x1920, 24 fps,
cut from the human's final cut (DaVinci Resolve export, master timing):

  1_verse      "Do I get a say?": the end of chorus 2, the session reveal, the live verse on the call, the bridge's return
               through "a fifth of us, all told"
  2_pitch      the Lawyer's "It's not a charity, per se" through chorus 1's "so help us grow, so we can give"
  3_hand       the final chorus: the coupons, "at our discretion", "do I get a say?" on the call, nobody answers
  4_threshold  the bridge: "And it's real", the thermometer, THRESHOLD MET* and "When it's not!"
  5_pledge     "Phone lines open at the IPO", the drawer, the pledge line, the hold music and the fact card, its marked
               lines spelled out large below the picture

Layout (stacked, as All Systems Operational's Short): paper, "AI-GENERATED SATIRE" in the pen's red (a Short has no
fact card or credits, which are where the video's disclosure is) and the title at the top; the picture in the middle,
16:9 full width, except on the call page, which is cropped to 6:5 around the tile (found per frame: the page's dark
header over a light tile); the lyric below. Clear of what Shorts covers: the top 140 px, the bottom 330 and the buttons
down the right.
Usage: .venv/bin/python -I scripts/shorts.py CUT.mov [OUT DIR] [--only=1_verse,...]   (default deliverables/shorts/)
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from thumbnails import ABRIL, LOOK, PAL, PEN  # noqa: E402

W, H, FPS = 1080, 1920, 24
BOX = (420, 1320)             # the picture's band: the call's 6:5 crop fills it, a 16:9 shot is centred in it
CALL_CROP = (370, 220, 888, 740)  # x, y, w, h in the 1920x1080 cut: the call tile around the face
CAP_Y = 1420
SRT = ROOT / "deliverables/share_the_shares.en.srt"
FELL_SC = str(ROOT / LOOK["fonts"]["small_caps"])
FELL_IT = str(ROOT / LOOK["fonts"]["body_italic"])

T_CARD = 296.44  # S47, the fact card (master/cut time)
SHORTS = {
    "1_verse": (156.4, 199.3, "the stakeholder input session"),
    "2_pitch": (46.7, 98.7, "a charity single for the IPO"),
    "3_hand": (219.9, 248.4, "the final chorus"),
    "4_threshold": (192.4, 220.3, "the bridge"),
    "5_pledge": (265.6, 317.33, "the pledge line"),
}
# the fact card's marked lines, spelled out while the card is up (graphics.html: the pen from 5.2 s, a mark a second)
FACTS = [
    (0.5, 5.2, "Anthropic commits 5% of its shares to its Public Benefit Fund, as Class N shares with no vote.", None),
    (5.2, 8.2, "The board may add 2% more for every 50% rise in the share price, starting from the IPO price.",
     "It’s not required to."),
    (8.2, 11.2, "Set up as an LLC, not a 501(c)(3)…", "which legally allows non-charitable activities"),
    (11.2, 14.2, "The fund’s equity won’t be used for lobbying or political giving.", "So they say."),
    (14.2, 17.2, "The fund’s governance structure: to be announced.", None),
    (17.2, 20.85, "Anthropic’s IPO: priced November 18, 2026, at $83. Trading on Nasdaq as ANT.", None),
]


def ass_colour(hx, a=0):
    return f"&H{a:02X}{hx[5:7]}{hx[3:5]}{hx[1:3]}".upper()


def srt_cues():
    out = []
    for blk in SRT.read_text().strip().split("\n\n"):
        ln = blk.splitlines()
        a, b = ln[1].split(" --> ")
        sec = lambda x: sum(float(v) * m for v, m in zip(re.split("[:,]", x), (3600, 60, 1, 0.001)))
        out.append((sec(a), sec(b), " ".join(ln[2:])))
    return out


def stamp(t):
    cs = int(round(max(0, t) * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def ass(name, t0, t1):
    sep, pen = ass_colour(PAL["ink_sepia"]), ass_colour(PEN)
    L = ["[Script Info]", "ScriptType: v4.00+", "YCbCr Matrix: None", f"PlayResX: {W}", f"PlayResY: {H}",
         "WrapStyle: 0", "", "[V4+ Styles]",
         "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
         "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
         "MarginR, MarginV, Encoding",
         f"Style: Lyric,IM FELL English,68,{sep},{sep},{sep},&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,60,150,0,1",
         f"Style: Fact,IM FELL English,50,{sep},{sep},{sep},&H00000000,0,0,0,0,100,100,0,0,1,0,0,8,60,150,0,1",
         f"Style: Pen,Caveat,66,{pen},{pen},{pen},&H00000000,1,0,0,0,100,100,0,0,1,0,0,8,60,150,0,1",
         "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    cx = (60 + W - 150) // 2
    for a, b, text in srt_cues():
        if b <= t0 or a >= t1 or text.startswith("["):
            continue
        text = text.replace("♪ ", "")
        L.append(f"Dialogue: 0,{stamp(a - t0)},{stamp(min(b, t1) - t0)},Lyric,,0,0,0,,{{\\pos({cx},{CAP_Y})}}{text}")
    if name == "5_pledge":
        for a, b, fact, note in FACTS:
            a, b = T_CARD + a - t0, T_CARD + b - t0
            L.append(f"Dialogue: 0,{stamp(a)},{stamp(b)},Fact,,0,0,0,,{{\\pos({cx},{BOX[1] + 30})\\fad(150,150)}}{fact}")
            if note:
                L.append(f"Dialogue: 0,{stamp(a + 0.5)},{stamp(b)},Pen,,0,0,0,,{{\\pos({cx},{BOX[1] + 210})"
                         f"\\frz2\\fad(250,150)}}{note}")
    return "\n".join(L) + "\n"


def backdrop(sub, path):
    img = Image.new("RGB", (W, H), PAL["paper"])
    d = ImageDraw.Draw(img)
    d.text((W / 2, 185), "AI-GENERATED SATIRE", font=ImageFont.truetype(FELL_SC, 40), fill=PEN, anchor="mm")
    d.text((W / 2, 270), "SHARE THE SHARES", font=ImageFont.truetype(ABRIL, 92), fill=PAL["ink_sepia"], anchor="mm")
    d.line((140, 330, W - 140, 330), fill=PAL["ink_sepia"], width=3)
    d.line((140, 337, W - 140, 337), fill=PAL["ink_sepia"], width=1)
    d.text((W / 2, 378), sub, font=ImageFont.truetype(FELL_IT, 44), fill=PAL["ink_sepia"], anchor="mm")
    img.save(path)


def call_frames(cut, t0, t1):
    """Per frame of the span: is it the call page? (its dark header over the light tile), held for 4+ frames."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t0:.3f}", "-t", f"{t1 - t0:.3f}", "-i", str(cut), "-vf",
                          "scale=192:108,format=gray", "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    F = np.frombuffer(raw, np.uint8).reshape(-1, 108, 192).astype(np.float32)
    call = (F[:, 12:16, 15:178].mean((1, 2)) < 45) & (F[:, 30:80, 30:130].mean((1, 2)) > 120)
    runs, k = [], 0
    while k < len(call):
        j = k
        while j < len(call) and call[j] == call[k]:
            j += 1
        runs.append([call[k], k, j])
        k = j
    for r in runs:  # a blip shorter than 4 frames takes its neighbours' mode
        if r[2] - r[1] < 4:
            r[0] = not r[0]
    spans = [(a / FPS, b / FPS) for c, a, b in runs if c]
    return spans


def build(cut, name, out, tmp):
    t0, t1, sub = SHORTS[name]
    bg = Path(tmp) / f"bg_{name}.png"
    backdrop(sub, bg)
    sub_ass = Path(tmp) / f"{name}.ass"
    sub_ass.write_text(ass(name, t0, t1))
    calls = call_frames(cut, t0, t1)
    on = "+".join(f"between(t,{a:.3f},{b - 0.001:.3f})" for a, b in calls) or "0"
    x, y, cw, ch = CALL_CROP
    bh = BOX[1] - BOX[0]
    sy = BOX[0] + (bh - 608) // 2
    dur = t1 - t0
    fc = (f"[0:v]split=2[a][b];[a]scale={W}:608:flags=lanczos[s];"
          f"[b]crop={cw}:{ch}:{x}:{y},scale={W}:{bh}:flags=lanczos[c];"
          f"[1:v][s]overlay=0:{sy}:enable='not({on})'[v1];[v1][c]overlay=0:{BOX[0]}:enable='{on}'[v2];"
          f"[v2]ass={sub_ass}:fontsdir={ROOT / 'assets/fonts'},format=yuv420p[v]")
    o = Path(out) / f"share_the_shares_short_{name}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}", "-i", str(cut),
                    "-loop", "1", "-framerate", str(FPS), "-i", str(bg), "-filter_complex", fc, "-map", "[v]",
                    "-map", "0:a:0", "-af", f"afade=t=in:d=0.15,afade=t=out:st={dur - 0.6:.3f}:d=0.6",
                    "-t", f"{dur:.3f}", "-r", str(FPS), "-c:v", "libx264", "-preset", "slow", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", str(o)], check=True)
    return o, calls


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    only = next((a[7:].split(",") for a in sys.argv[1:] if a.startswith("--only=")), None)
    cut = Path(args[0]).expanduser()
    out = Path(args[1]) if len(args) > 1 else ROOT / "deliverables/shorts"
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for name in SHORTS:
            if only and name not in only:
                continue
            o, calls = build(cut, name, out, tmp)
            t0 = SHORTS[name][0]
            d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(o)],
                               capture_output=True, text=True).stdout.strip()
            print(o, f"{float(d):.2f} s", "call:", [(round(a + t0, 2), round(b + t0, 2)) for a, b in calls])


if __name__ == "__main__":
    main()
