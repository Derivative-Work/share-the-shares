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
