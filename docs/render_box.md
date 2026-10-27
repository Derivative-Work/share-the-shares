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
4. **Node:** run `npm ci`. It also fetches Puppeteer's Chrome, which renders the graphics layer (`scripts/render_frames.mjs`).
5. **Smoke test:** render one 4K frame and compare it with the C5 frame at the same time:
   `blender -b --factory-startup --python scenes/blender/animatic.py -- --out renders/final/smoke --size 3840 2160 --samples 64 --times 268.6`
