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
