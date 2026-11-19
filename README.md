# Share the Shares

**AI-generated satire.** A 1980s all-star charity single for the Anthropic Public Benefit Fund, where every star is from the same company and the whole video takes place inside one engraved stock certificate, animated like paper puppets. A benefit single exists to get the public to give. This one ends up asking the public to buy, because most of the gift only grows if the stock does.

**Watch:** links are added here after the upload. The upload's title, description, chapters, thumbnails and the five Shorts are in [`METADATA.md`](METADATA.md).

**The fund is real.** On October 18, 2026, Anthropic committed 5% of its shares to the fund, and the song and the fact card say so. The satire is about the terms: the board's discretion over a growth escalator, governance still to come, and the timing, just before the IPO (priced November 18, 2026; trading as ANT from November 19).

**Conflict of interest:** the lyrics were drafted by Claude, a model made by Anthropic, the company the song is about, and Claude Code made the video. The video shows this: its live verse opens in the Claude Code session that made it, with the video sent as a file. Gemini 4 Argon (Google) reviewed the lyrics for bias on October 21 (`log/audits/`). Claude checked Gemini's factual claims as the conflicted party, and the human reviewed the lyrics on November 18.

This repository is the production record the credits point to. Claude Code produced the video. A human approved each stage, generated the song and the hold music in Suno, ran the post-filter, performed verse 3 and "do I get a say?" live, filmed the phone call and cut the final video. Each of those interventions is logged; the credits count the 39 up to the video's last build.

**The production log is written by the agent and is a record, not a statement of fact about Anthropic or anyone else:** where it discusses the fund, the fact card and its sources are the reference.

## How it was made

