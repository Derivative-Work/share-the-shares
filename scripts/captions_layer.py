"""The lyric captions alone, on transparency, for the edit in Resolve: the karaoke captions of the review cuts
(scripts/animatic_assemble.py ass(), "lyrics"), full length from the video's 0, as ProRes 4444 with alpha.

ffmpeg's libass filter draws a caption's colour but never writes alpha, so it is rendered twice: in colour on black
(premultiplied), and with every colour white at its own alpha (the coverage matte). The matte becomes the alpha and
the colour is un-premultiplied.

Usage: .venv/bin/python -I scripts/captions_layer.py OUT.mov [--only L45 L46 ... | --exclude L45 ...] [--size W H]
"""
import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import animatic_assemble as A  # noqa: E402

FIELDS = 4  # PrimaryColour, SecondaryColour, OutlineColour, BackColour follow Name, Fontname, Fontsize


def matte(script):
    """The same script with each style's colours white, keeping their alpha bytes (&HAABBGGRR)."""
    out = []
    for row in script.splitlines():
        if row.startswith("Style: "):
            f = row.split(",")
            for i in range(3, 3 + FIELDS):
                f[i] = re.sub(r"&H([0-9A-Fa-f]{2})[0-9A-Fa-f]{6}", r"&H\1FFFFFF", f[i])
            row = ",".join(f)
        out.append(row)
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--only", nargs="+")
    g.add_argument("--exclude", nargs="+")
    ap.add_argument("--size", nargs=2, type=int, default=[3840, 2160])
    a = ap.parse_args()
    ids = [ln["id"] for ln in A.TM["lines"]]
    only = set(a.only) if a.only else (set(ids) - set(a.exclude)) if a.exclude else None
    w, h = a.size
    total = A.PRE + A.DUR + A.POST
    n = int(round(total * A.FPS))
    with tempfile.TemporaryDirectory() as td:
        col, mat = Path(td) / "colour.ass", Path(td) / "matte.ass"
        script = A.ass(w, h, "lyrics", only)
        col.write_text(script)
        mat.write_text(matte(script))
        src = f"color=c=black:s={w}x{h}:r={A.FPS}:d={total:.3f}"
        fc = (f"[0:v]format=rgb24,ass={col}:fontsdir=assets/fonts,format=gbrp[c];"
              f"[1:v]format=rgb24,ass={mat}:fontsdir=assets/fonts,format=gbrp,extractplanes=g[m];"
              f"[c][m]alphamerge,unpremultiply=inplace=1,format=yuva444p10le[v]")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", src, "-f", "lavfi", "-i", src,
                        "-filter_complex", fc, "-map", "[v]", "-frames:v", str(n), "-c:v", "prores_ks", "-profile:v", "4",
                        "-vendor", "apl0", "-pix_fmt", "yuva444p10le", "-alpha_bits", "16", a.out], check=True)
    print(a.out, f"{n} frames ({total:.2f} s), {len(only) if only is not None else len(ids)} lines")


if __name__ == "__main__":
    main()
