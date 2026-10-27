"""C3: the timing map, the clock every later step reads.

Joins the beats and bars (scripts/meter.py), the aligned words (scripts/align_words.py), the key change
(scripts/key_windows.py), the drum onsets (scripts/stem_envelopes.py) and the brief's shot list (docs/brief.md) into
timing/timing_map.json and a readable timing/timing_map.md. Times are seconds of the Suno mix; frames are at the
style spec's fps (config/look.json).

Shot cues (brief: "Cues are lyric lines, not timestamps"): each shot's cue is resolved in reading order, searching
forward from the previous shot. An ordinal cue (The third "share the shares") is the n'th time the phrase is sung
after the previous shot, which places an insert inside a long line. A quoted cue is matched to the first line after that point holding most of its
words, and the shot starts at the first matched word. Event cues ("First piano chord", "The key change...", "The
downbeat after the chorus", "Last chord of the chorus", "The next line") are computed. The shots after the audio
ends (S45-S48) and the pre-roll (S01) get no time. A cue that can't be found (an ad-lib Suno didn't sing) is listed
for the ear check. config/shot_holds.json moves a shot's start off its cue (the human's notes), so the shot before
holds longer.

Usage: .venv/bin/python -I scripts/timing_map.py  ->  timing/timing_map.json, timing/timing_map.md, config/shot_anchors.json
"""
import json
import re
import sys
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from song import STEM, TRACK  # noqa: E402

FPS = json.loads(Path("config/look.json").read_text())["fps"]
HOLDS = {k: v for k, v in json.loads(Path("config/shot_holds.json").read_text()).items() if not k.startswith("_")}
ORDINALS = {"first": 1, "second": 2, "third": 3, "fourth": 4}
ORDINAL = re.compile(r"the (first|second|third|fourth) \"")


def fr(t):
    return None if t is None else int(round(t * FPS))


def norm(s):
    return re.sub(r"[^a-z0-9' ]", " ", s.lower().replace("’", "'")).split()


def shot_rows():
    rows = []
    for line in Path("docs/brief.md").read_text().splitlines():
        m = re.match(r"\| (S\d\d[a-z]?) \| (.*?) \| (.*?) \| (.*?) \|$", line)
        if m:
            rows.append({"id": m.group(1), "cue": m.group(2), "picture": m.group(3), "source": m.group(4)})
    return rows


def first_piano():
    y, sr = librosa.load(STEM.format("Keyboard"), sr=22050, mono=True)
    on = librosa.onset.onset_detect(y=y, sr=sr, units="time", backtrack=True)
    return float(on[0]) if len(on) else 0.0