| Stage | What | Tools |
| --- | --- | --- |
| Lyrics | Drafted with Claude in the [planning chat](docs/planning_chat/planning_chat.md): the Founder, the Board, the Lawyer and the Worker trading lines, and a choir. Reviewed for bias by Gemini 4 Argon | Claude, Gemini |
| Song | One Suno take (c0702797), post-filtered with a cleanup ("deslop") model. Suno moved the key change to before verse 2 (logged as an AI change) | Suno V6, music-deslop M6f |
| Hold music | A muzak cover of the song, made by the human with Suno's cover feature; the post-roll's dial tones and ring are synthesized | Suno V6 |
| Timing | Lyrics aligned word by word to the vocal stem, beats and downbeats from the mix; every shot cued to a lyric line | torchaudio MMS_FA, Beat This |
| The certificate | An invented company's certificate (AMALGAMATED BENEFIT, LLC; CLASS N · NON-VOTING) printed in green, sepia and gold on cream, built from public-domain banknote engravings by Asher B. and Cyrus Durand (The Met, Open Access), with generated lathe work, microprint (the guilloche is the letters LLC) and a corporate seal | Python, OpenCV |
| The cast | The engraved figures cut into hinged paper puppets: Progress (the Founder), Prudence (the Board), Mercury (the Lawyer), the cherub choir. The laborer at the anvil, his hammer raised, never moves | Blender 5.2 (Eevee) |
| Animation | Puppets on twos with boiling hatching, a document camera's pushes and flips, the props (scales, scissors, coupons, thermometer, seal, filing cabinet). Final render at 4K on an RTX 5090 | Blender 5.2 |
| Cards | The title, the LIVE bug, the fact card with the human's red-pen notes, the announcement page and the credits | HTML in headless Chrome (Puppeteer) |
| The live verse | A call page built for the video ([`apps/call_page/`](apps/call_page/)): "Public Benefit Fund: stakeholder input session", a participant list of you and "Board (not joined)", a Raise hand button, the dial-in 555-0142, and background replacement (the fund's own slide, behind the human) | HTML, MediaPipe |
| Live | The screen recording (the render playing, the Claude Code session, the call), the human's verse and "do I get a say?", and the phone call, on the human's camera | the human |
| Edit | The final cut, with the live sections in place on the master's timing | DaVinci Resolve (the human) |

## What's real, and what's made up

Real:
- **The fund, its terms and the IPO,** as the fact card states them, with sources.
- **The Claude Code session** in the screen recording (from 2:44) is the session that made the video, and the video in it is the real file it sent.
- **The human's performance** on the call and the phone call. The props on the desk in the phone call are real documents about AI and jobs: a recruiter's cold email (redacted) offering contract work producing Claude Code training data, and the public version of Microsoft's voluntary exit offer memo.
- **Anthropic's announcement page** in the closing bookend, a capture of the real page.

Made up:
- **The company on the certificate,** AMALGAMATED BENEFIT, LLC, and every name, number and seal on it. No real name, logo or ticker appears on the certificate; they're only on the fact card.
- **The call page and its slide.** It isn't a real meeting app, and the fund's "slide" ("Your input matters.* *Input is advisory and non-binding.") is the video's invention.
- **The pledge line,** 555-0142, from the range set aside for fiction, and its hold music.
- **The coupons:** coupons belong on bonds, not stock certificates, a visual liberty kept off the fact card.

## Sources

### The fact card, verbatim

1. Announced October 18, 2026: Anthropic commits 5% of its shares to the Anthropic Public Benefit Fund. Its November 10 IPO filing says these were contributed as Class N shares, which carry no vote except as required by law.
2. The board may add 2% more for every 50% rise in Anthropic's share price, starting from the IPO price. *(Red pen: "It's not required to.")*
3. Set up as a wholly owned LLC, not a 501(c)(3), to allow different forms of giving. *("to allow different forms of giving" struck through; red pen: "which legally allows non-charitable activities".)*
4. 5% goes to the fund. Anthropic says about 20% of its shares are committed to the public good in total, counting its other commitments. The fund's equity won't be used for lobbying or political giving. *(Red pen: "So they say.")*
5. The fund's governance structure: to be announced. Until then, Anthropic's board decides what it gives.
6. Anthropic's IPO: priced November 18, 2026, trading on Nasdaq as ANT since November 19, 2026, at $83.
7. In its IPO filing, Anthropic says it has met its own Responsible Scaling Policy threshold for AI-accelerated research, based on what it expects from future models rather than what it has observed from current ones.
8. Separately, Anthropic has given $40M to Public First Action. It says that money is limited to policy work and public education, not candidate spending.
9. AI-generated satire. Lyrics drafted by Claude, a model made by Anthropic. Reviewed for bias by a model from another lab: Gemini 4 Argon, October 21, 2026. *(Red pen: "and by the human, November 18, 2026".)*

Sources: [Anthropic's announcement](https://www.anthropic.com/news/public-benefit-fund) · [Anthropic's S-1/A, November 17, 2026 (SEC)](https://www.sec.gov/Archives/edgar/data/2130357/000162828026074338/anthropicpbc-sx1ax3.htm) · [Anthropic on Public First Action](https://www.anthropic.com/news/donation-public-first-action) · [TechCrunch](https://techcrunch.com/2026/10/18/anthropic-says-its-committing-5-of-its-shares-to-a-public-benefit-fund/) · [The National](https://www.thenationalnews.com/future/technology/2026/10/19/anthropic-public-benefit-fund-elon-musk/) · [ESG Today](https://www.esgtoday.com/anthropic-commits-5-of-shares-to-a-new-public-benefit-fund/) · [CNBC on the IPO price](https://www.cnbc.com/2026/11/18/anthropic-ipo-ai-offering-price.html) · [Gizmodo on the RSI threshold](https://gizmodo.com/anthropic-says-its-recursive-self-improvement-alarm-has-been-triggered-2000840253)

Lines 2 and 5 were corrected on November 19 from the November 17 filing, which sets the escalator's baseline at the IPO price. The song's "a line we haven't drawn just yet" and the certificate's "Baseline: TBA" satirize the October announcement, which left the baseline unstated.

## Where things are

- [`log/production_log.md`](log/production_log.md): every generation, analysis and render, with the command, inputs, outputs and whether it was kept.
- [`log/human_interventions.md`](log/human_interventions.md): every human action, in the human's words, with its rule (R1 approve or reject, R2 A/V sync, R3 technical fixes, R4 interfaces the agent can't reach).
- [`log/prompts/`](log/prompts/): the Suno takes (the song and the muzak), with Suno's page records. [`log/audits/`](log/audits/): Gemini's review, verbatim.
- [`docs/brief.md`](docs/brief.md): a plain-text mirror of the brief (concept, lyrics, the certificate's world, shot list S01–S48, the live shots, the fact card). [`docs/planning_chat/`](docs/planning_chat/): the planning chat.
- [`config/`](config/): the look, the cast, props, shot anchors and holds, the post-roll, the fact card's IPO line, render profiles and seeds. [`timing/`](timing/): the timing map, word alignment, beats and keys.
- [`scenes/blender/`](scenes/blender/): the certificate scene and its animation (`animatic.py`), the call's boardroom background. [`assets/`](assets/): the puppets, fonts, engraving sources (listed in `sources.tsv`) and the announcement capture.
- [`overlays/graphics.html`](overlays/graphics.html): every card and the red pen. [`apps/call_page/`](apps/call_page/): the call page.
- [`scripts/`](scripts/): one script per step, each documented at the top. Among them: [`certificate.py`](scripts/certificate.py), [`final_queue.sh`](scripts/final_queue.sh) (the 4K render), [`live_excerpts.sh`](scripts/live_excerpts.sh) (the files the screen recording plays), [`subtitles.py`](scripts/subtitles.py), [`thumbnails.py`](scripts/thumbnails.py) and [`shorts.py`](scripts/shorts.py).
- [`archive/`](archive/): superseded and rejected passes, kept.
- [`METADATA.md`](METADATA.md): the YouTube metadata, the checklist before upload, the thumbnails and the Shorts. Subtitles: [`deliverables/share_the_shares.en.srt`](deliverables/share_the_shares.en.srt).

## Reproducing it

Large files (audio, the 4K master and its sections, the live plates and excerpts, the Shorts) are not in git; [`MANIFEST.sha256`](MANIFEST.sha256) lists them with checksums.

- **Environment:** `uv sync` (Python, pinned in `uv.lock`), `npm install` (Puppeteer, for the cards), Blender 5.2.
- **Seeds:** every random process reads its seed from [`config/seeds.json`](config/seeds.json).
- **The render:** `scripts/final_queue.sh graphics`, then `a` and `b` side by side, then `join` (4K, 64 samples; about three and a half hours on an RTX 5090). The commands for each later rebuild are in `renders/final/logs/` and the production log.
- **Can't be regenerated:** the song and the hold music (Suno doesn't give the same song twice), the human's live footage and the final cut. The post-filter model is private for now.

## Licences

- **Video and assets:** [CC BY-NC-SA 4.0](LICENSE-media.md). That file lists exactly what it covers and what it doesn't: the public-domain engravings, Anthropic's announcement page, the fonts, MediaPipe, the audit and Suno's records.
- **Code:** [MIT](LICENSE).

## Credits

- **Lyrics:** Claude, drafted in the [planning chat](docs/planning_chat/planning_chat.md); reviewed for bias by Gemini 4 Argon (Google) and by the human.
- **Music:** Suno V6, one take (c0702797), post-filtered with music-deslop M6f, a cleanup model for AI-generated music that Claude Code built and trained from a human-written spec (private for now). Verse 3 and "do I get a say?" performed live by the human.
- **Hold music:** a muzak cover of the song, made by the human with Suno's cover feature.
- **Engravings:** Asher B. Durand and Cyrus Durand, banknote vignettes and lathe work, ca. 1824–42, The Metropolitan Museum of Art, Open Access.
- **Animation:** Claude Code with Claude Opus 5.5, paper puppets in Blender.
- **Edit:** the human, in DaVinci Resolve.
- **Fonts:** [Abril Fatface](https://fonts.google.com/specimen/Abril+Fatface), [IM Fell English](https://fonts.google.com/specimen/IM+Fell+English), [Pinyon Script](https://fonts.google.com/specimen/Pinyon+Script), [Caveat](https://fonts.google.com/specimen/Caveat) and [Noto Sans](https://fonts.google.com/noto/specimen/Noto+Sans) (SIL Open Font License 1.1), in [`assets/fonts/`](assets/fonts/).

Satire. Not affiliated with or endorsed by Anthropic or any company named here.
