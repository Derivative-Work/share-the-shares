# The RTX 5090 box

The 4K finals (`config/render_profiles.json` `final`) render here. The project moves over from the GTX 970 box with rsync.

## Transfer

Run from the GTX 970 box, with the repo clean (`git status` empty) and `MANIFEST.sha256` current (`scripts/manifest.sh`):

```
rsync -aHAX --info=progress2 --exclude-from=config/rsync-exclude.txt \
  ~/Projects/share-the-shares/ <5090 box>:~/Projects/share-the-shares/
```

- Keep the same path on the box. The queue scripts in `renders/c5/logs/` and the log's commands assume `~/Projects/share-the-shares`.
- `.git` goes with the rest, so the box has the full history and the commits continue from it.
- Excluded:
  - `.venv` (its Python is a symlink into this machine's uv store) and `node_modules`;
  - caches;
  - every frame sequence (`renders/c4/frames_v*`, `renders/c5/frames`), about 20 GB. They regenerate, and the finals replace them.
- Moved, about 2.7 GB in all (4,382 files):
  - the large files in `MANIFEST.sha256` (audio, stems, cuts, archive);
  - the git-ignored products that the 4K render reads directly: the ink pieces, prop prints and certificate prints in `assets/engravings/ink/` and `renders/c1/`, and the puppet layers in `assets/puppets/*/layers/`;
  - `models/` (SAM, used only for puppet cutting).

## On the box

1. **Check the copy:** `sha256sum -c --quiet MANIFEST.sha256 && git status --short` (prints nothing when everything arrived).
2. **Tools:** use the same versions as the draft box.
   - Blender 5.2.2 LTS. The scenes use Eevee, so there is no GPU device to set.
   - uv with Python 3.12.
   - Node 24 and ffmpeg.
3. **Python:** run `uv sync`. `pyproject.toml` pins CPU PyTorch, which is enough: torch is used only for alignment (C3) and puppet cutting (C2), and the render doesn't use it. Switch to the cu128 index only if those steps are re-run here.
4. **Node:** run `npm ci`. npm 11 skips Puppeteer's postinstall (not in `allowScripts`), so fetch the browser it renders the graphics layer with (`scripts/render_frames.mjs`, headless shell) yourself:
   `npx puppeteer browsers install chrome-headless-shell`
   A bare `puppeteer.launch()` fails here on Ubuntu's user-namespace restriction; the script's `--no-sandbox` is what lets it run.
5. **Smoke test:** render one 4K frame and compare it with the C5 frame at the same time:
   `blender -b --factory-startup --python scenes/blender/animatic.py -- --out renders/final/smoke --size 3840 2160 --samples 64 --times 268.6`
   The C5 frames aren't transferred, so compare with section 6's cut, which starts at 220.50 s (268.6 s is 48.10 s in).
   And one 4K graphics frame, the finished fact card:
   `node scripts/render_frames.mjs overlays/graphics.html renders/final/smoke/graphics_fact 500 501 graphics 3840 2160 24 "layer=fact&dur=20.890"`

## Set up (2026-10-26)

The box is ready: copy verified, environments built, both smoke frames match. See the production log, same date. Blender here is 5.2.3 LTS (snap), a patch past the draft box's 5.2.2; the smoke frame shows no difference.
