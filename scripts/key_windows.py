"""C3: the key over time, to place the key change (the human: "suno put the key change in right before verse 2").

Chroma (CQT) of the harmonic stems (Keyboard, Synth, Strings, Bass, Guitar, Brass, Woodwinds) in 4 s windows, hop
1 s, correlated with the Krumhansl-Kessler major and minor profiles in all 12 keys. Reports the best key per window
and the change points where the best key holds for at least 8 s on each side.
Usage: .venv/bin/python -I scripts/key_windows.py  ->  timing/keys.json
"""
import json
import sys
from pathlib import Path

import librosa
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from song import STEM  # noqa: E402

MAJ = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MIN = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
SR, HOP = 22050, 512
HARMONIC = ["Keyboard", "Synth", "Strings", "Bass", "Guitar", "Brass", "Woodwinds"]


def main():
    y = None
    for s in HARMONIC:
        x, _ = librosa.load(STEM.format(s), sr=SR, mono=True)
        y = x if y is None else y + x
    chroma = librosa.feature.chroma_cqt(y=y, sr=SR, hop_length=HOP)
    fps = SR / HOP
    T = chroma.shape[1] / fps
    profiles = [(f"{NAMES[k]} major", np.roll(MAJ, k)) for k in range(12)] + [(f"{NAMES[k]} minor", np.roll(MIN, k)) for k in range(12)]
    rows = []
    for t in np.arange(0, T - 4, 1.0):
        c = chroma[:, int(t * fps):int((t + 4) * fps)].sum(axis=1)
        if c.sum() < 1e-6:
            continue
        r = [(np.corrcoef(c, p)[0, 1], n) for n, p in profiles]
        r.sort(reverse=True)
        rows.append({"t": float(t), "key": r[0][1], "r": round(float(r[0][0]), 3), "second": r[1][1]})
    # smooth: majority over 9 windows
    keys = [r["key"] for r in rows]
    sm = []
    for i in range(len(keys)):
        win = keys[max(0, i - 4):i + 5]
        sm.append(max(set(win), key=win.count))
    changes, cur, since = [], sm[0], rows[0]["t"]
    for r, k in zip(rows, sm):
        if k != cur:
            changes.append({"t": r["t"] + 2.0, "from": cur, "to": k, "held_before_s": round(r["t"] - since, 1)})
            cur, since = k, r["t"]
    # The key change: the single split t and pair of keys (k1 before, k2 after) that best fit the whole song, by the
    # summed correlation of each window's chroma with its side's key profile. Robust to the per-window relative-
    # major/minor confusion above, since each side is scored against one profile throughout.
    C = np.stack([chroma[:, int(r["t"] * fps):int((r["t"] + 4) * fps)].sum(axis=1) for r in rows])
    R = np.array([[np.corrcoef(c, p)[0, 1] for _, p in profiles] for c in C])  # windows x 24
    cum = np.cumsum(R, axis=0)
    best = (-np.inf, None)
    for i in range(10, len(rows) - 10):
        before, after = cum[i - 1], cum[-1] - cum[i - 1]
        k1, k2 = int(np.argmax(before)), int(np.argmax(after))
        sc = before[k1] + after[k2]
        if sc > best[0]:
            best = (sc, (i, k1, k2))
    i, k1, k2 = best[1]
    split = {"t": rows[i]["t"] + 2.0, "before": profiles[k1][0], "after": profiles[k2][0],
             "semitones": (k2 - k1) % 12 if (k1 < 12) == (k2 < 12) else None}
    # Refine: 1 s windows every 0.5 s within 4 s of the split; the change is the first window where the new key's
    # profile correlates better than the old one's and stays better; then snap to the nearest beat (timing/beats.json).
    p1, p2 = profiles[k1][1], profiles[k2][1]
    fine = []
    for t in np.arange(split["t"] - 4, split["t"] + 4, 0.5):
        c = chroma[:, int(t * fps):int((t + 1) * fps)].sum(axis=1)
        fine.append((float(t), float(np.corrcoef(c, p1)[0, 1]), float(np.corrcoef(c, p2)[0, 1])))
    t_fine = next(t for i, (t, a, b) in enumerate(fine) if all(bb > aa for _, aa, bb in fine[i:i + 4]))
    split["t_fine"] = t_fine  # the first window wholly in the new key starts here; the one before it is mixed
    beats_path = Path("timing/beats.json")
    if beats_path.exists():
        bt = np.array(json.loads(beats_path.read_text())["beats"])
        split["beat"] = round(float(bt[np.argmin(np.abs(bt - split["t_fine"]))]), 4)
    Path("timing/keys.json").write_text(json.dumps({"method": "chroma_cqt 4 s windows, KK profiles, 9-window majority; "
                                                              "best single split, refined at 0.5 s and snapped to a beat",
                                                    "windows": rows, "smoothed": sm, "changes": changes,
                                                    "key_change": split}, indent=1) + "\n")
    print("key change (best single split):", split)
    for c in changes:
        print(f"{c['t']:7.1f} s  {c['from']} -> {c['to']}  (held {c['held_before_s']} s)")


if __name__ == "__main__":
    main()
