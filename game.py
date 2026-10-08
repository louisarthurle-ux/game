"""
THE JOB INTERVIEW DISASTER
An interactive "choose your own adventure" story with dark humour.

game.py - THE APP / LAUNCHER. Run this file to play:

    python game.py              -> the graphical game (main menu + HUD)
    python game.py --terminal   -> the simple text version

How the project is organised:
    story.py     all the text (scenes, choices, endings)      = DATA
    engine.py    the rules (Chaos counter, ending rules)       = LOGIC
    game.py      this file: the window, HUD and drawings       = INTERFACE
    terminal.py  the same game in the terminal                 = INTERFACE

The graphics use tkinter, which comes with Python (nothing to install).
Everything is drawn on ONE big Canvas, like a 2D visual novel:

    +-------------------------------------------------------------+
    | HUD: title, track | time, place | choice 2/5, CHAOS meter   |
    +-------------------------------------------------------------+
    |                                                             |
    |        background + characters      (choice buttons)        |
    |                                                             |
    |  [NAME]                                                     |
    |  +-------------------------------------------------------+  |
    |  | dialogue box (text appears letter by letter)          |  |
    +-------------------------------------------------------------+
"""

import json
import math
import random
import sys
from pathlib import Path

try:
    import tkinter as tk
    import tkinter.font as tkfont
    from tkinter import messagebox
except ImportError:          # no graphics on this computer -> text version
    tk = None

from engine import Game, MAX_CHAOS, TOTAL_CHOICES
from story import CHARACTERS, ENDINGS, TRACKS, MENU_QUOTES


# ===========================================================================
# SETTINGS
# ===========================================================================
W, H = 1024, 640                 # window size
HUD_H = 60                       # height of the HUD bar
BOX = (24, 456, 1000, 624)       # dialogue box (left, top, right, bottom)
TYPE_SPEED = 15                  # milliseconds between letters
SAVE_FILE = Path.home() / ".job_interview_disaster_save.json"

COLORS = {
    "bg": "#0f1220", "hud": "#151a2b", "panel": "#171c2e", "panel2": "#20263a",
    "hover": "#2d3552", "border": "#3a4363", "text": "#eef1f8", "muted": "#9aa3bd",
    "accent": "#ffcc4d", "safe": "#3ecf8e", "bold": "#ff5c6c",
    "final": "#ff9f43", "track": "#7fb2ff", "dim": "#1a1d29",
    "calm": "#4fc3f7", "medium": "#ffb74d", "wild": "#ff5370",
}
TYPE_COLORS = {"calm": COLORS["calm"], "medium": COLORS["medium"], "wild": COLORS["wild"]}
SHIRT_COLORS = {"white": "#f2f2ee", "orange": "#ff7a1a", "pink": "#ff8fc7"}


