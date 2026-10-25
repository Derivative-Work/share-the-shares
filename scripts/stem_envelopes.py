"""C3: per-frame loudness envelopes of the two vocal stems (lead, choir), and the drum stem's onsets.

Envelopes are RMS at the video's fps, in dB normalised to 0..1 over a 40 dB range, for mouths and swaying (the jaws
open on the lead, the cherubs on the choir). Drum onsets (librosa onset detection on the drum stem, backtracked) are
for stamps and hits. Usage: .venv/bin/python -I scripts/stem_envelopes.py -> timing/envelopes/*.npy, timing/drum_onsets.json
"""
import json
import sys
from pathlib import Path

import librosa
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from song import STEM  # noqa: E402

FPS = json.loads(Path("config/look.json").read_text())["fps"]
SR = 48000
out = Path("timing/envelopes")
out.mkdir(parents=True, exist_ok=True)
for stem, tag in (("Vocals", "vocals"), ("Backing Vocals", "backing")):
    y, _ = librosa.load(STEM.format(stem), sr=SR, mono=True)
    hop = SR // FPS
    rms = librosa.feature.rms(y=y, frame_length=hop * 2, hop_length=hop, center=True)[0]
    db = 20 * np.log10(rms / (rms.max() + 1e-12) + 1e-12)
    np.save(out / f"{tag}.npy", np.clip((db + 40) / 40, 0, 1).astype(np.float32))
    print(tag, len(rms), "frames")
y, _ = librosa.load(STEM.format("Drums"), sr=22050, mono=True)
on = librosa.onset.onset_detect(y=y, sr=22050, hop_length=256, backtrack=True, units="time", delta=0.12)
Path("timing/drum_onsets.json").write_text(json.dumps({"method": "librosa onset_detect, backtrack, delta 0.12",
                                                       "onsets": [round(float(t), 4) for t in on]}) + "\n")
print("drum onsets", len(on))
