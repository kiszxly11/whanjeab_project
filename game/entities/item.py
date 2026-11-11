from ..settings import CELL, GRID_TOP


class Item:
    """Special item sitting in a grid cell.

    kind 'plus'  -> +1 ball for the next round
    kind 'multi' -> splits the ball that touches it into three
    kind 'skill' -> after this volley ends, pick 1 of 3 random skills
    """

    def __init__(self, col, row, kind):
        self.col, self.row, self.kind = col, row, kind

    @property
    def pos(self):
        return (self.col * CELL + CELL / 2,
                GRID_TOP + self.row * CELL + CELL / 2)
