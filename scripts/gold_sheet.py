"""S36's gold re-ink as a picture: the certificate print with its green plate re-inked in gold, for the cards cut from
the print after the key change (S37's clipped coupons). The scene does the same mix in the sheet's shader
(animatic.py gold_reink): colour -> mix(colour, paper x gold, green-plate coverage).

Usage: .venv/bin/python -I scripts/gold_sheet.py <certificate dir>  ->  <dir>/sheet_gold.png
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
PAL = json.loads((ROOT / "config/look.json").read_text())["palette"]


def lin(hx):
    c = np.array([int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5)])
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def main(d):
    d = Path(d)
    sheet = cv2.imread(str(d / "sheet.png"), cv2.IMREAD_COLOR)[..., ::-1].astype(np.float64) / 255
    green = cv2.imread(str(d / "plate_green.png"), cv2.IMREAD_GRAYSCALE).astype(np.float64)[..., None] / 255
    s_lin = np.where(sheet <= 0.04045, sheet / 12.92, ((sheet + 0.055) / 1.055) ** 2.4)
    gold = lin(PAL["paper"]) * lin(PAL["ink_gold"])
    out = s_lin * (1 - green) + gold * green
    out = np.where(out <= 0.0031308, out * 12.92, 1.055 * out ** (1 / 2.4) - 0.055)
    cv2.imwrite(str(d / "sheet_gold.png"), np.round(np.clip(out, 0, 1) * 255).astype(np.uint8)[..., ::-1])
    print(d / "sheet_gold.png")


if __name__ == "__main__":
    main(sys.argv[1])
