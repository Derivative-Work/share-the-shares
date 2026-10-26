"""C5 prop sheet: every engraved prop (scripts/props.py) printed in the certificate's inks on its paper, each with its
shots and its source, for review before the props go into the shots.

Usage: .venv/bin/python -I scripts/c5_prop_sheet.py <out.jpg>
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
LOOK = json.loads((ROOT / "config/look.json").read_text())
CFG = json.loads((ROOT / "config/props.json").read_text())["props"]
INK = ROOT / "assets/engravings/ink/props"
SOURCES = {r.split("\t")[0]: r.split("\t") for r in (ROOT / "assets/engravings/sources.tsv").read_text().splitlines()
           if r and not r.startswith(("#", "file\t"))}
PAL = {k: np.array([int(v[i:i + 2], 16) for i in (1, 3, 5)], np.float32) for k, v in LOOK["palette"].items()}

# (tile, the prop files it prints, its config entry); in shot order
TILES = [
    ("studio", ["studio"], "studio"), ("mic", ["mic"], "mic"), ("door", ["door", "door_plaque@0.5,0.272,0.5"], "door"),
    ("calendar", ["calendar"], "calendar"),
    ("calendar pages", [f"calendar_page_{i}" for i in range(10)], "calendar_pages"),
    ("stamp", ["stamp"], "stamp"), ("coins", ["coins", "coin_face"], "coins"), ("quill", ["quill"], "quill"),
    ("eraser", ["eraser"], "eraser"), ("scroll", ["scroll"], "scroll"),
    ("transfer form (the back)", ["transfer_form"], "transfer_form"), ("face down", ["face_down"], "face_down"),
    ("thermometer", ["thermometer_full"], "thermometer_scale"), ("seal", ["seal", "seal_emboss"], "seal"),
    ("ledger", ["ledger"], "ledger"), ("scissors", ["scissors"], "scissors"), ("filing cabinet", ["cabinet"], "cabinet"),
]
TW, TH = 900, 760  # tile size; the picture fits in TW x (TH - 120)


def ink_rgb(sepia, green=None, emboss=False):
    """Two plates over the paper, as the certificate prints (subtractive: each ink darkens toward its colour)."""
    paper = np.broadcast_to(PAL["paper"], sepia.shape + (3,)).copy()
    if emboss:  # a blind emboss: light and shade from the height map, no ink
        gy, gx = np.gradient(cv2.GaussianBlur(sepia.astype(np.float32), (0, 0), 1.5) / 255.0)
        shade = np.clip((gx + gy) * 6.0, -0.35, 0.35)[..., None]
        return np.clip(paper * (1 + shade), 0, 255)
    out = paper
    for plate, col in ((green, PAL["ink_green"]), (sepia, PAL["ink_sepia"])):
        if plate is not None:
            a = (plate.astype(np.float32) / 255.0)[..., None]
            out = out * (1 - a) + col * a
    return out


def load(name):
    img = cv2.imread(str(INK / f"{name}.png"), cv2.IMREAD_GRAYSCALE)
    green = INK / f"{name}_green.png"
    return img, (cv2.imread(str(green), cv2.IMREAD_GRAYSCALE) if green.exists() else None)


def fit(img, w, h):
    s = min(w / img.shape[1], h / img.shape[0])
    return cv2.resize(img, (max(1, int(img.shape[1] * s)), max(1, int(img.shape[0] * s))), interpolation=cv2.INTER_AREA)


def tile_picture(names):
    """One prop's picture: a single piece, a piece with an inset placed on it (name@x,y,width), or a row of pieces."""
    pics = []
    base = None
    for spec in names:
        name, _, at = spec.partition("@")
        sep, green = load(name)
        rgb = ink_rgb(sep, green, emboss=name.endswith("_emboss"))
        if at and base is not None:
            fx, fy, fw = (float(v) for v in at.split(","))
            ins = cv2.resize(rgb, (int(base.shape[1] * fw), int(base.shape[1] * fw * rgb.shape[0] / rgb.shape[1])))
            x, y = int(base.shape[1] * fx - ins.shape[1] / 2), int(base.shape[0] * fy - ins.shape[0] / 2)
            base[y:y + ins.shape[0], x:x + ins.shape[1]] = ins
            continue
        base = rgb
        pics.append(base)
    h = max(p.shape[0] for p in pics)
    row = [cv2.resize(p, (int(p.shape[1] * h / p.shape[0]), h)) for p in pics]
    gap = np.broadcast_to(PAL["paper"], (h, max(8, h // 30), 3))
    per = 5 if len(row) > 6 else len(row)  # many pieces (the calendar's pages) set in rows
    lines = []
    for i in range(0, len(row), per):
        out = row[i]
        for p in row[i + 1:i + per]:
            out = np.hstack([out, gap, p])
        lines.append(out)
    if len(lines) == 1:
        return lines[0]
    w = max(ln.shape[1] for ln in lines)
    lines = [np.hstack([ln, np.broadcast_to(PAL["paper"], (h, w - ln.shape[1], 3))]) for ln in lines]
    vgap = np.broadcast_to(PAL["paper"], (h // 12, w, 3))
    return np.vstack([lines[0]] + [np.vstack([vgap, ln]) for ln in lines[1:]])


def source_line(entry):
    if entry.get("kind") != "cut":
        return "generated: the certificate's type, lathe work and hatching"
    r = SOURCES.get(entry["source"])
    if not r:
        return entry["source"]
    return f"{r[1][:70]} · {r[2]}, {r[3]} · {r[7].split(' (')[0]}"


def main(out):
    cols = 4
    rows = (len(TILES) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * TW, rows * TH + 110), tuple(int(v) for v in PAL["paper_shadow"]))
    d = ImageDraw.Draw(sheet)
    f_title = ImageFont.truetype(str(ROOT / LOOK["fonts"]["display"]), 64)
    f_head = ImageFont.truetype(str(ROOT / LOOK["fonts"]["small_caps"]), 34)
    f_note = ImageFont.truetype(str(ROOT / LOOK["fonts"]["body_italic"]), 22)
    d.text((30, 20), "C5 PROPS", font=f_title, fill=tuple(int(v) for v in PAL["ink_sepia"]))
    d.text((420, 50), "each prop in the certificate's inks; shots and sources under each", font=f_head,
           fill=tuple(int(v) for v in PAL["ink_sepia"]))
    for i, (title, names, key) in enumerate(TILES):
        x, y = (i % cols) * TW, (i // cols) * TH + 110
        pic = fit(tile_picture(names), TW - 40, TH - 130)
        card = Image.new("RGB", (TW - 16, TH - 16), tuple(int(v) for v in PAL["paper"]))
        card.paste(Image.fromarray(pic.astype(np.uint8)), ((TW - 16 - pic.shape[1]) // 2, 12))
        sheet.paste(card, (x + 8, y + 8))
        entry = CFG[key]
        d.text((x + 24, y + TH - 112), f"{title.upper()}  ·  {', '.join(entry['shots'])}", font=f_head,
               fill=tuple(int(v) for v in PAL["ink_sepia"]))
        d.text((x + 24, y + TH - 70), source_line(entry), font=f_note, fill=(90, 70, 50))
        d.text((x + 24, y + TH - 44), entry["role"][:96], font=f_note, fill=(90, 70, 50))
    sheet.save(out, quality=90)
    print(out, sheet.size)


if __name__ == "__main__":
    main(sys.argv[1])
