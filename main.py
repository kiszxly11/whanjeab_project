"""Entry point:  python main.py

Keep the folder layout intact: main.py must sit next to the `game/` folder.
"""
import os
import sys

# Make sure the folder containing main.py is importable, whatever the
# working directory or IDE run configuration is.
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

if not getattr(sys, "frozen", False) and not os.path.isdir(os.path.join(HERE, "game")):
    sys.exit("Missing 'game' folder next to main.py. Extract the whole zip "
             "and keep the folder structure (game/entities, game/systems).")

from game import Game  # noqa: E402


if __name__ == "__main__":
    Game().run()
