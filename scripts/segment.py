"""Cut each figure, then its parts, from its ink piece with Segment Anything (ViT-B), from config/puppets.json.

The prompts (box + positive/negative points) are the agent's, logged in config; SAM traces the outlines. A part's
mask is clipped to its figure's. Writes assets/puppets/<figure>/masks/{figure,<part>}.png and preview.jpg (the
cut outlines over the ink). The SAM weights live in models/ (sha256 ec2df627…, md5 01ec64…).
Usage: segment.py [figure ...]  (default: all)
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
from segment_anything import SamPredictor, sam_model_registry

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "config/puppets.json").read_text())["figures"]
COLORS = [(0, 0, 255), (0, 160, 0), (255, 0, 0), (0, 140, 255), (200, 0, 200), (0, 200, 200)]


def cut(pred, spec, clip=None):
    pts = [(p, 1) for p in spec["pos"]] + [(p, 0) for p in spec.get("neg", [])]
    masks, scores, _ = pred.predict(point_coords=np.array([p for p, _ in pts], np.float32),
                                    point_labels=np.array([l for _, l in pts]),
                                    box=np.array(spec["box"], np.float32), multimask_output=True)
    m = masks[int(np.argmax(scores))]
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8)).astype(bool)
    if clip is not None:
        m &= clip
    return m, float(scores.max())


def cut_by_hand(shape, spec, clip):
    m = np.zeros(shape, np.uint8)
    for poly in spec.get("polys", []):
        cv2.fillPoly(m, [np.array(poly, np.int32)], 1)
    for x0, y0, x1, y1, wd in spec.get("strips", []):
        cv2.line(m, (x0, y0), (x1, y1), 1, wd)
    return m.astype(bool) & clip


def main(names):
    torch.manual_seed(0)
    sam = sam_model_registry["vit_b"](checkpoint=str(ROOT / "models/sam_vit_b_01ec64.pth"))
    pred = SamPredictor(sam)
    for name in names or CFG:
        f = CFG[name]
        ink = cv2.imread(str(ROOT / "assets/engravings/ink" / f"{f['piece']}.png"), cv2.IMREAD_GRAYSCALE)
        rgb = cv2.cvtColor(255 - ink, cv2.COLOR_GRAY2RGB)  # black lines on white, as printed
        pred.set_image(rgb)
        out = ROOT / "assets/puppets" / name / "masks"
        out.mkdir(parents=True, exist_ok=True)
        fig, s = cut(pred, f["figure"])
        cv2.imwrite(str(out / "figure.png"), fig.astype(np.uint8) * 255)
        report = {"figure": round(s, 3)}
        prev = cv2.cvtColor(255 - ink, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(prev, cv2.findContours(fig.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0], -1, (60, 60, 60), 4)
        for i, (pn, p) in enumerate(f["parts"].items()):
            if "cut" in p:
                m, s = cut_by_hand(fig.shape, p["cut"], fig), 1.0
            else:
                m, s = cut(pred, p, clip=fig)
            cv2.imwrite(str(out / f"{pn}.png"), m.astype(np.uint8) * 255)
            report[pn] = round(s, 3)
            c = COLORS[i % len(COLORS)]
            cv2.drawContours(prev, cv2.findContours(m.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0], -1, c, 4)
            cv2.circle(prev, tuple(p["pivot"]), 12, c, -1)
            cv2.putText(prev, pn, (p["box"][0], p["box"][1] + 30), cv2.FONT_HERSHEY_SIMPLEX, 1.1, c, 3)
        cv2.imwrite(str(out.parent / "preview.jpg"), prev, [cv2.IMWRITE_JPEG_QUALITY, 85])
        print(name, report)


if __name__ == "__main__":
    main(sys.argv[1:])
