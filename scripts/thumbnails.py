"""The YouTube thumbnail options (METADATA.md, "Clickbait-adjacent titles and thumbnails"), 1280x720 JPEG, each from a
frame of the human's final cut (DaVinci Resolve export, 1920x1080, master timing).

Type: Abril Fatface for the engraved caps, Caveat for the fact card's red pen; the certificate's palette
(config/look.json). Frames that show the desk's papers or the Mac's screen are cropped to the phone, the call or the
player: the email, the terminal and the browser tabs stay out.

Usage: .venv/bin/python -I scripts/thumbnails.py CUT.mov [OUT DIR] [--only=2a_say,2b_say]   (default deliverables/thumbnails/)
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
LOOK = json.loads((ROOT / "config/look.json").read_text())
PAL = LOOK["palette"]
W, H = 1280, 720
PEN = "#B3261E"  # the fact card's red pen (overlays/graphics.html --pen)
ABRIL = str(ROOT / LOOK["fonts"]["display"])
CAVEAT = str(ROOT / "assets/fonts/Caveat-Variable.ttf")
FELL_IT = str(ROOT / LOOK["fonts"]["body_italic"])


def font(path, size, weight=None):
    f = ImageFont.truetype(path, size)
    if weight:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


def frame(cut, t, tmp):
    out = Path(tmp) / f"f_{t}.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", str(cut), "-frames:v", "1", str(out)], check=True)
    return Image.open(out).convert("RGB")


def crop(img, box):
    """box = (x0, y0, x1, y1) in the 1920x1080 frame, widened or heightened to 16:9 about its centre, then to WxH."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    if w / h > 16 / 9:
        h2 = w * 9 / 16
        y0, y1 = (y0 + y1) / 2 - h2 / 2, (y0 + y1) / 2 + h2 / 2
    else:
        w2 = h * 16 / 9
        x0, x1 = (x0 + x1) / 2 - w2 / 2, (x0 + x1) / 2 + w2 / 2
    return img.crop((round(x0), round(y0), round(x1), round(y1))).resize((W, H), Image.LANCZOS)


def text(img, xy, s, f, fill, anchor="la", stroke=0, stroke_fill=None, shadow=0, rotate=0):
    """Text with an optional soft shadow and a small rotation (the pen's lean)."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=stroke_fill)
    if rotate:
        bb = d.textbbox(xy, s, font=f, anchor=anchor, stroke_width=stroke)
        layer = layer.rotate(rotate, resample=Image.BICUBIC, center=((bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2))
    if shadow:
        a = layer.split()[3].filter(ImageFilter.GaussianBlur(shadow))
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sh.putalpha(a.point(lambda v: int(v * 0.75)))
        img.paste(sh, (0, 0), sh)
    img.paste(layer, (0, 0), layer)


def ellipse(img, box, width=7, color=PEN):
    """A hand-drawn loop: an ellipse that overshoots its start a little."""
    d = ImageDraw.Draw(img)
    d.arc(box, start=-160, end=215, fill=color, width=width)
    x0, y0, x1, y1 = box
    d.arc((x0 - 6, y0 + 4, x1 + 6, y1 - 4), start=200, end=235, fill=color, width=width - 2)


def band(img, y0, y1, color=PAL["paper"], alpha=235):
    over = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(over).rectangle((0, y0, W, y1), fill=color + "%02x" % alpha)
    img.paste(over, (0, 0), over)


def vignette(img, strength=0.55):
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse((-W * 0.25, -H * 0.3, W * 1.25, H * 1.3), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(120))
    dark = Image.new("RGB", (W, H), (0, 0, 0))
    return Image.composite(img, Image.blend(img, dark, strength), m)


# ---- the eight options --------------------------------------------------------------------------------------------

def t1_participant(cut, tmp):
    """I was the only one who showed up to the stakeholder meeting: the call, singing, and the participant list."""
    f = frame(cut, 172, tmp)
    img = crop(f, (150, 300, 1328, 960))  # the tile without its right edge: the singer right of centre, the slide's mark
    img = vignette(img, 0.2)
    # the participant list, enlarged, as a card on the right
    plist = f.crop((1500, 180, 1790, 370)).resize((round(290 * 1.3), round(190 * 1.3)), Image.LANCZOS)
    card = Image.new("RGB", (plist.width + 20, plist.height + 20), "#2a2a30")
    card.paste(plist, (10, 10))
    cx, cy = 24, 150
    img.paste(card, (cx, cy))
    ellipse(img, (cx + 4, cy + 172, cx + card.width - 2, cy + 246), width=6)
    text(img, (cx + card.width / 2, cy + card.height + 52), "no-show", font(CAVEAT, 70, 700), PEN, "mm", rotate=4,
         stroke=4, stroke_fill=PAL["paper"], shadow=3)
    band(img, 585, 720, PAL["ink_sepia"], 230)
    text(img, (36, 655), "1 PARTICIPANT", font(ABRIL, 112), PAL["paper"], "lm", shadow=6)
    return img


def t2_say(cut, tmp):
    """They're giving away 5% of the company. I asked one question: close on the face (S40)."""
    f = frame(cut, 240.3, tmp)
    img = crop(f, (150, 213, 1478, 960))
    text(img, (60, 210), "DO I GET", font(CAVEAT, 150, 700), PEN, "lm", rotate=-4, stroke=5, stroke_fill=PAL["paper"],
         shadow=4)
    text(img, (70, 360), "A SAY?", font(CAVEAT, 170, 700), PEN, "lm", rotate=-4, stroke=5, stroke_fill=PAL["paper"],
         shadow=4)
    return img


