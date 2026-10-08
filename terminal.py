"""
terminal.py - the simple TEXT version of the game (for the terminal).

Run it with:   python game.py --terminal
(It also starts automatically if your Python has no graphics library.)
"""

import textwrap
import time

from engine import Game, MAX_CHAOS, TOTAL_CHOICES, TIMER_SECONDS, earned_achievements
from story import CHARACTERS, TRACKS, ACHIEVEMENTS, DEFAULT_NAME

WIDTH = 72  # maximum width of a line of text


def say(game, speaker, text):
    """Print one line of dialogue, nicely wrapped."""
    text = game.fill(text)                    # {name} -> the player's name
    if speaker is None:                       # the narrator
        print(textwrap.fill(text, WIDTH))
    else:
        name = CHARACTERS[speaker]["name"].upper()
        if speaker == "you":
            name = game.player_name.upper()
        print(textwrap.fill(f"{name}: {text}", WIDTH, subsequent_indent="    "))


def play_lines(game, lines):
    """Show a list of lines. The player presses Enter to continue."""
    for speaker, text in lines:
        say(game, speaker, text)
        input("   ...")


def hud(game):
    """A small text HUD: choice number, Chaos meter and track."""
    scene = game.scene
    track = TRACKS[game.track]["name"] if game.track else "-"
    meter = "#" * game.chaos + "." * (MAX_CHAOS - game.chaos)
    print("=" * WIDTH)
    print(f" CHOICE {scene['number']}/{TOTAL_CHOICES}   CHAOS [{meter}]   "
          f"TRACK: {track}   {scene['time']} {scene['location']}")
    print("=" * WIDTH)


def ask(choices):
    """Show the choices and return the index the player picked."""
    for i, choice in enumerate(choices, start=1):
        tag = {"track": "", "safe": "[SAFE] ", "bold": "[BOLD] "}[choice["kind"]]
        print(f"  {i}) {tag}{choice['label']}")
    while True:
        answer = input("> Your choice: ").strip()
        if answer.isdigit() and 1 <= int(answer) <= len(choices):
            return int(answer) - 1
        print("  Please type a number from the list. Mayeul is sighing.")


def play_once(name, trophies, endings_found):
    game = Game()
    game.player_name = name
    print("\n" + "THE JOB INTERVIEW DISASTER".center(WIDTH) + "\n")

    while not game.is_over:
        scene = game.scene
        if not scene["choices"]:              # prologue: no choice
            play_lines(game, scene["lines"])
            game.continue_story()
            continue

        hud(game)
        play_lines(game, scene["lines"])
        print("\n" + game.fill(scene["question"]))
        timed_out = False
        if scene.get("final"):
            print(f"  (Quick! You have {TIMER_SECONDS} seconds, or Mayeul chooses for you.)")
        start = time.time()
        index = ask(scene["choices"])
        if scene.get("final") and time.time() - start > TIMER_SECONDS:
            timed_out = True                  # too slow: Mayeul picks BOLD
            index = [c["kind"] for c in scene["choices"]].index("bold")
        choice = game.choose(index, timed_out)
        reaction = list(choice["reaction"])
        if timed_out:
            reaction.insert(0, ("mayeul", "Time's up, {name}. Too slow. I chose for you. "
                                          "I always choose BOLD."))
        if choice.get("chaos"):
            print("  >>> +1 CHAOS <<<")
        play_lines(game, reaction)
        print()

    ending = game.ending
    print("=" * WIDTH)
    play_lines(game, ending["lines"])

    # Mayeul's notebook
    notes, verdict = game.notebook()
    print("\n" + "MAYEUL'S NOTEBOOK - OBSERVATIONS, VOLUME 7".center(WIDTH, "-"))
    for i, note in enumerate(notes, start=1):
        print(textwrap.fill(f" {i}. {note}", WIDTH, subsequent_indent="    "))
    print(textwrap.fill(f" VERDICT: {verdict}  - M.", WIDTH, subsequent_indent="    "))
    input("   ...")
    print("=" * WIDTH)
    print(f" ENDING {game.ending_id}/9: {ending['title'].upper()}")
    print(f" Type: {ending['type'].upper()}   Final Chaos: {game.chaos}/{MAX_CHAOS}")
    print("=" * WIDTH)

    # trophies
    endings_found.add(game.ending_id)
    for trophy in ACHIEVEMENTS:
        if trophy in earned_achievements(game, endings_found) - trophies:
            trophies.add(trophy)
            print(f" *** TROPHY UNLOCKED: {ACHIEVEMENTS[trophy][0]} - "
                  f"{ACHIEVEMENTS[trophy][1]}")
    print(f" Trophies: {len(trophies)}/{len(ACHIEVEMENTS)}")


def main():
    trophies, endings_found = set(), set()
    try:
        name = " ".join(input("MAYEUL: Name? Your real one, please. ").split())[:16]
        if not name:
            name = DEFAULT_NAME
            print(f"MAYEUL: No name? Fine. You are '{name}' now.")
        while True:
            play_once(name, trophies, endings_found)
            again = input("\nPlay again? (y/n) ").strip().lower()
            if not again.startswith("y"):
                break
    except (KeyboardInterrupt, EOFError):   # Ctrl+C: quit without an error
        print()
    print("Goodbye. Mayeul will remember this.")


if __name__ == "__main__":
    main()
