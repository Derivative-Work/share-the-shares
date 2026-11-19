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

## 2026-10-26T14:41:00-04:00 — C5 section 3 rendered; S24's back re-inked gold; section 4 rendering

- **Render:** section 3 (98.44–139.36 s), 983 frames, no errors. A first cut (`renders/c5/cuts/c5_3_keychange_verse2_prechorus2.mp4`) and its sheet were checked by the agent before sending.
- **Found on the sheet:** in S24 the certificate's back (the transfer form) still printed its lathe work in green, though S36 has re-inked the sheet gold. Both sides are one sheet.
- **Fix:**
  - `lib/puppet.py` `layer_material` takes the second plate's ink by palette name, and `prop_card` passes it on;
  - the back prints its lathe work in `ink_gold`.

  The ledger keeps its green ruling: it is Prudence's book, not the certificate.
- **Queued** (`renders/c5/logs/queue_s24_s5.sh`, after section 4): S24's frames (133.26–139.36 s), then section 5 (196.38–220.5 s). Section 3 will be re-cut and sent once S24 is re-rendered.
- **Started:** section 4 (139.36–196.38 s; log `renders/c5/logs/section4.log`).

## 2026-10-26T15:15:46-04:00 — C5 sections 3 and 4 cut; section 5 rendering

- **Renders:**
  - section 4 (139.36–196.38 s): 428 frames, no errors. Its live shots S26 and S29–S31 aren't rendered; they are slates until the human's footage.
  - S24 re-rendered with the gold back: 147 frames, no errors.
- **Cuts:**
  - `renders/c5/cuts/c5_3_keychange_verse2_prechorus2.mp4` (40.9 s, S36 and S18–S24). The green-back first cut is archived as `archive/renders/c5/cuts/c5_3_keychange_verse2_prechorus2_v1_green-back.mp4`.
  - `renders/c5/cuts/c5_4_chorus2_verse3.mp4` (57.0 s, S25–S31).

  Sheets in `renders/c5/sheets/`.
- **Checked:** both sheets; S24 at 36.5 s into its cut shows the transfer form's border in gold.
- **Status:** **C5 sections 3 and 4 are ready for review.** Section 5 (196.38–220.5 s) is rendering.

## 2026-10-26T15:49:16-04:00 — C5 section 5 rendered; S34's die face fixed; section 6 rendering

- **Render:** section 5 (196.38–220.5 s), 579 frames, no errors. A first cut (`renders/c5/cuts/c5_5_bridge.mp4`) was checked by the agent before sending.
- **Found on the sheet:** in S34 the seal's die came down as a plain grey disc. Its engraved face sat only 0.05 mm above the die's top and was hidden by it.
- **Fix:** the face now sits 0.4 mm above. Checked on a 720p still at 210.9 s: the die shows the seal (AMALGAMATED BENEFIT, LLC · CORPORATE SEAL, WHOLLY OWNED, MMXXVI) as it comes down.
- **Queued** (`renders/c5/logs/queue_s34.sh`, after section 6): S34's frames, 210.45–213.5 s (the descent, the hit and the lift-off into S35). Section 5 will be re-cut and sent after.
- **Started:** section 6 (220.5–283.44 s; log `renders/c5/logs/section6.log`).

## 2026-10-26T17:32:07-04:00 — C5 sections 5 and 6 cut; all six sections rendered

- **Renders:**
  - section 6 (220.5–283.44 s), 1,490 frames, no errors;
  - S34 re-rendered with the die's face, 75 frames (210.45–213.5 s), no errors.

  Every rendered frame of the film is now in `renders/c5/frames` (5,840 frames, 1920×1080, 16 samples).
- **Found on section 6's sheet:** S40's slate opened its quote with a closing mark (”do I get a say?”): the certificate's typeface draws a straight double quote as a right curly quote.
  - Fixed: the text in `config/c4_shots.json` now uses curly quotes.
  - `scripts/render_graphics.py` can re-render named jobs only, keeping the other jobs' entries; `slate_S40` was re-rendered at 1080p.
- **Cuts:**
  - `renders/c5/cuts/c5_5_bridge.mp4` (24.1 s, S32–S35);
  - `renders/c5/cuts/c5_6_finalchorus_outro_close.mp4` (93.9 s, S37–S44, then the S45–S48 cards);
  - sheets in `renders/c5/sheets/`.

  The first cuts are archived (`…_v1_grey-die`, `…_v1_straight-quotes`).
- **Checked:** stills of S34's descent, S44's shut drawer, and the fact card in motion.
- **Status:** **all six C5 sections are ready for review.**

## 2026-10-26T18:11:53-04:00 — C5: the red pen on the fact card; credits; the log's home

- **Why:** the human's notes after approving C5 (human interventions, 18:04:04; the fact card's annotations are an EXCEPTION, the human's text).
- **S47, the fact card (`overlays/graphics.html`):** the human's hedges are drawn on in red pen, in a handwritten face (Caveat, SIL OFL, fetched from github.com/google/fonts; `assets/fonts/Caveat-Variable.ttf`, `OFL-caveat.txt`, hashes in `SHA256SUMS`).
  - The marks are placed from the laid-out text: each marked phrase is a span, and the pen's notes and strokes are positioned from its box.
  - After the card's lines are up (5.2 s), one mark lands every 1.05 s: "It's not required to." above the board's 2%; "to allow different forms of giving" struck through, "which legally allows non-charitable activities" written above it; "So they say." after the lobbying line; "to be announced" circled; "Lyrics drafted by Claude, a model made by Anthropic" underlined; "and by the human, October 26, 2026" after Gemini's review.
  - Strokes draw on; notes write on left to right.
  - The lines with a note above them get 52 px more room. A first version let the struck line's correction overlap the line above, and drew carets that read as checkmarks: both fixed before cutting.
  - S47 now runs 15 s (from 7), so the marks can be read.
- **Credits (S48):**
  - "performed live by the human, one take";
  - "Claude Code with Opus 5.5: paper puppets in Blender; the human, DaVinci Resolve" (kept together on one line);
  - Type adds Caveat;
  - "Full production log: github.com/Derivative-Work/share-the-shares", where the human will host the log.
