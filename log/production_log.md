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
