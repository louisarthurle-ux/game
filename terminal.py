"""
terminal.py - the simple TEXT version of the game (for the terminal).

Run it with:   python game.py --terminal
(It also starts automatically if your Python has no graphics library.)
"""

import textwrap

from engine import Game, MAX_CHAOS, TOTAL_CHOICES
from story import CHARACTERS, TRACKS

WIDTH = 72  # maximum width of a line of text


def say(speaker, text):
    """Print one line of dialogue, nicely wrapped."""
    if speaker is None:                       # the narrator
        print(textwrap.fill(text, WIDTH))
    else:
        name = CHARACTERS[speaker]["name"].upper()
        print(textwrap.fill(f"{name}: {text}", WIDTH, subsequent_indent="    "))


def play_lines(lines):
    """Show a list of lines. The player presses Enter to continue."""
    for speaker, text in lines:
        say(speaker, text)
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


def play_once():
    game = Game()
    print("\n" + "THE JOB INTERVIEW DISASTER".center(WIDTH) + "\n")

    while not game.is_over:
        scene = game.scene
        if not scene["choices"]:              # prologue: no choice
            play_lines(scene["lines"])
            game.continue_story()
            continue

        hud(game)
        play_lines(scene["lines"])
        print("\n" + scene["question"])
        index = ask(scene["choices"])
        choice = game.choose(index)
        if choice.get("chaos"):
            print("  >>> +1 CHAOS <<<")
        play_lines(choice["reaction"])
        print()

    ending = game.ending
    print("=" * WIDTH)
    play_lines(ending["lines"])

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


def main():
    try:
        while True:
            play_once()
            again = input("\nPlay again? (y/n) ").strip().lower()
            if not again.startswith("y"):
                break
    except (KeyboardInterrupt, EOFError):   # Ctrl+C: quit without an error
        print()
    print("Goodbye. Mayeul will remember this.")


if __name__ == "__main__":
    main()