- **For C6:** the human's annotation "which legally allows non-charitable activities" joins the fact-card source check.
- **Renders:** `renders/c5/graphics` fact, announce and credits (their start times moved with S47's length). Section 6 re-cut: `renders/c5/cuts/c5_6_finalchorus_outro_close.mp4` (the previous cut is archived as `…_v2_before-red-pen`). The finished card is in `renders/c5/sheets/s47_fact_card_red_pen.png`.

## 2026-10-26T18:30:31-04:00 — The post-roll's sound (dialling, ring, hold music); the note's arrow

- **Why:** the human's notes (human interventions, same time).
- **The muzak:** the human's Suno cover, lyrics removed, style "muzak" (R4; `log/prompts/suno/muzak.md`). Copied to `audio/muzak/`; both copies' SHA-256 match the sources.
  - Its first chorus is at 72.82 s. The human said "roughly 1:10"; the agent matched the chroma of the song's first chorus (60.6 s) against the cover, best at 72.7–73.4 s for tempo ratios 1.0–1.12, and took the nearest beat.
- **`scripts/postroll_audio.py`** (new; `config/postroll.json`) → `audio/postroll/postroll.wav`: 39.0 s, the length of S45–S48.
  - The pledge line, 555-0142, dialled in standard DTMF (0.11 s tones, 0.07 s gaps) from 1.00 to 2.26 s.
  - One short ring (US ringback, 440 + 480 Hz) for 1.2 s from 2.61 s.
  - The muzak fades in from 3.60 s (from 71.42 s in the cover), so its chorus lands on the cut to S46, the hold music, at 5.00 s. It plays on under the terms and the credits at −3 dB and fades out over the last 2 s. Peak −7.0 dBFS.
- **`scripts/animatic_assemble.py`:** the post-roll's sound follows the song (concat), where there was silence.
- **Checked in the cut's audio:**
  - the first "5" (770 + 1336 Hz) at +1.00 s and the "1" (697 + 1209 Hz) at +1.72 s;
  - the ring at +2.7–3.7 s;
  - the muzak at −18 dB RMS in S46 and −21 dB under the credits, down to −41 dB in the last 0.3 s.
- **S47:** "It's not required to." moves up and to the right, above the middle of the board's line, and a hand-drawn arrow (a loose curve with a head) runs from it to "may add" after it is written.
- **Outputs:** `renders/c5/graphics/fact`; section 6 re-cut (`renders/c5/cuts/c5_6_finalchorus_outro_close.mp4`; the silent post-roll cut is archived as `…_v3_silent-postroll`).

## 2026-10-26T18:47:22-04:00 — S47 holds 20.89 s, so the muzak's chorus ends with the video

- **Why:** the human's note (human interventions, same time).
- **The chorus's end:** the song's own chorus end (90–98.4 s) matches the cover at 103.1–103.6 s by chroma, so the cover's first chorus, with its repeat, ends about 112 s, near the human's "roughly 1:50". `config/postroll.json` `chorus_end` is 112.71 s, the next beat.
- **S47** (`config/c4_shots.json`) is computed so the video ends there: post-roll 44.89 s, S47 20.89 s (from 15). The final fade is shortened to 1.2 s (from 2.0) so it doesn't swallow the chorus's last bar.
- **Re-made:**
  - `audio/postroll/postroll.wav` (44.89 s);
  - the fact card, announcement and credits in `renders/c5/graphics` (their spans moved);
  - section 6 (`renders/c5/cuts/c5_6_finalchorus_outro_close.mp4`, 107.8 s); the previous cut is archived as `…_v4_chorus-cut-short`.
- **Checked:** the cut's last 6 s match the cover from 106.72 s, so the video ends at 112.72 s of the cover.

## 2026-10-26T19:31:22-04:00 — S44: the drawer shuts after "Phone lines open at the IPO."

- **Why:** the human's note (human interventions, same time).
- **Change (`scenes/blender/animatic.py` `SHUT`):** the drawer front slid over Progress from 267.65 s, during "at the IPO" (the line runs 266.00–269.25 s). It now shuts from 0.25 s after the line ends, over 2 s (269.50–271.50 s).
- **Re-rendered:** S44's frames 267.6–271.75 s (101, no errors); section 6 re-cut (the previous cut is archived as `…_v5_drawer-early`).
- **Checked:** at 268.6 and 269.1 s Progress is in full view, saying the line; at 271.6 s the drawer is shut on WHOLLY OWNED.

## 2026-10-26T22:45:29-04:00 — Ready for the transfer to the RTX 5090 box

- **Why:** the human will rsync the project to the 5090 box for the 4K finals.
- **New:** `config/rsync-exclude.txt` and `docs/render_box.md`.
  - The transfer leaves out `.venv`, `node_modules`, caches and every frame sequence.
  - The doc covers the setup on the box: the hash check, the tool versions, `uv sync`, `npm ci` and a 4K smoke frame.
- **Checked:**
  - `scripts/manifest.sh` left `MANIFEST.sha256` unchanged (3,302 files), and `sha256sum -c` passes.
  - The tree is clean.
  - An rsync dry run moves 4,382 files, 2.7 GB. Only one path matches the exclude patterns, `scripts/render_frames.mjs`, and it isn't excluded (the patterns match directories only).
  - The scenes render with Eevee, so no GPU setting needs changing.

## 2026-10-26T23:23:23-04:00 — The RTX 5090 box set up for the 4K finals

- **Why:** the human rsynced the project here from the GTX 970 box (`docs/render_box.md`) and asked for it to be made ready to render.
- **The box:** RTX 5090 (32 GB, driver 595.99.02); Blender 5.2.3 LTS (snap; the draft box has 5.2.2), uv 0.13.0, Node 24.22.0, ffmpeg 8.0.1.
- **The copy:** `sha256sum -c MANIFEST.sha256` passes on all 3,302 files, and the tree is clean.
- **Environments:** `uv sync` (CPU torch, as pinned) and `npm ci`.
  - npm skipped Puppeteer's postinstall (not in `allowScripts`), so its browser wasn't fetched. Installed with `npx puppeteer browsers install chrome-headless-shell` (148.0.7778.97); `chrome` too, for a launch test.
  - A plain `puppeteer.launch()` dies on Ubuntu's user-namespace restriction; with `render_frames.mjs`'s own options (headless shell, `--no-sandbox`) it starts.
- **Smoke tests** (`renders/final/smoke/`):
  - Blender, S44 at 268.6 s, 3840 × 2160, 64 samples: 6 s for the frame. Downscaled to 1080p, it matches section 6's cut at 48.10 s (PSNR 31 dB; the differences are the cut's `S44` slug and its compression).
  - Graphics, the fact card's frame 500 at 3840 × 2160: the card and the red pen lay out as at 1080p.
- **`docs/render_box.md`:** the Puppeteer step, the two smoke commands, the box's Blender version.
- **`scripts/manifest.sh`:** adds the two smoke frames (3,304 files).

## 2026-10-26T23:45:00-04:00 — The 4K finals queued; the live plates; the post-filtered preview mix

- **Why:** the human: queue the 4K render, make the videos to composite into the live shots, and run the audio through the post-filter (`~/Code/music-deslop`) for this render, as a preview before the human redoes the mix with the live sections (human interventions, same time).
- **The post-filter** (music-deslop at `68441e2`, release weights `m6f_10k.safetensors`, default chain, `--source suno`; logs in `renders/final/logs/postfilter_*.log`):
  - `audio/master/postfilter_preview/song_postfilter.wav` from `audio/track/Share the Shares.wav`. The change is −32.1 dB against the music, peak −3.1 dBFS. The fallback partly faded two passages back to the original: 2:38.3–2:41.2 (88% of its change) and 4:02.2–4:06.8 (82%).
  - `muzak_postfilter.wav` from the human's muzak cover: change −36.1 dB.
  - Both are the same length as their sources, and cross-correlate at 0 samples, so the timing map holds.
  - `scripts/postroll_audio.py` takes `--muzak` and `--out`. With no options it writes the same `audio/postroll/postroll.wav` as before (checked). `postroll_postfilter.wav` is the post-roll built on the filtered muzak.
  - `share_the_shares_postfilter_preview_mix.wav`: the filtered song, then that post-roll; 328.33 s, peak −3.1 dBFS, 24-bit.
- **The live plates (`scenes/blender/animatic.py --flat [--figures-only]`):** the whole sheet seen straight down through an orthographic camera at its print resolution (4400 × 3400, edge to edge), with the desk left out. These follow the brief's "warp a flat render onto the track".
  - `sheet`: the certificate as rendered, figures moving. `figures`: the figures and props alone on transparency.
  - For S26, S29, S31 and S40, with 0.5 s handles. Not for S30, where the sheet lies face down with the static transfer form up, nor for S45–S46, after the song, where nothing on the sheet moves.
  - From S36 on the world is re-inked gold, so the plates show the gold sheet (`renders/c1/certificate_v05/sheet_gold.png` is its print).
  - Checked at 152.0 s (S26): both passes frame the sheet exactly; 4 s and 3 s a frame.
- **`scripts/animatic_assemble.py`:** `--captions none`, `--master` (ProRes 422 HQ, 10-bit 4:2:2, 24-bit PCM), `--no-audio`, `--tmp`. Tested on half a second at 640 × 360.
- **`scripts/final_queue.sh`** (new), started at 23:42:45 in four lanes (`renders/final/logs/queue.log`):
  - `graphics`: the graphics layer at 3840 × 2160, every frame. S30's post-filter tab also goes alone, with alpha, to `deliverables/live_plates/S30_postfilter_tab.mov`.
  - `a`: sections 1–3; `b`: the plates (`deliverables/live_plates/*.mov`, ProRes 4444 with alpha; `plates.json` gives their times), then sections 4–6.
  - Each section: 3840 × 2160, 64 samples, every frame, then a ProRes intermediate in `renders/final/sections/`. Its PNGs are removed once the intermediate holds every frame. The disk (111 GB free) can't hold all the 4K PNGs (about 12 MB each, 73 GB), and frame sequences are never archived.
  - `join`: the sections joined, with the preview mix, to `deliverables/final_4k/share_the_shares_4k_postfilter_preview.mov`, plus a 1080p H.264 copy to listen to.
  - The live shots keep their slates in the master; the human composites over them.
