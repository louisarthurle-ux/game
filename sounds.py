"""
sounds.py - MUSIC and SOUND EFFECTS.

1) MAKING THE SOUNDS
   All sounds are created by this file with maths (sine waves = musical
   notes) and saved as .wav files in the "sounds" folder. You can replace
   any .wav file with your own sound: keep the same file name.

2) PLAYING THE SOUNDS
   Python has no built-in way to play music on every computer, so we try:
       pygame (if installed)  -> best: music + sound effects together
       Windows                -> the Windows media player (no install)
       Mac                    -> afplay (no install)
       Linux                  -> paplay or aplay
       nothing works          -> the game stays silent (no crash)
"""

import math
import random
import shutil
import struct
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

RATE = 22050                                   # samples per second
SOUND_DIR = Path(__file__).resolve().parent / "sounds"


# ===========================================================================
# PART 1: MAKING THE SOUNDS
# ===========================================================================
def note(name):
    """'A4' -> 440.0 Hz. Works for C, C#, D ... B and octaves 1 to 7."""
    names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    midi = names.index(name[:-1]) + 12 * (int(name[-1]) + 1)
    return 440.0 * 2 ** ((midi - 69) / 12)


class Track:
    """An empty piece of audio where we can add notes."""

    def __init__(self, seconds):
        self.samples = [0.0] * int(seconds * RATE)

    def add(self, start, sound):
        """Add a list of samples, starting at `start` seconds."""
        first = int(start * RATE)
        for i, value in enumerate(sound):
            if first + i < len(self.samples):
                self.samples[first + i] += value

    def save(self, path, volume=1.0):
        peak = max(1e-9, max(abs(v) for v in self.samples))
        scale = min(1.0, 0.9 / peak) * volume * 32767
        data = b"".join(struct.pack("<h", int(v * scale)) for v in self.samples)
        with wave.open(str(path), "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(RATE)
            f.writeframes(data)


# --- instruments: each one returns a list of samples ----------------------
def piano(freq, dur, vol=0.3, decay=3.0):
    """A soft electric piano: sine wave + a bit of the octave, fading out."""
    out = []
    for i in range(int(dur * RATE)):
        t = i / RATE
        env = math.exp(-decay * t) * min(1.0, t * 200)
        out.append(vol * env * (math.sin(2 * math.pi * freq * t)
                                + 0.3 * math.sin(4 * math.pi * freq * t)))
    return out


def bass(freq, dur, vol=0.4):
    out = []
    for i in range(int(dur * RATE)):
        t = i / RATE
        env = math.exp(-2.5 * t) * min(1.0, t * 300)
        out.append(vol * env * (math.sin(2 * math.pi * freq * t)
                                + 0.15 * math.sin(6 * math.pi * freq * t)))
    return out


def buzzy(freq, dur, vol=0.3, vibrato=0.0, slide=0.0):
    """A rough 'trombone' sound (used for the sad CHAOS sound)."""
    out, phase = [], 0.0
    for i in range(int(dur * RATE)):
        t = i / RATE
        f = freq * (1 + slide * t) * (1 + vibrato * math.sin(2 * math.pi * 6 * t))
        phase += 2 * math.pi * f / RATE
        env = min(1.0, t * 30) * min(1.0, (dur - t) * 8)
        out.append(vol * env * sum(math.sin(k * phase) / k for k in range(1, 7)))
    return out


def noise(dur, vol=0.3, rng=random.Random(7)):
    out, last = [], 0.0
    for i in range(int(dur * RATE)):
        last = 0.6 * last + 0.4 * rng.uniform(-1, 1)    # a softer noise
        out.append(vol * last * min(1.0, (dur - i / RATE) * 20))
    return out


def tick(vol=0.25):
    """A clock 'tick' (the game is about being late!)."""
    return [vol * math.sin(2 * math.pi * 2200 * i / RATE) * math.exp(-i / 60)
            for i in range(int(0.03 * RATE))]


# --- the music ------------------------------------------------------------
def make_music_menu(path):
    """Hold music. The kind you hear for 45 minutes on the phone."""
    beat = 0.625                                       # 96 beats per minute
    chords = [["C4", "E4", "G4", "B4"], ["A3", "C4", "E4", "G4"],
              ["F3", "A3", "C4", "E4"], ["G3", "B3", "D4", "F4"]] * 2
    roots = ["C2", "A1", "F2", "G2"] * 2
    melody = [("E5", 0, 1.5), ("D5", 1.5, 0.5), ("C5", 2, 2),
              ("C5", 4, 1.5), ("B4", 5.5, 0.5), ("A4", 6, 2),
              ("A4", 8, 1), ("C5", 9, 1), ("F5", 10, 2),
              ("E5", 12, 1), ("D5", 13, 1), ("G4", 14, 2),
              ("E5", 16, 1.5), ("D5", 17.5, 0.5), ("C5", 18, 2),
              ("C5", 20, 1.5), ("B4", 21.5, 0.5), ("A4", 22, 2),
              ("A4", 24, 1), ("C5", 25, 1), ("F5", 26, 2),
              ("D5", 28, 1), ("F#5", 29, 1), ("C5", 30, 2)]   # one wrong note :)
    track = Track(32 * beat)
    for bar, chord in enumerate(chords):
        for step in range(8):                          # arpeggio in 8th notes
            freq = note(chord[[0, 1, 2, 3, 2, 1, 2, 3][step]])
            track.add((bar * 4 + step / 2) * beat, piano(freq, 0.6, 0.10, 4.0))
        for b in (0, 2):
            track.add((bar * 4 + b) * beat, bass(note(roots[bar]), 1.2))
    for name, start, length in melody:
        track.add(start * beat, piano(note(name), length * beat + 0.3, 0.18, 1.5))
    track.save(path, volume=0.55)


def make_music_game(path):
    """Nervous office music, with a clock ticking (you are late!)."""
    beat = 0.7                                         # about 86 bpm
    chords = [["A3", "C4", "E4"], ["F3", "A3", "C4"],
              ["D3", "F3", "A3"], ["E3", "G#3", "B3"]] * 2
    roots = ["A1", "F1", "D2", "E2"] * 2
    track = Track(32 * beat)
    for bar, chord in enumerate(chords):
        for step in range(8):                          # short nervous notes
            freq = note(chord[[0, 1, 2, 1, 0, 1, 2, 1][step]]) * 2
            track.add((bar * 4 + step / 2) * beat, piano(freq, 0.25, 0.09, 12.0))
        for b in range(4):
            track.add((bar * 4 + b) * beat, tick(0.08 if b % 2 else 0.12))
        track.add(bar * 4 * beat, bass(note(roots[bar]), 2.4, 0.45))
        track.add((bar * 4 + 2.5) * beat, bass(note(roots[bar]), 0.6, 0.3))
    track.save(path, volume=0.5)


# --- the sound effects ----------------------------------------------------
def make_effects(folder):
    t = Track(0.05)
    t.add(0, piano(1320, 0.05, 0.3, 60))
    t.save(folder / "blip.wav", 0.35)                  # new line of dialogue

    t = Track(0.12)
    t.add(0, piano(880, 0.12, 0.3, 30))
    t.save(folder / "click.wav", 0.5)                  # menu buttons

    t = Track(0.3)
    t.add(0, piano(note("E5"), 0.2, 0.3, 15))
    t.add(0.08, piano(note("B5"), 0.22, 0.3, 12))
    t.save(folder / "select.wav", 0.6)                 # you made a choice

    t = Track(2.0)                                     # +1 CHAOS: sad trombone
    for i, name in enumerate(["G3", "F#3", "F3"]):
        t.add(i * 0.35, buzzy(note(name), 0.4, 0.3))
    t.add(1.05, buzzy(note("E3"), 0.9, 0.3, vibrato=0.03))
    t.save(folder / "chaos.wav", 0.7)

    t = Track(0.7)                                     # Mayeul writes
    for i in range(5):
        t.add(i * 0.13, noise(0.1, 0.4))
    t.save(folder / "scribble.wav", 0.45)

    t = Track(2.2)                                     # calm ending
    for i, name in enumerate(["C5", "E5", "G5"]):
        t.add(i * 0.15, piano(note(name), 1.5, 0.25, 2.5))
    for name in ("C4", "E4", "G4", "C5"):
        t.add(0.5, piano(note(name), 1.7, 0.2, 2.0))
    t.save(folder / "ending_calm.wav", 0.7)

    t = Track(2.2)                                     # medium: 'ta-da'... ish
    for i, name in enumerate(["C5", "E5", "G5"]):
        t.add(i * 0.12, piano(note(name), 0.4, 0.25, 5))
    for name in ("G#3", "C4", "D#4", "G#4"):           # an unexpected chord
        t.add(0.42, piano(note(name), 1.7, 0.22, 2.0))
    t.save(folder / "ending_medium.wav", 0.7)

    t = Track(2.6)                                     # wild: total chaos
    names = ["C4", "E4", "G4", "C5", "E5", "G5", "C6", "G5", "D#5", "C5", "F#4", "C4"]
    for i, name in enumerate(names):
        t.add(i * 0.07, piano(note(name), 0.3, 0.25, 8))
    for name in ("C3", "F#3", "C4", "C#4", "G4"):     # a horrible cluster
        t.add(0.9, buzzy(note(name), 1.4, 0.12, vibrato=0.02))
    t.add(0.9, noise(1.2, 0.3))
    t.save(folder / "ending_wild.wav", 0.7)


MAKERS = {"music_menu.wav": make_music_menu, "music_game.wav": make_music_game}
EFFECTS = ["blip.wav", "click.wav", "select.wav", "chaos.wav", "scribble.wav",
           "ending_calm.wav", "ending_medium.wav", "ending_wild.wav"]


def sound_folder():
    """Create any missing .wav file. Returns the folder with the sounds."""
    folder = SOUND_DIR
    try:
        folder.mkdir(exist_ok=True)
        (folder / ".write_test").touch()
        (folder / ".write_test").unlink()
    except OSError:                             # read-only folder: use a temp one
        folder = Path(tempfile.gettempdir()) / "job_interview_disaster_sounds"
        folder.mkdir(exist_ok=True)
    for name, maker in MAKERS.items():
        if not (folder / name).exists():
            maker(folder / name)
    if not all((folder / name).exists() for name in EFFECTS):
        make_effects(folder)
    return folder


# ===========================================================================
# PART 2: PLAYING THE SOUNDS
# ===========================================================================
class PygameBackend:
    def __init__(self):
        import pygame
        pygame.mixer.init()
        self.pg, self.cache = pygame, {}

    def effect(self, path):
        if path not in self.cache:
            self.cache[path] = self.pg.mixer.Sound(str(path))
        self.cache[path].play()

    def music(self, path):
        self.pg.mixer.music.load(str(path))
        self.pg.mixer.music.play(-1)                   # -1 = loop forever

    def stop_music(self):
        self.pg.mixer.music.stop()

    def update(self):
        pass

    def close(self):
        self.pg.mixer.quit()


class WindowsBackend:
    """Uses the Windows media system (MCI). Nothing to install."""

    def __init__(self):
        import ctypes
        self.winmm = ctypes.windll.winmm
        self.buffer = ctypes.create_unicode_buffer(64)
        self.slot = 0
        self.looping = False

    def send(self, command):
        return self.winmm.mciSendStringW(command, self.buffer, 63, 0)

    def effect(self, path):
        self.slot = (self.slot + 1) % 6                # up to 6 sounds at once
        alias = f"fx{self.slot}"
        self.send(f"close {alias}")
        if self.send(f'open "{path}" type mpegvideo alias {alias}') == 0:
            self.send(f"play {alias}")

    def music(self, path):
        self.stop_music()
        if self.send(f'open "{path}" type mpegvideo alias music') == 0:
            # "repeat" loops the music; if it doesn't work, update() restarts it
            self.looping = self.send("play music repeat") != 0
            if self.looping:
                self.send("play music")

    def stop_music(self):
        self.send("close music")
        self.looping = False

    def update(self):
        if self.looping:
            self.send("status music mode")
            if self.buffer.value == "stopped":
                self.send("play music from 0")

    def close(self):
        self.send("close all")


class CommandBackend:
    """Mac (afplay) or Linux (paplay / aplay): one small program per sound."""

    def __init__(self, command):
        self.command = command
        self.music_proc, self.music_path = None, None
        self.effects = []

    def start(self, path):
        return subprocess.Popen(self.command + [str(path)], stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)

    def effect(self, path):
        self.effects = [p for p in self.effects if p.poll() is None]
        if len(self.effects) < 6:
            self.effects.append(self.start(path))

    def music(self, path):
        self.stop_music()
        self.music_path = path
        self.music_proc = self.start(path)

    def stop_music(self):
        if self.music_proc:
            self.music_proc.kill()
        self.music_proc, self.music_path = None, None

    def update(self):                                  # loop the music
        if self.music_proc and self.music_proc.poll() is not None:
            self.music_proc = self.start(self.music_path)

    def close(self):
        self.stop_music()
        for proc in self.effects:
            if proc.poll() is None:
                proc.kill()


def pick_backend():
    try:
        return PygameBackend()
    except Exception:
        pass
    if sys.platform.startswith("win"):
        try:
            return WindowsBackend()
        except Exception:
            return None
    for program, extra in (("afplay", []), ("paplay", []), ("aplay", ["-q"])):
        if shutil.which(program):
            return CommandBackend([program] + extra)
    return None


class SoundPlayer:
    """What the game uses: sound.effect("chaos"), sound.music("music_game")..."""

    def __init__(self, enabled=True):
        self.enabled = enabled
        self.current_music = None
        try:
            self.folder = sound_folder()
            self.backend = pick_backend()
        except Exception:                      # sound must NEVER crash the game
            self.backend = None

    def effect(self, name):
        if self.enabled and self.backend:
            self._safe(self.backend.effect, self.folder / f"{name}.wav")

    def music(self, name):
        """Start a looping music (does nothing if it is already playing)."""
        if name == self.current_music:
            return
        self.current_music = name
        if self.enabled and self.backend:
            self._safe(self.backend.music, self.folder / f"{name}.wav")

    def stop_music(self):
        self.current_music = None
        if self.backend:
            self._safe(self.backend.stop_music)

    def toggle(self):
        """Sound ON / OFF."""
        self.enabled = not self.enabled
        music, self.current_music = self.current_music, None
        if self.backend:
            self._safe(self.backend.stop_music)
        if self.enabled and music:
            self.music(music)
        else:
            self.current_music = music
        return self.enabled

    def update(self):
        """Called twice per second by the game (to loop the music)."""
        if self.enabled and self.backend:
            self._safe(self.backend.update)

    def close(self):
        if self.backend:
            self._safe(self.backend.close)

    def _safe(self, function, *args):
        try:
            function(*args)
        except Exception:
            self.backend = None                # something broke: go silent


if __name__ == "__main__":
    # "python sounds.py" re-creates all the sounds (delete the old ones first).
    print("Sounds are in:", sound_folder())
