"""
terminal.py - the simple TEXT version of the game (for the terminal).

Run it with:   python game.py --terminal
(It also starts automatically if your Python has no graphics library.)
"""

import textwrap
import time

import i18n
from engine import Game, MAX_CHAOS, TOTAL_CHOICES, TIMER_SECONDS, earned_achievements
from i18n import t
from story import CHARACTERS, TRACKS, ACHIEVEMENTS, DEFAULT_NAME, TIMEOUT_LINE

WIDTH = 72  # maximum width of a line of text


def say(game, speaker, text):
    """Print one line of dialogue, nicely wrapped."""
    text = game.fill(t(text))                 # translate + {name} -> the player's name
    if speaker is None:                       # the narrator
        print(textwrap.fill(text, WIDTH))
    else:
        name = t(CHARACTERS[speaker]["name"]).upper()
        if speaker == "you":
            name = game.display_name.upper()
        print(textwrap.fill(f"{name}: {text}", WIDTH, subsequent_indent="    "))


def play_lines(game, lines):
    """Show a list of lines. The player presses Enter to continue."""
    for speaker, text in lines:
        say(game, speaker, text)
        input("   ...")


def hud(game):
    """A small text HUD: choice number, Chaos meter and track."""
    scene = game.scene
    track = t(TRACKS[game.track]["name"]) if game.track else "-"
    meter = "#" * game.chaos + "." * (MAX_CHAOS - game.chaos)
    print("=" * WIDTH)
    print(" " + t("CHOICE {number}/{total}").format(number=scene["number"], total=TOTAL_CHOICES)
          + f"   [{meter}]   {track}   {t(scene['time'])} {t(scene['location'])}")
    print("=" * WIDTH)


def ask(choices):
    """Show the choices and return the index the player picked."""
    for i, choice in enumerate(choices, start=1):
        tag = {"track": "", "safe": f"[{t('SAFE')}] ", "bold": f"[{t('BOLD')}] "}[choice["kind"]]
        print(f"  {i}) {tag}{t(choice['label'])}")
    while True:
        answer = input("> " + t("Your choice:") + " ").strip()
        if answer.isdigit() and 1 <= int(answer) <= len(choices):
            return int(answer) - 1
        print("  " + t("Please type a number from the list. Mayeul is sighing."))


def play_once(name, trophies, endings_found):
    game = Game()
    game.player_name = name
    print("\n" + t("THE JOB INTERVIEW DISASTER").center(WIDTH) + "\n")

    while not game.is_over:
        scene = game.scene
        if not scene["choices"]:              # prologue: no choice
            play_lines(game, scene["lines"])
            game.continue_story()
            continue

        hud(game)
        play_lines(game, scene["lines"])
        print("\n" + game.fill(t(scene["question"])))
        timed_out = False
        if scene.get("final"):
            print("  " + t("(Quick! You have {seconds} seconds, or Mayeul chooses for you.)")
                  .format(seconds=TIMER_SECONDS))
        start = time.time()
        index = ask(scene["choices"])
        if scene.get("final") and time.time() - start > TIMER_SECONDS:
            timed_out = True                  # too slow: Mayeul picks BOLD
            index = [c["kind"] for c in scene["choices"]].index("bold")
        choice = game.choose(index, timed_out)
        reaction = list(choice["reaction"])
        if timed_out:
            reaction.insert(0, TIMEOUT_LINE)
        if choice.get("chaos"):
            print("  >>> " + t("+1 CHAOS!") + " <<<")
        play_lines(game, reaction)
        print()

    ending = game.ending
    print("=" * WIDTH)
    play_lines(game, ending["lines"])

    # Mayeul's notebook
    notes, verdict = game.notebook()
    print("\n" + (" " + t("MAYEUL'S NOTEBOOK") + " ").center(WIDTH, "-"))
    for i, note in enumerate(notes, start=1):
        print(textwrap.fill(f" {i}. {note}", WIDTH, subsequent_indent="    "))
    print(textwrap.fill(f" {t('VERDICT:')} {verdict}  - M.", WIDTH, subsequent_indent="    "))
    input("   ...")
    print("=" * WIDTH)
    print(" " + t("ENDING {number} OF 9").format(number=game.ending_id) + ": "
          + t(ending["title"]).upper())
    kind = {"calm": t("CALM"), "medium": t("MEDIUM"), "wild": t("WILD")}[ending["type"]]
    print(" " + t("{kind} ENDING").format(kind=kind) + "   "
          + t("CHAOS {chaos}/{max}").format(chaos=game.chaos, max=MAX_CHAOS))
    print("=" * WIDTH)

    # trophies
    endings_found.add(game.ending_id)
    for trophy in ACHIEVEMENTS:
        if trophy in earned_achievements(game, endings_found) - trophies:
            trophies.add(trophy)
            title, description = ACHIEVEMENTS[trophy]
            print(f" *** {t('TROPHY UNLOCKED')}: {t(title)} - {t(description)}")
    print(" " + t("TROPHIES: {won} / {total}").format(won=len(trophies), total=len(ACHIEVEMENTS)))


def choose_language():
    codes = list(i18n.LANGUAGES)
    for i, code in enumerate(codes, start=1):
        print(f"  {i}) {i18n.LANGUAGES[code]}")
    answer = input("> Language / Langue / Sprache / اللغة: ").strip()
    if answer.isdigit() and 1 <= int(answer) <= len(codes):
        i18n.set_language(codes[int(answer) - 1])


def main():
    trophies, endings_found = set(), set()
    try:
        choose_language()
        name = " ".join(input(t("Name? Your real one, please. I'll know if you lie.")
                              + " ").split())[:16]
        name = name or DEFAULT_NAME
        while True:
            play_once(name, trophies, endings_found)
            again = input("\n" + t("Play again? (y/n)") + " ").strip().lower()
            if not again[:1] in ("y", "o", "j", "ن"):      # yes / oui / ja / نعم
                break
    except (KeyboardInterrupt, EOFError):   # Ctrl+C: quit without an error
        print()
    print(t("Goodbye. Mayeul will remember this."))


if __name__ == "__main__":
    main()
