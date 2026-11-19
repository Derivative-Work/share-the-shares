"""English subtitles (SRT) for the upload: the lyrics line by line (timing/timing_map.json), "♪" on the sung lines,
plus a few sound cues (the music stopping at S29, the dial tones, the ring and the hold music in the post-roll).

The human cuts the final video (2026-11-18), and the cut leaves song time in three places: the music stops at S29 and
the live verse runs at its own length, the bridge comes back when the file is reopened (S31), and the phone call
(S45-S46) is live. So the lines are placed by anchors, each a time in the cut (seconds, or h:mm:ss.ms / m:ss.ms):
  --verse T          when the live verse's first line starts ("They call me a specific population"); its eight lines
                     keep the generated take's spacing from there. Or --verse-lines with all eight starts.
  --bridge T         when "And it's real, it isn't nothing" starts; everything from the bridge to the song's end
                     (including "do I get a say?", S40) keeps the master's spacing from there.
  --postroll T       when the song ends (S45 starts: the phone is picked up); the dial, ring and hold music follow at
                     config/postroll.json's times, the hold music running to --end.
  --end T            the cut's last frame.
With no anchors it is the master's own timing (deliverables/final_4k, song time = video time).
Verse 3 is written as the brief has it ("pledged"; the generated take sang "spent", before the audit): --spent if the
live take sings "spent".
Usage: .venv/bin/python -I scripts/subtitles.py [OUT.srt] [--verse T | --verse-lines T x8] [--bridge T]
       [--postroll T] [--end T] [--spent]     (default OUT: deliverables/share_the_shares.en.srt)
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TM = json.loads((ROOT / "timing/timing_map.json").read_text())
PR = json.loads((ROOT / "config/postroll.json").read_text())
PH = json.loads((ROOT / "config/c4_shots.json").read_text())["placeholders"]
SHOT = {s["id"]: s["t"] for s in TM["shots"] if s["t"] is not None}
SPOKEN = {"L01", "L02", "L03", "L04", "L72"}
VERSE = [f"L{n}" for n in range(45, 53)]
MASTER_END = TM["duration_s"] + sum(PH[s]["after_s"] for s in ("S45", "S46", "S47", "S48"))  # 328.33


def secs(v):
    p = [float(x) for x in v.split(":")]
    return sum(x * 60 ** i for i, x in enumerate(reversed(p)))


def stamp(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def cues(a):
    lines = {ln["id"]: ln for ln in TM["lines"]}
    v0 = lines["L45"]["start"]
    b0 = lines["L53"]["start"]
    vshift = (secs(a.verse) - v0) if a.verse else 0.0
    bshift = (secs(a.bridge) - b0) if a.bridge else 0.0
    end_song = secs(a.postroll) if a.postroll else TM["duration_s"] + bshift
    end = secs(a.end) if a.end else MASTER_END - TM["duration_s"] + end_song
    vstarts = [secs(x) for x in a.verse_lines] if a.verse_lines else None

    out = [(0.12, 2.6, "[electric piano]")]
    for ln in TM["lines"]:
        i, s, e, text = ln["id"], ln["start"], ln["end"], ln["text"]
        if i in VERSE:
            if vstarts:
                k = VERSE.index(i)
                s, e = vstarts[k], vstarts[k] + (e - s)
            else:
                s, e = s + vshift, e + vshift
            if i == "L47" and not a.spent:
                text = text.replace("spent", "pledged")
        elif s >= b0:
            s, e = s + bshift, e + bshift
        out.append((s, e, text if i in SPOKEN else "♪ " + text))
    # S29: the player exits and the music stops (the downbeat after chorus 2); the session holds before the call.
    # Only in a cut with the live verse: the master plays the generated verse straight through
    if a.verse or vstarts:
        out.append((SHOT["S30"], SHOT["S30"] + 2.0, "[music stops]"))
    # the post-roll (scripts/postroll_audio.py's times, from the song's end)
    d = PR["dial"]
    dial_end = d["start"] + len(PR["number"]) * (d["tone"] + d["gap"])
    ring = dial_end + PR["ring"]["after_dial"]
    out.append((end_song + d["start"], end_song + dial_end, "[phone dialing]"))
    out.append((end_song + ring, end_song + ring + PR["ring"]["length"], "[ringing]"))
    hold = end_song + PH["S45"]["after_s"] - PR["muzak"]["fade_in"]
    out.append((hold, end, "[hold music: “Share the Shares” as muzak]"))
    out.sort()
    # readable: at least 1.2 s and 0.3 s longer than sung where there's room; never overlapping the next cue
    done = []
    for k, (s, e, t) in enumerate(out):
        nxt = out[k + 1][0] if k + 1 < len(out) else end
        e = max(e + 0.3, s + 1.2)
        done.append((s, min(e, nxt - 0.04) if nxt > s else e, t))
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=str(ROOT / "deliverables/share_the_shares.en.srt"))
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--verse")
    g.add_argument("--verse-lines", nargs=8)
    ap.add_argument("--bridge")
    ap.add_argument("--postroll")
    ap.add_argument("--end")
    ap.add_argument("--spent", action="store_true")
    a = ap.parse_args()
    cs = cues(a)
    body = "".join(f"{n}\n{stamp(s)} --> {stamp(e)}\n{t}\n\n" for n, (s, e, t) in enumerate(cs, 1))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(body)
    print(a.out, len(cs), "cues")


if __name__ == "__main__":
    main()