# ===========================================================================
# SMALL HELPERS
# ===========================================================================
def mix(color1, color2, t):
    """Mix two '#rrggbb' colours. t=0 -> color1, t=1 -> color2."""
    a = [int(color1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(color2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def faded(color):
    """A greyer, slightly darker version of a colour (for silent characters)."""
    r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
    grey = round(0.3 * r + 0.59 * g + 0.11 * b)
    return mix(mix(color, f"#{grey:02x}{grey:02x}{grey:02x}", 0.65), COLORS["dim"], 0.3)


def load_unlocked():
    """Read the list of endings the player already found."""
    try:
        return set(json.loads(SAVE_FILE.read_text())["unlocked"])
    except (OSError, ValueError, KeyError, TypeError):
        return set()


def save_unlocked(unlocked):
    try:
        SAVE_FILE.write_text(json.dumps({"unlocked": sorted(unlocked)}))
    except OSError:
        pass  # not a problem: the game still works without saving


# ===========================================================================
# DRAWING: CHARACTERS
# Each character is drawn with simple shapes (ovals, rectangles, lines),
# using the "look" dictionary from story.py.
# ===========================================================================
def draw_person(c, cx, look, outfit, dim=False, lift=0, shirt=None):
    """Draw a character (head and shoulders) centred on x = cx."""
    def col(color):  # characters who are not talking become grey-ish
        return faded(color) if dim else color

    tags = ("stage",)
    hy = 286 - lift          # y of the centre of the head
    r = 50                   # head radius
    top = hy + r + 6         # y of the top of the shoulders
    skin, hair = look["skin"], look["hair"]
    style = look["hair_style"]

    # --- hair that goes BEHIND the head
    if style == "long":
        c.create_oval(cx - r - 10, hy - r - 6, cx + r + 10, hy + r + 70,
                      fill=col(hair), outline="", tags=tags)
    if style == "bun":
        c.create_oval(cx - 24, hy - r - 34, cx + 24, hy - r + 8,
                      fill=col(hair), outline="", tags=tags)

    # --- body
    c.create_oval(cx - 96, top, cx + 96, top + 96, fill=col(outfit), outline="", tags=tags)
    c.create_rectangle(cx - 96, top + 48, cx + 96, BOX[1] + 20, fill=col(outfit),
                       outline="", tags=tags)
    # neck
    c.create_rectangle(cx - 15, hy + r - 16, cx + 15, top + 22,
                       fill=col(mix(skin, "#000000", 0.12)), outline="", tags=tags)

    # --- collar, shirt, tie
    collar = look["collar"]
    if collar in ("tie", "shirt"):
        c.create_polygon(cx - 26, top + 4, cx + 26, top + 4, cx, top + 70,
                         fill=col("#f4f4f4"), outline="", tags=tags)
    if collar == "tie":
        c.create_polygon(cx - 7, top + 12, cx + 7, top + 12, cx + 11, top + 70,
                         cx, top + 84, cx - 11, top + 70,
                         fill=col("#c0392b"), outline="", tags=tags)
    if collar == "collar":
        c.create_polygon(cx - 20, top + 2, cx, top + 22, cx - 4, top + 34, cx - 30, top + 14,
                         fill=col(mix(outfit, "#ffffff", 0.35)), outline="", tags=tags)
        c.create_polygon(cx + 20, top + 2, cx, top + 22, cx + 4, top + 34, cx + 30, top + 14,
                         fill=col(mix(outfit, "#ffffff", 0.35)), outline="", tags=tags)

    # --- the player's shirt has details (the stain, the logo, the DAD text)
    if shirt == "white":
        # the coffee stain shaped like Italy (with Sicily!)
        x, y = cx + 30, top + 40
        boot = [0, 0, 10, -2, 16, 6, 18, 18, 28, 30, 38, 36, 40, 44, 32, 44,
                26, 38, 18, 34, 12, 24, 4, 12]
        pts = [v * 1.2 + (x if i % 2 == 0 else y) for i, v in enumerate(boot)]
        c.create_polygon(pts, fill=col("#8b5a2b"), outline="", smooth=True, tags=tags)
        c.create_oval(x + 14, y + 56, x + 30, y + 64, fill=col("#8b5a2b"), outline="", tags=tags)
    elif shirt == "orange":
        c.create_oval(cx - 34, top + 34, cx + 34, top + 102, fill=col("#ffffff"),
                      outline="", tags=tags)
        c.create_text(cx, top + 68, text="S", font=("Helvetica", 34, "bold"),
                      fill=col("#ff7a1a"), tags=tags)
    elif shirt == "pink":
        c.create_text(cx, top + 62, text="WORLD'S\nBEST DAD", justify="center",
                      font=("Helvetica", 13, "bold"), fill=col("#a3195b"), tags=tags)

    # --- head
    c.create_oval(cx - r, hy - r, cx + r, hy + r, fill=col(skin), outline="", tags=tags)
    # ears
    for side in (-1, 1):
        c.create_oval(cx + side * r - 8, hy - 6, cx + side * r + 8, hy + 16,
                      fill=col(skin), outline="", tags=tags)

    # --- hair on top of the head
    if style in ("short", "messy", "bun", "long"):
        c.create_arc(cx - r - 3, hy - r - 8, cx + r + 3, hy + 14, start=0, extent=180,
                     style="chord", fill=col(hair), outline="", tags=tags)
    if style == "messy":
        for dx in (-30, -8, 14, 34):
            c.create_polygon(cx + dx - 10, hy - r + 4, cx + dx + 4, hy - r - 22,
                             cx + dx + 12, hy - r + 4, fill=col(hair), outline="", tags=tags)
    if style == "bald":
        for side in (-1, 1):
            c.create_oval(cx + side * (r - 4) - 12, hy - 26, cx + side * (r - 4) + 12, hy + 4,
                          fill=col(hair), outline="", tags=tags)
        c.create_arc(cx - 26, hy - r + 6, cx + 6, hy - r + 30, start=60, extent=80,
                     style="arc", outline=col("#ffffff"), width=3, tags=tags)

    # --- cyclist helmet
    if look["accessory"] == "helmet":
        c.create_arc(cx - r - 8, hy - r - 18, cx + r + 8, hy + 22, start=0, extent=180,
                     style="chord", fill=col("#ffde59"), outline="", tags=tags)
        for dx in (-24, 0, 24):
            c.create_line(cx + dx, hy - r - 12, cx + dx, hy - 2, fill=col("#1d1d1d"),
                          width=4, tags=tags)

    # --- eyebrows
    brows = look["brows"]
    ey = hy + 4
    for side in (-1, 1):
        x = cx + side * 18
        if brows == "stern":
            c.create_line(x - 10 * side, ey - 11, x + 10 * side, ey - 19,
                          fill=col("#2a1d14"), width=4, tags=tags)
        elif brows == "worried":
            c.create_line(x - 10 * side, ey - 21, x + 10 * side, ey - 14,
                          fill=col("#2a1d14"), width=4, tags=tags)
        elif brows == "raised_one" and side == 1:
            c.create_arc(x - 11, ey - 30, x + 11, ey - 12, start=20, extent=140,
                         style="arc", outline=col("#2a1d14"), width=4, tags=tags)
        else:
            c.create_line(x - 10, ey - 16, x + 10, ey - 16,
                          fill=col("#2a1d14"), width=4, tags=tags)

    # --- eyes
    eyes = look["eyes"]
    for side in (-1, 1):
        x = cx + side * 18
        if eyes == "half":      # Mayeul's judging eyes
            c.create_line(x - 9, ey - 2, x + 9, ey - 2, fill=col("#1b1b1b"), width=3, tags=tags)
            c.create_oval(x - 4, ey - 1, x + 4, ey + 5, fill=col("#1b1b1b"), outline="", tags=tags)
        elif eyes == "wide":
            c.create_oval(x - 8, ey - 8, x + 8, ey + 8, fill=col("#ffffff"), outline="", tags=tags)
            c.create_oval(x - 3, ey - 3, x + 3, ey + 3, fill=col("#1b1b1b"), outline="", tags=tags)
        else:
            c.create_oval(x - 4, ey - 5, x + 4, ey + 5, fill=col("#1b1b1b"), outline="", tags=tags)

    if look["accessory"] == "glasses":
        for side in (-1, 1):
            x = cx + side * 18
            c.create_oval(x - 13, ey - 12, x + 13, ey + 12, outline=col("#222222"), width=3,
                          tags=tags)
        c.create_line(cx - 5, ey, cx + 5, ey, fill=col("#222222"), width=3, tags=tags)

    # --- mouth
    mouth = look["mouth"]
    my = hy + 28
    if mouth == "big_smile":     # Mr. Hargrove: the smile never moves
        c.create_arc(cx - 24, my - 22, cx + 24, my + 14, start=180, extent=180, style="chord",
                     fill=col("#5a1f1f"), outline="", tags=tags)
        c.create_rectangle(cx - 18, my - 4, cx + 18, my + 1, fill=col("#ffffff"),
                           outline="", tags=tags)
    elif mouth == "smile":
        c.create_arc(cx - 16, my - 18, cx + 16, my + 6, start=200, extent=140, style="arc",
                     outline=col("#5a1f1f"), width=3, tags=tags)
    elif mouth == "frown":
        c.create_arc(cx - 16, my - 2, cx + 16, my + 18, start=20, extent=140, style="arc",
                     outline=col("#5a1f1f"), width=3, tags=tags)
    elif mouth == "worried":
        c.create_line(cx - 14, my, cx - 5, my - 4, cx + 5, my + 2, cx + 14, my - 2,
                      fill=col("#5a1f1f"), width=3, smooth=True, tags=tags)
    elif mouth == "open":
        c.create_oval(cx - 10, my - 8, cx + 10, my + 12, fill=col("#5a1f1f"), outline="",
                      tags=tags)
    else:
        c.create_line(cx - 14, my, cx + 14, my, fill=col("#5a1f1f"), width=3, tags=tags)

    # --- other accessories
    acc = look["accessory"]
    if acc == "notebook":
        c.create_rectangle(cx + 38, top + 46, cx + 86, top + 112, fill=col("#f4e9c8"),
                           outline=col("#b59f6b"), width=2, tags=tags)
        for i in range(4):
            c.create_line(cx + 44, top + 60 + i * 12, cx + 80, top + 60 + i * 12,
                          fill=col("#8aa2c8"), tags=tags)
        c.create_line(cx + 90, top + 40, cx + 70, top + 96, fill=col("#2b2b2b"), width=4,
                      tags=tags)
    elif acc == "phone":
        c.create_rectangle(cx + r - 6, hy - 22, cx + r + 16, hy + 24, fill=col("#222222"),
                           outline=col("#555555"), width=2, tags=tags)
    elif acc == "lanyard":
        c.create_line(cx - 20, top + 6, cx, top + 96, fill=col("#2e86de"), width=4, tags=tags)
        c.create_line(cx + 20, top + 6, cx, top + 96, fill=col("#2e86de"), width=4, tags=tags)
        c.create_rectangle(cx - 18, top + 94, cx + 18, top + 130, fill=col("#d7dbe3"),
                           outline="", tags=tags)
        c.create_text(cx, top + 112, text=look.get("card", "?"), fill=col("#ff7a1a"),
                      font=("Helvetica", 16, "bold"), tags=tags)


def draw_pigeon(c, x, y, s=1.0):
    """The pigeon from the train tracks. It follows you everywhere."""
    t = ("stage",)
    c.create_oval(x - 22 * s, y - 12 * s, x + 18 * s, y + 12 * s, fill="#8d93a3", outline="", tags=t)
    c.create_oval(x + 8 * s, y - 24 * s, x + 26 * s, y - 6 * s, fill="#7a8194", outline="", tags=t)
    c.create_polygon(x + 25 * s, y - 16 * s, x + 33 * s, y - 13 * s, x + 25 * s, y - 11 * s,
                     fill="#e0a030", outline="", tags=t)
    c.create_oval(x + 17 * s, y - 19 * s, x + 21 * s, y - 15 * s, fill="#ff7b2e", outline="", tags=t)
    c.create_line(x - 4 * s, y + 12 * s, x - 6 * s, y + 20 * s, fill="#e0a030", width=2, tags=t)
    c.create_line(x + 6 * s, y + 12 * s, x + 6 * s, y + 20 * s, fill="#e0a030", width=2, tags=t)


def draw_clock(c, x, y, r, hhmm):
    """A wall clock showing the time of the scene (if it is a real time)."""
    t = ("stage",)
    c.create_oval(x - r, y - r, x + r, y + r, fill="#fdfdf8", outline="#333333", width=4, tags=t)
    for i in range(12):
        c.create_text(x + 0.78 * r * _sin(i * 30), y - 0.78 * r * _cos(i * 30), text="·",
                      font=("Helvetica", 10, "bold"), fill="#333333", tags=t)
    if ":" not in hhmm:
        return
    h, m = (int(v) for v in hhmm.split(":"))
    for angle, length, width in ((((h % 12) + m / 60) * 30, 0.5, 4), (m * 6, 0.75, 3)):
        c.create_line(x, y, x + length * r * _sin(angle), y - length * r * _cos(angle),
                      fill="#222222", width=width, capstyle="round", tags=t)


def _sin(deg):
    return math.sin(math.radians(deg))


def _cos(deg):
    return math.cos(math.radians(deg))


# ===========================================================================
# DRAWING: BACKGROUNDS (one function per place)
# ===========================================================================
def bg_station(c, time):
    t = ("stage",)
    c.create_rectangle(-20, -20, W + 20, H + 20, fill="#8fa3b8", outline="", tags=t)
    c.create_rectangle(-20, HUD_H, W + 20, HUD_H + 50, fill="#3b4250", outline="", tags=t)
    for x in range(0, W, 120):
        c.create_line(x, HUD_H + 50, x + 60, HUD_H + 10, fill="#2b313c", width=6, tags=t)
    c.create_rectangle(-20, 420, W + 20, H + 20, fill="#7a7a7a", outline="", tags=t)
    c.create_rectangle(-20, 420, W + 20, 432, fill="#f5c518", outline="", tags=t)
    # departures board
    c.create_rectangle(560, 140, 960, 300, fill="#1d1f24", outline="#444", width=4, tags=t)
    c.create_text(760, 160, text="DEPARTURES", fill="#f5c518", font=("Courier", 16, "bold"), tags=t)
    rows = [("08:47", "CITY CENTRE", "LATE"), ("09:02", "CITY CENTRE", "LATE"),
            ("09:15", "CITY CENTRE", "CANCELLED"), ("09:31", "YOUR FUTURE", "ARRIVED?")]
    for i, (hh, dest, status) in enumerate(rows):
        y = 194 + i * 26
        c.create_text(580, y, anchor="w", text=f"{hh}  {dest}", fill="#ffb347",
                      font=("Courier", 13, "bold"), tags=t)
        c.create_text(940, y, anchor="e", text=status, fill="#ff5c5c",
                      font=("Courier", 13, "bold"), tags=t)
    draw_clock(c, 120, 170, 52, time)
    draw_pigeon(c, 930, 400, 1.2)


def bg_reception(c, time):
    t = ("stage",)
    c.create_rectangle(-20, -20, W + 20, H + 20, fill="#c9bfa8", outline="", tags=t)
    c.create_rectangle(-20, 360, W + 20, 372, fill="#a99d84", outline="", tags=t)
    c.create_rectangle(-20, 470, W + 20, H + 20, fill="#6f6253", outline="", tags=t)
    # the famous sign
    c.create_rectangle(282, 92, 742, 150, fill="#2f3a56", outline="#1e2538", width=4, tags=t)
    c.create_text(512, 121, text="WELCOME TO THE SYNERGIX FAMILY!", fill="#ffffff",
                  font=("Helvetica", 17, "bold"), tags=t)
    c.create_text(720, 166, text="help", fill="#6b6b6b", font=("Courier", 11, "italic"), tags=t)
    # logo
    c.create_oval(40, 92, 100, 152, fill="#ff7a1a", outline="", tags=t)
    c.create_text(70, 122, text="S", fill="#ffffff", font=("Helvetica", 26, "bold"), tags=t)
    c.create_text(110, 112, anchor="w", text="SYNERGIX", fill="#2f3a56",
                  font=("Helvetica", 14, "bold"), tags=t)
    c.create_text(110, 132, anchor="w", text="SOLUTIONS", fill="#2f3a56",
                  font=("Helvetica", 10), tags=t)
    draw_clock(c, 900, 140, 48, time)
    # a dead plant
    c.create_polygon(890, 470, 960, 470, 950, 400, 900, 400, fill="#8a5a3c", outline="", tags=t)
    for dx, dy in ((-30, 330), (-5, 310), (20, 335), (40, 360)):
        c.create_line(925, 400, 925 + dx, dy, fill="#7a5a2a", width=3, smooth=True, tags=t)
        c.create_oval(925 + dx - 8, dy - 4, 925 + dx + 8, dy + 6, fill="#9c7a3c", outline="", tags=t)


def bg_office(c, time, rival=False):
    t = ("stage",)
    wall = "#c48b8b" if rival else "#9fb0c4"
    c.create_rectangle(-20, -20, W + 20, H + 20, fill=wall, outline="", tags=t)
    c.create_rectangle(-20, 470, W + 20, H + 20, fill="#4b5468" if not rival else "#5a3a3a", outline="", tags=t)
    # window with rain
    c.create_rectangle(640, 92, 940, 310, fill="#7d8a99", outline="#e8ecf2", width=8, tags=t)
    c.create_line(790, 92, 790, 310, fill="#e8ecf2", width=6, tags=t)
    for x in range(650, 940, 22):
        for y in (110, 170, 230, 280):
            c.create_line(x, y, x - 6, y + 16, fill="#b8c4d2", width=2, tags=t)
    # poster
    c.create_rectangle(80, 92, 330, 320, fill="#ffffff", outline="#2b2b2b", width=3, tags=t)
    if rival:
        c.create_text(205, 170, text="WE ARE NOT\nA FAMILY.", justify="center",
                      font=("Helvetica", 22, "bold"), fill="#b71c1c", tags=t)
        c.create_text(205, 250, text="WE ARE A TEAM.", font=("Helvetica", 15, "bold"),
                      fill="#2b2b2b", tags=t)
        c.create_text(280, 300, text="also help", font=("Courier", 10, "italic"),
                      fill="#777777", tags=t)
    else:
        c.create_rectangle(92, 104, 318, 266, fill="#5d8cc6", outline="", tags=t)
        c.create_polygon(110, 266, 205, 140, 300, 266, fill="#e8ecf2", outline="", tags=t)
        c.create_polygon(110, 266, 205, 170, 300, 266, fill="#6a7b8c", outline="", tags=t)
        c.create_text(205, 292, text="TEAMWORK", font=("Helvetica", 20, "bold"),
                      fill="#2b2b2b", tags=t)
    # plastic plant
    c.create_rectangle(470, 410, 520, 470, fill="#e0e0e0", outline="", tags=t)
    for dx in (-24, -10, 6, 22):
        c.create_oval(495 + dx - 14, 360, 495 + dx + 14, 420, fill="#3fa34d", outline="", tags=t)


def bg_street(c, time, window_mayeul=False):
    t = ("stage",)
    c.create_rectangle(-20, -20, W + 20, H + 20, fill="#a7c0d6", outline="", tags=t)
    buildings = [(0, 150, 180, "#8e9aaf"), (180, 210, 330, "#a3a9b8"), (330, 120, 520, "#7d8597"),
                 (520, 180, 640, "#99a0ae"), (640, 90, 900, "#5b6170"), (900, 200, 1024, "#8e9aaf")]
    for x0, y0, x1, color in buildings:
        c.create_rectangle(x0, y0, x1, 470, fill=color, outline="", tags=t)
        dark = color == "#5b6170"   # the mysterious grey building
        for wx in range(x0 + 16, x1 - 30, 46):
            for wy in range(y0 + 20, 440, 56):
                c.create_rectangle(wx, wy, wx + 28, wy + 36,
                                   fill="#2b2f3a" if dark else "#dfe8f2", outline="", tags=t)
    if window_mayeul:
        # Mayeul waving from a window on the second floor
        c.create_rectangle(708, 214, 790, 300, fill="#ffe8a3", outline="#2b2f3a", width=4, tags=t)
        c.create_oval(734, 236, 764, 266, fill="#d9a27a", outline="", tags=t)
        c.create_arc(732, 232, 766, 254, start=0, extent=180, style="chord", fill="#1f1611",
                     outline="", tags=t)
        c.create_rectangle(728, 270, 770, 300, fill="#3a3f58", outline="", tags=t)
        c.create_line(770, 280, 784, 236, fill="#d9a27a", width=6, capstyle="round", tags=t)
    c.create_rectangle(-20, 470, W + 20, H + 20, fill="#4a4d55", outline="", tags=t)
    c.create_rectangle(-20, 470, W + 20, 500, fill="#2e9e5b", outline="", tags=t)


def bg_park(c, time):
    t = ("stage",)
    c.create_rectangle(-20, -20, W + 20, H + 20, fill="#bfe3f5", outline="", tags=t)
    c.create_oval(860, 90, 940, 170, fill="#ffe27a", outline="", tags=t)
    c.create_rectangle(-20, 360, W + 20, H + 20, fill="#79b85a", outline="", tags=t)
    for x, s in ((90, 1.0), (300, 0.8), (720, 0.9), (960, 1.1)):
        c.create_rectangle(x - 12 * s, 260, x + 12 * s, 380, fill="#6b4a2e", outline="", tags=t)
        for dx, dy in ((-40, 0), (40, 0), (0, -40), (0, 10)):
            c.create_oval(x + dx * s - 60 * s, 220 + dy * s - 60 * s, x + dx * s + 60 * s,
                          220 + dy * s + 60 * s, fill="#4f9a3f", outline="", tags=t)
    # bench
    c.create_rectangle(140, 380, 880, 400, fill="#8a5a3c", outline="", tags=t)
    c.create_rectangle(140, 410, 880, 428, fill="#8a5a3c", outline="", tags=t)
    draw_pigeon(c, 960, 440, 1.1)


def bg_funeral(c, time):
    t = ("stage",)
    c.create_rectangle(-20, -20, W + 20, H + 20, fill="#4a4458", outline="", tags=t)
    for x in (0, W - 120):
        c.create_rectangle(x, HUD_H, x + 120, 470, fill="#5c2a4a", outline="", tags=t)
    c.create_rectangle(-20, 470, W + 20, H + 20, fill="#2c2733", outline="", tags=t)
    # framed photo of a perfectly healthy grandma (giving a thumbs up)
    c.create_rectangle(442, 90, 582, 240, fill="#d8c8a8", outline="#c9a54a", width=6, tags=t)
    c.create_oval(484, 112, 540, 168, fill="#f1d3c0", outline="", tags=t)
    c.create_arc(480, 104, 544, 150, start=0, extent=180, style="chord", fill="#f2f2f2",
                 outline="", tags=t)
    c.create_rectangle(470, 172, 554, 240, fill="#1b1b1f", outline="", tags=t)
    c.create_text(512, 258, text="R.I.P. (?)", fill="#e8e0f0", font=("Helvetica", 13, "bold"),
                  tags=t)
    c.create_line(442, 90, 472, 120, fill="#000000", width=10, tags=t)
    # flowers
    for x in (180, 300, 724, 844):
        for i, color in enumerate(("#ff6b6b", "#ffd166", "#ffffff", "#c77dff", "#ff9ecd")):
            c.create_oval(x - 40 + i * 16, 330 - (i % 2) * 18, x - 14 + i * 16, 356 - (i % 2) * 18,
                          fill=color, outline="", tags=t)
        c.create_rectangle(x - 6, 350, x + 6, 470, fill="#3e7d3a", outline="", tags=t)


BACKGROUNDS = {
    "station": bg_station,
    "reception": bg_reception,
    "office": bg_office,
    "rivalex": lambda c, time: bg_office(c, time, rival=True),
    "street": bg_street,
    "street_window": lambda c, time: bg_street(c, time, window_mayeul=True),
    "park": bg_park,
    "funeral": bg_funeral,
}


# ===========================================================================
# THE APP
# ===========================================================================
class GameApp:
    def __init__(self, root):
        self.root = root
        root.title("The Job Interview Disaster")
        root.resizable(False, False)
        root.configure(bg=COLORS["bg"])

        self.c = tk.Canvas(root, width=W, height=H, bg=COLORS["bg"], highlightthickness=0)
        self.c.pack()

        # fonts: use nice fonts if the computer has them
        families = set(tkfont.families())
        ui = next((f for f in ("Segoe UI", "Helvetica Neue", "Inter", "Ubuntu",
                               "DejaVu Sans", "Arial") if f in families), "Helvetica")
        serif = next((f for f in ("Georgia", "DejaVu Serif", "Times New Roman")
                      if f in families), "Times")
        self.F = {
            "title": (serif, 36, "bold"), "h1": (serif, 26, "bold"), "h2": (ui, 16, "bold"),
            "text": (ui, 15), "italic": (ui, 15, "italic"), "small": (ui, 11),
            "small_b": (ui, 11, "bold"), "btn": (ui, 14), "btn_b": (ui, 14, "bold"),
            "tiny": (ui, 9, "bold"), "hud_big": (ui, 16, "bold"),
        }

        self.game = Game()
        self.unlocked = load_unlocked()
        self.mode = "menu"        # menu / dialogue / choice / ending / screen
        self.frame = 0            # increases every redraw (stops old animations)
        self.queue = []           # dialogue lines waiting to be shown
        self.when_done = None     # function to call when the queue is empty
        self.stage = None         # the scene or ending currently on screen
        self.typing = False
        self.type_job = None
        self.button_count = 0

        root.bind("<Key>", self.on_key)
        self.c.bind("<Button-1>", self.on_click)
        self.show_menu()

    # ------------------------------------------------------------------
    # BUTTONS (drawn on the canvas, with a hover effect)
    # ------------------------------------------------------------------
    def button(self, x0, y0, x1, y1, text, command, color=None, font=None, fill=None):
        self.button_count += 1
        tag = f"btn{self.button_count}"          # a unique name for this button
        fill = fill or COLORS["panel2"]
        rect = self.c.create_rectangle(x0, y0, x1, y1, fill=fill,
                                       outline=color or COLORS["border"], width=2,
                                       tags=("btn", tag))
        self.c.create_text((x0 + x1) / 2, (y0 + y1) / 2, text=text, fill=COLORS["text"],
                           font=font or self.F["btn_b"], tags=("btn", tag))
        self._hover(tag, rect, fill, command)
        return tag, rect

    def _hover(self, tag, rect, fill, command):
        self.c.tag_bind(tag, "<Enter>", lambda e: (self.c.itemconfig(rect, fill=COLORS["hover"]),
                                                   self.c.config(cursor="hand2")))
        self.c.tag_bind(tag, "<Leave>", lambda e: (self.c.itemconfig(rect, fill=fill),
                                                   self.c.config(cursor="")))
        self.c.tag_bind(tag, "<Button-1>", lambda e: command())

    def clear(self):
        """Erase everything and stop old animations."""
        self.frame += 1
        if self.type_job:
            self.root.after_cancel(self.type_job)
            self.type_job = None
        self.c.delete("all")
        self.c.config(cursor="")

    # ------------------------------------------------------------------
    # LAUNCHER SCREENS: main menu, how to play, endings gallery
    # ------------------------------------------------------------------
    def show_menu(self):
        self.clear()
        self.mode = "menu"
        bg_reception(self.c, "10:25")
        draw_person(self.c, 650, CHARACTERS["you"]["look"], SHIRT_COLORS["white"],
                    dim=True, shirt="white")
        draw_person(self.c, 860, CHARACTERS["mayeul"]["look"], "#3a3f58", lift=10)

        self.c.create_rectangle(30, 70, 500, 600, fill=COLORS["panel"],
                                outline=COLORS["border"], width=2)
        # a coffee-cup ring stain on the menu (of course)
        self.c.create_oval(350, 92, 470, 212, outline="#6b4423", width=9)
        self.c.create_oval(366, 108, 454, 196, outline="#4a3018", width=2)
        self.c.create_text(60, 96, anchor="nw", text="THE JOB\nINTERVIEW\nDISASTER",
                           font=self.F["title"], fill=COLORS["text"])
        self.c.create_text(62, 306, anchor="w", fill=COLORS["accent"], font=self.F["h2"],
                           text="A dark comedy in five bad decisions")

        found = len(self.unlocked)
        items = [("NEW GAME", self.new_game, COLORS["accent"]),
                 (f"ENDINGS  ({found}/9)", self.show_gallery, None),
                 ("HOW TO PLAY", self.show_help, None),
                 ("QUIT", self.root.destroy, None)]
        for i, (label, cmd, color) in enumerate(items):
            y = 350 + i * 58
            self.button(60, y, 470, y + 46, label, cmd, color=color)

        self.c.create_rectangle(520, 560, 1000, 616, fill=COLORS["panel"],
                                outline=CHARACTERS["mayeul"]["color"], width=2)
        self.c.create_text(760, 588, text=random.choice(MENU_QUOTES), width=450,
                           font=self.F["small"], fill=COLORS["text"], justify="center")

    def screen_panel(self, title):
        """A dark panel with a title, used by the help and gallery screens."""
        self.clear()
        self.mode = "screen"
        self.c.create_rectangle(-20, -20, W + 20, H + 20, fill=COLORS["bg"], outline="")
        self.c.create_text(W / 2, 50, text=title, font=self.F["h1"], fill=COLORS["accent"])
        self.button(W / 2 - 120, 574, W / 2 + 120, 618, "BACK TO MENU", self.show_menu)

    def show_help(self):
        self.screen_panel("HOW TO PLAY")
        text = (
            "You are a recent graduate with one clean shirt and a lot of anxiety. "
            "You arrive at Synergix Solutions at 10:25... for a 10:00 interview.\n\n"
            "CONTROLS\n"
            "   Click, SPACE or ENTER  -  continue the dialogue\n"
            "   Click a button or press 1 / 2 / 3  -  make a choice\n"
            "   ESC  -  back to the main menu\n\n"
            "THE RULES\n"
            "   Every story has exactly 5 choices.\n"
            "   Choice 1 picks your track:  A) Lie   B) Tell the truth   C) Run away\n"
            "   Choices 2, 3 and 4:  SAFE (no risk) or BOLD (+1 CHAOS)\n"
            "   Choice 5 is the final decision:  SAFE or BOLD\n\n"
            "THE ENDINGS\n"
            "   Safe final choice                   ->  CALM ending\n"
            "   Bold final choice + Chaos 0 or 1    ->  MEDIUM ending\n"
            "   Bold final choice + Chaos 2 or 3    ->  WILD ending\n\n"
            "There are 9 endings. One of them is a secret. Mayeul knows which one."
        )
        self.c.create_rectangle(110, 90, 914, 556, fill=COLORS["panel"],
                                outline=COLORS["border"], width=2)
        self.c.create_text(140, 112, anchor="nw", text=text, width=740,
                           font=self.F["text"], fill=COLORS["text"])

    def show_gallery(self):
        self.screen_panel(f"ENDINGS FOUND: {len(self.unlocked)} / 9")
        for col, letter in enumerate("ABC"):
            x0 = 40 + col * 322
            self.c.create_text(x0 + 146, 104, text=f"TRACK {letter} - {TRACKS[letter]['name'].upper()}",
                               font=self.F["h2"], fill=COLORS["track"])
            for row, kind in enumerate(("calm", "medium", "wild")):
                number = TRACKS[letter]["endings"][kind]
                ending = ENDINGS[number]
                y0 = 130 + row * 145
                found = number in self.unlocked
                color = TYPE_COLORS[kind] if found else COLORS["border"]
                self.c.create_rectangle(x0, y0, x0 + 292, y0 + 130, fill=COLORS["panel"],
                                        outline=color, width=2)
                self.c.create_text(x0 + 14, y0 + 16, anchor="w", text=f"#{number}",
                                   font=self.F["small_b"], fill=COLORS["muted"])
                self.c.create_text(x0 + 278, y0 + 16, anchor="e", text=kind.upper(),
                                   font=self.F["small_b"], fill=color)
                if found:
                    title, fill = ending["title"], COLORS["text"]
                elif ending.get("secret"):
                    title, fill = "??? (secret ending)", COLORS["muted"]
                else:
                    title, fill = "???", COLORS["muted"]
                self.c.create_text(x0 + 146, y0 + 72, text=title, width=260, justify="center",
                                   font=self.F["h2"], fill=fill)

    # ------------------------------------------------------------------
    # PLAYING THE STORY
    # ------------------------------------------------------------------
    def new_game(self):
        self.game.reset()
        self.enter_scene()

    def enter_scene(self):
        """Show the current scene: its lines, then its choices."""
        scene = self.game.scene
        self.stage = scene
        if scene["choices"]:
            self.play_lines(scene["lines"], self.show_choices)
        else:                                   # the prologue has no choice
            self.play_lines(scene["lines"], self.after_prologue)

    def after_prologue(self):
        self.game.continue_story()
        self.enter_scene()

    def play_lines(self, lines, when_done):
        """Put lines in the queue; call when_done() after the last one."""
        self.queue = list(lines)
        self.when_done = when_done
        self.mode = "dialogue"
        self.next_line()

    def next_line(self):
        if self.queue:
            speaker, text = self.queue.pop(0)
            self.draw_frame(speaker)
            self.type_text(text)
        else:
            callback, self.when_done = self.when_done, None
            callback()

    def advance(self):
        """Click / SPACE: finish the current text, or show the next line."""
        if self.typing:
            self.finish_typing()
        else:
            self.next_line()

    def show_choices(self):
        scene = self.game.scene
        self.mode = "choice"
        self.draw_frame(None, question=scene["question"])

        choices = scene["choices"]
        bw, bh, gap = 760, 58, 14
        total = len(choices) * bh + (len(choices) - 1) * gap
        y = BOX[1] - 26 - total
        x0 = W / 2 - bw / 2
        for i, choice in enumerate(choices):
            self.choice_button(x0, y, x0 + bw, y + bh, i, choice, scene)
            y += bh + gap

    def choice_button(self, x0, y0, x1, y1, index, choice, scene):
        kind = choice["kind"]
        if kind == "track":
            label = f"TRACK {choice['track']}"
            color = COLORS["track"]
        elif kind == "safe":
            label, color = "SAFE", COLORS["safe"]
        elif scene.get("final"):
            label, color = "BOLD", COLORS["final"]
        else:
            label, color = "BOLD  +1", COLORS["bold"]

        tag = f"choice{index}"
        fill = COLORS["panel2"]
        rect = self.c.create_rectangle(x0, y0, x1, y1, fill=fill, outline=color, width=2,
                                       tags=("btn", tag))
        self.c.create_rectangle(x0, y0, x0 + 112, y1, fill=color, outline=color,
                                tags=("btn", tag))
        self.c.create_text(x0 + 56, (y0 + y1) / 2, text=label, font=self.F["small_b"],
                           fill="#111111", tags=("btn", tag))
        self.c.create_text(x0 + 128, (y0 + y1) / 2, anchor="w", text=choice["label"], width=570,
                           font=self.F["btn"], fill=COLORS["text"], tags=("btn", tag))
        self.c.create_text(x1 - 18, (y0 + y1) / 2, text=str(index + 1), font=self.F["h2"],
                           fill=COLORS["muted"], tags=("btn", tag))
        self._hover(tag, rect, fill, lambda: self.pick(index))

    def pick(self, index):
        """The player made a choice."""
        if self.mode != "choice":
            return
        choice = self.game.choose(index)      # the ENGINE applies the rules
        self.play_lines(choice["reaction"], self.after_choice)
        if choice.get("chaos"):
            self.chaos_effect()

    def after_choice(self):
        if self.game.is_over:
            self.start_ending()
        else:
            self.enter_scene()

    # ------------------------------------------------------------------
    # ENDINGS
    # ------------------------------------------------------------------
    def start_ending(self):
        self.stage = self.game.ending
        self.play_lines(self.game.ending["lines"], self.show_ending_card)

    def show_ending_card(self):
        game, ending = self.game, self.game.ending
        is_new = game.ending_id not in self.unlocked
        self.unlocked.add(game.ending_id)
        save_unlocked(self.unlocked)

        self.clear()
        self.mode = "ending"
        color = TYPE_COLORS[ending["type"]]
        self.c.create_rectangle(-20, -20, W + 20, H + 20, fill=COLORS["bg"], outline="")
        for _ in range(40):  # a few "confetti" squares
            x, y = random.randint(0, W), random.randint(0, H)
            self.c.create_rectangle(x, y, x + 6, y + 6, outline="",
                                    fill=random.choice(list(TYPE_COLORS.values())))
        self.c.create_rectangle(60, 40, W - 60, H - 40, fill=COLORS["panel"], outline=color,
                                width=3)

        label = f"ENDING {game.ending_id} OF 9"
        if ending.get("secret"):
            label += "  -  SECRET ENDING!"
        self.c.create_text(W / 2, 80, text=label, font=self.F["h2"], fill=COLORS["muted"])
        self.c.create_text(W / 2, 135, text=ending["title"], font=self.F["h1"],
                           fill=COLORS["text"], width=820, justify="center")
        self.c.create_rectangle(W / 2 - 110, 180, W / 2 + 110, 216, fill=color, outline="")
        self.c.create_text(W / 2, 198, text=f"{ending['type'].upper()} ENDING",
                           font=self.F["h2"], fill="#111111")
        if is_new:
            self.c.create_text(W / 2, 236, text="NEW ENDING UNLOCKED!",
                               font=self.F["small_b"], fill=COLORS["accent"])

        # explain WHY the player got this ending (useful in class!)
        final_kind = game.history[-1]["kind"].upper()
        why = (f"Final choice: {final_kind}    |    Chaos: {game.chaos}/{MAX_CHAOS}"
               f"    |    Track {game.track}: {TRACKS[game.track]['name']}")
        self.c.create_text(W / 2, 262, text=why, font=self.F["small"], fill=COLORS["text"])

        # the 5 choices of this playthrough
        self.c.create_text(120, 296, anchor="w", text="YOUR PATH", font=self.F["small_b"],
                           fill=COLORS["accent"])
        for i, step in enumerate(game.history):
            y = 324 + i * 32
            kind = step["kind"]
            tag = {"track": "TRACK", "safe": "SAFE", "bold": "BOLD"}[kind]
            tcolor = {"track": COLORS["track"], "safe": COLORS["safe"],
                      "bold": COLORS["bold"]}[kind]
            self.c.create_text(120, y, anchor="w", text=f"{step['number']}.",
                               font=self.F["small_b"], fill=COLORS["muted"])
            self.c.create_rectangle(146, y - 11, 210, y + 11, fill=tcolor, outline="")
            self.c.create_text(178, y, text=tag, font=self.F["tiny"], fill="#111111")
            self.c.create_text(224, y, anchor="w", text=step["label"], font=self.F["small"],
                               fill=COLORS["text"])

        self.c.create_text(W / 2, 498, text=f"Endings found: {len(self.unlocked)} / 9",
                           font=self.F["small_b"], fill=COLORS["muted"])
        self.button(150, 520, 380, 570, "PLAY AGAIN  (R)", self.new_game, color=COLORS["accent"])
        self.button(397, 520, 627, 570, "ENDINGS", self.show_gallery)
        self.button(644, 520, 874, 570, "MAIN MENU  (M)", self.show_menu)

    # ------------------------------------------------------------------
    # DRAWING ONE FRAME OF THE STORY: background, characters, HUD, box
    # ------------------------------------------------------------------
    def draw_frame(self, speaker, question=None):
        self.clear()
        stage = self.stage
        BACKGROUNDS[stage["place"]](self.c, stage["time"])

        # characters, spread across the screen; the speaker is lighter + higher
        cast = stage["cast"]
        for i, key in enumerate(cast):
            x = W / 2 + (i - (len(cast) - 1) / 2) * min(260, 900 / len(cast))
            look = CHARACTERS[key]["look"]
            if key == "man" and stage.get("secret"):
                look = dict(look, card="S")    # the lanyard is turned around!
            if key == "you":
                outfit, shirt = SHIRT_COLORS[self.game.shirt], self.game.shirt
            else:
                outfit, shirt = look["outfit"], None
            talking = speaker == key
            dim = question is not None or (speaker is not None and not talking)
            draw_person(self.c, x, look, outfit, dim=dim, lift=14 if talking else 0, shirt=shirt)

        self.draw_hud()
        self.draw_box(speaker, question)

    def draw_hud(self):
        c, game, stage = self.c, self.game, self.stage
        in_ending = stage is game.ending      # are we showing an ending?
        c.create_rectangle(0, 0, W, HUD_H, fill=COLORS["hud"], outline="")
        c.create_line(0, HUD_H, W, HUD_H, fill=COLORS["border"], width=2)

        # left: title + track
        c.create_text(20, 20, anchor="w", text="THE JOB INTERVIEW DISASTER",
                      font=self.F["small_b"], fill=COLORS["accent"])
        if in_ending:
            track_text = "THE END"
        elif game.track:
            track_text = f"TRACK {game.track}  -  {TRACKS[game.track]['name'].upper()}"
        else:
            track_text = "PROLOGUE" if stage.get("number") == 0 else "THE BEGINNING"
        c.create_text(20, 42, anchor="w", text=track_text, font=self.F["small_b"],
                      fill=COLORS["track"])

        # centre: time + place
        c.create_text(W / 2, 20, text=stage["time"], font=self.F["hud_big"], fill=COLORS["text"])
        c.create_text(W / 2, 43, text=stage["location"], font=self.F["small"],
                      fill=COLORS["muted"])

        # right: choice progress (5 dots)
        number = stage.get("number", TOTAL_CHOICES + 1)
        done = len(game.history)
        label = "ENDING" if in_ending else (
            "PROLOGUE" if number == 0 else f"CHOICE {number}/{TOTAL_CHOICES}")
        c.create_text(690, 20, anchor="w", text=label, font=self.F["small_b"],
                      fill=COLORS["text"])
        for i in range(TOTAL_CHOICES):
            x = 696 + i * 18
            if i < done:
                c.create_oval(x - 6, 36, x + 6, 48, fill=COLORS["accent"], outline="")
            elif i == number - 1:
                c.create_oval(x - 6, 36, x + 6, 48, fill="", outline=COLORS["accent"], width=2)
            else:
                c.create_oval(x - 6, 36, x + 6, 48, fill=COLORS["border"], outline="")

        # right: CHAOS meter (3 pips)
        c.create_text(808, 20, anchor="w", text=f"CHAOS {game.chaos}/{MAX_CHAOS}",
                      font=self.F["small_b"], fill=COLORS["bold"] if game.chaos else COLORS["text"])
        for i in range(MAX_CHAOS):
            x = 808 + i * 30
            on = i < game.chaos
            c.create_rectangle(x, 34, x + 24, 48, outline="", tags="chaos_pip",
                               fill=COLORS["bold"] if on else COLORS["border"])

        # menu button
        self.button(926, 14, 1006, 46, "MENU", self.ask_menu, font=self.F["small_b"])

    def draw_box(self, speaker, question):
        c = self.c
        x0, y0, x1, y1 = BOX
        c.create_rectangle(x0 + 4, y0 + 4, x1 + 4, y1 + 4, fill="#05060b", outline="")
        c.create_rectangle(x0, y0, x1, y1, fill=COLORS["panel"], outline=COLORS["border"], width=2)

        if question is not None:
            name, role, color = "YOUR CHOICE", "Choose wisely. Or don't.", COLORS["accent"]
        elif speaker is None:
            name = None
        else:
            ch = CHARACTERS[speaker]
            name, role, color = ch["name"].upper(), ch["role"], ch["color"]

        if name:   # the name plate above the box, and the role next to it
            label = c.create_text(x0 + 40, y0 - 5, anchor="w", text=name, font=self.F["h2"],
                                  fill="#111111")
            right = max(c.bbox(label)[2] + 20, x0 + 150)
            plate = c.create_rectangle(x0 + 20, y0 - 22, right, y0 + 12, fill=color, outline="")
            c.tag_lower(plate, label)
            info = c.create_text(right + 14, y0 - 5, anchor="w", text=role,
                                 font=self.F["small"], fill=COLORS["text"])
            bx0, by0, bx1, by1 = c.bbox(info)
            back = c.create_rectangle(right, by0 - 3, bx1 + 12, by1 + 3, fill=COLORS["panel"],
                                      outline="")
            c.tag_lower(back, info)

        font = self.F["italic"] if (speaker is None and question is None) else self.F["text"]
        color = "#c9cfe0" if (speaker is None and question is None) else COLORS["text"]
        self.text_id = c.create_text(x0 + 30, y0 + 30, anchor="nw", text=question or "",
                                     width=x1 - x0 - 70, font=font, fill=color)
        if question is not None:
            c.create_text(x1 - 20, y1 - 16, anchor="e", font=self.F["small"],
                          fill=COLORS["muted"], text="Click a choice or press 1 / 2 / 3")

    # ------------------------------------------------------------------
    # ANIMATIONS: typewriter text, blinking arrow, chaos shake
    # ------------------------------------------------------------------
    def type_text(self, text):
        self.full_text = text
        self.shown = 0
        self.typing = True
        self._type_step()

    def _type_step(self):
        self.shown += 2
        self.c.itemconfig(self.text_id, text=self.full_text[:self.shown])
        if self.shown >= len(self.full_text):
            self.finish_typing()
        else:
            self.type_job = self.root.after(TYPE_SPEED, self._type_step)

    def finish_typing(self):
        if self.type_job:
            self.root.after_cancel(self.type_job)
            self.type_job = None
        self.typing = False
        self.c.itemconfig(self.text_id, text=self.full_text)
        arrow = self.c.create_text(BOX[2] - 24, BOX[3] - 18, text="▼  click / space",
                                   anchor="e", font=self.F["small"], fill=COLORS["accent"])
        self._blink(arrow, self.frame, True)

    def _blink(self, item, frame, visible):
        if frame != self.frame:      # the screen changed: stop blinking
            return
        self.c.itemconfig(item, state="normal" if visible else "hidden")
        self.root.after(450, self._blink, item, frame, not visible)

    def chaos_effect(self):
        """+1 CHAOS: the screen shakes and a red message flies up."""
        frame = self.frame
        popup = self.c.create_text(890, 90, text="+1 CHAOS!", font=self.F["hud_big"],
                                   fill=COLORS["bold"])
        offsets = [10, -10, 8, -8, 5, -5, 2, -2]

        def shake(step=0):
            if frame != self.frame:
                return
            if step < len(offsets):
                self.c.move("stage", offsets[step], 0)
                self.c.move(popup, 0, -4)
                self.root.after(35, shake, step + 1)
            else:
                self.root.after(600, lambda: self.c.delete(popup))
        shake()

    # ------------------------------------------------------------------
    # INPUT: mouse and keyboard
    # ------------------------------------------------------------------
    def on_click(self, event):
        # clicks on buttons are handled by the buttons themselves
        current = self.c.find_withtag("current")
        if current and "btn" in self.c.gettags(current[0]):
            return
        if self.mode == "dialogue":
            self.advance()

    def on_key(self, event):
        key = event.keysym
        if key == "Escape":
            if self.mode in ("dialogue", "choice"):
                self.ask_menu()
            elif self.mode != "menu":
                self.show_menu()
        elif self.mode == "dialogue" and key in ("space", "Return", "KP_Enter", "Right"):
            self.advance()
        elif self.mode == "choice" and event.char in ("1", "2", "3"):
            index = int(event.char) - 1
            if index < len(self.game.scene["choices"]):
                self.pick(index)
        elif self.mode == "menu" and key in ("Return", "space"):
            self.new_game()
        elif self.mode == "ending" and event.char.lower() == "r":
            self.new_game()
        elif self.mode == "ending" and event.char.lower() == "m":
            self.show_menu()

    def ask_menu(self):
        if messagebox.askyesno("Back to menu?",
                               "Go back to the main menu?\nThis story will be lost. "
                               "Mayeul will pretend he didn't see anything."):
            self.show_menu()


# ===========================================================================
# START
# ===========================================================================
def main():
    if "--terminal" in sys.argv or tk is None:
        import terminal
        terminal.main()
        return
    try:
        root = tk.Tk()
    except tk.TclError:                      # no screen available
        import terminal
        terminal.main()
        return
    GameApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
