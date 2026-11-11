"""Everything about grid items lives here: the Item itself, what each kind does,
how it looks and how often it spawns.

An Item sits in a grid cell. When a ball touches it, the item is removed and its
`on_collect` runs. To add a new item, write a class below and decorate it with
@register, then give it a spawn weight in settings.ITEM_WEIGHTS. Spawning, collecting
and drawing pick it up automatically.

    @register
    class MyItem(ItemType):
        kind = "my_item"                       # unique id (also stored on Item.kind)

        def on_collect(self, ball, ctx):       # a ball touched it
            ctx.manager.extra_balls += 1       # ctx.hero, ctx.manager, ctx.effect(...)

        def draw(self, r, surface, x, y):      # r = Renderer (r._text, r._star, r.small ...)
            ...

Visual-only effects (floating text, particles) are sent with ctx.effect("heal", ...);
the matching handler is in Game.on_ball_effect (app.py).
Tuning numbers (spawn weights, heal amount) are in settings.py.
"""
import math
import random

import pygame

from .entities import Ball
from .settings import (BALL_SPEED, CELL, GRID_TOP, HEAL_RATIO, ITEM_HEAL, ITEM_MULTI,
                       ITEM_PLUS, ITEM_R, ITEM_SKILL, ITEM_WEIGHTS, WHITE)


# ------------------------------------------------------------------- data
class Item:
    """An item sitting in a grid cell: just a position and a kind.
    What the kind does and looks like is defined by the classes below."""

    def __init__(self, col, row, kind):
        self.col, self.row, self.kind = col, row, kind

    @property
    def pos(self):
        return (self.col * CELL + CELL / 2,
                GRID_TOP + self.row * CELL + CELL / 2)


# --------------------------------------------------------------- plumbing
class ItemContext:
    """What an item hook may touch while a ball collects it."""

    def __init__(self, manager, hero, pos, on_effect=None):
        self.manager = manager            # the BallManager (balls, extra_balls, ...)
        self.hero = hero
        self.pos = pos                    # centre of the item
        self.on_effect = on_effect

    def effect(self, kind, **data):
        if self.on_effect:
            self.on_effect(kind, pos=self.pos, **data)


class ItemType:
    kind = ""

    def on_collect(self, ball, ctx):
        """A ball touched the item (the item is already removed from the field)."""

    def draw(self, r, surface, x, y):
        """Draw the item centred at (x, y). `r` is the Renderer."""


ITEMS = {}                        # kind -> ItemType instance, in registration order


def register(cls):
    ITEMS[cls.kind] = cls()
    return cls


def pick_kind():
    """Random item kind for a new item cell, using settings.ITEM_WEIGHTS."""
    kinds = list(ITEMS)
    return random.choices(kinds, weights=[ITEM_WEIGHTS.get(k, 0) for k in kinds])[0]


# ------------------------------------------------------------------ items
@register
class PlusItem(ItemType):
    """+1 ball for the next round."""
    kind = ITEM_PLUS

    def on_collect(self, ball, ctx):
        ctx.manager.extra_balls += 1

    def draw(self, r, surface, x, y):
        r._gem(surface, x, y, (70, 205, 105), ITEM_R + 2)
        c = (int(x), int(y) + 1)
        r._text(surface, "+1", r.small, (15, 70, 30), center=(c[0] + 1, c[1] + 1))
        r._text(surface, "+1", r.small, WHITE, center=c)


@register
class MultiItem(ItemType):
    """Splits the ball that touches it into three (the children keep its kind)."""
    kind = ITEM_MULTI

    def on_collect(self, ball, ctx):
        ang = math.atan2(ball.vy, ball.vx)
        for off in (-0.35, 0.35):
            a = ang + off
            ctx.manager.balls.append(Ball(ball.x, ball.y,
                                          math.cos(a) * BALL_SPEED,
                                          math.sin(a) * BALL_SPEED,
                                          ball.kind))

    def draw(self, r, surface, x, y):
        r._gem(surface, x, y, (70, 150, 255), ITEM_R + 2)
        c = (int(x), int(y) + 1)
        r._text(surface, "x3", r.small, (15, 40, 110), center=(c[0] + 1, c[1] + 1))
        r._text(surface, "x3", r.small, WHITE, center=c)


@register
class HealItem(ItemType):
    """Instantly restores HEAL_RATIO of the hero's max HP."""
    kind = ITEM_HEAL

    def on_collect(self, ball, ctx):
        gained = ctx.hero.heal(max(1, round(ctx.hero.max_hp * HEAL_RATIO)))
        ctx.effect("heal", amount=gained)

    def draw(self, r, surface, x, y):
        r._gem(surface, x, y, (255, 95, 135), ITEM_R + 2)
        cx, cy = int(x), int(y) + 1
        for dx, dy, col in ((1, 1, (150, 30, 70)), (0, 0, WHITE)):           # shadow, then white cross
            pygame.draw.rect(surface, col, (cx - 2 + dx, cy - 6 + dy, 4, 12), border_radius=1)
            pygame.draw.rect(surface, col, (cx - 6 + dx, cy - 2 + dy, 12, 4), border_radius=1)


@register
class SkillItem(ItemType):
    """After the volley ends, the hero picks 1 of 3 random skills."""
    kind = ITEM_SKILL

    def on_collect(self, ball, ctx):
        ctx.manager.skills_collected += 1
        ctx.effect("skill_item")

    def draw(self, r, surface, x, y):
        c = (int(x), int(y))
        R = ITEM_R + 3                                   # a little bigger: it's the rare one
        pulse = int(2 * math.sin(pygame.time.get_ticks() / 150))
        pygame.draw.circle(surface, (255, 230, 120), c, R + 4 + pulse, 2)    # pulsing ring
        r._gem(surface, x, y, (255, 200, 60), R)
        r._star(surface, x, y + 1, 8, 3.5, (120, 65, 0))
