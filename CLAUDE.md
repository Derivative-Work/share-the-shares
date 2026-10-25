# Share the Shares

An AI-made 1980s all-star charity single for the Anthropic Public Benefit Fund, where the video takes place inside one engraved stock certificate, animated like paper puppets. The human performs the Worker's verse live, the only live footage. The agent does the production; the human may only approve or reject (R1), correct A/V sync (R2), fix technical failures the agent can't (R3), and run interfaces the agent has no access to, such as Suno and the mastering post-filter (R4). The live shots (L) and the human's recorded voice are exceptions the brief plans for; log each one.

**Start here:** the brief is the Claude Doc https://claude.ai/artifact/9kd8kySs1GK8P5ExFjM6Wu (read it with the docs tools, not a web fetch; mirrored in `docs/brief.md`). It has no production rules of its own: they are inherited from Ghost in the Machine, Sandbox Rhapsody and Not Yet (`docs/brief.md` in each sibling repo under `~/Projects`). Then read the latest entries of `log/production_log.md` and `log/human_interventions.md`.

Rules that apply to every step:
- **Logs:** append to `log/production_log.md` for every action. Log every human action with its rule in `log/human_interventions.md`. Prompts go in `log/prompts/`; the planning chat is in `docs/planning_chat/` and the lyric audits go verbatim in `log/audits/`.
- **Commits:** one git commit per logged step.
- **Assets:** never delete or overwrite an asset. Superseded or rejected files go to `archive/` with a log note.
- **Large files** stay out of git; run `scripts/manifest.sh` after adding any. Frame sequences, caches, venvs and node_modules are never archived.
- **Engravings:** build from public-domain certificate art only, and log each piece's source in `assets/engravings/sources.tsv`. No real names or logos on the certificate; they belong only on the fact card.
- **Shot IDs** never change: inserts take a letter suffix, removals retire their ID.
- **Render tiers:** `config/render_profiles.json`. Iterate at 720p on the GTX 970 box; final 4K on the RTX 5090 box.
