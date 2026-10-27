# Human interventions

Every human action: timestamp, what, why, and which production rule allows it. Rules:
(R1) approve/reject a take, render or plan; (R2) correct A/V sync; (R3) fix technical failures the agent cannot; (R4) run an interface the agent has no access to (Suno, the mastering post-filter). Anything else is an EXCEPTION. The brief plans two kinds of exception: the live shots (L), and the human's recorded voice (verse 3, "do I get a say?" in S40, and the Lawyer's patter if the generator sings it).

## 2026-10-25T08:15 (from the files' mtimes) — Source files supplied to the agent

- **What:** A human placed the Suno mix (WAV, MP3) and the stems-and-MIDI archive for "Share the Shares" in `~/Downloads`. They pointed the agent at the brief, the planning chat's share link and the sibling projects (Ghost in the Machine, Folks Like Us, Sandbox Rhapsody), with the note: "render availability is limited, so if you need any individual frames just re-render them."
- **Why:** Inputs for the project.
- **Rule:** Not a touch on the work (supplying inputs). Logged for completeness.

## 2026-10-22T02:04Z (from Suno's tag) — Track generated in Suno — R4 (choice of take: R1)

- **What:** A human ran Suno and chose take `c0702797-fae7-4b4a-8ad9-5d65f0c6843e` (283.44 s). It is one full-song take, not the section-by-section build the brief describes. The stored lyrics differ from the brief's (production log, step 1).
- **Why:** The agent has no access to Suno.
- **Rule:** R4 to run Suno; R1 to choose the take. Whether the lyric differences are Suno's or the human's (a human edit would be an EXCEPTION) is still open.
- **Still needed:** the Suno share link, the style prompt and settings as submitted, any rejected takes, and whether the master will go through the mastering post-filter.

## 2026-10-25T09:20 — Suno link, take confirmed, post-filter plan, Gemini version — R1

