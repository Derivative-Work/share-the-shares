# Production log

Append-only. One entry per action: timestamp, step (shot ID where relevant), what, exact command/prompt/script, outputs, why.

## 2026-10-25T08:24:00-04:00 — Step 1: repo scaffolding, the brief and supplied audio

- **What:** Read the brief (Claude Doc rev 28) in full. It is a creative brief with no production rules, inputs or checkpoints, so this project inherits them: the Ghost in the Machine brief's production rules, Sandbox Rhapsody's inputs and pre-production steps, and Not Yet's layout and audit records (`docs/brief.md` in each sibling repo; the human: "the specs you'll import from the other projects"). Created Not Yet's directory layout plus `takes/live/` (the human's footage) and `assets/engravings/`. Copied in `.gitignore`, the 50 MiB pre-commit hook, `scripts/manifest.sh`, `CLAUDE.md`, the logs, `package.json` and `config/render_profiles.json`. Mirrored the brief to `docs/brief.md`. Copied the Suno mix and stems in from `~/Downloads` (originals left in place) and checked each copy's SHA-256 against its source (3/3 OK).
- **Commands:**
  - `git init`
  - `mkdir -p log/prompts/{suno,other} log/audits scripts/hooks docs lyrics archive style timing shots config scenes/blender/{lib,sets} overlays assets/engravings renders deliverables reference takes/live audio/{track,stems/midi,master}`
  - `cp ../not-yet/{.gitignore,package.json,package-lock.json,config/render_profiles.json,scripts/hooks/pre-commit,scripts/{manifest.sh,doc_to_md.py,fetch_share.mjs,chat_snapshot_to_md.py,midi_io.py}}` (package name changed to `share-the-shares`); `git config core.hooksPath scripts/hooks`
  - `cp -p ~/Downloads/"Share the Shares".{wav,mp3} audio/track/`; `cp -p ~/Downloads/"Share the Shares Stems.zip" audio/`; `sha256sum -c` against the sources; `unzip -q … -d audio/stems && mv audio/stems/*.mid audio/stems/midi/`
  - Brief: docs `read` of project `46e05c0f-8098-4842-97de-31fa74da433a`, node `ffb64806-5985` (full value, rev 28), then `python3 -I scripts/doc_to_md.py <read result> docs/brief.md`
  - `ffprobe -v error -show_entries format_tags=lyrics-eng -of default=nw=1:nk=1 "audio/track/Share the Shares.mp3" > log/prompts/suno/lyrics_submitted.txt`
- **Outputs:** the files above; `audio/track/Share the Shares.{wav,mp3}`; `audio/stems/` (12 WAV stems) and `audio/stems/midi/` (12 `.mid`); `docs/brief.md`; `log/prompts/suno/lyrics_submitted.txt`
- **Script change:** `scripts/doc_to_md.py` (from Not Yet) dropped hard line breaks and italics, so every lyric section ran together on one line. It now writes a hard break as a Markdown line break and italics as `*…*`.
- **Findings:**
  - **The track:** Suno, `id=c0702797-fae7-4b4a-8ad9-5d65f0c6843e`, created 2026-10-22T02:04:54Z (MP3 comment tag). PCM s16le, 48 kHz stereo, **283.44 s** (4:43), not the brief's "about 3:30".
  - **One take, not assembled sections:** the stems archive holds one full-song take: Vocals, Backing Vocals, Keyboard, Synth, Guitar, Bass, Drums, Percussion, Brass, Strings, Woodwinds and FX, each with MIDI. The brief planned soloists generated section by section and assembled in a DAW.
  - **The take predates the audit:** it was created at 02:04Z on 2026-10-22, before Gemini's audit (03:53Z) changed "spent" to "pledged". The stored lyrics have "spent". Verse 3 is the human's live performance, which replaces the generated verse, so the live take can sing "pledged".
  - **The stored lyrics differ from the brief** (the MP3's lyrics tag; Not Yet found this tag can carry export artifacts, so check against Suno's page):
    - the bracketed singer notes are kept, though the brief says to remove them;
    - the [Verse 1], [Pre-Chorus], [Verse 3], [Bridge] and [Final Chorus] tags are missing;
    - chorus 1 repeats its last two lines, and chorus 2 is written out;
    - the bridge doubles "then watch us when it's not." and ends on "(choir) In the coming months!" instead of "(choir, building) When it's not, when it's not...";
    - the final chorus has no key-change tag and only the Worker's ad-lib; the Board's and the Lawyer's are missing.
- **Why:** the brief (rev 28); the inherited rules (Ghost "Production rules": `.gitignore` and the 50 MiB check before the first commit; Sandbox Rhapsody pre-production step 1).
- **Environment:** Claude Code (Opus 5.5); Blender 5.2.2 LTS; ffmpeg 8.0.1; Python 3.14.4 (system), uv 0.13.1; Node v24.22.0; git. GPU: GTX 970 4 GB, driver 580.178.04 (draft box; finals on the RTX 5090). Disk: 132 GB free.

## 2026-10-25T08:24:30-04:00 — Step 2 (first part): planning chat and the Gemini audit archived

- **What:** Fetched the planning chat's share page with Not Yet's scripts (headless Chrome via Puppeteer 24.43.1) and converted it to Markdown. Saved the Gemini audit (messages 21–24) verbatim to `log/audits/`.
- **Commands:**
  - `npm ci`
  - `node scripts/fetch_share.mjs https://claude.ai/share/75dfaaef-866c-4979-8016-b7747f9ddaa3 docs/planning_chat/planning_chat`
  - `python3 -I scripts/chat_snapshot_to_md.py docs/planning_chat/planning_chat.json https://claude.ai/share/75dfaaef-866c-4979-8016-b7747f9ddaa3 > docs/planning_chat/planning_chat.md`
  - Audit: an inline Python script that writes messages 21–24 from the snapshot JSON, verbatim, to `log/audits/01_gemini.md`
- **Outputs:** `docs/planning_chat/planning_chat.{json,html,txt,md}`, `log/audits/{README,01_gemini}.md`
- **Findings:**
  - Snapshot "Song: Share the Shares (Anthropic's Public Benefit Fund)", taken 2026-10-25T12:19:48Z: 28 messages, 2026-10-20 to 2026-10-25. Messages 13–14 aren't in the share (probably an edited branch); archived as shared.
  - Gemini's full output is pasted as text in message 21, so the share holds it whole, unlike Not Yet's attached audits. Its version isn't recorded anywhere (open item, needed for the fact card).
  - The chat shows the video's path: a clay telethon (message 12), rendered instead of generated (16), the share certificate (18–20), a screen for the transitions (25), then a printed sheet (27–28) and the telethon removed (29–30). The brief has only the final version.
- **Why:** Ghost "Production rules": the planning chat is published as part of the making-of record. Not Yet: audits saved verbatim with model, version and date.

## 2026-10-25T09:22:50-04:00 — Step 2: Suno take logged; post-filter plan; Gemini version

- **What:** The human gave the Suno share link, said the one-shot take worked (the live verse will replace its Worker audio), that the master goes through the post-filter on the RTX 5090 box, and that the audit ran on Gemini 4 Argon. Fetched the Suno page with Not Yet's scripts, extracted the take's metadata and submitted lyrics, and wrote `log/prompts/suno/takes.md`. Recorded the Gemini version in the audit records.
- **Commands:**
  - `cp ../not-yet/scripts/{fetch_suno.mjs,suno_meta.py} scripts/`
  - `mkdir -p log/prompts/suno/fetch_accepted && node scripts/fetch_suno.mjs https://suno.com/s/1sz8sZONKQyqeqTj log/prompts/suno/fetch_accepted` (the first run failed because the output folder didn't exist yet)
  - `python3 -I scripts/suno_meta.py log/prompts/suno/fetch_accepted`
- **Outputs:** `log/prompts/suno/fetch_accepted/{clip.json,lyrics.txt,page.html,page.txt,resp_*.json}`, `log/prompts/suno/takes.md`, `scripts/{fetch_suno.mjs,suno_meta.py}`; `log/audits/{README,01_gemini}.md` updated
- **Script change:** `suno_meta.py` cut the lyrics between Not Yet's first and last lines (`[Verse 1]` … `Goodnight.`), so it wrote an empty file. The bounds are now `[Intro]` … `Phone lines open at the IPO.`
- **Findings:**
  - Suno V6 (`chirp-hawk`), `aug_creativity` 1, created 2026-10-21T02:27:00Z per Suno's page (the MP3 tag's 2026-10-22T02:04:54Z is probably the export time). Either way it predates the Gemini audit (2026-10-22T03:53Z).
  - **Correction to step 1:** the lyric differences listed there come from the MP3's lyrics tag, not from what was submitted. Suno's page lyrics match the brief's, except that chorus 2 is written out and verse 3 says "spent" (pre-audit). So there is no lyric exception. The tag's differences are a lead for the as-sung lyrics at C3.
  - The style prompt asks for 72 BPM, gated-reverb drums, FM electric piano, saxophone and a gospel choir, with "many solo vocalists trading lines" and a whole-step key change into the final chorus. Whether Suno delivered the key change and distinct soloists gets checked at C3; the stems include Brass and Woodwinds (likely the sax).
  - The brief's "about 3:30" doesn't hold: the take is 283.44 s. Shot cues are lyric lines, so the shot list still applies.