def _say_base(cut, tmp):
    """The S40 close-up with the face pushed right of centre: the left half is the slide's plain paper."""
    f = frame(cut, 240.3, tmp)
    return crop(f, (150, 200, 1250, 819))


def t2a_say(cut, tmp):
    """#2, more legible: the pen, bigger and heavier, on the clear paper left of the face, with a dark edge."""
    img = _say_base(cut, tmp)
    for y, s_, size in ((215, "DO I GET", 132), (375, "A SAY?", 158)):
        text(img, (30, y), s_, font(CAVEAT, size, 700), PEN, "lm", rotate=-3, stroke=11, stroke_fill="#FFFFFF",
             shadow=10)
    return img


def t2b_say(cut, tmp):
    """#2, engraved: the question in Abril caps, sepia on the paper, the pen underlining SAY."""
    img = _say_base(cut, tmp)
    band(img, 0, 720, PAL["paper"], 0)
    f1, f2 = font(ABRIL, 92), font(ABRIL, 136)
    text(img, (34, 230), "DO I GET", f1, PAL["ink_sepia"], "lm", stroke=6, stroke_fill=PAL["paper"], shadow=6)
    text(img, (30, 370), "A SAY?", f2, PAL["ink_sepia"], "lm", stroke=6, stroke_fill=PAL["paper"], shadow=6)
    d = ImageDraw.Draw(img)
    w = d.textlength("A SAY?", font=f2)
    d.line([(36, 452), (30 + w * 0.55, 446), (30 + w - 6, 456)], fill=PEN, width=10, joint="curve")
    return img


