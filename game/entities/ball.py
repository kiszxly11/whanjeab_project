from ..settings import BALL_NORMAL


class Ball:
    """A ball in flight.

    kind is BALL_NORMAL or one of the SKILL_* names from settings
    ('fire', 'ice', 'lightning', 'bounce').
    """

    def __init__(self, x, y, vx, vy, kind=BALL_NORMAL):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.kind = kind
        self.active = True