- **Why:** Sandbox Rhapsody's pre-production step 2: log the audio retroactively. Not Yet: audits recorded with model name and version.

## 2026-10-25T09:26:30-04:00 — Step 2: Suno's key change logged; timing source set

- **What:** Logged the human's report that Suno put the key change right before verse 2, not before the final chorus as the lyrics' `[Final Chorus] (key change up a step, full gospel choir)` tag and the style prompt ("building to a whole-step key change into the final chorus") asked. Set the timing source: the Suno mix, since the post-filter doesn't change timing (the human).
- **Outputs:** `log/prompts/suno/takes.md` (note added), `log/human_interventions.md`
- **Findings:**
  - **An AI change, not a human one:** the generator moved the song's one structural surprise, as Suno did with Ghost in the Machine's key change (it dropped it there). The rest of the song, verse 2 onward, is presumably in the higher key, so the final chorus has no lift of its own. C3 confirms the exact time and both keys from the stems.
  - **Shots this touches:** S36 ("The key change": the certificate re-inks brighter, with gold creeping into the green) is cued to a key change that now falls before verse 2 (S18), not at the final chorus. Whether S36 moves with the key change or stays at the final chorus is a creative call for the human at C4; the shot list stays as briefed until then.
  - **Live verse key:** the brief says to start verse 3 "in the key of the generated take". After the change, that's the higher key. C3 will report it.
  - **Timing:** the timing map uses `audio/track/Share the Shares.wav`. The master's offset still gets one cross-correlation check when it arrives (inherited Sandbox Rhapsody step 2), expected 0 samples. The human's live A/V will be synced with fixed offsets against this audio.
- **Why:** Ghost brief, "Lyrics": Suno's changes are logged as AI changes. Sandbox Rhapsody step 2: master offset.

## 2026-10-25T09:47:00-04:00 — Brief: S36 moved to the key change

- **What:** In the brief, moved row S36 from the "Final chorus" table to the top of "Verse 2 and pre-chorus 2", and reworded its cue to "The key change, just before verse 2 (where Suno put it)". Shot IDs don't change.
- **Commands:** Docs connector `update` on node `ffb64806-5985`: `move` of row `mqnwstgerpq.22228` after the header row `mqnwstgerpq.19876`, then a text `replace` in that row's cue cell. Doc rev 28 → 30. `docs/brief.md` will be re-exported at the next brief change or checkpoint.
- **Why:** The human's decision (human_interventions, same time).

## 2026-10-25T09:47:00-04:00 — C1: style spec, look config, the certificate and two test frames

- **What:** There are no inspiration videos, so the style references are public-domain certificate and banknote art.
  - Searched Wikimedia Commons and the Met's collection API, and downloaded 14 engravings and 6 reference certificates, each with its source logged.
  - Cut the five figures' rest poses into clean ink maps.
  - Composed the certificate's static art (two ink plates on cream paper, with generated guilloche and rosettes and OFL type) as a printed sheet for the prop, plus a figure-free version for renders.
  - Rendered two test frames in Blender at 720p and made the review sheet. Wrote `style/style_spec.md`.
- **Commands:**
  - Sources: inline Python against the Commons API (`list=search`, `prop=imageinfo`) and the Met API (`/public/collection/v1.1/search`, `/v1/objects/<id>`); full-size files into `assets/engravings/source/` and `reference/certificates/`; tables in each `sources.tsv` (title, artist, date, page, image URL, licence, hash)
  - Fonts: `curl` from github.com/google/fonts `ofl/` (Abril Fatface, IM Fell English roman, italic and SC, Pinyon Script) with their OFL texts; `assets/fonts/SHA256SUMS`
  - `uv sync` (Python 3.12: numpy 2.5.4, scipy 1.18.1, pillow 13.0.0, opencv-python-headless 5.0.0.93)
  - `.venv/bin/python -I scripts/ink_extract.py`
  - `.venv/bin/python -I scripts/certificate.py renders/c1/certificate_v04`
  - `blender -b --factory-startup --python scenes/blender/c1_test_frame.py -- renders/c1/certificate_v04 renders/c1/c1_test_frame_{wide,close}.png 1280 720 64 {wide,close}` (about 5 s each on the GTX 970)
  - `.venv/bin/python -I scripts/c1_sheet.py renders/c1/certificate_v04 renders/c1/c1_test_frame_wide.png renders/c1/c1_test_frame_close.png renders/c1/c1_sheet.jpg`
- **Outputs:** `style/style_spec.md`; `config/{look,engravings,seeds}.json`; `scripts/{ink_extract,certificate,c1_sheet}.py`; `scenes/blender/c1_test_frame.py`; `assets/engravings/{sources.tsv,source/,ink/}`; `reference/certificates/{sources.tsv,*.jpg}`; `assets/fonts/`; `pyproject.toml`, `uv.lock`; `renders/c1/certificate_v0{1..4}/`, `renders/c1/draft_{wide,close}_v0{1..5}.png`, `renders/c1/c1_test_frame_{wide,close}.png`, `renders/c1/c1_sheet.jpg`
- **Sources chosen:**
  - **Figures:** Asher Brown Durand's banknote vignettes, ca. 1824–37 (Met Open Access, public domain). They are one engraver's work, so the cast matches:
    - Progress: Allegory of America, 393940;
    - Prudence: the seated Justice, with sword and scales, 393946;
    - Mercury: the flying putto with winged helmet and caduceus, 393925;
    - the cherub choir: three putti, 393931;
    - the laborer: a blacksmith and forge, 393945.
  - **Rejected:** NARA's Continental and National Bank Note specimen book, which is lettering only; Rijksmuseum vignettes, an earlier etched style; and the Commons "Guilloche.jpg", which is CC BY-SA.
  - **Ornament:** Cyrus Durand's lathe work is the reference for the generated ornament; nothing is copied. One piece, 393986, is a lathe rosette built from the repeated words "Five thousand", a real precedent for S11's LLC guilloche.
  - **Layout references:** six real certificates, 1863–1916, never composited, because they carry real company names.
- **Iterations** (each version kept under its own name):
  1. Certificate v01: the cherubs ran into the number-of-shares box and the certificate number; Mercury sat on the body text, and the laborer on a counter and the President line. v02 moved them; v03 split the shares label and pulled the signature lines in from the counters. The laborer's levels went from [0.06, 0.62] to [0.10, 0.85] (too dark, then too pale) and settled at [0.08, 0.74]. Mercury's and Prudence's crops were adjusted once.
  2. Render draft v01 was blown out (key light 55 W). The light was calibrated against the paper's printed colour: 4 W renders it at 186/255 and 8 W clips, so the key is 6.5 W and the fill 1.3 W.
  3. Close v02 was soft. At 400 dpi the laborer is only about 500 px across on the sheet. Certificate v04 therefore also writes a figure-free `static/` print, and each figure renders as its own layer at the ink piece's resolution (2177 px for the laborer). That is also how the figures will animate.
  4. Close v03's layers were grey and grainy (dithered transparency at 16 samples) and showed a seam. Blended transparency and a 0.2 mm lift fixed both. v04's grey sheen came from the ink's specular; the ink now uses the paper's roughness. v05 at f/16 is sharp. Then the layer ink colour was pre-multiplied by the paper colour, so layers match the press's multiply.
- **Script fix:** `scripts/manifest.sh` (inherited) exited 1 whenever the last file it checked was tracked: `check-ignore && printf` fails under `pipefail`. It now uses an `if`. The manifest also covers the downloaded sources.
- **Findings for the brief:**
  - **Coupons:** the brief's note "Coupons belong on bonds, not stock certificates" is not quite right. European share certificates carried dividend coupons; Commons has a category of them, and two of the references (Russian General Oil 1916, Norsk Hydro 1912) have coupon sheets. So the coupons are period-accurate, not a liberty. The fact card is unaffected.
  - **The laborer's hammer** rests against the anvil block. S07 says "hammer raised" and S29 match-cuts from "the engraved laborer's raised hammer". He never moves, so either another source with a raised hammer, or new wording.
  - **Progress** holds a spear, not a torch: the torch is a prop piece for the puppet build. The shield carries stars and stripes, an allegory rather than a logo, but it reads as American.