- **Pace:** 3.6 s a frame for the sections and 4.3 s for the plates, with two Blender lanes on the GPU; about 4 hours in all.
- **`scripts/manifest.sh`** runs when the queue finishes, so it doesn't hash files still being written.

## 2026-10-26T23:53:37-04:00 — The 4K frames are kept

- **Why:** the human freed disk space by archiving and deleting renders of videos already published (human interventions, same time). There is now 375 GB free, against 111 GB before.
- **Change:** `scripts/final_queue.sh` no longer removes a section's PNGs once its ProRes intermediate holds every frame. With the frames kept (about 73 GB), a later change to the graphics or timing needs only a re-assembly, not the 4K render again.
  - The new script replaced the old one as a new file, so the running lanes never read a half-edited script.
  - Lanes `a` and `b` were stopped and restarted on it. That lost about 11 minutes: the first frames of section 1, and the S26 plate, which was rendering. The graphics lane had finished (23:47:42), and the join lane only waits.

## 2026-10-27T00:05:27-04:00 — The repository pushed to GitHub

- **Why:** the human created github.com/Derivative-Work/share-the-shares (private) and gave the agent access (human interventions, same time). The credits already name it as the production log's home.
- **Before the push:** the history was scanned for credentials and API keys (none) and for large blobs. The largest are 1.5 MB, puppet previews. Large media stay out of git, listed in `MANIFEST.sha256`.
- **Pushed:** `main`, 46 commits through `21b7983`, as `origin` (https), tracking `origin/main`. This entry follows as its own commit.

## 2026-10-27T04:05:00-04:00 — The 4K finals rendered; the live plates; the post-filtered preview master

- **Queue** (`scripts/final_queue.sh`, `renders/final/logs/queue.log`): 23:53:37 to 03:53:24. No failures.
  - Plates done 01:03:56. Sections, by finish time: 1 (01:29:57), 4 (01:47:18), 5 (02:20:30), 2 (02:36:43), 3 (03:33:38), 6 (03:52:03).
  - Pace: 3–5 s a frame, with two Blender lanes sharing the GPU.
  - Each section's ProRes intermediate held every frame: 1,125 + 1,238 + 982 + 1,368 + 579 + 2,588 = 7,880. The 4K PNGs are kept in `renders/final/frames/s1`–`s6`.
- **The master:** `deliverables/final_4k/share_the_shares_4k_postfilter_preview.mov` (ProRes 422 HQ, 3840 × 2160, 10-bit 4:2:2, 24-bit PCM, 328.33 s, 23.4 GB). Also `share_the_shares_1080p_postfilter_preview.mp4` (H.264 CRF 18, AAC 320k), to listen to.
  - The master has 7,879 frames. The mix (328.33 s) is 3 ms shorter than the picture (328.333 s), so `-shortest` dropped the last frame, which falls in the final fade to black.
  - Its audio is identical, sample for sample, to `audio/master/postfilter_preview/share_the_shares_postfilter_preview_mix.wav`.
  - A contact sheet at 11 times (title, S11, the key change, the S26/S30/S40/S45 slates with S30's tab, the bridge's thermometer, S44, the fact card, the announcement page): every frame as intended, with no captions.
- **The live plates** (`deliverables/live_plates/`, ProRes 4444 with alpha, 9.7 GB):
  - S26: 187 frames. S29: 31. S31: 114. S40: 46. Each in `sheet` and `figures`.
  - Also `S30_postfilter_tab.mov`, 685 frames at 3840 × 2160.
  - `plates.json` gives each plate's first frame in video time. A mid-S31 frame was checked in both passes.
- **Housekeeping:**
  - `deliverables/live_plates/plates.json.tmp`, the queue's scratch file, was committed by mistake with the 23:45 and 23:53 steps; it is removed from git and `plates.json` added.
  - `scripts/manifest.sh` now covers `deliverables/` too. `MANIFEST.sha256`: 5,222 files, including the master, the plates, the section intermediates and the post-filter preview audio.

## 2026-10-27T08:55:00-04:00 — The gold held at the key change; the captions layer; the alignment sheet; the mouths looked into

- **Why:** the human's notes (human interventions, same time).
- **The gold (S36 into S18):** S36 lasted 1.05 s (98.44–99.49 s), but the gold's creep took 2.6 s, so S18 cut in with the sheet less than half gold.
  - `config/shot_holds.json` (new) moves S18's start off its cue to 101.06 s, the beat before "who". S36 now eats "Now you might ask" (99.49–101.17 s). `scripts/timing_map.py` applies it after resolving each cue. Regenerated, the map changes only S18 (`t` 99.49 → 101.06, frame 2388 → 2425; checked by diff).
  - `scenes/blender/animatic.py` `GOLD_SPAN`: 2.6 → 2.2 s, so the gold is complete at 100.64 s and holds 0.4 s, fully visible on the wide shot, before the cut.
  - Re-rendered the 4K frames 98.44–103.38 s (120, `renders/final/logs/s3_gold_hold.log`). Section 3 re-assembled (982 frames), and the master re-joined (`scripts/final_queue.sh join`).
  - Checked in the master at 98.6 (green), 99.6 (creeping), 100.4, 100.8 and 101.02 (gold) and 101.1 s (S18).
  - Archived as `archive/final_4k/*_v1_gold-cut-early.*`: the previous master, its 1080p copy and section 3's intermediate.
- **The captions layer (`scripts/captions_layer.py`, new):** the review cuts' karaoke lyrics alone, full length from 0:00, 3840 × 2160, ProRes 4444 with alpha, in `deliverables/captions/`.
  - `lyrics_captions_4k.mov` has 64 lines, everything but the live verse. `lyrics_captions_4k_verse3_generated_timing.mov` has L45–L52 at the generated take's timing, for the human to retime or drop against the live verse.
  - ffmpeg's libass filter writes no alpha (and its `alpha=1` option made the frame opaque). So each layer is drawn twice, in colour on black and as a white coverage matte, then merged and un-premultiplied.
  - Found on the way: an ASS script without `YCbCr Matrix` is taken as TV.601, and ffmpeg squeezes its colours into 16–235, so the review cuts' captions were slightly dull (fill 220 for 238). `ass()` now declares `YCbCr Matrix: None`, and the fill and outline come out exact. The master has no captions, so it is unaffected.
  - Checked: captions at L63 (frame 5420) and L46 (frame 4080), composited over the render.
- **The alignment sheet (`scripts/alignment_sheet.py`, new; `deliverables/alignment_sheet/`):**
  - Page 1, the print: the flat render of the sheet at 170.0 s, during the live verse, when nothing on it moves. It has the figures at rest and is gold, so it matches the plates.
    - The C1 print file is out of date: its corners are the old "5" rosettes, not the rendered "5 %" discs, and its gold is a different shade.
  - Five registration marks, sepia, 0.28 in across, on clean paper away from everything that moves.
    - Each is the emptiest window in its zone, and stays clean in every other frame of all four sheet plates (worst 0.0043).
    - No marks on the coupons: they are cut away in the final chorus, so S40's plate has a hole there.
    - None under the signature lines either: faint ink everywhere.
  - The four corner discs are listed as tracking points. They never change by more than 3/255 in any plate.
  - Page 2, the key: the marks' and discs' plate-pixel coordinates (plate pixels are print pixels at 400 dpi), and how to print and pin.
  - The PDF holds both pages losslessly. Pillow's PDF writer stores RGB as JPEG, so the script writes its own Flate-compressed PDF.
  - Also `alignment_print_4400x3400.png` and `marks.json`.
