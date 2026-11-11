import random

from ..entities import Block
from ..items import Item, pick_kind
from ..settings import COLS, MAX_ROWS


class Field:
    """Owns all blocks and items on the grid."""

    def __init__(self):
        self.blocks = []
        self.items = []

    def reset(self):
        self.blocks.clear()
        self.items.clear()

    def spawn_row(self, turn, stage):
        """Fill row 0 with random blocks / items (skips cells still occupied)."""
        taken = {o.col for o in self.blocks + self.items if o.row == 0}
        for col in range(COLS):
            if col in taken:                  # a frozen block is still sitting here
                continue
            r = random.random()
            if r < 0.45:
                lo = max(1, (turn + stage) // 2)
                hi = turn + stage * 2
                self.blocks.append(Block(col, 0, random.randint(lo, hi)))
            elif r < 0.52:
                kind = pick_kind()
                self.items.append(Item(col, 0, kind))

    def move_down(self):                  # Block Movement System
        """Move everything down one row, except frozen blocks.

        Objects are processed bottom-first, so anything above a frozen block
        (or an item stuck behind one) waits instead of overlapping it.
        """
        taken = set()
        for obj in sorted(self.blocks + self.items, key=lambda o: -o.row):
            frozen = getattr(obj, "frozen", 0)
            if frozen > 0:
                obj.frozen -= 1               # this turn's move is skipped
            elif (obj.col, obj.row + 1) not in taken:
                obj.row += 1
            taken.add((obj.col, obj.row))
        self.items = [i for i in self.items if i.row < MAX_ROWS]

    def block_hit_hero(self):             # Block and Hero Collision Detection
        return any(b.row >= MAX_ROWS for b in self.blocks)