- **Self-assessment for C1:**
  - Holds up: it reads at a glance as a real two-colour certificate. The figures share one engraver's line. The paper, raised ink and curl read in both frames, and the close-up keeps the engraving's line.
  - Weaker: the counter rosettes are loopier and coarser than Durand's lathe work. The Recipient line sits close to the bottom-right counter. The desk is dark and plain. The green underprint behind the company name is faint at the wide framing.
  - Not in C1: the puppet cuts and torch, the transfer form on the back (S24), the seal (S34), the title card, animation and line boil, and the live composite.
- **Why:** The inherited checkpoint C1: a style spec, plus a contact sheet of the references beside a test frame in the style.
- **Status:** **C1 is ready for review.** The agent stops here for approval.

## 2026-10-25T10:42:07-04:00 — C2: the cast as paper puppets, and a cast test

- **What:** Cut the four moving figures into hinged paper puppets, built their layers, wrote the Blender rig, and rendered a 4 s cast test of every puppet doing the gestures its shots need, on twos with the lines boiling. The laborer never moves, so he is printed, not rigged.
- **Commands:**
  - `uv add torch==2.8.* torchvision==0.23.* segment-anything==1.0` (CPU wheels; the GTX 970's sm_52 isn't in current CUDA builds)
  - `curl -o models/sam_vit_b_01ec64.pth https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth` (sha256 ec2df627…, md5 01ec64…, matching the official checksum)
  - `.venv/bin/python -I scripts/segment.py` (SAM ViT-B on CPU, 26 s for all four)
  - `.venv/bin/python -I scripts/puppet_build.py`
  - `scripts/render_c2.sh` (`scenes/blender/c2_cast_test.py` per view, 1280×720, 24 samples, 96 frames; ffmpeg H.264 CRF 16)
  - `.venv/bin/python -I scripts/c2_sheet.py renders/c2/c2_sheet.jpg`
- **Outputs:** `config/puppets.json` (the cut prompts and hand cuts, pivots, parents); `scripts/{segment,puppet_build,c2_sheet}.py`, `scripts/render_c2.sh`; `assets/puppets/<figure>/{masks/,layers/,puppet.json,preview.jpg}`; `scenes/blender/lib/{sheet,puppet}.py`, `scenes/blender/c2_cast_test.py`; `renders/c2/cast_{wide,progress,prudence,mercury,cherubs}.mp4`, `renders/c2/c2_sheet.jpg`
- **The cast:**

  | Figure | Layers |
  | --- | --- |
  | Progress | background, body, spear arm, head, jaw |
  | Prudence | background, body, sword arm, scales arm, head, jaw |
  | Mercury | background, body, arm with caduceus, head, wing, back leg, front leg |
  | Cherubs | background, body, three heads, left arm; mirrored for the right side |

  Each layer's origin is its hinge.
- **How the cuts were made:**
  - **Silhouettes:** SAM traced each figure's silhouette from a box plus positive and negative points (scores 0.91–0.97). The prompts are the agent's, in `config/puppets.json`.
  - **SAM parts:** SAM also cut the heads, jaws, wing, legs and three of the cherubs' parts well (0.81–0.98).
  - **Hand cuts:** SAM follows the hatching rather than the limb where a limb lies over drapery. Progress's spear arm took the whole cape, and Prudence's sword arm half her body. Those three, plus the left cherub's profile head, are cut by agent-placed polygons and strips (the spear, the blade), clipped to the SAM silhouette. That's how a paper cutout is cut anyway: straight scissor lines at the joints.
- **Fills:** wherever a layer loses pixels to a layer in front of it, the hole is filled with a generated engraved line screen. Its tone comes from the surrounding pixels; its direction is one angle per hole, measured from the hatching in a ring around it. The vignette behind each figure is ruled horizontally, as Durand's skies are, so a figure can step out (S03). Fills reach only 40 px past a layer's own pixels, so a head over the sky doesn't give the body a head-shaped paper patch.
- **The rig** (`lib/puppet.py`):
  - Body and parts are opaque paper cutouts carrying their ink; the background is ink printed on the sheet.
  - A geometry-nodes modifier adds the sheet's curl at each vertex's world position, so a layer stays on the curved paper however it turns.
  - Keys go every two frames with constant interpolation.
  - The line boil is a UV nudge of half a source pixel, reseeded every two frames by a driver on a noise texture's W.
  - `lib/sheet.py` holds C1's approved sheet, desk, light and camera values for reuse.
- **Problems fixed on the way** (test frames `renders/c2/frames_progress_t1…t6`):
  1. Layers took their height from the curl at their own pivot, and the background ended up above the body. Then flat cards near the top of the page sank under the paper, which lifts about 2 mm there, so only their shadows showed. Fixed by the world-space curl modifier.
  2. The jaw landed at the world origin: a new object's `matrix_world` is stale until the depsgraph updates, so the parenting used identity. Fixed with `view_layer.update()` before parenting.
  3. Texture aliasing: cubic sampling skips mipmaps, and pieces are minified up to about 12×. Fixed with linear (mipmapped) sampling.
  4. Eevee draws only the frontmost of several overlapping **blended** surfaces, so stacked layers vanished. Cutouts are now **dithered** (their alpha is the cut, nearly binary); only the print layers stay blended.
  5. The first renders of the Prudence, Mercury and cherub close-ups came out black: the camera was nearer than Blender's 0.1 m default clip. They were archived to `archive/renders/c2/*_superseded_near-clip-black*` and re-rendered with a 2 mm clip.
- **Self-assessment:**
  - Holds up: each figure reads as engraved paper. The hinges turn cleanly and the boil is subtle. What a swing uncovers reads as engraving, not blank paper.
  - Weaker: the fills are a little paler and more regular than Durand's hatching around them, so a big swing (Prudence's scales arm) shows a lighter ruled patch. The jaws are the whole lower face, which reads as a cutout gag but is coarse.
  - Not built yet: props (the torch, pen, scissors, coins, scroll, ledger, quill), the transfer form on the back, the second, tinier certificates (S09), and the studio vignette (verse 1).
- **Also:**
  - `.gitignore` now covers frame sequences of any name (`**/frames_*/`), `archive/renders/` and the regenerable puppet layers. The masks stay in git, since SAM's output could differ on another machine.
  - The brief was re-exported at doc rev 30 (S36 moved); `docs/brief.md` differs from rev 28 only in that row.
- **Why:** The puppet build comes before the animatic (C4). The inherited checkpoints have no step for it, so this is checkpoint C2 here: C2's track check was done retroactively in step 2.

## 2026-10-25T10:42:07-04:00 — C3: as-sung lyrics, word alignment, beats and bars, the key change, the timing map and its preview

- **What:**
  - Transcribed both vocal stems to find what is sung where, and drafted the as-sung lyrics.
  - Aligned every word, built the 4/4 grid, and located the key change.
  - Built the timing map, with every shot in the brief resolved to the clock, and rendered the C3 preview against the Suno mix.
- **Commands** (all `.venv/bin/python -I`, in order):
  - `uv add torchaudio==2.8.* librosa soundfile mido faster-whisper "beat-this @ git+…@b95c8ab"` (the beat_this pin approved in Not Yet)
  - `scripts/first_pass.py`: faster-whisper medium.en, int8, CPU. Its own audio decoding fails on the installed PyAV (`metadata_errors`), so audio is decoded with librosa.
  - `scripts/align_words.py` (torchaudio MMS_FA, ported from Not Yet; each section names its stem)
  - `scripts/beats_beat_this.py`, `scripts/meter.py` (ported to 4/4, drum stem), `scripts/key_windows.py`, `scripts/stem_envelopes.py`, `scripts/timing_map.py`, `scripts/c3_preview.py`