- **What:** The human gave the Suno share link (https://suno.com/s/1sz8sZONKQyqeqTj) and said: "the oneshot take worked (though I will be replacing the audio for the worker verse as described). master will go through post-filter on the 5090 box (requires the VRAM). Gemini 4 Argon."
- **Why:** These answer the open questions from step 1.
- **Rule:** R1 (approving the one-shot take over the brief's section-by-section plan). The post-filter run will be R4, logged when it happens. Replacing the Worker verse's audio with the human's performance is one of the brief's planned EXCEPTIONS, logged when recorded.
- **Lyrics:** Suno's page shows the submitted lyrics match the brief's (production log, step 2). So the earlier entry's open question is answered: no human lyric edit, no exception. "Spent" in verse 3 predates the audit, and the live verse replaces it.

## 2026-10-25T09:26:30-04 — Key change placement; master timing; A/V offsets — R2 (timing information)

- **What:** The human: "note that suno put the key change in right before verse 2, not where the lyrics prompted. the master does not change the timing -- the only offsets we will need to handle are from the human A/V, which (once I have it) will be fixed offsets against this audio for the end only"
- **Why:** Information from listening, for the timing map and the shot list.
- **Rule:** R2 (A/V sync information). Not a creative change.
- **Consequences:** the timing map (C3) is built on the Suno mix now, without waiting for the post-filtered master. The human's live A/V is synced by fixed offsets against this audio. The key change is Suno's change (below), not the human's.

## 2026-10-25T09:47:00-04 — S36 moves to the key change — R1 (a creative change, asked for in words)

- **What:** The human: "(and yes move S36 to the key change)". The agent moved S36 in the brief from the final chorus to the top of the verse 2 table, cue "The key change, just before verse 2 (where Suno put it)" (Claude Doc rev 30).
- **Why:** Suno moved the key change (production log, step 2).
- **Rule:** R1 (choosing between the two options the agent offered). The human said it in words and the agent made the change.

## 2026-10-25T09:48:54-04 — C1 approved — R1

- **What:** The human: "Looks good, keep going". C1 (style spec, look config, the certificate, the two test frames) is approved.
- **Rule:** R1.
- **Still open from C1:** the laborer's resting hammer (S07, S29) and Progress's stars-and-stripes shield. The agent keeps both as engraved for now (each is reversible) and raises them again at the next checkpoint.

## 2026-10-25T11:04:57-04 — Review formats for C2 and C3 — R1 (feedback in words)

- **What:** The human asked how much the non-vocal sync matters and said the lane preview "is hard for me to read -- a score is best if good sync for things like the drums is necessary". Of the cast test: "they look good but mostly the same across frames". The agent's answer: nothing here is note-driven, so C3 needs only the beat grid and three sync points. The human: "yes go ahead" to a click-track ear check and a pose sheet.
- **Rule:** R1 (choosing how a plan is reviewed). No creative change.

## 2026-10-25T11:17:24-04 — Fix the fill patches — R1 (a change asked for in words)

- **What:** The human: "Yes fix the fill patches". The agent replaced the generated line-screen fill with texture synthesis from the surrounding engraving.
- **Rule:** R1. The human said it in words and the agent made the change.

## 2026-10-25T17:05:37-04 — C3 approved; the poses leave pieces behind — R1

- **What:** The human: "the clicks are correct, but none of the poses are working quite right -- there's bits and pieces of all of them that need to be moved but haven't". C3 (the beat grid, the key change at 98.44 s, the live-verse cut and return) is approved. The C2 pose sheet is rejected: parts of every figure stay put when the limb they belong to moves.
- **Rule:** R1 (approve; reject with the reason). The agent re-cut the puppets; the human named no fix.

## 2026-10-25T17:29:43-04 — Smaller fill cells with blended seams — R1 (a change asked for in words)

- **What:** The human: "Yes try the smaller build cells with blended seams" (the agent's offer).
- **Rule:** R1. The human said it in words and the agent made the change.

## 2026-10-25T17:56:55-04 — C2 approved; the hammer raised; the shield kept — R1

- **What:** The human: "good enough, let's keep going for now. raise the hammer, and keep the stars-and-stripes shield". C2 (the puppets, as on the pose sheet) is approved, with the remaining patchwork fill under Prudence's widest swings accepted for now. The two open questions from C1 are answered: the laborer is engraved with his hammer raised (S07, S29), and Progress keeps her stars-and-stripes shield.
- **Rule:** R1 (approve; choose between options the agent offered).

## 2026-10-25T20:30:16-04 — C4: the sync isn't right; are the cut-out mouths intended? — R2 (sync) and R1 (a question)

- **What:** The human: "the sync is not quite right, and are the cutout (as opposed to natural) mouth movements intentional".
- **Rule:**
  - R2 for the sync report. The agent diagnosed and fixed it (production log, same time).
  - R1 for the question. The agent answered that the hinged jaw is the brief's ("hinged paper-puppet limbs and jaws on twos"), and offered replacement mouths as an alternative. The human hasn't chosen yet.

## 2026-10-25T21:24:26-04 — The sync test approved; the hinged jaws kept — R1

- **What:** The human: "the sync is correct, and the mouths now make sense with the sync in place". The sync fix is approved, and the hinged cut-out jaws (the brief's) stay. No replacement mouths.
- **Rule:** R1.

## 2026-10-25T21:31:43-04 — C4: inserts in the long chorus holds; S39 moved — R1 (choosing between the options offered)

- **What:** The human: "do both", to the agent's two questions:
  - the long holds: add inserts returning to the S13–S16 images, or keep the holds;
  - S39: retire it, or move it to the line after "at our discretion".

  The agent read it as both changes. It did not read it as both options of the S39 question, since retiring S39 and moving it can't both happen.
- **Brief edit (Claude Doc rev 30 → 31, made by the agent):**
  - New rows S17a and S17b (chorus 1's repeat), and S25a, S25b and S25c (chorus 2). Inserts take a letter suffix.
  - S39's cue becomes "The more we grow, the more we give", the line after "at our discretion", with a note that Suno didn't sing "baseline to be announced!". The final chorus sings "at our discretion" once, and S38 holds it.
- **Rule:** R1. The human chose, and the agent made the changes.

## 2026-10-25T22:40:03-04 — C4 v2 review: S24's repeat, the post-filter, the placeholder graphics, the 5% — R1, R2

- **What:** The human:
  - "S24: 'through this fund' is repeated in the song, which seems to be messing up the following line (it recovers afterwards though)";
  - "has this been run through the postfilter yet?", then "oh whoops never mind about the postfilter then";
  - "create and fill in the graphics in the placeholders";
  - "the 5% in the corners is hard to read".
- **Rule:** R2 for S24 (a sync error, information from listening). R1 for the graphics and the 5% (changes asked for in words). The post-filter question was withdrawn: no change, and the master's post-filter stays the human's step on the 5090 box (R4).

## 2026-10-26T07:33:32-04:00 — C4 v3 review: the lyric timing at the start, and Suno's other repeats — R2

- **What:** The human: "Check the lyrics timing, particularly at the beginning, again. There's also at least one other spot where Suno repeated lyrics".
- **Rule:** R2: a sync error, information from listening. The agent found the causes and made the fixes.

## 2026-10-26T08:05:00-04:00 — The plan for the stand-in props: approved — R1

- **What:** The agent proposed a plan for the stand-ins:
  - the grey prop cards drawn as engraved props, from public-domain engravings, pre-1931 US patent drawings, and the certificate's own type and guilloche;
  - a prop sheet for review before C5;
  - the S01 capture left to the human (R4);
  - the credits awaiting approval;
  - the fact-card check at C6.

  The human: "yes go ahead".
- **Rule:** R1.

## 2026-10-26T10:13:03-04:00 — C5 prop sheet v1 review: clipped text — R1

- **What:** The human: "Check them for clipped text, such as in the calendar".
- **Rule:** R1 (a rejection, with the fault named). The agent found and fixed every case.

## 2026-10-26T10:14:51-04:00 — C5 prop sheet v2: approved — R1

- **What:** The human: "These look great, keep going".
- **Rule:** R1.

## 2026-10-26T13:16:18-04:00 — C5 section 1 review: S01 cut, S08 too still — R1

- **What:** The human: "My only notes on this: I don't think S01 (the Suno screen grab) fits for this at all. S08 is sitting still for too long."
- **Rule:** R1 (a rejection of S01, and a change asked for in words for S08). This also ends the planned R4 step of capturing the real Suno screen.

## 2026-10-26T18:04:04-04:00 — C5 approved; the human's red-pen hedges on the fact card; credits — R1, EXCEPTION

- **What:** The human: "Video is fine." Then:
  - more hedging on the end card (S47), "via a red pen in a handwritten font":
    - above "The board may add 2% more…": "It's not required to.";
    - cross out "to allow different forms of giving" and add next to it "which legally allows non-charitable activities";
    - after "The fund's equity won't be used for lobbying or political giving.": "So they say.";
    - circle "to be announced";
    - underline "Lyrics drafted by Claude, a model made by Anthropic";
    - after "Reviewed for bias…": "and by the human, October 26, 2026".
  - "Production log will be hosted on https://github.com/Derivative-Work/share-the-shares."
  - Credits: "Verse 3…" reads "performed live by the human, one take"; "Animations and edit" adds "the human, DaVinci Resolve".
- **Rule:**
  - R1 for the video (C5 approved) and for the credits' wording.
  - **EXCEPTION** for the fact card: the human wrote the annotations' text. Their claim "which legally allows non-charitable activities" joins the C6 fact-card source check.
  - The annotation "and by the human, October 26, 2026" records a bias review by the human, alongside Gemini's.
  - The credit "the human, DaVinci Resolve" records that the human does the final edit, a further EXCEPTION, logged as the edit happens.

## 2026-10-26T18:24:39-04:00 — The hold music made in Suno; the fact card's arrow — R4, R1, EXCEPTION

- **What:** The human:
  - "put the "it's not required to" further to the right and add a handwritten-looking arrow pointing from it to the line it's referencing."
  - "The musak is in ~/Downloads, made by using the "cover" feature in Suno, removing the lyrics, and replacing the style with just "muzak". The chorus starts at roughly 1:10: add dial tone corresponding to that number, one short "ring", then fade into the song but keep it playing for the rest of the video (including the terms and credits). Suno link: https://suno.com/s/XvG9otSmBT8EHh2h"
- **Rule:**
  - R4: the human ran Suno's cover feature (an interface the agent can't reach). The settings are logged in `log/prompts/suno/muzak.md`.
  - R1: the instructions for the post-roll's sound, and for the note's placement.
  - The arrow belongs to the human's annotation, the EXCEPTION logged at 18:04:04.

## 2026-10-26T18:47:22-04:00 — The terms page holds until the muzak's chorus ends — R1

- **What:** The human: "make the "terms" page sit longer with the human edits -- just enough that the muzak is allowed to finish the chorus by the very end (roughly 1:50)".
- **Rule:** R1.

## 2026-10-26T19:31:22-04:00 — S44: the drawer shuts after the whole line — R1

- **What:** The human: "time the cut to the "wholly owned" a bit later so that the whole "phone lines open at the IPO" can be seen with the mouth moving".
- **Rule:** R1.

## 2026-10-26T23:20:00-04:00 — The project moved to the RTX 5090 box — R3

- **What:** The human rsynced the project from the GTX 970 box to the RTX 5090 box (`docs/render_box.md`): "I just moved over this project from the draft box. Prepare it to render here".
- **Rule:** R3: the agent has no access between the two machines.

## 2026-10-26T23:45:00-04:00 — Queue the 4K finals, plates for the live shots, a post-filtered preview — R1

- **What:** The human: "go ahead and queue the 4K render. I'm also going to need the videos to composite into the live sections. Also run the audio through the postfilter (~/Code/music-deslop) for this render so I can preview what it sounds like before I properly redo the mix with the live sections included."
- **Rule:** R1. The post-filter was planned as the human's step (R4, 2026-10-25T09:20) because it needs this box's VRAM. Here the agent has access, so the agent ran it at the human's direction; it isn't an R4. The human will do the final mix with the live audio, and that will be logged when it happens.

## 2026-10-26T23:53:00-04:00 — Disk space freed on the 5090 box — R3

- **What:** The human: "I freed up some space by archiving and deleting renders from already-published videos".
- **Rule:** R3. The agent was removing each 4K section's frames for lack of disk, and the other projects' renders aren't the agent's to delete.

## 2026-10-27T00:05:27-04:00 — The GitHub repository created — R4

- **What:** The human: "I created github.com/Derivative-Work/share-the-shares and gave you access, go ahead and push what you so far there".
- **Rule:** R4: creating a repository in the Derivative-Work organization, and granting access to it, are things the agent can't do. Pushing is the agent's step.

## 2026-10-27T08:20:00-04:00 — Mouths, the gold's hold, a captions layer, an alignment sheet — R1

- **What:** The human: "It seems like there is some missing mouth movement. Hold the gold at the transition a little longer (eating into "now you might ask..." slightly) so that its fully visible. I also need a render of the captions (with transparency) so it's easy to bring into Resolve (where I'll do the final edit with live footage and compositing). Also generate me an alignment sheet that I can print for said compositing."
- **Rule:** R1. The final edit in Resolve, with the live footage and compositing, will be the human's, and will be logged when it happens.

## 2026-10-27T09:05:00-04:00 — The mouths to fix; the history rewrite approved — R1

- **What:** Asked which missing mouth movement they meant, the human chose "Mercury's lines" and "Prudence too subtle". Asked whether to rewrite the pushed history to drop the alignment sheet's binaries, the human chose "Rewrite and force-push".
- **Rule:** R1.

## 2026-10-27T19:30:00-04:00 — A video for the phone in S45 — R1

- **What:** The human: "make me a video I can play on my phone for the pre-credits dialer scene".
- **Rule:** R1. Playing it on the phone during the live take will be the human's part of S45–S46, and will be logged with the live footage.

## 2026-10-27T19:50:00-04:00 — No hang-up on the phone's screen — R1

- **What:** The human, of the phone video: "remove the hangup".
- **Rule:** R1.
