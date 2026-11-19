# Upload metadata

YouTube metadata for the main video. Written by the agent; the human cuts the video (DaVinci Resolve) and uploads. Prepared November 19, 2026, the day ANT starts trading. The video is done (the human, November 19). The brief says to post shortly after trading starts, once the final price is on the fact card, and it is ($83, production log 2026-11-18T23:15).

**Before uploading:**
- **Facts** (the brief's "Facts to verify before release"), checked by the agent on November 19 against the filings on EDGAR and Anthropic's pages. "Confirmed" means a primary source says it; the rest needs a look in a browser.
  - **Class N, no vote:** confirmed. The last amended S-1 (S-1/A, November 17) says the fund got 846,840,960 Class N shares, 5% of fully diluted shares as of June 30, 2026, and that Class N "is not entitled to vote on any matter that is submitted to a vote of stockholders, except as otherwise required by law".
  - **The RSI threshold:** confirmed, same filing: "we made a determination that we have met this threshold based on what we expect from future models and our overall rate of progress, rather than on what we have observed from current models."
  - **The fund's terms:** the announcement still says what the card says: LLC "rather than a 501(c)(3)", for "adjustability between different forms of giving"; "roughly 20%" in total; no fund equity "for lobbying or political giving, in the US or abroad".
  - **$40M to Public First Action:** confirmed on Anthropic's page: two $20M donations (February and July 2026), which "cannot be used to influence the election of any candidate".
  - **The IPO:** $83, priced November 18, trading from November 19 (CNBC). The final prospectus (424B4) wasn't on EDGAR yet when checked (last filings: an S-1MEF and an FWP on November 18). Check it, or the opening trade, before upload.
  - **Changed since the card was drafted: the baseline and the managers.** The November 17 filing says the board may add up to 2% "each time our share price appreciates 50% above the prior share price milestone, beginning with our initial public offering price". So the baseline is the IPO price, $83, and the first milestone is $124.50. The card's "above a baseline not yet announced" is out of date, and so is the "valuation milestones" part of "Structure, governance and valuation milestones: to be announced". The filing also names the fund's initial managers (Dario Amodei, Daniela Amodei, Jack Clark, Neil "Buddy" Shah). The board decides the fund's giving "until it approves a specific governance structure", so governance itself is still to come. The lyrics and the certificate's TBA gags satirize the October announcement and can stand. **Fixed on the card** (the human, November 19; master v8): "The board may add 2% more for every 50% rise in Anthropic's share price, starting from the IPO price." and "The fund's governance structure: to be announced. Until then, Anthropic's board decides what it gives." Swap the cut's last 32 s (from S47, 4:56) for the new master's.
- **The repository is private.** The credits and the description point to github.com/Derivative-Work/share-the-shares, so make it public before the video goes up.
- **Licence:** video and assets CC BY-NC-SA 4.0 (`LICENSE-media.md`, `LICENSES/`), code MIT (`LICENSE`), confirmed by the human on November 19.
- **The brief's review checklist** still has the Gemini rerun open. The card dates the human's own review November 18, 2026; Gemini's pass stays October 21.
- **Timing:** the human's cut keeps the master's timing (the live sections replace shots in place; human, 2026-11-19), so the chapters and subtitles below are in master time and final.
- **Intervention count: frozen at 39** (the human, November 19: "the video itself is done"). The credits and the description read 39, the entries up to the IPO line on November 18. Entries logged after that come after the video and don't change it.

**Links to verify:**
- Anthropic's last amended S-1, November 17 (Class N, the fund, the baseline, the managers, the RSI threshold): https://www.sec.gov/Archives/edgar/data/2130357/000162828026074338/anthropicpbc-sx1ax3.htm. It's large; search the page for "Initial Public Benefit Issuance", "beginning with our initial public offering price", "initial managers" and "observe or expect".
- Anthropic's filings, for the final prospectus (424B4) when it appears: https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=2130357&type=424B4
- The fund's announcement, October 18: https://www.anthropic.com/news/public-benefit-fund
- Public First Action, $40M: https://www.anthropic.com/news/donation-public-first-action
- The IPO price: https://www.cnbc.com/2026/11/18/anthropic-ipo-ai-offering-price.html
- The managers, as reported (citing the November 10 filing): https://www.billionaires.africa/2026/11/16/american-billionaires-dario-and-daniela-amodei-to-run-anthropics-66-billion-benefit-fund/

---

## Main video (16:9, 3840×2160, 24 fps)

**Source for the cut:** `deliverables/final_4k/share_the_shares_4k_postfilter_preview.mov` (ProRes 422, 24-bit PCM, 5:28.33; v8, rebuilt November 19 with the IPO line and the filing's baseline and governance). The cut replaces S29–S31 and S40 with the screen recording and S45–S46 with the phone call. **Captions:** `deliverables/share_the_shares.en.srt` (76 cues, master time, which the cut keeps). **Thumbnail:** one of `deliverables/thumbnails/` (see Settings).

### Title

Recommended (51 characters):

```
Share the Shares — an all-star benefit single (sort of)
```

Alternatives:
- `Share the Shares: a 1980s charity single for a pre-IPO fund`
- `Share the Shares — help us grow, so we can give`

### Clickbait-adjacent titles and thumbnails

Each title is paired with a thumbnail. The titles stay true to the video, so none of them is bait the video doesn't pay off. All eight are made from the human's cut (`deliverables/thumbnails/thumbnail_<n>_*.jpg`, in table order); **(yours)** marks the ones built on the human's footage.

| Title | Thumbnail |
|---|---|
| `I was the only one who showed up to the stakeholder meeting` | **(yours)** Your call tile, alone, with "Board (not joined)" greyed out in the participant list. The boardroom background is behind you and your hand is raised. Big text: **1 PARTICIPANT**. |
| `They're giving away 5% of the company. I asked one question.` | **(yours)** The raised-hand frame from S40, close on your face, with **DO I GET A SAY?** in the certificate's red pen and no reply. |
| `Anthropic's AI wrote a charity single about Anthropic's IPO` | **(yours)** The S29 session reveal: the Claude Code session with the video sent as a file, a red-pen circle on the file, and **IT MADE THIS ABOUT ITSELF**. Check that everything legible on screen is fine to publish. |
| `I called the pledge line. Please hold.` | **(yours)** S45/S46: you at the desk with the phone to your ear, looking at the camera, with **PLEASE HOLD** in engraved capitals. |
| `"Threshold met*" (*based on what we expect)` | S34's seal close up: THRESHOLD MET* embossed, with the red pen circling "*based on what we expect". From the master at 3:30–3:32. |
| `Help us grow, so we can give (buy the stock)` | The certificate wide, the corner 5 flipped to 5%, with the red pen's arrow to "at our discretion" and **BUY TO GIVE?** |
| `The board may add 2%. It's not required to.` | The fact card's line with the red pen's "It's not required to." large, the rest of the card soft behind it (296–317 s in the master). |
| `Share the Shares — an all-star benefit single (sort of)` | Prudence with her scissors raised over the coupons (S38, from 3:52), the cherubs behind. The straight option. |

The first two are the strongest: a face and a question beat a document, and "Board (not joined)" works as a joke on its own without the song. For a set of A/B thumbnails (YouTube's "Test & compare"), pair the call tile with the seal.

### Description

```
AI-generated satire. A 1980s all-star charity single where every star is from the same company, sung inside an engraved stock certificate. A benefit single asks the public to give. This one ends up asking them to buy, because most of the gift only grows if the stock does.

The fund is real: on October 18, 2026, Anthropic committed 5% of its shares to the Anthropic Public Benefit Fund. The song is about its terms: the growth escalator, a baseline the announcement left unstated, governance still to come, and the timing, just before the IPO.

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
• The board may add 2% more for every 50% rise in Anthropic's share price, starting from the IPO price.
• Set up as a wholly owned LLC, not a 501(c)(3), to allow different forms of giving.
• 5% goes to the fund. Anthropic says about 20% of its shares are committed to the public good in total, counting its other commitments. The fund's equity won't be used for lobbying or political giving.
• The fund's governance structure: to be announced. Until then, Anthropic's board decides what it gives.
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
| Thumbnail | Eight options in `deliverables/thumbnails/` (1280×720 JPEG, `contact_sheet.jpg` to compare), made by `scripts/thumbnails.py` from the human's cut, numbered as the table in "Clickbait-adjacent titles and thumbnails". |
| Chapters | From the description (first at 0:00; each over 10 s), at the master's shot and line times. |
| End screen | Over the credits' last seconds. The cut ends on the credits, about 6 s long in the master, so lengthen that card if you want a full 20 s end screen. |
| Comments | Open. |
| Visibility | Unlisted for a check pass, then public. |

---

## Subtitles

`deliverables/share_the_shares.en.srt` comes from `scripts/subtitles.py`: the 72 lyric lines (line by line from `timing/timing_map.json`, "♪" on sung lines), plus `[electric piano]` at the start and the post-roll's `[phone dialing]`, `[ringing]` and `[hold music: "Share the Shares" as muzak]`. It is in the master's time, which the cut keeps.

- Verse 3 reads "pledged" (the brief, after the audit). If the live take sings "spent", run `.venv/bin/python -I scripts/subtitles.py --spent`.
- If a live line lands well off the generated take's time, `--verse-lines` takes the eight verse starts; `--verse`, `--bridge`, `--postroll` and `--end` shift whole stretches, for a cut that moves them.
