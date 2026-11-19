An AI-made 1980s all-star charity single for the Anthropic Public Benefit Fund, where every star is from the same company and the video takes place inside one engraved stock certificate, animated like paper puppets. Claude Code (Opus 5.5) produced the video in Blender. Suno V6 made the music, post-filtered with music-deslop. Claude drafted the words. The human performed verse 3 and "do I get a say?" live on a made-up video call, filmed the phone call, and cut the final video in DaVinci Resolve. Every human action is logged in [log/human_interventions.md](https://github.com/Derivative-Work/share-the-shares/blob/main/log/human_interventions.md).

AI-generated satire about a real commitment. The fact card's text and its sources are in the [README](https://github.com/Derivative-Work/share-the-shares#sources), checked against Anthropic's filings on November 19. Conflict of interest: Claude, made by Anthropic, drafted the lyrics about Anthropic's fund, and Claude Code made the video. The video shows it, in the session that made it. Gemini 4 Argon reviewed the lyrics for bias, and so did the human.

**Watch:** [the video](https://www.youtube.com/watch?v=YpJn6DwTLlk)

## Files

| File | What |
| --- | --- |
| `share_the_shares_1920x1080.mov` | The video, 5:28.6, H.264 1080p, 24 fps, 24-bit PCM: the human's final cut, the YouTube upload file itself |
| `share_the_shares_short_1_verse.mp4` | Short 1, 42.9 s: the session reveal and the live verse on the call, to the bridge's return |
| `share_the_shares_short_2_pitch.mp4` | Short 2, 52.0 s: "It's not a charity, per se" through chorus 1 |
| `share_the_shares_short_3_hand.mp4` | Short 3, 28.5 s: the final chorus and the raised hand nobody answers |
| `share_the_shares_short_4_threshold.mp4` | Short 4, 27.9 s: the bridge and the THRESHOLD MET* seal |
| `share_the_shares_short_5_pledge.mp4` | Short 5, 51.8 s: the pledge line, the hold music and the fact card, its marked lines spelled out |
| `share_the_shares.en.srt` | English subtitles for the video: the lyrics line by line, with sound cues |
| `share_the_shares_thumbnails.zip` | The thumbnail options and their contact sheets |
| `share_the_shares_call_page.html` | The call page, one file: open it in Chrome; S for setup, B cycles the backgrounds |
| `inputs.tar` | The audio git doesn't hold, none of which can be regenerated: Suno's take and its stems as downloaded, the muzak cover, the post-filtered audio and the post-roll |
| `SHA256SUMS` | Checksums for every file above |

Every file inside the tar, and every render, frame and superseded take, is listed with its SHA-256 hash in [MANIFEST.sha256](https://github.com/Derivative-Work/share-the-shares/blob/main/MANIFEST.sha256). The [production log](https://github.com/Derivative-Work/share-the-shares/blob/main/log/production_log.md) has the command for each, and [scripts/release.sh](https://github.com/Derivative-Work/share-the-shares/blob/main/scripts/release.sh) builds this release.

Not included:
- the 4K ProRes master and its sections (24 GB, over the 2 GiB limit per file; they regenerate with `scripts/final_queue.sh`);
- the human's raw live footage and the DaVinci Resolve project;
- the Claude Code session transcript.

## Licences

Video, music and assets: [CC BY-NC-SA 4.0](https://github.com/Derivative-Work/share-the-shares/blob/main/LICENSE-media.md). Code: [MIT](https://github.com/Derivative-Work/share-the-shares/blob/main/LICENSE). Satire; not affiliated with or endorsed by Anthropic or any company named.
