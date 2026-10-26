"""C4 sync test: rendered excerpts (animatic.py --step 1 --from --to) with their stretch of the Suno mix, joined
with a half-second of black between, so the mouths, the sway and the stride can be judged against the sound.

Usage: .venv/bin/python -I scripts/c4_sync_test.py <frames dir> <out.mp4> <from>-<to> [<from>-<to> ...]
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

TM = json.loads(Path("timing/timing_map.json").read_text())
FPS = TM["fps"]


def main():
    frames, out, spans = Path(sys.argv[1]), sys.argv[2], [tuple(map(float, a.split("-"))) for a in sys.argv[3:]]
    with tempfile.TemporaryDirectory() as td:
        parts = []
        for k, (a, b) in enumerate(spans):
            f0 = int(a * FPS)
            n = len([f for f in range(f0, int(b * FPS) + 1) if (frames / f"f_{f:05d}.png").exists()])
            p = Path(td) / f"p{k}.mp4"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-start_number", str(f0),
                            "-i", str(frames / "f_%05d.png"), "-ss", f"{f0 / FPS:.4f}", "-t", f"{n / FPS:.4f}",
                            "-i", TM["audio"], "-frames:v", str(n), "-map", "0:v", "-map", "1:a",
                            "-vf", "tpad=stop_mode=add:stop_duration=0.5:color=black", "-af", "apad=pad_dur=0.5",
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(p)], check=True)
            parts.append(p)
        lst = Path(td) / "list.txt"
        lst.write_text("".join(f"file '{p}'\n" for p in parts))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", out],
                       check=True)
    print(out)


if __name__ == "__main__":
    main()