- **The mouths:** measured how much of each lyric line its singer's jaw is open for, and looked at shut/open frame pairs in the 4K renders.
  - The gating works: 98–100% for the soloists, 64–72% for the choir in a few full-cast lines.
  - Progress's jaw clearly opens. Prudence's opens, but subtly (−8° against Progress's −14°).
  - Mercury (the Lawyer) and the cherubs (the choir) have no jaw cut. They nod (C2), so no mouth moves on any of their lines. Asked the human which they mean before cutting jaws.
- **`scripts/manifest.sh`:** run after the new files.

## 2026-10-27T09:00:00-04:00 — The alignment sheet's binaries taken out of git

- **What happened:** the previous commit (`5c4fb35`, pushed) added `alignment_sheet.pdf` (21 MB) and `alignment_print_4400x3400.png` (17 MB) to git. `.gitignore` covered `*.mov` and `*.mp4` but not PNG or PDF under `deliverables/`.
- **Fix:** `.gitignore` now leaves out `deliverables/**/*.png` and `*.pdf`. Both files are untracked (kept on disk) and hashed in `MANIFEST.sha256` (5,231 files). `marks.json` stays tracked.
- **Still in history:** the 38 MB stay in `5c4fb35`. Removing them means rewriting pushed history and a force-push; that is the human's call, and was asked.

## 2026-10-27T09:10:00-04:00 — History rewritten to drop the alignment sheet's binaries

- **Why:** the human chose to rewrite history and force-push, so the 38 MB that `5c4fb35` put in git don't stay there (human interventions, same time).
- **What:**
  - `5c4fb35` was rebuilt as `a58765d`: the same tree, less the two binaries, with the same message and dates.
  - `b562d4a` was rebuilt as `127c7f4` with the exact same tree, so the files are identical to before.
  - `main` was force-pushed with a lease on `b562d4a`.
  - No blob over 2 MB is reachable from `origin/main`.
  - The old commits stay on a local branch only, `backup/pre-rewrite-5c4fb35`, until the human is happy to delete it.

## 2026-10-27T09:05:00-04:00 — Mercury's jaw cut; Prudence's jaw opens wider; the re-render queued

- **Why:** the human chose "Mercury's lines" and "Prudence too subtle" (human interventions, 09:05).
- **Mercury's jaw (`config/puppets.json`):** a hand cut, like Progress's and Prudence's.
  - The chin is below the mouth line, at piece pixels (985–1046, 228–276), hinged behind the cheek at (960, 215), parented to the head.
  - It was placed from the 4K S39 close-up, matching the ear's swirl and the dark mouth mark to the ink piece, and checked by overlaying the cut on the engraving.
  - `scripts/segment.py mercury`: SAM reproduced every existing mask byte for byte. New `masks/jaw.png`, and a new `preview.jpg` (the previous one archived to `archive/puppets/mercury/preview_before-jaw.jpg`).
  - `scripts/puppet_build.py mercury`: a jaw layer of 2,126 px. The head's hole is filled with engraving.
- **Poses (`scenes/blender/animatic.py`):**
  - Mercury: jaw −22° with his words. His nod drops from 5° to 2° (and from 3° to 1° in S23), so the mouth carries the line.
  - Prudence: jaw −16° (was −8°; Progress's is −14°).
  - The docstring's note that Mercury has no jaw is corrected.
- **Checked:**
  - Mercury at 236.25 s (S39), nod off, jaw open against shut: only an 85 × 73 px patch at his mouth changes. On his small cross-hatched face it reads as a chin flap.
  - At rest (the flat sheet at 170 s), the new cut differs from before only along its seam: 49 px at 400 dpi. So the S26, S29 and S31 plates and the alignment print stand.
  - 1080p previews of S39 (Mercury) and S38 (Prudence's close-up), with the song, were sent to the human.
- **Re-render** (`renders/final/logs/rerender_jaws.sh`, started 09:03:25; `queue.log` JAWS_*):
  - Two lanes: the Lawyer's lines (46.88–58.14 s), the final chorus's full-cast lines (220.5–248.59 s), all of section 3, and the S40 plates (every figure sings "do I get a say?").
  - Then: the superseded master (v2), its 1080p copy, the section 2, 3 and 6 intermediates and the S40 plates are archived (`*_before-jaws`), the sections re-assembled, the plates re-encoded and the master re-joined.

## 2026-10-27T10:12:00-04:00 — The master rebuilt with the new jaws

- **Re-render** (`renders/final/logs/rerender_jaws.sh`, 09:03:25–10:09:23, no errors):
  - Lane 1: 271 frames of the Lawyer's lines, then the final chorus's full-cast lines.
  - Lane 2: all of section 3, then the S40 plates.
- **Rebuilt:**
  - Sections 2, 3 and 6; every intermediate holds its full count (1,125 / 1,238 / 982 / 1,368 / 579 / 2,588).
  - The S40 plates: 46 frames each.
  - The master, re-joined: 7,879 frames, as before. Its 1080p copy too.
- **Checked:** in the master, Prudence's jaw is clearly open at 233.7 s (S38). Mercury's chin movement in S39 is small at full frame, as in the close-up test.
- **Archived:**
  - `archive/final_4k/*_v2_before-jaws.*`: the master, its 1080p copy, and the section 2, 3 and 6 intermediates. Sections 2 and 6 were in fact their first versions; the name follows the master's.
  - `archive/live_plates/S40_*_v1_before-jaws.mov`.
- **`scripts/manifest.sh`:** run.

## 2026-10-27T19:40:00-04:00 — The phone's screen for S45–S46 (the dialer video)

- **Why:** the human asked for a video to play on their phone for the pre-credits dialer scene (S45, dialling the pledge line; S46, the hold music and the hang-up).
- **`scripts/phone_dialer.py`** (new; `config/phone_dialer.json`) → `deliverables/phone/S45_S46_dialer.mp4`: 1080 × 2400 portrait, 24 fps, H.264 with AAC, 16.0 s.
  - An invented dialer (no real phone's interface): a black screen, a 3 × 4 keypad of round keys, a green call key.
  - 4.0 s of empty keypad lead-in, to start the video and lift the phone.
  - Then 555-0142 is typed on the post-roll's DTMF timing (`config/postroll.json`), each key lit while its tone plays: from 5.00 s in the video (post-roll 1.00 s).
  - "Calling…" from 6.46 s, over the ring; "On hold" with a timer from 7.81 s, through the hold music; "Call ended" at the hang-up, 13.00 s (post-roll 9.00 s, 4 s into S46, leaving 4 s to fold the sheet into the guitar case; `hang_up` in the config); black for the last second.
  - Its sound is `audio/postroll/postroll.wav` to the hang-up, so the tones the set's mic picks up line up with the post mix (R2).
- **Font:** Noto Sans Regular and Bold (OFL), copied into `assets/fonts` with `OFL-notosans.txt`; `SHA256SUMS` updated.
- **Checked:** a contact sheet of 8 frames (empty pad, "555", "555-01" with the 1 lit, calling, on hold 0:01, call ended); the first tone starts at 5.001 s, on the first digit's frame.
- **`scripts/manifest.sh`:** run (the mp4 is git-ignored).

## 2026-10-27T19:55:00-04:00 — The phone video without the hang-up

- **Why:** the human: "remove the hangup" (human interventions, 19:50).
- **`scripts/phone_dialer.py`, `config/phone_dialer.json`:** the "Call ended" screen and the black tail are gone (`hang_up`, `ended_hold` and `tail` removed). The call stays "On hold", its timer running, to the end of the post-roll. The sound is the whole post-roll: dialling, ring, then the hold music to its fade.
- **`deliverables/phone/S45_S46_dialer.mp4`:** 48.88 s (1,173 frames), long enough to hang up whenever the take needs. The first tone is still at 5.00 s, and "On hold" at 7.81 s. The previous version is archived as `archive/phone/S45_S46_dialer_v1_hang-up.mp4`.
- **Checked:** frames at 13.5, 30 and 48.5 s are all on hold (0:05, 0:22, 0:40).
- **`scripts/manifest.sh`:** run.

## 2026-10-27T20:05:00-04:00 — The transfer form, printable (the sheet's back)

- **Why:** the human asked for it (human interventions, 19:58); the brief's "The prop" puts the transfer form on the sheet's back, face up in S30.
- **`scripts/transfer_form_print.py`** (new) → `deliverables/transfer_form/`:
  - `transfer_form.pdf`: the back alone, letter landscape (11 × 8.5 in), 4400 × 3400 at 400 dpi, lossless (the alignment sheet's Flate PDF writer).
  - `prop_duplex.pdf`: page 1 the face (the alignment print, with its marks), page 2 the back, for printing both sides at once.
  - `transfer_form_4400x3400.png`.
- **Shading:** as the render shades the back (`layer_material`): the paper printed with the sepia plate, then the lathe plate multiplied over it in gold, as the back is from S36 on (S24's `green_ink="ink_gold"`), which covers every live shot. Mixed in linear light from `config/look.json`'s palette, written as sRGB. The paper tone is printed, as on the face's print.
- **Orientation:** the render has no flip axis (S24 cuts to the back lying beside the sheet), so either duplex setting works. With "flip on short edge", the back reads upright when the sheet is turned over side to side, as in S31.
- **Checked:** the whole page and a crop of the type at full resolution; a re-run gives byte-identical files.
- **`scripts/manifest.sh`:** run (the PNG and PDFs are git-ignored).

## 2026-10-27T21:27:00-04:00 — S12: the calendar's pages lie on its pad; the 4K re-render queued

- **Why:** the human: "the calendar is not aligned" (human interventions, 20:10). In S12 the pages were upright cards hovering over the engraved calendar, which is drawn at an angle: they covered its top edge and never sat on the pad.
- **`scenes/blender/animatic.py`:**
  - `CAL_PAD`: the pad's top page in the engraving's pixels, a parallelogram measured on `calendar.png`. Its corners are the curl (205, 295), the binding strip's ends (895, 75) and (1145, 405), and the rounded corner (455, 630).
  - Each page's mesh is mapped onto it each frame (`on_pad`).
  - A page turns over the binding on its right, its free edge sweeping to the strip and lifting.
  - Each page now shows from 0.18 s before the one above it turns, so the next page lies underneath instead of bare pad.
- **`scripts/props.py` `calendar_pages`:** the pages redrawn landscape (700 × 400) to the pad's drawn proportions. They have the same band, month and company line, and a fold line at the binding instead of the holes. The previous pages and masks are archived in `archive/props/calendar_pages_v1_upright/`.
- **Checked:** 4K test frames at 58.20, 58.30, 58.34, 58.37 and 60.40 s. The page's outline matches the pad's, NOV turns to show DEC under it, and the last page, SOON, also sits on the pad.
- **Re-render** (`renders/final/logs/rerender_calendar.sh`; `queue.log` CAL_*): S12, 58.14–60.61 s, at 4K and 64 samples into section 2's frames. Then the master (v3), its 1080p copy and section 2's intermediate are archived (`*_v3_before-calendar`), section 2 re-assembled and the master re-joined. The calendar isn't on the sheet in any live shot, so the plates and the alignment print stand.

## 2026-10-27T21:40:00-04:00 — The master rebuilt with the calendar on its pad

- **Re-render** (`renders/final/logs/rerender_calendar.sh`, 21:27:33–21:34:29, no errors): 60 frames of S12 at 4K, 64 samples.
- **Rebuilt:** section 2 (1,238 frames), the master (7,879 frames, as before) and its 1080p copy. Every section intermediate holds its full count.
- **Checked in the master:** at 58.2, 58.35, 59.0 and 60.4 s the page sits on the pad; Q1 is seen turning over the binding with the next page under it.
- **Archived:** `archive/final_4k/*_v3_before-calendar.*` (the master, its 1080p copy, section 2's intermediate).
- **`scripts/manifest.sh`:** run.

## 2026-10-28T10:15:00-04:00 — S11's guilloche microprinted; the fine print kept inside the border; the re-render queued

- **Why:** the human asked for the "LLC LLC LLC LLC" and similar text zooms to be more convincing (human interventions, 09:20).
  - In S11 a green line of "LLC LLC LLC LLC LLC" grew from nothing over the strands and the banner's "A". Nothing in the guilloche became letters.
  - The fine print in S10 (the ticker) and S39 ran on over the border's lathe work and into the stub, and S39's ran over the first signature rule.
- **S11, real microprint (`scripts/microprint.py`, new) → `renders/c1/microprint/`:**
  - The banner's left end, 870–1710 × 1100–1600 sheet px, is printed again at 16 px per sheet px (13,440 × 8,000).
  - Each of the underprint's nine strands is set as a line of tiny "LLC" letters (cap height 2.4 sheet px), computed from the strands' own formula in `certificate.py`.
  - The sepia type (the company name and "ORGANIZED…") is set again at the same scale. The paper's grain is resampled from the sheet's own seed.
  - **Checked against the static print:** the sepia differs by 0.97 of 255 on average. The only other differences are the strands themselves, now letters, which read a little lighter.
  - **`scenes/blender/animatic.py`:** the patch is a card 0.04 mm over the sheet, shown only in S11, with the paper's material (the same roughness and ink relief). The growing LLC text object is removed.
  - **`config/c4_shots.json`:** S11 now opens wider (GUILLOCHE 940–1640 × 1153–1547, was 1150–1430 × 1270–1430) and pushes in at a constant rate (`ease: exp`) to the same close-up. The strands read as fine dotted lines at the cut, become legible halfway through, and fill the frame with LLC LLC at the end.
  - Checked in 4K test frames at 52.76, 54.0, 55.3, 56.6 and 58.1 s. The patch covers the frame throughout; the soft shape at the bottom of the opening frame is Mercury's cutout casting its shadow, not a seam.
- **The fine print (S10, S39):**
  - Both lines now print through a material clipped between the border's lathe work (its inner edge at x 815) and the first signature rule (from x 1575): x 840–1555 (`clipped()`). The S10 ticker now slides in and out at the border.
  - S39's line is left-aligned at x 860, 24 px (was 30, centred on x 1140), and reads "BASELINE TO BE ANNOUNCED · AT THE BOARD'S DISCRETION" so it ends whole before the rule. It was "… · SUBJECT TO THE BOARD'S DISCRETION · TERMS APPLY", and the new wording echoes the lyric's "at our discretion".
  - Checked in 4K test frames at 48.5, 51.5 and 236.6 s.
- **Re-render** (`renders/final/logs/rerender_text.sh`, started 10:14:34; `queue.log` TEXT_*):
  - 4K at 64 samples: S10–S11 (46.88–58.14 s), S39 (234.44–239.654 s).
  - The S40 plates, both passes: their 0.5 s lead-in handle (from 239.125 s) is in S39 and showed the old fine print.
  - Then the master (v4), its 1080p copy, the section 2 and 6 intermediates and the S40 plates (v2) are archived. Sections 2 and 6 are re-assembled, the plates re-encoded and the master re-joined.

## 2026-10-28T10:45:00-04:00 — The master rebuilt with S11's microprint and the fine print inside the border

- **Re-render** (`renders/final/logs/rerender_text.sh`, 10:14:34–10:39:26, no errors): S10–S11, 271 frames; S39, 126 frames; the S40 plates, 46 frames each pass.
- **Rebuilt:**
  - Sections 2 and 6; every intermediate holds its full count (1,125 / 1,238 / 982 / 1,368 / 579 / 2,588).
  - The master, re-joined: 7,879 frames, as before. Its 1080p copy too.
  - The S40 plates, re-encoded.
- **Checked:**
  - In the master: the S10 ticker stops at the border (49.0 s); S11 opens on dotted strands (52.8 s), which are legible by 55.3 s and fill the frame as LLC LLC by 58.0 s; S39's line is whole and clear of the rule (236.6 s).
  - The S40 sheet plate's first frame (the handle, in S39) shows the new line.
- **Archived:** `archive/final_4k/*_v4_before-text.*` (the master, its 1080p copy, the section 2 and 6 intermediates) and `archive/live_plates/S40_*_v2_before-fineprint.mov`.
- **`scripts/manifest.sh`:** run.

## 2026-11-17T23:07:00-05:00 — Brief rev 50 audited against the build; the certificate, seal, shots and fact card brought in line; the full 4K re-render queued

- **Why:** the human revised the brief (human interventions, 22:40) and asked that everything it changes be in before the render.
- **The audit:** `docs/brief.md` re-exported from the doc at rev 50 (`scripts/doc_to_md.py`; rev 34's mirror archived as `archive/docs/brief_rev34.md`) and diffed against rev 34. What it changes in the picture:
  - **The class line** ("CLASS N · NON-VOTING"): it wasn't on the certificate. **No ticker** on it: none was. **No all-seeing eye:** none of the engravings has one (`assets/engravings/sources.tsv`).
  - **S34:** the seal embosses THRESHOLD MET*, and the fine print adds "*based on what we expect". It embossed WHOLLY OWNED, with no footnote.
  - **S26, S29–S31, S40** are a screen recording of this render playing, not the printed sheet; S45–S46 are the mirrorless camera at the desk. The render had slates there.
  - **The fact card:** three new lines (the Class N shares, the IPO with its price and dates to come, the RSI threshold).
  - **Retired with the printed sheet:** the alignment print, the printable transfer form and the flat live plates. Left in `deliverables/` for now; not rebuilt.
- **The certificate, `certificate_v06`** (`scripts/certificate.py`; v05 kept): "CLASS N" over "NON-VOTING" under the Number of Shares box, mirroring its label above. One line runs into the border at any legible size. Only the sepia plate changes (3763–4105 × 1128–1224 px). `scripts/gold_sheet.py` run for v06; `scenes/blender/animatic.py` and `scripts/microprint.py` now default to v06 (the microprint patch is outside the change).
- **The seal** (`scripts/props.py seal`): the centre reads THRESHOLD / MET* / MMXXVI, its field widened from radius 150 to 196 to hold it. The WHOLLY OWNED die is archived in `archive/props/seal_v1_wholly-owned/`.
- **The footnote** (`animatic.py` S34): "*BASED ON WHAT WE EXPECT", small caps, 26 px, under the seal at y 2308. It types in from 0.2 s after the hit to 0.9 s, while the die is down, and stays printed. S34's push now ends on `SEAL_FINE` (1390–1910 × 1930–2380; was `SEAL_TIGHT`) so the footnote is in frame.
- **The screen-recorded shots** (`config/c4_shots.json`): the file the screen recording plays shows render under the player:
  - S26: held wide, for the controls' flicker.
  - S29: S28's close on the laborer, held to the downbeat.
  - S31: wide, as the file reopens.
  - S40: S39's framing.
  Only S30, the call, stays a slate. Its placeholder text and the S45/S46 slates were updated to rev 50 (`scripts/render_graphics.py`, `overlays/graphics.html`: a slate now says SCREEN or LIVE).
- **The fact card** (`overlays/graphics.html`): the rev 50 draft's lines are added. The Public First Action line is kept.
  - The IPO line reads from `config/fact_card.json` (new) and keeps the brief's [date] and [final price] placeholders until pricing (expected Nov 18 and 19). Filling them needs only the card, section 6 and the join re-made.
  - Type is 30 px (was 35) so nine items fit, with the red pen's notes given their room. The sources add the IPO filing, CNBC and Gizmodo.
- **Checked:** 1080p test stills at 147.5, 152, 163.95, 194, 211.0, 211.4, 212.45, 225 and 240 s, and the fact card's last frame.
- **`scripts/final_queue.sh`:** lane b no longer makes the plates (`plates` alone still does).
- **Re-render** (`renders/final/logs/rerender_brief50.sh`; `queue.log` BRIEF50_*):
  1. Archive the v5 master, its 1080p copy and the six section intermediates as `*_v5_before-brief50`.
  2. The graphics layer.
  3. Lanes a and b (every section at 4K, 64 samples).
  4. The join.

## 2026-11-17T23:10:00-05:00 — The call page for the live verse (`apps/call_page/index.html`)

- **Why:** brief rev 50, "The call page" (human interventions, 22:40): "Build it as a simple browser page (Claude Code), not a real call app, so there are no brand logos and every label is exact". The human asked for a SPA to run on their Mac beside the Claude app, with either the live webcam or a video file.
- **What it shows:**
  - The title bar: the meeting title "Public Benefit Fund: stakeholder input session", a call timer, the dial-in number 555-0142 (the pledge line, `config/postroll.json`, in the fiction range) and a count of 1.
  - Your tile, the only video, with your name and a mic that lights with your level, plus a green speaking ring.
  - The participant list: you in the call, "Board (not joined)" greyed under Invited, and "To join by phone, dial 555-0142".
  - The toolbar: Mute, Stop video, Raise hand, Participants, Leave. Leave does nothing. Raise hand puts the hand icon on your tile, and nothing else happens (S40).
- **Sources:**
  - **The live camera:** any camera macOS offers, Continuity Camera included, at 1080p, 720p or 4K. A mic is measured for the speaking ring, never played.
  - **A video file:** picked or dropped on the page. It loads paused at a start time you set, Space plays, and its own sound plays and drives the ring.
  - **Mirror** is off by default, so the guitar reads the right way round.
- **For the capture:**
  - The setup panel (S) is never in shot. The cursor hides after 2 s still.
  - "Post-filter: no change" is off by default, since the edit adds it, and O shows it.
  - F goes full screen, so the page is its own Space for the swipe.
  - One self-contained file with no network requests. Settings are remembered in the browser's localStorage, guarded.
- **Checked** headless (Chrome's fake camera, then a file from the v5 master), screenshots at 1512 × 945 @2x:
  - Camera mode: 1920 × 1080.
  - File mode: plays; Raise hand shows the badge; the ring follows the file's sound; the overlay toggles.
  - No page errors.

## 2026-11-18T03:05 — Brief rev 50 master rendered; the live-verse excerpts cut

- The full 4K re-render (`renders/final/logs/rerender_brief50.sh`) finished at 02:48:49 (BRIEF50_DONE), with no errors in the section logs. Section frame counts: 1125/1238/982/1368/579/2588; the master and its 1080p copy have 7,879 frames each. The v5 master and its sections are archived in `archive/final_4k/*_v5_before-brief50*`.
- Spot-checked in the 1080p copy:
  - S26 (152 s) and S31 (194 s) are wide renders, no longer slates.
  - The class line (CLASS N / NON-VOTING) is under the shares box.
  - S34's seal embosses THRESHOLD MET*; its footnote is half-typed at 211.4 s and complete at 212.45 s.
  - S40 is the Mercury pop.
- `scripts/live_excerpts.sh` cut the files the screen recording plays into `deliverables/live_excerpts/` (2560×1440, H.264 CRF 18, AAC 256k):
  - `share_the_shares_chorus2.mp4`: 136.36–164.14 s, 27.8 s, 22 MB.
  - `share_the_shares_bridge_on.mp4`: 192.68–243.54 s, 50.9 s, 49 MB.
  - The spans are in `excerpts.json`.
- The excerpts were sent in this Claude Code session for the session reveal (brief, "The screen recording").
- Note: the two previous entries' timestamps were corrected (they had read 23:30 and 23:55; the true times are 23:07 and 23:10).
- Still open: the fact card's IPO line keeps the brief's [placeholders] until pricing (Nov 18–19). Fill in `config/fact_card.json`, then re-render the fact graphics, section 6 and the join.

## 2026-11-18T03:20 — The bridge excerpt resized for the session upload

- The session's file upload refused `share_the_shares_bridge_on.mp4` (47.1 MiB; the limit is 30 MiB). `scripts/live_excerpts.sh` now makes a two-pass copy with the same name in `deliverables/live_excerpts/sendable/` (4,338 kb/s video, AAC 192k; 27.5 MiB), and that copy was sent. The chorus file (21 MiB) was sent as cut. The full-quality original is kept.

## 2026-11-18T19:25 — Two virtual backgrounds for the call page, to compare

- **The boardroom** (`scenes/blender/boardroom.py` → `scripts/call_backgrounds.py boardroom`):
  - An empty boardroom modelled in Blender, seen from the head of the table at seated webcam height (24 mm on 36 mm, level). Seven empty high-backed chairs a side and one at the far end; tall windows on the left with the sun through them; panelling, portraits and a fireplace on the right; a clock and a double door on the far wall, behind the head.
  - The Met's public-domain boardroom prints (*Microcosm of London*, 1808–09: 744281, 744579, 744447) were looked at and not used: the rooms are full of people, and they are coloured aquatints, not line engravings.
  - Engraved from the passes: iso-lines of a world coordinate on each surface (horizontal on walls, receding on floors and table tops), widened with shadow and crossed in the darks. Lines are kept 9 px apart at 2560 wide, so they don't moiré when the call tile is scaled down. Contours at creases and depth jumps; ruled sky in the windows; sepia multiplied into the paper.
  - Tone from Eevee. Normals and positions from Cycles: Eevee's film is half float, and its position steps (1/2048) broke the line spacing.
  - Output: `deliverables/call_backgrounds/boardroom_3840.png`.
- **The fund slide** (`scripts/call_backgrounds.py slide`):
  - Paper with the certificate's gold lathe-work frame.
  - Top left: an "AB" rosette mark, AMALGAMATED BENEFIT, LLC and *Public Benefit Fund*. The initials replace a lone A that could read as a real company's mark.
  - Bottom left: STAKEHOLDER INPUT SESSION, *Your input matters.** and *Input is advisory and non-binding.*
  - A faint underprint rosette bottom right; the middle is left empty for the head.
  - Output: `deliverables/call_backgrounds/fund_slide_3840.png`.
- Both are 3840×2160 and fictional only: no real names or logos.

## 2026-11-18T19:50 — The call page replaces the background

- `apps/call_page/index.html`: a Background section in setup, plus the B key to cycle. The options:
  - None.
  - Blur (the camera's own picture, blurred).
  - The engraved boardroom.
  - The fund's slide.
  - Your image (pick one or drop it on the page; it isn't remembered, like the video file).
  - Edge: normal, soft or sharp.
- How it works:
  - The person is cut out in the browser by MediaPipe Tasks Vision 1.2.0 (pinned, jsDelivr) with the selfie segmenter's landscape model (float16, version 1, Google's model storage). GPU delegate, CPU fallback.
  - Both load from the web the first time a background is chosen. If they fail, the page says so and turns the background off.
  - The video is drawn cover-cropped to a 640×360 input. The mask is eased over frames (0.65 new) against flicker, through a smoothstep threshold, and feathered.
  - The person, then the background, are drawn on a canvas over the hidden video. Mirroring flips only the person and the blur, so the slide's words never read backwards.
  - A paused file isn't re-segmented.
- `scripts/build_call_page.py` inlines the two backgrounds (WebP, 2560×1440, 945 KB and 169 KB) into `deliverables/call_page/call_page.html` (1.5 MB; git-ignored, in the manifest). The source page offers only blur and your own image.
- Tested headless (puppeteer, a fake camera playing a public-domain portrait photograph: the Met 286624, *Peter Force*, ca. 1858, salted paper print; scratch only, not kept):
  - The mask's confidence is the person's: 0.32 in the middle of the frame, 0 at the edges.
  - The boardroom, the slide with mirroring on, and blur all composite.
  - The unbuilt page falls back to no background without errors.
  - The faint 1858 print reads at low confidence (the coat comes through partly see-through); a colour webcam picture should score far higher.

## 2026-11-18T23:15 — The IPO line filled in; the human's review date and live credit changed; section 6 and the master rebuilt

- **The IPO** (`config/fact_card.json`, with its source): Anthropic priced on Wednesday, November 18, 2026 at $83 a share, above its $70–78 range; it trades on Nasdaq as ANT from Thursday, November 19 (CNBC, 2026-11-18; the same price is reported by StockAnalysis, Crypto Briefing and Stock Titan). The card reads "Anthropic's IPO: priced November 18, 2026, trading on Nasdaq as ANT since November 19, 2026, at $83." Trading starts tomorrow, so "since" is true from the video's release.
- **The red-pen note** under the satire line (`overlays/graphics.html`): "and by the human, November 18, 2026" (was October 26). Gemini's date, October 21, stands. (A first pass changed Gemini's date by mistake; it was caught on the rendered card and put back before anything was assembled.)
- **The credits:** "Verse 3 and “do I get a say?” — performed live by the human" (", one take" removed). The human-interventions count reads 39.
- **Rebuilt** (`renders/final/logs/rerender_ipo.sh`): the fact and credits graphics at 4K; section 6 re-assembled from its frames on disk (graphics only changed; no Blender render); the master and its 1080p copy re-joined.
- **Archived:** `archive/final_4k/*_v6_before-ipo.*` (the master, its 1080p copy, section 6's intermediate).
- The human will cut the whole video themselves from here.

## 2026-11-19T00:10 — The subtitles and the upload metadata

- **Subtitles** (`scripts/subtitles.py` → `deliverables/share_the_shares.en.srt`, 76 cues):
  - The 72 lyric lines from `timing/timing_map.json`, "♪" on the sung ones, kept on screen at least 1.2 s and never overlapping.
  - Sound cues: `[electric piano]` at the start, and in the post-roll `[phone dialing]`, `[ringing]` and `[hold music: "Share the Shares" as muzak]` (`config/postroll.json`'s times).
  - Verse 3 reads "pledged", the brief's post-audit word; the generated take sang "spent". `--spent` switches it.
- **Timing:** the human: "Just use the timing from the master you have; my edits did not adjust the timing around my sections, and within them they are pretty close to where the originals were". So the file is in master time. The script's anchors (`--verse`, `--verse-lines`, `--bridge`, `--postroll`, `--end`) are kept for a cut that moves things; with none given, the master's timing is used and there is no `[music stops]` cue. Recorded here as information about the human's cut; the cut itself is the human's to log.
- **`METADATA.md`** (new, as in the sibling repos):
  - Title options, a description with the disclosure, chapters at the master's times, the fact card's terms with sources, credits, tags and settings.
  - Open before upload: the brief's facts to verify (the final prospectus for the price, Class N and RSI wording; Public First; any announced baseline); the repo is private and the credits point to it; this repo has no licence files (the series' CC BY-NC-SA 4.0 / MIT is assumed in the description, pending the human); no thumbnail yet (three candidates named).

## 2026-11-19T01:10 — Facts checked against the filings; licences added; title and thumbnail options

- **Facts** (the brief's "Facts to verify before release"), against the November 17 S-1/A on EDGAR (downloaded and searched), Anthropic's announcement and its Public First page:
  - Confirmed: Class N's 846,840,960 shares to the fund and their lack of a vote; the RSI threshold "met … based on what we expect"; the announcement's LLC, 20% and no-lobbying wording; $40M to Public First Action with the candidate restriction.
  - Not yet checkable: the final prospectus (no 424B4 on EDGAR; the latest are an S-1MEF and an FWP, November 18). The $83 price stands on CNBC's report.
  - **Out of date on the card:** the filing sets the 2% top-ups' baseline at the IPO price ("beginning with our initial public offering price") and names the fund's initial managers; the board decides the fund's giving until it approves a governance structure. "Above a baseline not yet announced" and the "valuation milestones" in "to be announced" no longer hold. Left for the human to decide (METADATA.md); the video is otherwise done.
- **Licences** (the human's R1): `LICENSE` (MIT), `LICENSE-media.md` (CC BY-NC-SA 4.0, with what it does and doesn't cover: the public-domain engravings, Anthropic's announcement page, the OFL fonts, MediaPipe, the audits, Suno's records) and `LICENSES/CC-BY-NC-SA-4.0.txt`, the same legal code as the sibling repos.
- **METADATA.md:** the fact status and links to verify; the licence confirmed; the intervention count frozen at 39; eight clickbait-adjacent title and thumbnail pairs (four from the human's footage, four from the master).

## 2026-11-19T01:10 — The fact card's baseline and governance lines corrected; section 6 and the master rebuilt (v8)

- **Why:** the S-1/A of November 17 sets the 2% top-ups' baseline at the IPO price and leaves the fund's giving to the board until a governance structure is approved (production log 2026-11-19T01:10, facts). The human: "Yes fix the fact card." This is the human's R1 on a correction the agent found; the intervention count stays frozen at 39.
- **The card** (`overlays/graphics.html`):
  - "The board may add 2% more for every 50% rise in Anthropic's share price, starting from the IPO price." (was "… in Anthropic's value above a baseline not yet announced.")
  - "The fund's governance structure: to be announced. Until then, Anthropic's board decides what it gives." (was "Structure, governance and valuation milestones: to be announced.")
  - The red pen still lands where it did: the arrow to "may add" and the circle on "to be announced". Each line still fits on one line, so the layout is unchanged.
- **Rebuilt** (`renders/final/logs/rerender_baseline.sh`): the fact graphics; section 6 re-assembled from its frames (2,588); the master and its 1080p copy re-joined (7,879 frames each). Checked at 316 s in the 1080p copy.
- **Archived:** `archive/final_4k/*_v7_before-baseline.*`.
- `METADATA.md`: the description's terms match the card; the cut's last 32 s (from S47, 4:56) come from the new master.

## 2026-11-19T01:45 — The thumbnail options, from the human's cut

- **Source:** the human's final cut from DaVinci Resolve, `~/Downloads/share-the-shares-master.mov` (H.264 1920×1080, 24 fps, 5:28.6, master timing; not copied into the repo).
- **`scripts/thumbnails.py`** → `deliverables/thumbnails/thumbnail_1…8_*.jpg` (1280×720) and `contact_sheet.jpg`, one per title in METADATA.md:
  1. The call (172 s) with the participant list enlarged, "Board (not joined)" circled, "no-show", **1 PARTICIPANT**.
  2. Close on the face at "do I get a say?" (240.3 s), **DO I GET A SAY?** in the pen.
  3. The session (164.5 s), cropped to the conversation column (the session title and the player), the player circled, **IT MADE THIS ABOUT ITSELF**. The terminal, the browser tabs and the menu bar are cropped out.
  4. The phone on hold over the stub and the 5% corner (292 s), **PLEASE HOLD**. The printed email above it is cropped out.
  5. The seal just embossed with its whole footnote (212.3 s), contrast raised, the footnote circled, "says who?". A first version pasted the footnote from another frame; the camera had moved, so it was replaced by this single frame.
  6. The certificate wide in chorus 1 (66 s), **BUY TO GIVE?**
  7. The fact card's "may add" line (316 s) enlarged on paper, **THE BOARD MAY ADD 2%**, "It's not required to."
  8. Prudence with the scissors (233.5 s), **SHARE THE SHARES**, "(sort of)".
- Type: Abril Fatface, the pen in Caveat, the certificate's palette.
- **Noticed in the cut, left to the human:** the session reveal (from 2:44) shows a terminal with a hostname, an internal IP and a file listing, plus the browser's tabs. The phone call's desk (from 4:43) shows a printed email with a name and an email address, and a real company memo.

## 2026-11-19T02:05 — Thumbnail #2 made more legible; more titles

- **The human:** "I like #2 but the text could be more readable. Also suggest some more options for tile." Taken as "title".
- **`scripts/thumbnails.py`:** `--only=` renders a subset. Three new variants of #2 sit beside it (the first stays as made), each framed a little tighter so the face is right of centre over the slide's plain paper:
  - `thumbnail_2a_say.jpg`: the pen in Caveat, heavier, with a white edge and a shadow.
  - `2b`: Abril caps in sepia, the pen underlining "A SAY?".
  - `2c`: the pen's question on a cream card, tilted, with a shadow.
  - `contact_sheet_2_say_2a_say_2b_say_2c_say.jpg` compares the four.
- **`METADATA.md`:** a "More titles" section, nine titles, most of them from the call page's own slide ("Your input matters.*", "*Input is advisory and non-binding.").
- **The human on the cut's legible details** (production log 2026-11-19T01:45, "noticed"):
  - The session reveal is meant to look real, and its terminal, tabs and menu bar were left in on purpose.
  - The desk's papers are props about AI-driven job changes: a redacted recruiter's cold email (contract work producing Claude Code RLHF data); the human's email address, which is meant to be public and already is; and the public version of Microsoft's voluntary buyout memo.
  - Nothing to change.

## 2026-11-19T02:10 — The five Shorts; the README

- **The human:** "Make all of them, then I'll release as appropriate. Also make the README".
- **`scripts/shorts.py`** → `deliverables/shorts/share_the_shares_short_{1_verse,2_pitch,3_hand,4_threshold,5_pledge}.mp4` (1080×1920, 24 fps, H.264 CRF 18, AAC 256k; from the human's cut, `~/Downloads/share-the-shares-master.mov`):
  - Lengths and spans (cut time): 1 verse, 42.9 s (156.4–199.3); 2 pitch, 52.0 s (46.7–98.7); 3 hand, 28.5 s (219.9–248.4); 4 threshold, 27.9 s (192.4–220.3); 5 pledge, 51.8 s (265.6–317.33).
  - **Layout:** stacked. At the top, "AI-GENERATED SATIRE" in the pen's red, SHARE THE SHARES in Abril between rules, and a subtitle in Fell italic. The picture sits in the band from y 420 to 1320: 16:9 at full width, or, on the call page, a 6:5 crop around the tile (888×740 from x 370, y 220). The lyric sits below at y 1420, in IM Fell English 68, from the subtitles file with its "♪" and sound cues dropped. Everything stays clear of the top 140 px, the bottom 330 and the right-hand buttons.
  - **The call page is found per frame:** its dark header (mean < 45) over a light tile (mean > 120) at 192×108, with runs under 4 frames ignored. Found: 165.73–193.07 (the verse) and 239.82–241.48 (S40). Short 4 opens on the last 0.67 s of the call, as the file is reopened on "And it's real".
  - **Short 5:** while the fact card is up, its marked lines are spelled out below it in turn (IM Fell English 50), with the red pen's notes in Caveat, timed from the card's start: 0.5 s, then from 5.2 s, when the pen starts, every 3 s.
  - Checked on frames from each: the call crop, the stacked shots, the captions and the fact lines.
- **`METADATA.md`:** a Shorts section with each file, its span, title, description and the shared settings.
- **`README.md`** (new, as in the sibling repos): what the video is, the conflict of interest, how it was made, what's real and made up, the fact card verbatim with sources, where things are, how to reproduce it, the licences and the credits. The upload links are added after the upload.

## 2026-11-19T02:45 — The v1.0 release staged; the video's link

- **The final cut** is copied into the repository's large files: `deliverables/final_cut/share_the_shares_1920x1080.mov` (525,717,782 bytes, from the human's `~/Downloads/share-the-shares-master.mov`; git-ignored, in the manifest).
- **`scripts/release.sh`** (as All Systems Operational's) stages `release/` (git-ignored; the videos hard-linked) with:
  - the video, the five Shorts, the subtitles, the thumbnails (zip) and the call page;
  - `inputs.tar` (722 MB): Suno's take, its stems zip, the muzak, the post-filtered audio and the post-roll;
  - `SHA256SUMS`.
  It checks every file against the 2 GiB limit, and every file in the tar against `MANIFEST.sha256`. Left out: the 24 GB 4K master and its sections (they regenerate); the human's raw footage and the DaVinci project; the session transcript.
- **The notes:** `docs/release_notes.md`. `scripts/release.sh --draft docs/release_notes.md` creates the draft release v1.0.
- **The link** (https://www.youtube.com/watch?v=YpJn6DwTLlk) is in the README, METADATA.md (uploaded November 19) and the Shorts' shared description.
- `.gitignore`: `release/`.
