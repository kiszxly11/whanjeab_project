"""Global constants and tuning values for Punball."""
import math

W, H = 480, 800
FPS = 60
TITLE = "Punball"

COLS = 8
CELL = W // COLS
GRID_TOP = 130
MAX_ROWS = 10
BOSS_H = 110
FLOOR_Y = H - 30
HERO_R = 14
HERO_Y = FLOOR_Y - HERO_R
BOTTOM_STRIP_Y = H - 90
HERO_MOVE_SPEED = 400

BALL_R = 6
BALL_SPEED = 620
FIRE_INTERVAL = 0.07
MIN_AIM_ANGLE = math.radians(10)

HERO_MAX_HP = 100
START_BALLS = 5
BALL_DAMAGE = 1

ITEM_R = 11
ITEM_PLUS = "plus"
ITEM_MULTI = "multi"
ITEM_SKILL = "skill"
ITEM_HEAL = "heal"
HEAL_RATIO = 0.05            # heal item restores this fraction of the hero's max HP
ITEM_WEIGHTS = {             # relative spawn chance of each item kind (any positive numbers)
    ITEM_PLUS: 38,
    ITEM_MULTI: 22,
    ITEM_HEAL: 20,
    ITEM_SKILL: 20,
}

END_PHASE_DELAY = 0.7
ATTACK_FX_TIME = 0.5
SHAKE_TIME = 0.35
SHAKE_POWER = 8
HIT_SHAKE_TIME = 0.1
HIT_SHAKE_POWER = 3
BLOCK_FLASH = 0.09
PARTICLE_COUNT = 12
MAX_PARTICLES = 300
FF_SPEED = 3

# ---- skills (special balls) -------------------------------------------
BALL_NORMAL = "normal"
SKILL_FIRE = "fire"
SKILL_ICE = "ice"
SKILL_LIGHTNING = "lightning"
SKILL_BOUNCE = "bounce"

BURN_TURNS = 5               # fire ball: turns a block keeps burning
BURN_DAMAGE_RATIO = 0.5      # burn damage per turn = ceil(hero.damage * ratio), min 1
FREEZE_TURNS = 2             # ice ball: turns a block can't move down
SKILL_CHOICES = 3            # how many skills are offered each time
SKILL_PICK_DELAY = 0.35      # seconds the choice screen ignores input (no accidental clicks)
BOLT_TIME = 0.25             # lightning visual duration

BG = (24, 24, 34)
GRID_LINE = (32, 32, 44)
WHITE = (255, 255, 255)

_BLOCK_STOPS = [          # (ratio, colour), lowest HP first
    (0.00, (70, 200, 150)),    # mint
    (0.30, (120, 205, 85)),    # green
    (0.55, (250, 195, 60)),    # yellow
    (0.78, (250, 125, 75)),    # orange
    (1.00, (235, 75, 120)),    # pink-red
]


def block_color(ratio):
    """Block colour from its remaining-HP ratio (1.0 = full)."""
    ratio = max(0.0, min(1.0, ratio))
    for (r0, c0), (r1, c1) in zip(_BLOCK_STOPS, _BLOCK_STOPS[1:]):
        if ratio <= r1:
            t = (ratio - r0) / (r1 - r0)
            return tuple(int(c0[i] + (c1[i] - c0[i]) * t) for i in range(3))
    return _BLOCK_STOPS[-1][1]


class State:
    AIM = "aim"
    ATTACK = "attack"
    END = "end"
    WIN = "win"
    LOSE = "lose"
