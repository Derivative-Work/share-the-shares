"""This song's files and stems, in one place for every analysis script."""
TITLE = "Share the Shares"
TRACK = f"audio/track/{TITLE}.wav"  # the Suno mix; timing is built on it (the post-filter does not move timing)
STEM = f"audio/stems/{TITLE} ({{}}).wav"
MIDI = f"audio/stems/midi/{TITLE} ({{}}).mid"
STEMS = ["Vocals", "Backing Vocals", "Keyboard", "Synth", "Guitar", "Bass", "Drums", "Percussion", "Brass", "Strings",
         "Woodwinds", "FX"]