def main():
    B = json.loads(Path("timing/beats.json").read_text())
    beats, down = np.array(B["beats"]), B["downbeat_beats"]
    lines = json.loads(Path("timing/words.json").read_text())["lines"]
    keys = json.loads(Path("timing/keys.json").read_text())
    drums = json.loads(Path("timing/drum_onsets.json").read_text())["onsets"]
    dur = sf.info(TRACK).duration
    bars = []
    for i, k in enumerate(down):
        end_b = down[i + 1] if i + 1 < len(down) else len(beats)
        nb = end_b - k
        span = (beats[end_b] if end_b < len(beats) else beats[-1] + np.median(np.diff(beats))) - beats[k]
        bars.append({"n": i + 1, "beat": int(k), "start": round(float(beats[k]), 4), "beats": int(nb),
                     "bpm": round(60 * nb / span, 1), "frame": fr(beats[k])})
    dts = np.array([b["start"] for b in bars])
    sections = []
    for ln in lines:
        if not sections or ln["section"] != sections[-1]["name"]:
            sections.append({"name": ln["section"], "singer": ln["singer"], "stem": ln["stem"], "start": ln["start"]})
        sections[-1]["end"] = ln["end"]
    for s in sections:
        s["frame"] = fr(s["start"])
    for ln in lines:
        ln["start_frame"], ln["end_frame"] = fr(ln["start"]), fr(ln["end"])
        for w in ln["words"]:
            w["start_frame"], w["end_frame"] = fr(w["start"]), fr(w["end"])
    sec = {s["name"]: s for s in sections}
    kc = keys["key_change"]
    kc_down = kc.get("beat", float(dts[np.argmin(np.abs(dts - kc["t"]))]))  # the beat it lands on (not a downbeat)
    ch2_end = sec["Chorus 2"]["end"]
    # The music must cut before the generated verse 3's first word (its pickup comes before the next downbeat), so the
    # cut is the beat before that word, not the downbeat after the chorus (proposal for the ear check).
    v3 = sec["Verse 3"]["start"]
    after_ch2 = float(beats[beats < v3 - 0.05][-1])
    last_ch2 = float(dts[dts <= ch2_end][-1])
    live = {"start": after_ch2, "end": sec["Bridge"]["start"],
            "note": "S29-S30: the music cuts at the flip; the human's live take replaces the generated verse 3"}
    events = {"first piano chord": first_piano(), "the key change": kc_down, "the downbeat after the chorus": after_ch2,  # see v3
              "last chord of the chorus": last_ch2}
    shots, cursor, prev_line, unresolved = [], 0.0, None, []
    for r in shot_rows():
        cue, t, line_id, how = r["cue"], None, None, None
        low = cue.lower()
        quoted = re.findall(r'"([^"]+)"', cue)
        ev = next((k for k in events if low.startswith(k)), None)
        if r["picture"].startswith("Retired"):
            how = "retired"  # an ID that no longer appears (IDs never change: removals retire theirs)
        elif r["id"] == "S01" or low in ("silence", "hold music", "after the hang-up", "last"):
            how = "outside the audio" if r["id"] != "S01" else "pre-roll"
        elif ev:
            t, how = events[ev], "event"
        elif low == "the next line" and prev_line is not None:
            # the moment the previous cue's line ends (in the brief, the line after the ad-lib)
            t, line_id, how = prev_line["end"], prev_line["id"], "end of the previous cue's line"
        elif quoted and ORDINAL.match(low):
            # "The third "share the shares"": the n'th time the phrase is sung after the previous shot, inside lines
            n = ORDINALS[ORDINAL.match(low).group(1)]
            want = norm(quoted[0])
            flat = [(w, ln) for ln in lines for w in ln["words"] if w["start"] >= cursor - 0.01]
            toks = [norm(w["w"]) for w, _ in flat]
            hits = [i for i in range(len(flat) - len(want) + 1)
                    if [t[0] if t else "" for t in toks[i:i + len(want)]] == want]
            if len(hits) >= n:
                w, ln = flat[hits[n - 1]]
                prev_line = ln
                t, line_id, how = w["start"], ln["id"], f"lyric ({n} occurrence after the previous shot)"
            else:
                unresolved.append(r["id"])
                how = "NOT FOUND in the as-sung lyrics"
        elif quoted:
            want = norm(quoted[0].split(" through ")[0])
            best = None
            for ln in lines:
                if ln["end"] < cursor - 0.01:
                    continue
                toks = [norm(w["w"]) for w in ln["words"]]
                flat = [x for tk in toks for x in tk]
                hit = sum(1 for w in want if w in flat) / len(want)
                if hit >= 0.75:
                    # the first word of the cue that is sung here (a cue may open with words Suno dropped), at or after
                    # the cursor
                    wi = next((i for i, tk in enumerate(toks) if set(tk) & set(want) and ln["words"][i]["start"] >= cursor - 0.01), None)
                    if wi is not None:
                        if best is None:
                            best = (ln, ln["words"][wi]["start"], wi)
                        elif wi == 0 and best[2] > 0 and ln["start"] - best[1] < 4.0:
                            best = (ln, ln["words"][wi]["start"], wi)  # a line that opens with the cue beats one ending in it
                            break
                        else:
                            break
            if best:
                prev_line = best[0]
                t, line_id, how = best[1], best[0]["id"], "lyric"
            else:
                unresolved.append(r["id"])
                how = "NOT FOUND in the as-sung lyrics"
        if r["id"] in HOLDS and t is not None:
            how += f" (held: starts {HOLDS[r['id']]['t'] - t:+.2f} s off its cue, config/shot_holds.json)"
            t = HOLDS[r["id"]]["t"]
        if t is not None:
            cursor = t
        shots.append({**r, "t": None if t is None else round(t, 3), "frame": fr(t), "line": line_id, "how": how,
                      "downbeat": None if t is None else round(float(dts[np.argmin(np.abs(dts - t))]), 4)})
    Path("config/shot_anchors.json").write_text(json.dumps({
        "_doc": "Shot anchors (scripts/timing_map.py): each brief cue resolved to the Suno mix's clock.",
        "shots": {s["id"]: {"t": s["t"], "frame": s["frame"], "line": s["line"]} for s in shots},
        "unresolved": unresolved}, indent=1) + "\n")
    tm = {"fps": FPS, "duration_s": round(dur, 3), "duration_frames": fr(dur), "audio": TRACK, "meter": "4/4",
          "beats": B["beats"], "downbeat_beats": down, "bars": bars, "sections": sections, "lines": lines,
          "shots": shots, "drum_onsets": drums, "live_verse": live,
          "key_change": {"t": kc_down, "detected_t": kc.get("t_fine", kc["t"]), "from": kc["before"], "to": kc["after"],
                         "semitones": kc["semitones"]},
          "keys": [{"t": 0.0, "key": kc["before"]}, {"t": kc_down, "key": kc["after"]}]}
    Path("timing/timing_map.json").write_text(json.dumps(tm) + "\n")
    L = ["# Timing map", "", f"C3. Generated by `scripts/timing_map.py`. {FPS} fps; {dur:.2f} s ({fr(dur)} frames) of the "
         f"Suno mix; 4/4, {len(bars)} bars at a median {np.median([b['bpm'] for b in bars]):.1f} bpm. Key change "
         f"{kc['before']} → {kc['after']} ({kc['semitones']} semitone) on the beat at {kc_down:.2f} s.", "",
         "## Sections", "", "| Section | Singer | Stem | Start (s) | End (s) |", "| --- | --- | --- | --- | --- |"]
    L += [f"| {s['name']} | {s['singer']} | {s['stem']} | {s['start']:.2f} | {s['end']:.2f} |" for s in sections]
    L += ["", f"The live verse: {live['start']:.2f}–{live['end']:.2f} s ({live['note']}).", "",
          "## Shots", "", "| ID | Cue | t (s) | Frame | Line | How |", "| --- | --- | --- | --- | --- | --- |"]
    for s in shots:
        L.append(f"| {s['id']} | {s['cue']} | {'' if s['t'] is None else f'{s[chr(116)]:.2f}'} | "
                 f"{'' if s['frame'] is None else s['frame']} | {s['line'] or ''} | {s['how']} |")
    irregular = [b for b in bars if b["beats"] != 4]
    L += ["", "## Bars that are not 4 beats (for the ear check)", "", "| Bar | Start (s) | Beats |", "| --- | --- | --- |"]
    L += [f"| {b['n']} | {b['start']:.2f} | {b['beats']} |" for b in irregular]
    L += ["", "## Words with low alignment confidence (score < 0.3)", ""]
    low = [f"{ln['id']} {w['w']} ({w['score']})" for ln in lines for w in ln["words"] if w["score"] < 0.3]
    L += [", ".join(low)]
    Path("timing/timing_map.md").write_text("\n".join(L) + "\n")
    print(f"{len(bars)} bars, {len(lines)} lines, {len(shots)} shots; unresolved {unresolved}; live {live['start']:.2f}-"
          f"{live['end']:.2f}; key change {kc_down:.2f}")


if __name__ == "__main__":
    main()
