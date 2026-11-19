# Upload metadata

YouTube metadata for the main video. Written by the agent; the human cuts the video (DaVinci Resolve) and uploads. Prepared November 19, 2026, the day ANT starts trading. The brief says to post shortly after trading starts, once the final price is on the fact card, and it is ($83, production log 2026-11-18T23:15).

**Before uploading:**
- **The facts the brief asks to verify** ("Facts to verify before release"). Status as of November 19:
  - **IPO price and dates:** on the card as priced November 18, trading from November 19, at $83 (CNBC, November 18). Most reports call it confirmed; StockAnalysis said Anthropic hadn't announced it yet. Check the final prospectus (424B4) or Anthropic's release once it's out.
  - **The Class N and RSI-threshold wording:** still checked only against the November 10 filing. Check the final prospectus; the certificate's class line, S34's seal and the card all use it.
  - **The $40M to Public First Action and Anthropic's caveat:** recheck against current reporting.
  - **Baseline, governance or milestones:** if any have been announced, the TBA gags (S33, the card's "to be announced") need a decision before release.
- **The repository is private.** The credits and the description point to github.com/Derivative-Work/share-the-shares, so make it public before the video goes up.
- **Licence:** this repo has no `LICENSE` or `LICENSE-media.md` yet. The series uses video and assets CC BY-NC-SA 4.0 and code MIT (Not Yet, All Systems Operational), and the description below says so. Confirm, and the agent adds the files.
- **The brief's review checklist** still has the Gemini rerun open. The card now dates the human's own review November 18, 2026 (human interventions 39); Gemini's pass stays October 21.
- **Timing:** the human's cut keeps the master's timing (the live sections replace shots in place; human, 2026-11-19), so the chapters and subtitles below are in master time and final.
- **Intervention count:** the credits read 39 (`grep -c '^## ' log/human_interventions.md`). The live verse, "do I get a say?", the phone call and the cut itself are logged as the human's when done; if that raises the count before release, the credits card is re-rendered (`scripts/render_graphics.py 3840 2160 1 renders/final/graphics credits`; then section 6 and the join, as `renders/final/logs/rerender_ipo.sh`).

---

## Main video (16:9, 3840×2160, 24 fps)

**Source for the cut:** `deliverables/final_4k/share_the_shares_4k_postfilter_preview.mov` (ProRes 422, 24-bit PCM, 5:28.33; v7, rebuilt November 18 with the IPO line). The cut replaces S29–S31 and S40 with the screen recording and S45–S46 with the phone call. **Captions:** `deliverables/share_the_shares.en.srt` (76 cues, master time, which the cut keeps). **Thumbnail:** none made yet (see Settings).

### Title

Recommended (51 characters):

```
Share the Shares — an all-star benefit single (sort of)
```

Alternatives:
- `Share the Shares: a 1980s charity single for a pre-IPO fund`
- `Share the Shares — help us grow, so we can give`

### Description

```
AI-generated satire. A 1980s all-star charity single where every star is from the same company, sung inside an engraved stock certificate. A benefit single asks the public to give. This one ends up asking them to buy, because most of the gift only grows if the stock does.

The fund is real: on October 18, 2026, Anthropic committed 5% of its shares to the Anthropic Public Benefit Fund. The song is about its terms: the growth escalator, a baseline and governance still to be announced, and the timing, just before the IPO.

A disclosure: the lyrics were drafted by Claude, a model made by Anthropic, the company this song is about, and the video was made by Claude Code in the session you see at 2:44. So the lyrics were reviewed for bias by a model from another lab (Gemini 4 Argon, Oct 21) and by the human (Nov 18). The human performed verse 3 and "do I get a say?" live, and cut the video. Every prompt, production step and human intervention is logged:
https://github.com/Derivative-Work/share-the-shares

CHAPTERS
0:00 Intro: a job is changing
0:20 Verse 1: a fund we keep at home
0:46 Pre-chorus: an LLC, wholly owned
1:00 Chorus: share the shares
1:39 Verse 2: who holds the purse
2:07 Pre-chorus 2: through this fund
2:19 Chorus 2
2:44 Verse 3, live: do I get a say?
3:12 Bridge: watch us when it's not
3:40 Final chorus
4:08 Outro: phone lines open at the IPO
4:43 The pledge line
4:56 The terms
5:17 The announcement and credits

THE TERMS
• Announced Oct 18, 2026: Anthropic commits 5% of its shares to the Anthropic Public Benefit Fund. Its Nov 10 IPO filing says these were contributed as Class N shares, which carry no vote except as required by law.
• The board may add 2% more for every 50% rise in Anthropic's value above a baseline not yet announced.
• Set up as a wholly owned LLC, not a 501(c)(3), to allow different forms of giving.
• 5% goes to the fund. Anthropic says about 20% of its shares are committed to the public good in total, counting its other commitments. The fund's equity won't be used for lobbying or political giving.
• Structure, governance and valuation milestones: to be announced.
• Anthropic's IPO priced Nov 18, 2026 at $83 a share; it trades on Nasdaq as ANT from Nov 19.
• In its IPO filing, Anthropic says it has met its own Responsible Scaling Policy threshold for AI-accelerated research, based on what it expects from future models rather than what it has observed from current ones.
• Separately, Anthropic has given $40M to Public First Action. It says that money is limited to policy work and public education, not candidate spending.

SOURCES
Anthropic: https://www.anthropic.com/news/public-benefit-fund
TechCrunch: https://techcrunch.com/2026/10/18/anthropic-says-its-committing-5-of-its-shares-to-a-public-benefit-fund/
The National: https://www.thenationalnews.com/future/technology/2026/10/19/anthropic-public-benefit-fund-elon-musk/
ESG Today: https://www.esgtoday.com/anthropic-commits-5-of-shares-to-a-new-public-benefit-fund/
Anthropic's IPO filing (DRS/A, SEC): https://www.sec.gov/Archives/edgar/data/0002130357/000213035726000014/filename1.htm
CNBC, the IPO price: https://www.cnbc.com/2026/11/18/anthropic-ipo-ai-offering-price.html
Gizmodo, the RSI threshold: https://gizmodo.com/anthropic-says-its-recursive-self-improvement-alarm-has-been-triggered-2000840253

The company on the certificate, Amalgamated Benefit, LLC, is invented, and so is the pledge line (555-0142, a number set aside for fiction). The engraved figures are allegories: Progress (the Founder), Prudence (the Board), Mercury (the Lawyer) and the cherub choir.

CREDITS
Words: Claude; reviewed for bias by Gemini 4 Argon and by the human
Music: Suno V6, one take (c0702797); post-filtered with music-deslop
Verse 3 and "do I get a say?": performed live by the human
Hold music: a muzak cover of the chorus in Suno
Engravings: Asher B. Durand and Cyrus Durand, banknote vignettes and lathe work, ca. 1824–42, The Metropolitan Museum of Art, Open Access
Animation: Claude Code with Opus 5.5, paper puppets in Blender
Edit: the human, DaVinci Resolve
Type: Abril Fatface, IM Fell English, Pinyon Script and Caveat (SIL OFL)
Video and assets: CC BY-NC-SA 4.0 · Code: MIT
Satire. Not affiliated with or endorsed by Anthropic or any company named here.
#AIgenerated #musicvideo #satire
```

### Tags

Paste as one comma-separated line:

```
Share the Shares, AI music video, AI generated, AI satire, Anthropic, Anthropic IPO, ANT, Public Benefit Fund, charity single, benefit single, 1980s, all-star, stock certificate, engraving, paper puppets, Suno, Claude, Claude Code, Blender, Derivative Work
```

### Settings

| Setting | Value |
|---|---|
| Category | Music |
| Audience | Not made for kids |
| Altered or synthetic content | **Yes.** The singing voices (all but the human's verse and "do I get a say?") are AI-generated, and the certificate world is rendered. The video call is a page built for the video, not a real call; the session reveal and the human's footage are real. |
| Language / caption language | English / English |
| Captions | Upload `deliverables/share_the_shares.en.srt` as English subtitles. Not burned in. |
| License | Standard YouTube License. YouTube's only Creative Commons option is CC BY, which would drop the NC-SA terms; the description states the licence instead. |
| Thumbnail | None yet. Candidates from the master: S34's seal embossing THRESHOLD MET* (3:30–3:32), Prudence with the scissors raised (S38, from 3:52), or the empty call tile with "Board (not joined)" from the live footage. Say which and the agent makes it at 1280×720 with the title. |
| Chapters | From the description (first at 0:00; each over 10 s), at the master's shot and line times. |
| End screen | Over the credits' last seconds. The cut ends on the credits, about 6 s long in the master, so lengthen that card if you want a full 20 s end screen. |
| Comments | Open. |
| Visibility | Unlisted for a check pass, then public. |

---

## Subtitles

`deliverables/share_the_shares.en.srt` comes from `scripts/subtitles.py`: the 72 lyric lines (line by line from `timing/timing_map.json`, "♪" on sung lines), plus `[electric piano]` at the start and the post-roll's `[phone dialing]`, `[ringing]` and `[hold music: "Share the Shares" as muzak]`. It is in the master's time, which the cut keeps.

- Verse 3 reads "pledged" (the brief, after the audit). If the live take sings "spent", run `.venv/bin/python -I scripts/subtitles.py --spent`.
- If a live line lands well off the generated take's time, `--verse-lines` takes the eight verse starts; `--verse`, `--bridge`, `--postroll` and `--end` shift whole stretches, for a cut that moves them.
