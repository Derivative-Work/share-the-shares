#!/usr/bin/env bash
# The v1.0 release (the human, 2026-11-19: "Prepare the release"), the way the series' earlier videos made theirs: the
# upload files with their captions and thumbnails, the five Shorts, and the audio git doesn't hold. Staged in release/
# (git-ignored; the videos hard-linked), then a draft GitHub release of this repository.
#
#   share_the_shares_1920x1080.mov          the main video: the human's final cut from DaVinci Resolve, the YouTube upload
#                                           file (deliverables/final_cut/, copied from the human's export)
#   share_the_shares_short_<n>_*.mp4        the five Shorts, 1080x1920 (scripts/shorts.py)
#   share_the_shares.en.srt                 the main video's English subtitles (scripts/subtitles.py)
#   share_the_shares_thumbnails.zip         the thumbnail options (scripts/thumbnails.py) and their contact sheets
#   share_the_shares_call_page.html         the call page, one file with its backgrounds (scripts/build_call_page.py)
#   inputs.tar   the audio none of which can be regenerated: Suno's take (audio/track) and stems as downloaded (the zip;
#                audio/stems is that zip unpacked), the muzak cover (audio/muzak), the post-filtered audio
#                (audio/master/postfilter_preview; the post-filter model is private) and the post-roll (audio/postroll)
#   SHA256SUMS   for every file above; the files inside the tar are in MANIFEST.sha256
# Left out: the 4K ProRes master and its sections (24 GB, over GitHub's 2 GiB per-file limit; they regenerate from
# scripts/final_queue.sh); the human's raw live footage and the DaVinci project (the human's); renders, frames, live
# plates and excerpts, which regenerate from the logged commands; the public-domain engraving sources (re-downloadable,
# listed in sources.tsv); and the Claude Code session transcript.
#
# Usage: scripts/release.sh [--draft <notes.md>]   (stages release/; --draft also creates the draft release v1.0 with gh)
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
TAG=v1.0
R=release
P=share_the_shares
mkdir -p "$R"
rm -f "$R"/*.mov "$R"/*.mp4 "$R"/*.srt "$R"/*.zip "$R"/*.html "$R"/*.tar "$R"/SHA256SUMS
ln deliverables/final_cut/${P}_1920x1080.mov "$R/${P}_1920x1080.mov"
for f in deliverables/shorts/${P}_short_*.mp4; do ln "$f" "$R/$(basename "$f")"; done
cp deliverables/${P}.en.srt "$R/${P}.en.srt"
(cd deliverables/thumbnails && zip -q -X "../../$R/${P}_thumbnails.zip" *.jpg)
cp deliverables/call_page/call_page.html "$R/${P}_call_page.html"
tar -cf "$R/inputs.tar" audio/track "audio/Share the Shares Stems.zip" audio/muzak audio/master/postfilter_preview \
  audio/postroll
FILES=("${P}_1920x1080.mov" $(cd "$R" && ls ${P}_short_*.mp4) "${P}.en.srt" "${P}_thumbnails.zip" "${P}_call_page.html"
       inputs.tar)
(cd "$R" && sha256sum "${FILES[@]}" > SHA256SUMS)
for f in "$R"/*; do
  (( $(stat -c %s "$f") < 2147483648 )) || { echo "$f is over 2 GiB" >&2; exit 1; }
done
# every file in the tar as the manifest lists it, and still matching it
tar -tf "$R/inputs.tar" | grep -v '/$' | while IFS= read -r f; do
  grep -qF "  $f" MANIFEST.sha256 || { echo "$f: not in MANIFEST.sha256" >&2; exit 1; }
done
(grep -F -e "  audio/track/" -e "  audio/Share the Shares Stems.zip" -e "  audio/muzak/" -e "  audio/master/postfilter_preview/" \
  -e "  audio/postroll/" -e "  deliverables/final_cut/" -e "  deliverables/shorts/" MANIFEST.sha256 | sha256sum -c --quiet) \
  || { echo "MANIFEST.sha256 is stale" >&2; exit 1; }
ls -l "$R"
cat "$R/SHA256SUMS"
if [[ ${1:-} == --draft ]]; then
  gh release create "$TAG" --draft --target main --title "Share the Shares v1.0" --notes-file "$2" \
    $(for f in "${FILES[@]}" SHA256SUMS; do echo "$R/$f"; done)
fi