- **Outputs:** `lyrics/as_sung_draft.txt`; `timing/{first_pass_vocals,first_pass_backing,words,beat_this,beats,keys,drum_onsets,timing_map}.json`, `timing/envelopes/{vocals,backing}.npy`, `timing/timing_map.md`; `config/{meter,shot_anchors}.json`; `scripts/{song,first_pass,align_words,beats_beat_this,meter,key_windows,stem_envelopes,timing_map,c3_preview}.py`; `renders/c3/c3_preview.mp4` (960×540, 24 fps, 283.4 s)
- **Findings:**
  - **Tempo and bars:** 68.2 bpm, steady (p5–p95 66.7–69.8), against the prompt's 72. 82 bars, all 4 beats except two 2-beat bars:
    - 131.6 s, where the lyrics' "(beat)" pause before "through this fund" falls; it may be real;
    - 235.6 s, in the final chorus.
  - **The key change:** A major → **Bb major**, on the beat at **98.44 s**. That's beat 3 of the bar before verse 2's pickup, so it does sit right before verse 2, as the human heard. A dominates the 1 s windows to 97.5 s and Bb from 98.5 s. It's a **half step**, not the whole step the prompt asked for: another of Suno's changes. S36 now sits at 98.44 s.
  - **Verse 3** (the live one) is in **Bb major**, the key the human plays in.
  - **The live window:** 163.90–192.68 s. The brief's S29 says "the downbeat after the chorus" (164.78 s), but the generated verse 3's pickup ("They call me…") starts at 164.14 s, before that downbeat. The map proposes the cut on the beat before the pickup (163.90 s), so no generated word leaks before the music cuts. The music re-enters with the bridge, "And it's real", at 192.68 s. This is for the ear check.
  - **Suno's changes to the sung words**, from the first pass, to check by ear:
    - chorus 2 opens with "share the shares" four times;
    - the choir chants "a place of peace" under the Worker's verse (173–202 s), which is in no draft;
    - an "oh" choir runs through the bridge into the final chorus (203–232 s);
    - the bridge's closing "When it's not!" is sung once, by the lead, not twice by the choir;
    - the final chorus has no "baseline to be announced!": **S39's cue isn't sung**;
    - the Worker's "do I get a say?" in the final chorus is sung by Suno (239.66 s), and the human's own recording replaces it (S40);
    - verse 3 is sung as submitted, with "spent".
  - **Alignment:** all 68 lines aligned; 112 of 421 words score below 0.3, nearly all choir lines under the full band. The words are listed in `timing/timing_map.md`.
  - **Shot cues:** 42 of 48 resolve to the clock. S01 is pre-roll and S45–S48 come after the audio ends, so they have no time; S39 isn't sung.
- **Why:** The inherited checkpoint C3: a low-res preview with captions and beat flashes; the human checks sync by ear.
- **Status:** **C2 and C3 are ready for review.** The agent stops here.

## 2026-10-25T11:04:57-04:00 — C2 and C3 re-presented: a pose sheet, and a click-track ear check

