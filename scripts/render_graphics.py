"""Render the graphics layer (overlays/graphics.html) for the animatic: each graphic as a PNG sequence at the
animatic's frame rate, for its shot's span (timing/timing_map.json, config/c4_shots.json placeholders).

Writes renders/c4/graphics/<job>/<frame>.png and renders/c4/graphics/jobs.json (each job's layer, video-time start in
song seconds, duration and frame count), which scripts/animatic_assemble.py composites.
  overlays on the rendered picture: the S02 title, the LIVE bug (steady on S13; blinking on S25-S25c), the S30
  "Post-filter: no change" tab;
  full frames: S01's stand-in screen, the live slates (S26, S29-S31, S40, S45, S46), the S47 fact card, S48's
  announcement page and the "Derived from" credits.
Usage: .venv/bin/python -I scripts/render_graphics.py [width height step [out dir [job ...]]]  (default 640 360 2,
       renders/c4/graphics; naming jobs re-renders only those, keeping the others' entries in jobs.json)
"""
import json
import subprocess
import sys
import urllib.parse
from pathlib import Path

TM = json.loads(Path("timing/timing_map.json").read_text())
PLAN = json.loads(Path("config/c4_shots.json").read_text())
FPS = TM["fps"]
PH = PLAN["placeholders"]
OUT = Path(sys.argv[4]) if len(sys.argv) > 4 else Path("renders/c4/graphics")
SHOTS = [s for s in TM["shots"] if s["t"] is not None]
SPAN = {s["id"]: (s["t"], SHOTS[k + 1]["t"] if k + 1 < len(SHOTS) else TM["duration_s"]) for k, s in enumerate(SHOTS)}


def interventions():
    return sum(1 for ln in Path("log/human_interventions.md").read_text().splitlines() if ln.startswith("## "))


def jobs():
    """(name, layer, start in song seconds, duration, extra query). Times before 0 are the pre-roll, after the song's
    end the post-roll."""
    J = []
    a, _ = SPAN["S02"]
    J.append(("title", "title", a + 0.6, SPAN["S03"][0] + 1.2 - (a + 0.6), {}))
    J.append(("bug_S13", "bug", *SPAN["S13"][:1], SPAN["S13"][1] - SPAN["S13"][0], {}))
    J.append(("bug_S25", "bug", SPAN["S25"][0], SPAN["S25c"][1] - SPAN["S25"][0], {"blink": "1"}))
    J.append(("postfilter", "postfilter", SPAN["S30"][0], SPAN["S30"][1] - SPAN["S30"][0], {}))
    pre = PH["S01"]["before_s"]
    if pre:  # S01 was retired at C5 (before_s 0): no card
        J.append(("S01", "s01", -pre, pre, {}))
    # brief rev 50: S26, S29, S31 and S40 are render (the file the screen recording plays); only S30, the call, is a
    # slate (until 2026-11-17 all five were, for the printed-sheet live shots)
    for sid in ("S30",):
        a, b = SPAN[sid]
        kind, text = PH[sid]["text"].split(" · ", 1)[1].split(": ", 1)
        J.append((f"slate_{sid}", "slate", a, b - a, {"id": sid, "kind": kind, "text": text, "still": "1"}))
    t = TM["duration_s"]
    for sid in ("S45", "S46", "S47", "S48"):
        d = PH[sid]["after_s"]
        if sid in ("S45", "S46"):
            kind, text = PH[sid]["text"].split(" · ", 1)[1].split(": ", 1)
            J.append((f"slate_{sid}", "slate", t, d, {"id": sid, "kind": kind, "text": text, "still": "1"}))
        elif sid == "S47":
            J.append(("fact", "fact", t, d, {}))
        else:  # S48: the real page, then the credits
            J.append(("announce", "announce", t, d * 0.45, {}))
            J.append(("credits", "credits", t + d * 0.45, d * 0.55, {"interventions": str(interventions())}))
        t += d
    return J


def main():
    w, h, step = (int(a) for a in sys.argv[1:4]) if len(sys.argv) > 3 else (640, 360, 2)
    fps = FPS / step
    OUT.mkdir(parents=True, exist_ok=True)
    data = Path("overlays/data")
    data.mkdir(exist_ok=True)
    s01 = {"style": Path("log/prompts/suno/style_prompt.txt").read_text(),
           "lyrics": Path("log/prompts/suno/fetch_accepted/lyrics.txt").read_text()}
    (data / "s01.js").write_text("window.S01 = " + json.dumps(s01) + ";\n")
    # the fact card's IPO line (config/fact_card.json)
    (data / "fact.js").write_text("window.FACT = " + Path("config/fact_card.json").read_text().strip() + ";\n")
    only = sys.argv[5:]
    old = {j["name"]: j for j in json.loads((OUT / "jobs.json").read_text())["jobs"]} if only else {}
    meta = []
    for name, layer, start, dur, extra in jobs():
        if only and name not in only and name in old:
            meta.append(old[name])
            continue
        still = extra.pop("still", None)
        n = 1 if still else max(1, int(round(dur * fps)))
        q = urllib.parse.urlencode({"layer": layer, "dur": f"{dur:.3f}", **extra})
        d = OUT / name
        subprocess.run(["node", "scripts/render_frames.mjs", "overlays/graphics.html", str(d), "0", str(n), "graphics",
                        str(w), str(h), f"{fps:g}", q], check=True)
        meta.append({"name": name, "layer": layer, "start": round(start, 3), "dur": round(dur, 3), "frames": n,
                     "still": bool(still), "full": layer not in ("title", "bug", "postfilter")})
        print(f"{name}: {n} frames")
    (OUT / "jobs.json").write_text(json.dumps({"fps": fps, "size": [w, h], "jobs": meta}, indent=1) + "\n")


if __name__ == "__main__":
    main()
