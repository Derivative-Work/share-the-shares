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
