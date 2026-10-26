"""C3: word-level forced alignment of the as-sung lyrics (lyrics/as_sung_draft.txt) against the vocal stems.

Method from Not Yet's align_words.py (itself from Sandbox Rhapsody): torchaudio's MMS forced aligner (MMS_FA,
multilingual wav2vec2 CTC) aligns each section's words as one continuous sequence inside the section's window, which
keeps every word in sung order, then splits it back into lines; words are trimmed to where the stem has energy
(-38 dB). Here each section names its own stem: the soloists are on Vocals, the choir on Backing Vocals.

Section windows come from the first pass (scripts/first_pass.py, faster-whisper medium.en on both vocal stems):
each runs from just before its first line to just before the next section's.

Usage: .venv/bin/python -I scripts/align_words.py  ->  timing/words.json
"""
import json
import re
import sys
from pathlib import Path

import librosa
import numpy as np
import torch
import torchaudio

sys.path.insert(0, str(Path(__file__).resolve().parent))
from song import STEM  # noqa: E402

SR = 16000
WINDOWS = {  # section: (start s, end s), from the first pass
    "Intro": (0.0, 19.5),
    "Verse 1": (19.5, 46.4),
    "Pre-Chorus": (46.0, 57.9),
    "Pre-Chorus tag": (57.5, 60.3),
    "Chorus": (60.0, 98.9),
    "Verse 2": (98.9, 126.8),
    "Pre-Chorus 2": (126.0, 132.9),
    # C4 correction (spectrogram + a re-transcription of 131-141 s): Suno sings the choir's "Through this fund!" first
    # (132.3 s, "fund" held to ~137 s), then the lead's "through this fund" (134.5 s, a melisma to ~138.5 s); chorus 2
    # starts at 139.4 s with three "share the shares", not four from 133.3 s
    "Pre-Chorus 2 tag": (131.9, 137.6),
    "Pre-Chorus 2 echo": (134.2, 139.1),
    "Chorus 2": (139.0, 163.2),
    "Verse 3": (163.2, 191.9),
    "Bridge": (191.9, 215.0),
    "Final Chorus": (214.5, 247.3),
    "Outro": (247.3, 263.5),
    "Tag": (263.5, 283.4),
}
SPOKEN = {"llc": "l l c", "ipo": "i p o", "tba": "t b a", "isn't": "isnt", "can't": "cant", "we'll": "well",
          "it's": "its", "i'd": "id", "who's": "whos", "haven't": "havent", "milestone's": "milestones",
          "holding's": "holdings", "don't": "dont"}


def sections():
    out, cur = [], None
    for line in Path("lyrics/as_sung_draft.txt").read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"\[(.+)\]$", line)
        if m:
            name, stem, singer = (x.strip() for x in m.group(1).split("|"))
            cur = {"section": name, "stem": stem, "singer": singer, "lines": []}
            out.append(cur)
        else:
            cur["lines"].append(line)
    return out


def spoken(word):
    w = word.lower().replace("’", "'")
    w = re.sub(r"[^a-z'\-]", "", w)
    w = SPOKEN.get(w, w)
    w = {"two": "two", "hundred": "hundred"}.get(w, w)
    return [p for p in re.split(r"[\s\-]+", w.replace("'", "")) if p]


def trim(words, y, a, floor_db=-38.0):
    hop = 160
    rms = librosa.feature.rms(y=y, frame_length=640, hop_length=hop)[0]
    db = 20 * np.log10(rms / (rms.max() + 1e-12) + 1e-12)
    for w in words:
        f0, f1 = int((w["start"] - a) * SR / hop), int((w["end"] - a) * SR / hop)
        loud = np.where(db[f0:f1 + 1] > floor_db)[0]
        if len(loud):
            s0, s1 = (f0 + loud[0]) * hop / SR + a, (f0 + loud[-1] + 1) * hop / SR + a
            if s1 - s0 >= 0.08:
                w["start"], w["end"] = round(s0, 3), round(s1, 3)
    return words


def main():
    bundle = torchaudio.pipelines.MMS_FA
    model = bundle.get_model(with_star=False)
    tokenizer, aligner = bundle.get_tokenizer(), bundle.get_aligner()
    stems = {}
    out = []
    for sec in sections():
        if sec["stem"] not in stems:
            stems[sec["stem"]] = librosa.load(STEM.format(sec["stem"]), sr=SR, mono=True)[0]
        voc = stems[sec["stem"]]
        a, b = WINDOWS[sec["section"]]
        i0, i1 = int(a * SR), min(len(voc), int(b * SR))
        y = voc[i0:i1] / (np.abs(voc[i0:i1]).max() + 1e-9)
        display = [(k, w) for k, ln in enumerate(sec["lines"]) for w in ln.split()]
        parts = [spoken(w) for _, w in display]
        flat = [p for ps in parts for p in ps]
        with torch.inference_mode():
            emission, _ = model(torch.from_numpy(y).float().unsqueeze(0))
            spans = aligner(emission[0], tokenizer(flat))
        ratio = (i1 - i0) / emission.shape[1] / SR
        per_line = [[] for _ in sec["lines"]]
        j = 0
        for (k, w), ps in zip(display, parts):
            seg = spans[j:j + len(ps)]
            j += len(ps)
            start, end = seg[0][0].start * ratio + a, seg[-1][-1].end * ratio + a
            score = float(np.mean([s.score for sp in seg for s in sp]))
            per_line[k].append({"w": w, "start": round(start, 3), "end": round(end, 3), "score": round(score, 3)})
        for text, words in zip(sec["lines"], per_line):
            words = trim(words, y, a)
            out.append({"id": f"L{len(out) + 1:02d}", "section": sec["section"], "stem": sec["stem"],
                        "singer": sec["singer"], "text": text,
                        "start": words[0]["start"], "end": words[-1]["end"], "words": words})
            low = [w["w"] for w in words if w["score"] < 0.3]
            print(f"{out[-1]['id']} {out[-1]['start']:7.2f}-{out[-1]['end']:7.2f} {text[:56]:56s} "
                  f"{'low: ' + ' '.join(low) if low else ''}")
    Path("timing/words.json").write_text(json.dumps({"aligner": "torchaudio MMS_FA", "torchaudio": torchaudio.__version__,
                                                     "lines": out}, indent=1) + "\n")


if __name__ == "__main__":
    main()
