"""
engine.py - the RULES of the game (no text, no graphics).

The Game class remembers where the player is and counts the Chaos points.
The graphical version (game.py) and the terminal version (terminal.py)
both use this same class, so the rules are written only once.
"""

from story import SCENES, ENDINGS, TRACKS, FIRST_SCENE

MAX_CHAOS = 3        # 3 Bold choices possible (choices 2, 3 and 4)
TOTAL_CHOICES = 5    # every path has exactly 5 choices


def get_ending_type(final_choice_is_bold, chaos):
    """THE ENDING RULES (the heart of the game).

    - Safe final choice                 -> "calm"
    - Bold final choice + Chaos 0 or 1  -> "medium"
    - Bold final choice + Chaos 2 or 3  -> "wild"
    """
    if not final_choice_is_bold:
        return "calm"
    if chaos <= 1:
        return "medium"
    return "wild"


class Game:
    """Keeps the state of one playthrough."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Start a new game from the very beginning."""
        self.scene_id = FIRST_SCENE   # where we are in the story
        self.chaos = 0                # Chaos counter (0 to 3)
        self.track = None             # "A", "B" or "C" after choice 1
        self.shirt = "white"          # the shirt can change during the game!
        self.history = []             # the choices the player made
        self.ending_id = None         # becomes 1..9 when the game is over

    @property
    def scene(self):
        """The dictionary of the current scene."""
        return SCENES[self.scene_id]

    def continue_story(self):
        """For scenes without a choice (the prologue): go to the next one."""
        self.scene_id = self.scene["next"]

    def choose(self, index):
        """The player picks choice number `index` (0, 1 or 2).

        Updates the Chaos counter, the track and the shirt, then moves to the
        next scene OR decides the ending. Returns the chosen choice so the
        interface can show the reaction lines.
        """
        scene = self.scene
        choice = scene["choices"][index]

        # 1) Chaos: Bold options in choices 2, 3 and 4 give +1.
        self.chaos += choice.get("chaos", 0)

        # 2) Choice 1 decides the track (A = Lie, B = Truth, C = Run away).
        if "track" in choice:
            self.track = choice["track"]

        # 3) Some choices change your shirt (orange polo, pink DAD shirt...).
        if "shirt" in choice:
            self.shirt = choice["shirt"]

        # 4) Remember the choice (we show the full path at the end).
        self.history.append({
            "number": scene["number"],
            "label": choice["label"],
            "kind": choice["kind"],
        })

        # 5) Final choice? Then apply the ending rules. Otherwise, next scene.
        if scene.get("final"):
            ending_type = get_ending_type(choice["kind"] == "bold", self.chaos)
            self.ending_id = TRACKS[self.track]["endings"][ending_type]
        else:
            self.scene_id = choice["next"]

        return choice

    @property
    def ending(self):
        """The dictionary of the ending (or None if the game isn't over)."""
        if self.ending_id is None:
            return None
        return ENDINGS[self.ending_id]

    @property
    def is_over(self):
        return self.ending_id is not None
