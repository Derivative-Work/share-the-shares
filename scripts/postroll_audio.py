"""The post-roll's sound (config/postroll.json): the pledge line dialled in DTMF, one short ring, then the hold
music (the human's Suno muzak cover) faded in so its first chorus lands on the cut to S46, playing to the end of the
video. Written at the song's sample rate and channel count, for scripts/animatic_assemble.py to follow the song with.

Usage: .venv/bin/python -I scripts/postroll_audio.py  ->  audio/postroll/postroll.wav
"""
import json
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "config/postroll.json").read_text())
PH = json.loads((ROOT / "config/c4_shots.json").read_text())["placeholders"]
TM = json.loads((ROOT / "timing/timing_map.json").read_text())
# the standard DTMF pairs (low row, high column), Hz
DTMF = {"1": (697, 1209), "2": (697, 1336), "3": (697, 1477), "4": (770, 1209), "5": (770, 1336), "6": (770, 1477),
        "7": (852, 1209), "8": (852, 1336), "9": (852, 1477), "0": (941, 1336), "*": (941, 1209), "#": (941, 1477)}


def db(x):
    return 10 ** (x / 20)


def tone(freqs, length, sr, edge=0.005):
    t = np.arange(int(length * sr)) / sr
    y = sum(np.sin(2 * np.pi * f * t) for f in freqs) / len(freqs)
    e = np.clip(np.minimum(t, length - t) / edge, 0, 1)  # no clicks at the ends
    return y * e


def main():
    song, sr = sf.read(ROOT / TM["audio"], frames=1, always_2d=True)
    ch = song.shape[1]
    post = sum(PH[s]["after_s"] for s in ("S45", "S46", "S47", "S48"))
    out = np.zeros((int(round(post * sr)), ch))

    def add(y, at):
        a = int(round(at * sr))
        b = min(len(out), a + len(y))
        out[a:b] += y[:b - a, None] if y.ndim == 1 else y[:b - a]

    d = CFG["dial"]
    for i, digit in enumerate(CFG["number"]):
        add(db(d["level_db"]) * tone(DTMF[digit], d["tone"], sr), d["start"] + i * (d["tone"] + d["gap"]))
    dial_end = d["start"] + len(CFG["number"]) * (d["tone"] + d["gap"])
    r = CFG["ring"]
    ring_at = dial_end + r["after_dial"]  # the ring follows the dialling after a short pause
    add(db(r["level_db"]) * tone((440, 480), r["length"], sr, edge=0.02), ring_at)
    m = CFG["muzak"]
    lands = PH["S45"]["after_s"] if m["lands_at"] == "S46" else 0.0  # the chorus lands on the cut to S46
    start = lands - m["fade_in"]  # post-roll time the muzak comes in
    muz, msr = sf.read(ROOT / m["file"], always_2d=True)
    assert msr == sr, (msr, sr)
    a = int(round((m["chorus"] - m["fade_in"]) * sr))
    n = len(out) - int(round(start * sr))
    seg = muz[a:a + n, :ch] * db(m["level_db"])
    t = np.arange(len(seg)) / sr
    env = np.clip(t / m["fade_in"], 0, 1) ** 2 * np.clip((len(seg) / sr - t) / m["fade_out"], 0, 1)
    add(seg * env[:, None], start)
    peak = np.abs(out).max()
    assert peak < 1.0, peak
    dst = ROOT / "audio/postroll"
    dst.mkdir(parents=True, exist_ok=True)
    sf.write(dst / "postroll.wav", out, sr, subtype="PCM_16")
    print(f"audio/postroll/postroll.wav: {post:.2f} s; dial {d['start']:.2f}-{dial_end:.2f} s, ring {ring_at:.2f}-"
          f"{ring_at + r['length']:.2f} s, muzak from {start:.2f} s (its {m['chorus'] - m['fade_in']:.2f} s), chorus at "
          f"{lands:.2f} s (S46); peak {20 * np.log10(peak):.1f} dBFS")


if __name__ == "__main__":
    main()
