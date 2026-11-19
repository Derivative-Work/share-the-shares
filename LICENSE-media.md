# Licence for the video and its assets

Copyright 2026 Albert Armea.

"Share the Shares" (the video) and its assets are licensed under the
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International licence](https://creativecommons.org/licenses/by-nc-sa/4.0/)
(CC BY-NC-SA 4.0). The full legal code is in [LICENSES/CC-BY-NC-SA-4.0.txt](LICENSES/CC-BY-NC-SA-4.0.txt).

The code is under the MIT licence instead: see [LICENSE](LICENSE).

## What this covers

- The video in all its cuts, with its subtitles and thumbnail, and the live footage in it: the screen recording, the
  call and the phone call.
- The music: the Suno V6 take (c0702797), its stems and the post-filtered mix; the human's live verse and "do I get a
  say?"; the muzak cover and the post-roll's sound (`audio/`).
- The certificate and everything printed on it as built: the plates, the puppets (`assets/puppets/`), the props, the
  microprint and the seal; the rendered frames, sections, masters and live excerpts.
- The on-screen text and graphics: the title, the LIVE bug, the cards, the fact card, the credits, the call page's
  labels and the two call backgrounds, and the frames the code renders from them.
- The production record, written by the agent: the logs and prompts under `log/`, the timing maps, the lyrics files,
  the documents under `docs/` (with the brief) and the planning chat in `docs/planning_chat/`.

## What this doesn't cover

- **Code** (`scripts/`, `scenes/`, `overlays/`, `apps/`, `config/` and the build files): MIT, see [LICENSE](LICENSE).
  Where a source file holds both code and on-screen text or design, the code is MIT and the frames it renders are
  CC BY-NC-SA.
- **The engravings' sources** (`assets/engravings/`, `reference/certificates/`): public-domain works, mostly Asher B.
  and Cyrus Durand's banknote vignettes and lathe work from The Metropolitan Museum of Art's Open Access collection
  (CC0), each listed with its source in `sources.tsv`. They stay in the public domain; what is built from them is
  covered as above.
- **The real announcement page** in the closing bookend (`assets/screens/`): Anthropic's page and words belong to
  Anthropic. It appears as a documentary record and isn't licensed here.
- **The fonts** in `assets/fonts/` (Abril Fatface, IM Fell English, Pinyon Script, Caveat, Noto Sans): SIL Open Font
  License 1.1, licence text beside each font.
- **MediaPipe**, which the call page loads from a CDN for background replacement, is not part of this repository; it is
  used under its own licence (Apache 2.0), with Google's selfie segmentation model under its terms.
- **The auditors' outputs** in `log/audits/` are kept verbatim as a record of the audit, only as far as each
  provider's terms allow.
- **The Suno page records** (`log/prompts/suno/fetch_*/`) are Suno's metadata for the take, kept as a record.
- **The news reports, filings and company statements** behind the fact card are cited, not reproduced.

## Attribution

Credit "Share the Shares" by Albert Armea, made with Claude Code (Opus 5.5) and Suno V6, licensed CC BY-NC-SA 4.0,
with a link to https://github.com/Derivative-Work/share-the-shares.
