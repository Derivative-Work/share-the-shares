"""C4 sync fix: correct the aligned words (timing/words.json) against the vocal stems' onsets.

The human at C4: "the sync is not quite right". Measured: the aligner's word starts sit 15-90 ms ahead of the vocal
attacks section by section (fine: a mouth should lead the sound a little), but 10 of 68 lines came out 120-385 ms
late. Two passes, per line, on the line's own stem (Vocals or Backing Vocals):
  1. the line's lag: the shift (within +-400 ms) that best lines up its word starts with the stem's onset-strength
     envelope (5 ms frames). A line is moved by it only when it is 100 ms or more, and never past its neighbours.
  2. each word start snaps to the nearest detected onset (backtracked to where the energy rises) within +-60 ms,
     keeping the words in order and at least 40 ms long. Word ends move with their starts, never past the next word.
timing/words.json (the C3 alignment) is kept; timing/timing_map.py reads the snapped file when it exists.
Usage: .venv/bin/python -I scripts/snap_words.py  ->  timing/words_snapped.json, timing/words_snapped.md
"""
import json
import sys
from pathlib import Path

import librosa
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from song import STEM  # noqa: E402

SR, HOP = 22050, 110  # 5 ms frames
MOVE_MIN, MAX_LAG, SNAP = 0.100, 0.400, 0.060


def main():
    W = json.loads(Path("timing/words.json").read_text())
    env, ons = {}, {}
    for stem in {ln["stem"] for ln in W["lines"]}:
        y, _ = librosa.load(STEM.format(stem), sr=SR, mono=True)
        o = librosa.onset.onset_strength(y=y, sr=SR, hop_length=HOP)
        env[stem] = o / (o.max() + 1e-9)
        ons[stem] = librosa.onset.onset_detect(onset_envelope=o, sr=SR, hop_length=HOP, units="time", backtrack=True)
    fr = lambda t: int(round(t * SR / HOP))
    lines = W["lines"]
    report = ["# Word timing corrections", "", "C4 sync fix (scripts/snap_words.py). Lines moved as a whole:", "",
              "| Line | Start (s) | Moved (ms) | Text |", "| --- | --- | --- | --- |"]
    snapped = 0
    for i, ln in enumerate(lines):
        e = env[ln["stem"]]
        a, b = ln["start"] - 0.5, ln["end"] + 0.5
        imp = np.zeros(fr(b) - fr(a) + 1)
        for w in ln["words"]:
            imp[min(len(imp) - 1, max(0, fr(w["start"]) - fr(a)))] = 1
        imp = np.convolve(imp, np.hanning(9), "same")
        seg = e[fr(a):fr(a) + len(imp)]
        lags = range(-int(MAX_LAG * SR / HOP), int(MAX_LAG * SR / HOP) + 1)
        best = max(lags, key=lambda L: float(np.dot(np.roll(imp, -L)[:len(seg)], seg)))
        lag = best * HOP / SR  # + = the words are late
        if abs(lag) >= MOVE_MIN:
            lo = lines[i - 1]["end"] + 0.02 if i else 0.0
            hi = lines[i + 1]["start"] - 0.02 if i + 1 < len(lines) else 1e9
            d = -lag
            d = max(d, lo - ln["start"]) if d < 0 else min(d, hi - ln["end"])
            for w in ln["words"]:
                w["start"], w["end"] = round(w["start"] + d, 3), round(w["end"] + d, 3)
            ln["start"], ln["end"] = ln["words"][0]["start"], ln["words"][-1]["end"]
            ln["moved_ms"] = int(round(d * 1000))
            report.append(f"| {ln['id']} | {ln['start']:.2f} | {d * 1000:+.0f} | {ln['text']} |")
        on = ons[ln["stem"]]
        prev = lines[i - 1]["end"] if i else 0.0
        for k, w in enumerate(ln["words"]):
            near = on[(on >= w["start"] - SNAP) & (on <= w["start"] + SNAP) & (on > prev + 0.01)]
            if len(near):
                t = float(near[np.argmin(np.abs(near - w["start"]))])
                nxt = ln["words"][k + 1]["start"] if k + 1 < len(ln["words"]) else w["end"] + 1
                if t < nxt - 0.04:
                    d = t - w["start"]
                    w["start"] = round(t, 3)
                    w["end"] = round(min(max(w["end"] + d, t + 0.04), nxt), 3)
                    snapped += abs(d) > 0.005
            prev = w["start"]
        ln["start"], ln["end"] = ln["words"][0]["start"], ln["words"][-1]["end"]
    W["snapped"] = {"script": "scripts/snap_words.py", "move_min_s": MOVE_MIN, "max_lag_s": MAX_LAG, "snap_s": SNAP,
                    "words_snapped": snapped}
    Path("timing/words_snapped.json").write_text(json.dumps(W, indent=1) + "\n")
    report += ["", f"Then {snapped} word starts snapped to an onset within ±{SNAP * 1000:.0f} ms."]
    Path("timing/words_snapped.md").write_text("\n".join(report) + "\n")
    print("\n".join(report))


if __name__ == "__main__":
    main()