def t2c_say(cut, tmp):
    """#2, as a sticky note: the pen's question on a cream card with a shadow, tilted, over the paper."""
    img = _say_base(cut, tmp).convert("RGBA")
    card = Image.new("RGBA", (450, 330), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((10, 10, 440, 320), 14, fill="#FFF8E1", outline=PAL["paper_shadow"], width=3)
    t = Image.new("RGB", card.size)
    text(card, (225, 110), "DO I GET", font(CAVEAT, 112, 700), PEN, "mm")
    text(card, (225, 240), "A SAY?", font(CAVEAT, 136, 700), PEN, "mm")
    card = card.rotate(5, resample=Image.BICUBIC, expand=True)
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    a = card.split()[3].point(lambda v: int(v * 0.55)).filter(ImageFilter.GaussianBlur(14))
    sh.paste((0, 0, 0, 255), (44, 196), a)
    img.alpha_composite(sh)
    img.alpha_composite(card, (28, 176))
    return img.convert("RGB")


def t3_itself(cut, tmp):
    """Anthropic's AI wrote a charity single about Anthropic's IPO: the session, with the video sent as a file."""
    f = frame(cut, 164.5, tmp)
    img = crop(f, (488, 88, 1420, 612))  # the conversation's column: the session title and the player, nothing else
    img = vignette(img, 0.35)
    ellipse(img, (175, 205, 900, 640), width=8)
    band(img, 0, 120, "#141210", 235)
    text(img, (W / 2, 62), "IT MADE THIS ABOUT ITSELF", font(ABRIL, 82), PAL["paper"], "mm", shadow=6)
    return img


def t4_hold(cut, tmp):
    """I called the pledge line. Please hold: the phone on the certificate, on hold."""
    f = frame(cut, 292, tmp)
    img = crop(f, (280, 470, 1290, 1038))  # the phone, the stub and the 5% corner; the email above stays out
    img = vignette(img, 0.3)
    text(img, (1210, 110), "PLEASE", font(ABRIL, 120), PAL["ink_sepia"], "rm", stroke=6, stroke_fill=PAL["paper"],
         shadow=5)
    text(img, (1210, 240), "HOLD", font(ABRIL, 150), PAL["ink_sepia"], "rm", stroke=6, stroke_fill=PAL["paper"],
         shadow=5)
    return img


def t5_seal(cut, tmp):
    """"Threshold met*" (*based on what we expect): the seal just embossed, its footnote whole and circled. Contrast
    raised so the blind emboss reads at thumbnail size."""
    f = frame(cut, 212.3, tmp)
    img = ImageEnhance.Contrast(crop(f, (200, 40, 1700, 1000))).enhance(1.45)
    ellipse(img, (245, 590, 940, 695), width=8)
    text(img, (1080, 600), "says who?", font(CAVEAT, 92, 700), PEN, "mm", rotate=8, stroke=3, stroke_fill=PAL["paper"])
    return img

def t6_buy(cut, tmp):
    """Help us grow, so we can give (buy the stock): the certificate, 5% in every corner."""
    f = frame(cut, 66, tmp)
    img = crop(f, (120, 20, 1780, 1050))
    img = vignette(img, 0.25)
    text(img, (W / 2, 640), "BUY TO GIVE?", font(ABRIL, 112), PAL["paper"], "mm", stroke=8, stroke_fill=PAL["ink_sepia"],
         shadow=6)
    return img


def t7_required(cut, tmp):
    """The board may add 2%. It's not required to: the fact card's line, enlarged, with the pen's note."""
    f = frame(cut, 316, tmp)
    img = Image.new("RGB", (W, H), PAL["paper"])
    strip = f.crop((150, 322, 1500, 366))  # "The board may add 2% more ..." (1080p card, below the note's arrow)
    strip = strip.resize((W - 60, round(44 * (W - 60) / 1350)), Image.LANCZOS)
    img.paste(strip, (30, 300))
    d = ImageDraw.Draw(img)
    d.rectangle((14, 14, W - 15, H - 15), outline=PAL["ink_green"], width=10)
    d.rectangle((34, 34, W - 35, H - 35), outline=PAL["ink_green"], width=2)
    text(img, (W / 2, 150), "THE BOARD MAY ADD 2%", font(ABRIL, 92), PAL["ink_sepia"], "mm")
    # the pen: a loop round "may", the note under it
    mx = 30 + (330 - 150) * (W - 60) / 1350
    ellipse(img, (mx - 4, 292, mx + 132, 352), width=7)
    text(img, (W / 2 + 40, 520), "It’s not required to.", font(CAVEAT, 124, 700), PEN, "mm", rotate=3)
    return img


def t8_prudence(cut, tmp):
    """Share the Shares — an all-star benefit single (sort of): Prudence with her scissors raised (S38)."""
    f = frame(cut, 233.5, tmp)
    img = crop(f, (120, 60, 1500, 1060))
    band(img, 0, 150, PAL["paper"], 225)
    text(img, (W / 2, 80), "SHARE THE SHARES", font(ABRIL, 104), PAL["ink_sepia"], "mm")
    text(img, (W - 40, 660), "(sort of)", font(FELL_IT, 64), PAL["ink_sepia"], "rm", stroke=4, stroke_fill=PAL["paper"])
    return img


OPTIONS = [("1_participant", t1_participant), ("2_say", t2_say), ("2a_say", t2a_say), ("2b_say", t2b_say), ("2c_say", t2c_say), ("3_itself", t3_itself), ("4_hold", t4_hold),
           ("5_seal", t5_seal), ("6_buy", t6_buy), ("7_required", t7_required), ("8_prudence", t8_prudence)]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--only=")]
    only = next((a[7:].split(",") for a in sys.argv[1:] if a.startswith("--only=")), None)
    cut = Path(args[0]).expanduser()
    out = Path(args[1]) if len(args) > 1 else ROOT / "deliverables/thumbnails"
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tiles = []
        for name, fn in OPTIONS:
            if only and name not in only:
                continue
            img = fn(cut, tmp)
            p = out / f"thumbnail_{name}.jpg"
            img.save(p, quality=90, optimize=True)
            tiles.append(img)
            print(p, p.stat().st_size)
        rows = (len(tiles) + 1) // 2
        sheet = Image.new("RGB", (W * 2 + 30, (H + 15) * rows + 15), "#111")
        for k, im in enumerate(tiles):
            sheet.paste(im, (10 + (k % 2) * (W + 10), 15 + (k // 2) * (H + 15)))
        name = "contact_sheet.jpg" if not only else f"contact_sheet_{'_'.join(only)}.jpg"
        sheet.resize((sheet.width // 2, sheet.height // 2), Image.LANCZOS).save(out / name, quality=88)


if __name__ == "__main__":
    main()
