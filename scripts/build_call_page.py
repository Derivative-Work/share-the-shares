"""The call page as one file to carry to the Mac: apps/call_page/index.html with the built-in backgrounds inlined.

The source page (in git) has no images; this writes deliverables/call_page/call_page.html (git-ignored, in the
manifest) with the boardroom and the fund's slide from deliverables/call_backgrounds/ as WebP data URLs, 2560 x 1440
(the call tile is at most about that wide on the Mac's screen).
Usage: .venv/bin/python -I scripts/build_call_page.py
"""
import base64
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "apps/call_page/index.html"
OUT = ROOT / "deliverables/call_page/call_page.html"
BGS = {"boardroom": ("boardroom_3840.png", 80), "slide": ("fund_slide_3840.png", 85)}
MARK = "/*BACKGROUNDS*/{}/*END*/"


def main():
    page = SRC.read_text()
    assert page.count(MARK) == 1, "the page's background marker"
    parts = []
    for name, (fn, q) in BGS.items():
        img = cv2.imread(str(ROOT / "deliverables/call_backgrounds" / fn))
        img = cv2.resize(img, (2560, 1440), interpolation=cv2.INTER_AREA)
        ok, buf = cv2.imencode(".webp", img, [cv2.IMWRITE_WEBP_QUALITY, q])
        assert ok
        parts.append(f'"{name}": "data:image/webp;base64,{base64.b64encode(buf.tobytes()).decode()}"')
        print(name, len(buf), "bytes")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page.replace(MARK, "/*BACKGROUNDS*/{" + ", ".join(parts) + "}/*END*/"))
    print(OUT, OUT.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