- **What:**
  - **C3:** replaced the lane preview as the thing to review with `renders/c3/c3_clicks.mp3`: the mix 6 dB down, a click on every beat (accented on downbeats), and a two-note tone at the key change, the cut before the live verse and the music's return. Instructions are in `renders/c3/c3_clicks.md`. The lane preview is kept but is no longer the review item.
  - **C2:** a pose sheet with each puppet at rest beside three extreme poses (20–40° swings, against the cast test's 4–14°).
- **Commands:** `.venv/bin/python -I scripts/c3_clicks.py`; `blender -b --factory-startup --python scenes/blender/c2_poses.py -- renders/c1/certificate_v04 renders/c2/poses 1280 720 32`; `.venv/bin/python -I scripts/c2_pose_sheet.py renders/c2/poses renders/c2/c2_poses.jpg`
- **Outputs:** `scripts/{c3_clicks,c2_pose_sheet}.py`, `scenes/blender/c2_poses.py`, `renders/c3/c3_clicks.{wav,mp3,md}`, `renders/c2/poses/`, `renders/c2/c2_poses.jpg`
- **Bug found:** the first pose sheet showed swirled moiré patches behind Mercury's legs and the cherubs. Their layers dated from the first fill method: only Progress and Prudence had been rebuilt after the fill was reworked. So the C2 cast clips of Mercury and the cherubs also carry the old fill. Rebuilt both (`scripts/puppet_build.py mercury cherubs`) and re-rendered the poses. The first sheet is archived in `archive/renders/c2/*poses_superseded_stale-fill*`.
- **Seen at full swing:** the fills read as straight engraved ruling, but they're visible as patches where a big swing uncovers a large area: Mercury's back leg, and under the cherubs' lifted arm. Prudence's scales arm leaves a lighter ruled strip.
- **Why:** The human's feedback (human_interventions, same time).

## 2026-10-25T11:17:24-04:00 — C2: fills by texture synthesis from the surrounding engraving

- **What:** `scripts/puppet_build.py` now fills every hole (what a moved part uncovers, and the vignette behind each figure) with exemplar-based texture synthesis, after Efros–Leung and Criminisi et al., simplified:
  - holes are filled in 24 px cells, from the edge inward;
  - each cell copies the patch within 280 px whose known 14 px surround best matches (masked squared difference, OpenCV `matchTemplate`);
  - a tone constraint (the candidate's mean ink within ±30% of the surround's, and at least 70% of it) stops bare paper from "matching" faint sky;
  - one of the four best candidates is picked at random (seeded), so large holes don't repeat;
  - sources are untouched pixels only, so nothing synthesised is copied again.

  The line screen (`line_screen`) is kept in the file but is no longer called.
- **Commands:** `.venv/bin/python -I scripts/puppet_build.py` (6 min for all four figures on CPU); `blender -b --factory-startup --python scenes/blender/c2_poses.py -- renders/c1/certificate_v04 renders/c2/poses 1280 720 32`; `.venv/bin/python -I scripts/c2_pose_sheet.py renders/c2/poses renders/c2/c2_poses.jpg`
- **Iterations:**
  1. Without the tone constraint, blank paper outside the vignette won for faint sky, leaving white blocks in Mercury's background. Cells skipped for lack of a source were also dropped, not retried.
  2. Retries (up to 6) and the tone constraint fixed both. The floor was then tightened from "+0.02" to "at least 70% of the surround".
- **Outputs:** `assets/puppets/*/layers/` rebuilt; `renders/c2/poses/`, `renders/c2/c2_poses.jpg`. The line-screen pose sheet is archived as `archive/renders/c2/*line-screen-fill*`.
- **Result:** what a swing uncovers continues Durand's own stipple, ruling and drapery hatching. The C2 cast clips (`renders/c2/cast_*.mp4`) still show the old fill and are superseded for review by the pose sheet.
- **Remaining:** under Prudence's raised scales arm, the 24 px cells show as faint blocky seams in the diamond hatching at full size; they're not visible at the pose sheet's scale. That's the largest uncovered area in the cast.

## 2026-10-25T17:05:37-04:00 — C2: every moving part re-cut by hand; the cherubs get bodies

- **Why:** the human rejected the pose sheet: bits of every pose stayed behind (human interventions, same time). C3 is approved.
- **Diagnosis:** the old cuts. SAM, prompted with boxes and points, followed the hatching, not the limbs, and every part was clipped to SAM's figure outline. So:
  - Progress's arm polygon sat on her sleeve, beside the forearm, and missed the fist. The spear strip ran up to 27 px off the shaft.
  - Prudence's scales-arm polygon sat on the drapery to the left of the arm. Her sword cut missed half the cross-guard.
  - Mercury's figure outline stopped at his fist, so the caduceus was never cut. His bent leg had no layer.
  - The cherubs swayed as one piece with the cartouche, and their heads lost cheeks, a nose and a hand to the body.
- **What:**
  1. Every moving part is now a hand cut, traced over the ink on a coordinate grid (agent-authored polygons and strips in `config/puppets.json`, same as the earlier prompts). The exceptions are Prudence's head and Mercury's head, wing and two legs, which SAM cut whole. The spear and sword blade were re-measured from ink-row profiles.
  2. `scripts/segment.py`: a hand cut is no longer clipped to SAM's figure; it extends it. A new `tight` polygon keeps only the engraved strokes inside it (connected strokes of 300 px or more), so the caduceus's snakes move without the sky between them.
  3. New hinges:
     - Progress's forearm, fist and spear bend at the elbow; her head takes the white plume left of the spear.
     - Both jaws are now the chin below the mouth line, not the lower face.
     - Mercury has a third leg (`leg_bent`).
     - Each cherub has its own body (`body_top`, `body_left`, `body_center`) carrying its head (and the left cherub's arm). The frame and scrollwork stay put. The top cherub's body takes its cross-hatched legs.
  4. `scripts/puppet_build.py`:
     - SAM's slivers along a traced cut (a limb's outline stroke, the edge of a spear) are handed to the part they touch, or to the static background if they touch none, instead of staying on the body as thin paper strips.
     - Fill cells the synthesis can't reach are dropped from a cutout's mask (the background's fill shows), not painted as a flat grey tint.
  5. `scenes/blender/c2_poses.py`: poses updated for the new hinges.
- **Commands:** `.venv/bin/python -I scripts/segment.py`; `.venv/bin/python -I scripts/puppet_build.py` (6 min); `blender -b --factory-startup --python scenes/blender/c2_poses.py -- renders/c1/certificate_v04 renders/c2/poses 1280 720 32`; `.venv/bin/python -I scripts/c2_pose_sheet.py renders/c2/poses renders/c2/c2_poses.jpg`
- **Iterations:**
  1. The first re-cut left one edge of the sword blade on the body: its shaded right edge lies outside a 34 px strip. It was re-measured, and the strip is now 46 px, offset right.
  2. A paper box appeared where the spear tip had covered the border, and grey blots where the fill had nothing to copy. The sliver hand-off and the unreached-cell drop fixed both.
- **Checks:** a cut map (each part tinted over the ink) for each figure before the build, then each pose at full size.
- **Outputs:** `assets/puppets/*/masks/`, `preview.jpg`, `puppet.json` and `layers/` rebuilt. The SAM cuts are archived in `archive/puppets/<figure>/sam-cuts/`, the rejected pose renders in `archive/renders/c2/poses_sam-cuts/` and `archive/renders/c2/c2_poses_sam-cuts.jpg`. New: `renders/c2/poses/`, `renders/c2/c2_poses.jpg`.
- **Remaining:**
  - The fill is still blocky where a swing uncovers a large area across two textures: under Prudence's raised scales arm (sky lines copied into the drapery) and in her sword's path.
  - A few ragged fill edges where the left cherub sways.

## 2026-10-25T17:29:43-04:00 — C2: smaller fill cells, feathered seams, holes split by the nearer side

- **Why:** the human asked for it (human interventions, same time), for the blocky fill under Prudence's swings.
- **What:** `scripts/puppet_build.py`:
  1. Synthesis cells 24 → 16 px (overlap border 14 → 10).
  2. Each new patch fades into the already-synthesised pixels around it (never into original ink); see iteration 1 for the width.
  3. A layer now takes only the part of a hole that lies nearer its own pixels than the background, using distance transforms. A hole over the sky is filled by the background with sky ruling; a hole over drapery goes to the body.
- **Commands:** `.venv/bin/python -I scripts/puppet_build.py` (7 min, twice); `blender -b --factory-startup --python scenes/blender/c2_poses.py -- renders/c1/certificate_v04 renders/c2/poses 1280 720 32`; `.venv/bin/python -I scripts/c2_pose_sheet.py renders/c2/poses renders/c2/c2_poses.jpg`
- **Iterations:**
  1. 16 px cells with an 8 px feather softened the seams only a little, and blending two misaligned cross-hatches greyed them. The feather is now 3 px.
  2. The cause turned out to be the hole split: the strip the scales arm uncovers had been cut down the middle, half pale body paper with a scissor edge, half sky. The nearer-side split fixed it.
- **Outputs:** `assets/puppets/*/layers/` rebuilt; `renders/c2/poses/` and `renders/c2/c2_poses.jpg`. The previous renders are archived as `archive/renders/c2/poses_24px-cells/` and `archive/renders/c2/c2_poses_24px-cells.jpg`.
- **Result:**
  - Where Prudence's scales arm crossed the sky, the uncovered strip now continues the ruling, with no pale strip.
  - Seams between fill cells are softer.
  - Still visible at full size: where a swing uncovers her strongly curved drapery (below the scales arm, and along the sword's path), the copied patches can't follow the curve, so they read as patchwork. At the pose sheet's scale it reads as engraving.

## 2026-10-25T17:56:55-04:00 — The laborer's hammer raised; certificate v05

- **Why:** the human chose it (human interventions, same time). C2 is approved. Progress's shield stays as engraved; nothing to change.
- **What:**
  1. `config/laborer.json`: hand-traced cuts over the ink on a grid, as for the puppets:
     - the forearm and fist, turned 60° at the elbow;
     - the hammer (its handle re-measured from ink-row profiles), turned a further 70° at the fist.
  2. `scripts/laborer_raise.py` bakes the pose into a new ink piece, `assets/engravings/ink/laborer_raised.png` (the rest-pose piece is kept):
     - the hole is filled by the puppets' texture synthesis;
     - the two pieces are pasted back turned, with the scissor edge.

     He still never moves; only his engraving changes.
  3. `scripts/puppet_build.py`: `synth`/`fill` take a search radius. The laborer uses 60 px, so the shirt and apron fill from themselves rather than from the forge's glow, with a second pass at 280 px for the cells it can't reach.
  4. `config/look.json`: `laborer_ink`, the ink file for the laborer's box. `scripts/certificate.py`, `scenes/blender/lib/puppet.py` (`print_piece`) and the C2 scenes read it.
  5. `scenes/blender/laborer_close.py`: a still of the corner in S07's framing.
- **Commands:** `.venv/bin/python -I scripts/laborer_raise.py`; `.venv/bin/python -I scripts/certificate.py renders/c1/certificate_v05`; `blender -b --factory-startup --python scenes/blender/laborer_close.py -- renders/c1/certificate_v05 renders/c2/laborer_raised_close.png 1280 720 32`
- **Iterations:**
  1. An 18 px handle strip left the handle's shaded edge behind. It is now 34 px.
  2. A 280 px search filled the shirt with grey forge glow. 60 px plus a second pass fixed it.
- **Outputs:** `renders/c1/certificate_v05/` (sheet and plates with the raised hammer; its `static/` and `layout.json` are byte-identical to v04's). `renders/c2/laborer_raised_close.png`, `assets/puppets/laborer/raise_preview.jpg`. Later steps use v05.

## 2026-10-25T19:42:59-04:00 — C4: the animatic

- **What:** the whole cut at final timing, in grey-box, low-res, on the GTX 970: 640×360, Eevee at 8 samples, every second frame (2,920 frames in 42 min, 0.86 s a frame), with the S01 and S45–S48 placeholder cards around the song.
- **Code and config:**
  - `scenes/blender/animatic.py`: the certificate world (v05 static print, desk, the C1 light), the C2 puppets, the raised laborer, and every prop the shot list names.
    - Props in the certificate's type and inks where the brief gives their words: 5%, LLC, the calendar, the shares figures, the transfer form, BASELINE: TBA, +50%, WHOLLY OWNED.
    - Grey labelled cards elsewhere: mic, door, pen, eraser, quill, scissors, coins, scroll, ledger, seal.
    - Every frame is a function of song time: puppets on twos, camera smooth, cutting between shots. Nothing is keyed by hand.
    - Jaws open on each word of the figure's own sections, and the cherubs sway one side per beat through the choruses. The shot actions are tied to their anchors.
    - Props on the page bend with the sheet's curl (the puppets' world-space modifier).
  - `config/c4_shots.json`: the agent's framing per rendered shot (from and to boxes in sheet pixels), and the placeholder texts and lengths.
  - `scripts/animatic_assemble.py`: frames, black cards for the unrendered shots, the mix (delayed by the 4 s S01 pre-roll), and burned-in captions in the certificate's fonts: karaoke lyrics, shot IDs, the title and LIVE bug as graphics stand-ins, and the C5 notes.
  - `scripts/c4_anchor_sheet.py`: one still per rendered shot.
- **Commands:** `blender -b --factory-startup --python scenes/blender/animatic.py -- --out renders/c4/anchors_v1 --anchors`; `… -- --out renders/c4/frames_v1 --step 2`, then `… --from 266.0` after S44's reframe; `.venv/bin/python -I scripts/animatic_assemble.py renders/c4/frames_v1 2 renders/c4/c4_animatic.mp4`; `.venv/bin/python -I scripts/c4_anchor_sheet.py renders/c4/anchors_v1 renders/c4/c4_anchor_sheet.jpg 6`
- **Iterations:**
  1. Anchors, first pass:
     - the tinier certificate's box didn't match where it is drawn;
     - the torch box ignored the raised tip;
     - Mercury's run panned away from him;
     - S08's mic card covered the plaque;
     - the seal's label drifted off (it was parented while the seal sat at the origin).
  2. The camera now aims with an explicit look-at with north up, since `to_track_quat`'s up axis is ill-conditioned looking straight down. A corner projection confirmed the framing.
  3. S44 originally pushed in from wide over 17 s, so the drawer shut before Progress read. It is now close on her. The wide frames are archived in `archive/renders/c4/frames_v1_S44_wide/`.
  4. One assembly was cut off mid-encode by a shell timeout and was re-run.
- **Outputs:** `renders/c4/c4_animatic.mp4` (313.4 s), `renders/c4/c4_anchor_sheet.jpg`, `renders/c4/anchors_v1/`, `renders/c4/c4_review.md` (what to judge, the stand-ins, the open questions).
- **Open for the human (`c4_review.md`):**
  - the long holds in S17 and S25 (inserts or not);
  - S39, which isn't sung (retire it or move it);
  - only one cherub has an arm cut;
  - the stand-ins for S36 and S44;
  - the placeholder lengths;
  - the print files for the live shoot (the back's transfer form still to draw).
- **Status:** **C4 is ready for review.**

## 2026-10-25T20:30:16-04:00 — C4: the sync fix (mouths on the voice, the sway on the beat), and a sync test

- **Why:** the human: "the sync is not quite right" (human interventions, same time).
- **Diagnosis:**
  1. Mouths: each jaw opened for whole words and closed only at a word's end. 37% of the gaps between words are under 60 ms, so fast lines read as a mouth hanging open. C3's vocal envelopes, made for mouths, were never used.
  2. The cherubs' sway (`sin` of the beat phase) crossed centre on each beat and peaked between beats, which reads as late. Mercury's stride had the same fault.
  3. Word timings, checked by cross-correlating the aligned word starts with each vocal stem's onset envelope:
     - per section, they sit 15–90 ms ahead of the attacks;
     - per line, 10 lines were flagged at 120–385 ms late.

     Spectrograms showed that measure is unreliable: it locks onto the loud part of a word, not its start. Only L09's first words ("So we") are late, by about 150 ms, which the new 170 ms early gate covers.

     A first fix that moved lines by that measure (`snap_words.py`) was wrong and is archived unused in `archive/timing/snap_rejected/`. The C3 alignment stands.
- **What:** `scenes/blender/animatic.py`:
  - Jaws are now driven by C3's envelopes, gated to the figure's own words (from 170 ms before each word to just after it). Within the gate, the stem's loudness against its local peaks and dips (±5 frames) sets the opening, one frame ahead of the sound, in three positions (shut, half, open). That gives about 4 jaw changes a second, close to syllable rate, and the jaw shuts in pauses.
  - The sway and the stride now use `cos` of the beat phase, so the extreme lands on the beat.
- **New:** `scripts/c4_sync_test.py`; `renders/c4/c4_sync_test_v1.mp4` (20.3 s: S03–S04, S10, S13, S18 excerpts at 24 fps with the mix).
- **Next:** re-render the whole animatic once the human has checked the test clip.

## 2026-10-25T21:31:43-04:00 — C4 v2: the chorus inserts, S39 placed, the sync fix, full re-render

- **Why:** the human's "do both" (human interventions, same time), and the approved sync fix.
- **Brief:** Claude Doc rev 31 (rows S17a, S17b, S25a, S25b, S25c; S39's cue). Re-exported to `docs/brief.md` with `scripts/doc_to_md.py`; the diff against rev 30 is exactly those six rows.
- **Timing map:** `scripts/timing_map.py` now takes ordinal cues ('The third "share the shares"'): the n'th time the phrase is sung after the previous shot. That places an insert inside a long line.
  - New anchors: S17a 85.01, S17b 90.49, S25a 141.12, S25b 143.38, S25c 146.26, S39 234.45. No other anchor moved.
  - S25a was checked on a spectrogram. Chorus 2's first "shares" is held for 5 s under a lead melisma (134.5–139.3 s), so the third "share the shares" is at 141.1 s, as aligned.
- **Animatic (`scenes/blender/animatic.py`, `config/c4_shots.json`):**
  - framings for the six shots;
  - the shares figures keep changing through S17b, and again in S25c;
  - S39: Mercury dips below a line of fine print and pops up out of it, growing from almost nothing with an overshoot, then raises the caduceus. An earlier test that slid him 300 px down showed him over the laborer's vignette, and was replaced.
- **Render:** `renders/c4/frames_v2` (full, `--step 2`) and `renders/c4/anchors_v2`, assembled to `renders/c4/c4_animatic.mp4`. The v1 cut is archived as `archive/renders/c4/c4_animatic_v1_word-gated-jaws.mp4`.
- **Result (v2):** 2,920 frames in 43 min, with no errors. `renders/c4/c4_animatic.mp4` is 313.4 s. `renders/c4/c4_anchor_sheet_v2.jpg` shows the six new shots in place. The v1 anchor sheet is archived as `archive/renders/c4/c4_anchor_sheet_v1.jpg`.
- **Status:** **C4 v2 is ready for review.**

## 2026-10-25T22:40:03-04:00 — C4 v3: S24's exchange re-aligned, the graphics layer, legible 5%

- **Why:** the human's C4 v2 review (human interventions, same time).
- **S24 ("through this fund"), found on spectrograms and a re-transcription of 131–141 s (faster-whisper medium.en):**
  - Suno sings the exchange in the opposite order from the lyrics: the choir's "Through this fund!" first (from about 133.3 s, "fund" held to about 137 s), then the lead's echo "through this fund" (134.9 s, a melisma to about 138.5 s).
  - Chorus 2 starts only at 139.4 s, with three "share the shares", not four.
  - `lyrics/as_sung_draft.txt` had only the choir's line, and four "share the shares" from 133.3 s. So the alignment put chorus 2 on top of "this fund", and the captions, the mouths and S25 were wrong until "five in every hundred".
  - Fixed: a new section `[Pre-Chorus 2 echo | Vocals | the Lawyer]`, chorus 2 with three "share the shares", and new windows in `scripts/align_words.py`. Re-aligned, and the timing map rebuilt.
  - S24 now starts on the choir's "Through" (133.26 s) and holds through Mercury's echo; S25 starts at 139.36 s.
- **S25a:** with three "share the shares", the third (142.7 s) left S25a 0.7 s. Its cue is now the second (141.12 s): brief rev 32, mirrored in `docs/brief.md`.
- **The graphics layer (`overlays/graphics.html`):**
  - Approach: following Ghost in the Machine's HTML overlays rendered with Puppeteer (`scripts/render_frames.mjs`, copied), not Remotion. `package.json` was already set up for it. `scripts/render_graphics.py` renders each layer for its shot, and `scripts/animatic_assemble.py` composites them per frame.
  - Over the picture:
    - the S02 title in ruled engraved capitals, resolving left to right on a paper plate;
    - the LIVE bug, telethon style with the pledge line (steady on S13, blinking on S25–S25c);
    - S30's "Post-filter: no change" tab.
  - Full frames:
    - S01, a stand-in screen built from the logged style prompt, lyrics and take. The real screen capture is the human's (R4).
    - Styled slates for the live shots.
    - S47, the fact card: the brief's draft text with "Gemini 4 Argon" filled in, appearing line by line. Checked against the sources at C6.
    - S48, the real announcement page (`scripts/capture_page.mjs`: `assets/screens/announcement.png` with its text and fetch metadata), scrolling, then the "Derived from" credits. The brief doesn't define those credits; the agent followed Ghost's end card (sources, music take, lyrics and audit, the live verse, animation, the intervention count read from this log, the log link at publish).
  - S48 now runs 11 s.
- **The 5%:** each corner's face is now a round green counter covering the centre and inner rosette (r 180 px of 210). The "5" is as large as the printed one (205 px) with a smaller "%" beside it, where the first version had a square card with "5%" at 150 px. A first test had the type 0.05 mm above the face, and it flickered into it; it is now 0.5 mm above.
- **Outputs:** `renders/c4/frames_v3`, `renders/c4/anchors_v3`, `renders/c4/c4_anchor_sheet_v3.jpg`, `renders/c4/c4_animatic.mp4`. v2 is archived in `archive/renders/c4/`.
- **Result (v3):** 2,920 frames in 41 min, with no errors. `renders/c4/c4_animatic.mp4` is 318.4 s (S48 now runs 11 s). Checked on stills:
  - S24 holds the transfer form through the choir's "Through this fund!" and Mercury's echo, with the captions in step;
  - the four corners read "5%" in the wide shots;
  - the graphics land in their places.

  The S30 slate's text no longer repeats the post-filter tab.
- **Status:** **C4 v3 is ready for review.**

## 2026-10-26T07:33:32-04:00 — C4 v4: the animatic's audio offset, and Suno's repeats re-aligned

- **Why:** the human's C4 v3 review (human interventions, same time).
- **The start: the audio ran 1.5 s early (v1–v3).** Measured by cross-correlating the animatic's decoded audio with the Suno mix:
  - it sat 2.47 s after the picture where the pre-roll is 4.00 s, and the gap grew to 2.82 s by 260 s;
  - the AAC stream had broken packet timestamps: one 1.6 s packet at 4.03 s (the pre-roll's end) and pairs of 1-sample packets through the song. Players that follow the timestamps were right, and players that just play the samples ran the audio about 1.5 s early, so the captions and mouths read late against it;
  - the same audio chain encoded on its own measures exactly 4.000 s throughout. The cause was encoding the delayed audio in the same ffmpeg graph as the slow video and captions;
  - fixed in `scripts/animatic_assemble.py`: the audio is encoded on its own (`adelay`, `apad`, AAC), then muxed in with `-c:a copy`.

  The intro's own alignment checks out against the vocal stem's energy ("Right" at 2.80 s, where the voice starts at 2.77 s).
- **Suno's repeats, found by re-transcribing both vocal stems in overlapping 14 s windows (faster-whisper medium.en), then 6 s windows of the stems and the mix for 208–226 s and 244–264 s, with onsets and a spectrogram:**
  - Chorus 1's repeat: the choir sings "the more we give" twice (86.6 and 90.3 s), and the lead's "so help us grow" comes only at 91.8 s. A new line; S17b moves 90.49 → 92.00 s.
  - "So help us grow" (both in chorus 1): the choir holds "the more we give" under the lead, and on the choir stem the line was squeezed 0.5–1 s early. Those two lines are now aligned on the lead stem in their own windows (`ON_STEM`). S17 moves 77.47 → 77.96 s.
  - Chorus 2 has two "share the shares" after the tag, not three: the v3 count was wrong. "Five" is at 142.7 s, and S25b moves 143.36 → 142.70 s. S25a (the second) stays at 141.12 s.
  - The bridge's "When it's not!" is sung three times (212.5, 214.9, 216.5 s; the last "not" held to 220.3 s), and the final chorus opens with two "share the shares" (220.5, 222.3 s). The as-sung draft had one of each, while the brief's cues (S35, S37) already had the repeats. New sections: `Bridge tag`, with one window per line (as one window, its lines came out up to 2 s late), and `Final Chorus open` on the choir stem, where the lead's is a blur. S35 moves 212.95 → 212.53 s, S37 216.48 → 220.50 s, and S38 231.97 → 232.67 s.
  - The outro matches the lyrics: the lead sings "grow" where the choir sings "give", and the captions follow the choir.
  - Known: the aligner ends the held last "not!" at 218.3 s, so the Founder's jaw shuts 2 s before the note ends. A C5 item.
- **Code:** `scripts/align_words.py` takes per-group windows (line count, start, end) and `ON_STEM` lines; `lyrics/as_sung_draft.txt`; `timing/words.json` and `timing/timing_map.json` rebuilt (72 lines, 53 shots, none unresolved).
- **Render:** `renders/c4/frames_v4` is a copy of v3, with the frames re-rendered for every shot whose span moved and every re-aligned line (74.6–99.0, 139.0–147.0, 210.0–236.0 s; `--step 2`). The graphics layer's timings are unchanged. The v3 cut is archived as `archive/renders/c4/c4_animatic_v3_audio-early.mp4`.
- **Outputs:** `renders/c4/frames_v4`, `renders/c4/anchors_v4`, `renders/c4/c4_anchor_sheet_v4.jpg` (the v3 sheet archived), and `renders/c4/c4_animatic.mp4`.
- **Result (v4):** 704 frames re-rendered, with no errors. The cut is 318.4 s, assembled from 2,920 frames.
  - The audio is clean AAC (fixed-size packets), and its delay measures 4.000 s at 3, 8, 30, 100, 200, 260 and 280 s.
  - Checked on stills: the captions are on the right lines at 3.0, 78.6, 92.6, 143.0, 213.0, 215.2, 221.0 and 222.6 s.
- **Status:** **C4 v4 is ready for review.**

## 2026-10-26T09:50:55-04:00 — C5 props: the prop sheet (v1)

- **Why:** the plan the human approved (human interventions, 08:05): engraved props in place of the C4 grey cards, reviewed on one sheet before they go into the shots.
- **Sources (logged in `assets/engravings/sources.tsv`; files in `assets/engravings/source/`):**
  - US patent drawings, all published before 1931 (public domain), from the USPTO's full-text PDFs (`image-ppubs.uspto.gov/…/downloadPdf/<number>`, page 1's embedded 300 dpi scan via `pdfimages`). Found with Google Patents search (`patents.google.com/xhr/query`, US, published by 1930-12-31) until it started refusing requests (503).
    - Used: 1,318,874 (microphone), 1,183,842 (door), 979,010 (filing cabinet), 551,026 (hand stamp) and 1,083,913 (desk calendar).
    - Considered and not used, marked in the table: 1,005,339 (thermometer) and 44,459 (seal press).
  - Met Open Access 393924: Durand's arched framing element, the studio's crown. It is the same banknote set as the figures; the agent listed the set's titles from the Met API (393922–393995).
  - Wikimedia Commons, Pearson Scott Foresman's public-domain line art: Quill (PSF) and Scissors (PSF). The quill is cut out of a writer's hand.
- **Code:**
  - `config/props.json`: the cut props (crop, erase boxes and polygons for numerals and lead lines, trim, despeckle) and the generated ones;
  - `scripts/props.py`: cuts, re-set labels and the generated props, drawn in the certificate's type, lathe work and a new line-hatching helper → `assets/engravings/ink/props/`;
  - `scripts/c5_prop_sheet.py` → `renders/c5/c5_props_v1.jpg`.
- **The props:**
  - Cut from sources: the studio microphone, the arch, the door, the desk calendar, the hand stamp (its label reads +2%), the quill (it serves as S20's pen), the scissors, and the filing cabinet's four drawers. The cabinet's example names are erased and the labels re-set with the brief's still-to-be-announced terms: BASELINE, GOVERNANCE, MILESTONES and WHOLLY OWNED.
  - Generated:
    - the studio (the arch over a panelled wall and a boarded floor, with a SILENCE plaque);
    - the door's WHOLLY OWNED plaque;
    - ten calendar pages (the C4 animatic's months);
    - coins (a face reading FIVE IN EVERY HUNDRED, and a stack);
    - an India-rubber eraser;
    - Mercury's scroll ("Not for lobbying, not for campaigns, not for politics, we swear.");
    - the transfer form for the certificate's back, at the sheet's size, for the render and the printed prop;
    - the face-down document, whose print only shows through, reversed and blurred;
    - the thermometer (a bulb on a BASELINE: TBA ribbon, and a +50% scale);
    - the corporate seal's die and its embossed impression;
    - the ledger, its ruling in the green plate.
- **Known:** a few leftover stubs from the erased numerals (the stamp's top, the calendar's margin, the cabinet's edges). The patent drawings are line art, with less tone than Durand's engravings.
- **Not yet:** the props are not in the shots, which waits on the human's review of the sheet. S36's gold re-ink is not a prop and comes with C5's renders.
- **Status:** **the C5 prop sheet is ready for review.**

## 2026-10-26T10:13:03-04:00 — C5 props: clipped type fixed (prop sheet v2)

- **Why:** the human's review of prop sheet v1 (human interventions, same time).
- **Found:**
  - The calendar pages: NOV, DEC, JAN, SOON, TBD and NEXT ran past the page border; the Q of Q1 and Q2 hit the company line.
  - The scroll's last lines of fine print ran under the bottom roller's shading, and the last line stopped mid-clause.
  - The filing cabinet's labels printed at 16–27 px: the patent figure is small, so WHOLLY OWNED would not read in S44.
  - The sheet's own captions: role lines cut at 96 characters, and source lines running off their tiles.
- **Fixed:**
  - `scripts/props.py` sets every line with `fit()`, given the frame the line sits in: the largest size up to the design size whose inked extent (ascenders and descenders, measured on the rendered glyphs) clears the frame by a margin, centred on the ink.
  - Every line is recorded, and each run reports the lines that were shrunk and any that still overflow. This run: 117 lines, 35 shrunk, none overflowing.
  - The scroll sets only whole clauses that clear the roller, ending on a full stop.
  - The cabinet cut is enlarged three times before its labels are set (`upscale` in `config/props.json`); WHOLLY OWNED now prints at 48 px on a 1028 px-wide piece.
  - The thermometer's scale labels are larger.
  - `scripts/c5_prop_sheet.py` shrinks each source line to fit its tile and wraps each role over two lines, with the captions moved clear of the pictures.
- **Checked by eye at full size:** the calendar pages, the cabinet, the seal and coin legends (set on a circle, which `fit()` doesn't cover; nothing collides), the eraser, the thermometer, the transfer form, the scroll, the ledger, the door plaque, the studio's SILENCE plaque and the stamp, plus every caption on the sheet.
- **Outputs:** `renders/c5/c5_props_v2.jpg`; v1 archived as `archive/renders/c5/c5_props_v1_clipped-type.jpg`.
- **Status:** **the C5 prop sheet v2 is ready for review.**

## 2026-10-26T10:26:07-04:00 — C5: the engraved props in the shots

- **Why:** the human approved prop sheet v2 ("These look great, keep going"; human interventions).
- **Scene (`scenes/blender/animatic.py`):** every grey card is replaced.
  - New helpers:
    - `prop_card`: a print on the sheet, or a paper cutout with the prop's silhouette, with an optional green plate;
    - `emboss_card`: a blind emboss from a height map;
    - `prop_box`: the prop's own aspect.
  - `scenes/blender/lib/puppet.py` `layer_material` takes a second (green) plate.
- **Per shot:**
  - **S06:** the studio, as one print with the two microphones composed into it, either side of Progress. Overlapping prints would hide each other in Eevee, which draws only the frontmost blended surface. S09's tiny certificates now appear from S09, not S06: from S06 they covered the left microphone.
  - **S08:** the door, its WHOLLY OWNED plaque composed in and centred in the PLAQUE framing (the door moved 71 px down).
  - **S12:** the calendar is printed in the margin, and its ten pages are paper cutouts that flip up over the binding in turn.
  - **S15, S18, S19:** the stamp, the coins on Prudence's scales, and the quill are cutouts.
  - **S20:** the quill rules the baseline, its nib on the line.
  - **S21, S23:** the eraser, and Mercury's scroll on his arm.
  - **S24:** the certificate's back is the transfer form, the face-down document under it.
  - **S32–S33:** the thermometer is a paper card over the stub, covering the stub's own fields; the column of spirit (sepia) rises; the BASELINE: TBA ribbon appears at S33 + 1 s.
  - **S34:** the seal's die carries the seal; after the hit it lifts away (0.8–1.6 s) and leaves the blind-embossed impression.
  - **S37–S38:** the ledger (green ruling) and the scissors.
  - **S44:** the sliding lid is the drawer front. Its WHOLLY OWNED label holder is ruled fresh: the patent's holder, cropped, didn't line up with the re-set label. The label is placed where the closing frame sees the lid, which rides 6 cm above the sheet (measured on a render).
- **Props (`scripts/props.py`):**
  - silhouette masks for the cutouts;
  - `COMPOSE`: overlapping prints are composed into one texture, each piece knocked out of what's behind it;
  - the thermometer redrawn at the stub's size and split into glass, ribbon and column (geometry in `thermometer_geom.json`);
  - `drawer_front` added;
  - the arch's ink floor raised, to clear the scan's grain.
- **Checked:** 720p stills of every prop shot (`renders/c5/props_check_v1`–`v3`).
- **Next:** S36's gold re-ink, the cherubs' arms, then the C5 renders section by section.

## 2026-10-26T10:28:29-04:00 — C5: S36's gold re-ink

- **What:** at the key change (S36, 98.44 s), the certificate's green plate re-inks in gold.
  - It creeps in from the sheet's edges over 2.6 s, as a noisy front, and stays for the rest of the film. The gold catches a little light (metallic 0.55, roughness 0.45 against the paper's 0.82).
  - The corner discs (S14) turn gold with it.
  - The light lifts a little less than at C4 (+10%, where it was +18%), since the ink now carries the change.
- **Code:**
  - `scenes/blender/animatic.py` `gold_reink()`: a reveal value drives the mix toward paper × gold where the green plate printed;
  - `scripts/gold_sheet.py` → `renders/c1/certificate_v05/sheet_gold.png`: the same mix as a picture, for S37's clipped coupons, which are cut from the print;
  - `scripts/animatic_assemble.py`: the C4 caption notes for S36 and S06 are dropped, now that both exist.
- **Checked:** 720p stills at 98.3, 99.2, 100.0, 102.0 and 226.6 s (`renders/c5/gold_check_v1`).

## 2026-10-26T10:39:20-04:00 — C5: every cherub points

- **Why:** the brief's "every cherub points" (S17, S27, S42); at C4 only the left cherub had an arm cut (c4_review open question 3).
- **New cuts (`config/puppets.json`):**
  - `arm_top`: the top cherub's arm, shoulder to elbow and back up toward the chin, pivoting at the shoulder (878, 205). The hand under its cheek stays with the head.
  - `arm_center`: the centre cherub's hanging arm with its whole hand, pivoting at the shoulder (915, 728). The first cut ended at y 1016 and left the hand on the hoop at full swing (checked on a pose render); it now runs to 1064.
- **Pointing (`scenes/blender/animatic.py`):** left −40° (as at C4), top +30°, centre +55°. On the pose sheet, the top arm at ±55° crooked into the legs or doubled over the face, so it lifts less. The centre arm at −55° folded across the chest; at +55° it reaches out.
- **Known:** small synthesis artifacts where the arms hung (a dark mark at the centre cherub's hip); they don't show in the wide shots where the cherubs point.
- **Commands:** `.venv/bin/python -I scripts/segment.py cherubs`; `… puppet_build.py cherubs` (2.5 min); `blender … c2_poses.py -- renders/c1/certificate_v05 renders/c5/cherub_poses 1280 720 16 cherubs` (`c2_poses.py` now takes optional figure names); stills at the three cues (`renders/c5/cherub_point_v1`).
- **Outputs:** `assets/puppets/cherubs` (the one-armed C4 build is archived as `archive/puppets/cherubs_c4_one-arm`).

## 2026-10-26T10:49:21-04:00 — C5 render benchmark; section 1 started (GTX 970)

- **Benchmark** (1920×1080, 64 samples, frames 2–4 of a run after shader compile): S06 (studio) 24.0 s/frame, S13 (wide choir) 18.2, S24 (the back) 11.5, S37 (coupons) 8.8. The whole film at 64 samples would take about 28 h.
  - At 16 samples S06 takes 6.35 s, and at 32 samples 12.2 s.
  - 16 against 64 on the same frame: mean |diff| 0.61 of 255 (p99 7). The difference is the noise of the studio print's blended layer and the dither at cutout edges, invisible by eye at 1:1 and within the line boil the style asks for.
- **Chosen:** `config/render_profiles.json` `c5`: 1920×1080, 16 samples, on the GTX 970. About 6.5 h for every rendered frame. The final 4K profile stays with the RTX 5090.
- **Sections** (`config/c5_sections.json`): six review cuts on shot boundaries, rendered and sent one at a time.
- **Tools:**
  - `scripts/animatic_assemble.py` takes `--graphics DIR`, `--from/--to` (a section; the pre- and post-roll belong to the first and last) and `--captions ids` (shot IDs only, for the C5 cuts). Tested on 130–142 s of the v4 frames: song 133 s lands at 3.000 s into the cut.
  - `scripts/render_graphics.py` takes an output directory.
- **Started:**
  - section 1 (0–46.88 s) into `renders/c5/frames` (log `renders/c5/logs/section1.log`);
  - the graphics layer at 1920×1080 and 24 fps into `renders/c5/graphics`.

## 2026-10-26T12:26:25-04:00 — C5 section 1 cut (S01–S09); section 2 started

- **Render:** section 1, 0–46.88 s: 1,126 frames at 1920×1080 and 16 samples in 1 h 34 min (5.0 s/frame on average), no errors. The graphics layer at 1080p (15 jobs) also finished.
- **Cut:** `renders/c5/cuts/c5_1_intro_verse1.mp4`: 50.9 s (S01's 4 s pre-roll and S02–S09), 1920×1080, shot IDs only. Contact sheet `renders/c5/sheets/c5_1_intro_verse1.jpg` (`scripts/c5_section_sheet.py`, new: one still per shot, 0.5 s in).
- **Fix:** the caption styles were sized for the 360p animatic, so at 1080p the shot ID was a third of its size. `scripts/animatic_assemble.py` now sets the subtitle play resolution to 640×360, and libass scales the styles to the frame. The first cut was re-made, not kept.
- **Started:** section 2 (46.88–98.44 s) into `renders/c5/frames` (log `renders/c5/logs/section2.log`).
- **Status:** **C5 section 1 is ready for review.**

## 2026-10-26T13:16:18-04:00 — S01 retired; S08 pushes in

- **Why:** the human's section 1 review (human interventions, same time).
- **S01 retired:**
  - Brief edit (Claude Doc rev 32 → 34, made by the agent): the opening bookend no longer opens on the generation screen, and S01's row reads "Retired at C5 (it didn't fit the video)". IDs never change, so S01 is retired, not reused. Mirrored in `docs/brief.md`.
  - The film now opens on S02's push into the certificate, at song time 0, with no pre-roll.
  - Code: `timing_map.py` gives a retired row no time; `config/c4_shots.json` sets S01 `before_s` to 0; `render_graphics.py`, `animatic_assemble.py` and `c5_section_sheet.py` skip S01 without a pre-roll; S01 dropped from both graphics job lists.
- **S08:** it held one framing (PLAQUE) for 6.8 s. It is now a slow push from the whole door (DOOR, sheet px 2880–3300 × 520–1020) into the plaque (PLAQUE_TIGHT, 2990–3190 × 625–735).
- **Queued** (`renders/c5/logs/queue_s08_s3.sh`, after section 2): S08's frames (36.89–43.71 s), then section 3 (98.44–139.36 s).

## 2026-10-26T13:53:52-04:00 — C5 section 1 re-cut (no S01, S08 pushing); section 2 cut; section 3 rendering

- **Renders:** section 2 (46.88–98.44 s), 1,238 frames, no errors; S08 re-rendered with its push, 165 frames (36.89–43.71 s), no errors. Section 3 (98.44–139.36 s) is rendering (log `renders/c5/logs/section3.log`).
- **Cuts:**
  - `renders/c5/cuts/c5_1_intro_verse1.mp4` (46.9 s, S02–S09; the film opens on S02 at song time 0);
  - `renders/c5/cuts/c5_2_prechorus_chorus1.mp4` (51.6 s, S10–S17b);
  - contact sheets in `renders/c5/sheets/`.

  The first section 1 cut and its sheet are archived in `archive/renders/c5/cuts/` (`…_v1_with-S01_static-S08`).
- **Checked:** stills at 0.0 s (S02's push), and at 37.0, 40.3 and 43.6 s (S08, from the whole door to the plaque).
- **Status:** **C5 sections 1 (revised) and 2 are ready for review.**
