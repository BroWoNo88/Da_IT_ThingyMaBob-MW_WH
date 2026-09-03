import mido

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

# Standard MIDI Note numbers mapped to pitch names
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def midi_to_note_name(midi_number):
    """Converts a MIDI note number (0-127) to a string like 'C4' or 'F#5'."""
    note = NOTE_NAMES[midi_number % 12]
    octave = (midi_number // 12) - 1
    return f"{note}{octave}"


def ticks_to_fraction(ticks, ticks_per_beat):
    """Converts MIDI ticks into a standard musical fraction string (1/16, 1/8, 1/4, etc.)."""
    quarter_notes = ticks / ticks_per_beat
    whole_notes = quarter_notes / 4.0

    grid_units = max(1, round(whole_notes * 16))

    numerator = grid_units
    denominator = 16

    common_divisor = gcd(numerator, denominator)
    num = numerator // common_divisor
    den = denominator // common_divisor

    if den == 1:
        return f"{num}"
    return f"{num}/{den}"


def list_tracks(mid):
    """Print every track with its index, name (if any), and note count,
    so you can match it up against what an online viewer shows you."""
    print(f"\nFile has {len(mid.tracks)} track(s) (indices 0 to {len(mid.tracks) - 1}):\n")
    for i, track in enumerate(mid.tracks):
        name = None
        note_count = 0
        for msg in track:
            if msg.type == "track_name" and name is None:
                name = msg.name
            if msg.type == "note_on" and msg.velocity > 0:
                note_count += 1
        label = name if name else "(unnamed)"
        print(f"  [{i}] {label} - {note_count} note-on events")
    print()


def list_channels(track):
    """Print every channel used within a track, with its note count and
    program (instrument) number if set. Useful for Type 0 files where
    everything lives in one track and instruments are split by channel."""
    counts = {}
    programs = {}
    for msg in track:
        if msg.type == "note_on" and msg.velocity > 0:
            counts[msg.channel] = counts.get(msg.channel, 0) + 1
        if msg.type == "program_change":
            programs[msg.channel] = msg.program

    print(f"\nChannels found in this track:\n")
    for ch in sorted(counts):
        prog = programs.get(ch)
        prog_str = f", program {prog}" if prog is not None else ""
        print(f"  [channel {ch}] {counts[ch]} note-on events{prog_str}")
    print()

    return sorted(counts.keys())


def parse_midi_to_script_format(midi_file_path, track_index, channel=None):
    """If channel is None, every channel in the track is included (old
    behaviour). If channel is an int (0-15), only note_on/note_off
    messages on that channel are used to build song_notes - rests are
    still measured against the full track's timeline, since a rest on
    one instrument is only a "gap" for that instrument."""
    mid = mido.MidiFile(midi_file_path)
    ticks_per_beat = mid.ticks_per_beat

    if track_index < 0 or track_index >= len(mid.tracks):
        print(
            f"Track index {track_index} out of range "
            f"(valid range is 0 to {len(mid.tracks) - 1}). Aborting."
        )
        return

    track = mid.tracks[track_index]

    song_notes = list()
    active_notes = {}
    current_tick = 0
    last_event_tick = 0

    for msg in track:
        current_tick += msg.time

        if msg.type not in ("note_on", "note_off"):
            continue
        if channel is not None and getattr(msg, "channel", None) != channel:
            continue

        if msg.type == "note_on" and msg.velocity > 0:
            if not active_notes and (current_tick > last_event_tick):
                rest_duration = current_tick - last_event_tick
                rest_frac = ticks_to_fraction(rest_duration, ticks_per_beat)
                song_notes.append((None, rest_frac))

            active_notes[msg.note] = current_tick
            last_event_tick = current_tick

        elif msg.type == "note_off" or (
            msg.type == "note_on" and msg.velocity == 0
        ):
            if msg.note in active_notes:
                start_tick = active_notes.pop(msg.note)
                duration_ticks = current_tick - start_tick

                note_name = midi_to_note_name(msg.note)
                frac_len = ticks_to_fraction(duration_ticks, ticks_per_beat)

                song_notes.append((note_name, frac_len))
                last_event_tick = current_tick

    if not song_notes:
        print(f"Warning: track {track_index} produced 0 notes. "
              f"You may have picked a meta/control track rather than the melody.")

    with open("output.txt", "w") as f:
        f.write("song_notes = [\n    ")
        for note, length in song_notes:
            f.write(f"[{note!r}, {length!r}], ")
        f.write("\n]")

    print(f"Wrote {len(song_notes)} entries to output.txt")


# --- Usage Example ---
midi_path = "song.mid"
mid = mido.MidiFile(midi_path)
list_tracks(mid)

ti = int(input("Which track index (see list above)?\n> "))

available_channels = list_channels(mid.tracks[ti])

if len(available_channels) > 1:
    ch_input = input(
        "Multiple channels found. Enter a channel number to isolate one "
        "instrument, or press Enter to include all channels in this track.\n> "
    ).strip()
    channel = int(ch_input) if ch_input else None
else:
    channel = None  # only one channel present, no need to filter

parse_midi_to_script_format(midi_path, ti, channel)