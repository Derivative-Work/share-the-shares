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
