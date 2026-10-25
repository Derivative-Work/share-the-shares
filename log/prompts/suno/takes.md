# Suno takes

## Chosen

- **Take:** `c0702797-fae7-4b4a-8ad9-5d65f0c6843e`, "Share the Shares" (https://suno.com/s/1sz8sZONKQyqeqTj)
- **Model:** Suno V6 (`chirp-hawk`), `aug_creativity` 1, not instrumental, not a remix
- **Created:** 2026-10-21T02:27:00Z (Suno's page); length 283.44 s. The MP3's comment tag reads `created=2026-10-22T02:04:54Z`, about a day later; it is probably the export time.
- **Style prompt (as Suno stored it):** "1980s slow power ballad, 72 BPM, polished studio mix with gated reverb drums and a long fade-out; glassy FM electric piano, warm synth pads, soaring featured saxophone fills, and big gospel choir; many solo vocalists trading lines in high, light registers with clipped, rhythmic staccato phrasing, opening with spoken voice and building to a whole-step key change into the final chorus."
- **Display tags:** power ballad, 1980s, gospel
- **Lyrics as submitted:** `fetch_accepted/lyrics.txt` (Suno's page). The brief's lyrics with two differences:
  - chorus 2 is written out in full where the brief has only the `[Chorus] (everyone)` tag (a repeat, not a lyric change);
  - verse 3 has "two hundred million **spent** to learn": the take was made before the Gemini audit changed it to "pledged". The live verse replaces this audio, so the human can sing "pledged".
  The bracketed singer notes were submitted too, although the brief says to remove them. Whether Suno sang any of them gets checked by ear at C3.
- **One-shot take:** the whole song in one generation, not the section-by-section build the brief planned. The human: "the oneshot take worked."
- **Fetch:** `fetch_accepted/` (`page.*`, `resp_*.json`, `clip.json`)

## Rejected

None supplied.

## Note: the MP3's lyrics tag

The downloaded MP3's `lyrics-eng` tag (`lyrics_submitted.txt`, extracted in step 1) differs from Suno's page. It drops the [Verse 1], [Pre-Chorus], [Verse 3], [Bridge] and [Final Chorus] tags, repeats chorus 1's last two lines and "then watch us when it's not.", ends the bridge on "(choir) In the coming months!", and drops the Board's and the Lawyer's final-chorus ad-libs. Suno's page is what was submitted, so these aren't lyric edits by the human. The tag may instead track what Suno sang, so it is a lead for the as-sung lyrics at C3, not their source. (Not Yet's MP3 tag also differed from its page, there by one repeated line.)
