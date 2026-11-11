"""All skills live here.

A skill is a special ball the hero gets +1 of every volley after picking it.
To add a new one, write a class below and decorate it with @register. That is all:
it then shows up on the choice screen, in the HUD, in the hero's volley and gets its
own icon. Nothing else in the project needs to change.

    @register
    class PoisonBall(Skill):
        kind = "poison"                       # unique id (also stored on Ball.kind)
        name = "Poison Ball"
        desc = "One line shown on the choice card."
        color = (120, 220, 80)

        def on_block_hit(self, ball, blk, ctx):     # a ball of this kind hit a block
            ...
        def on_boss_hit(self, ball, boss, ctx):     # return True to keep the ball alive
            return False
        def on_turn_end(self, field, hero):         # once per turn after the volley
            return []                               # [(center, hp_ratio)] of blocks it killed
        def draw_glyph(self, surface, cx, cy, k):   # white symbol inside the round icon
            ...

Hooks (all optional) get a HitContext: ctx.hero, ctx.field, ctx.hurt_block(blk, amount),
ctx.destroy(blk, damage) and ctx.effect(kind, **data) for visual-only events.
Tuning numbers belong in settings.py.
"""
import math

import pygame

from .settings import (BALL_R, BURN_DAMAGE_RATIO, BURN_TURNS, FREEZE_TURNS,
                       SKILL_BOUNCE, SKILL_FIRE, SKILL_ICE,
                       SKILL_LIGHTNING, WHITE, block_color)


# --------------------------------------------------------------- plumbing
class HitContext:
    """What a skill hook may touch while a ball hit something."""

    def __init__(self, hero, field, on_block_break=None, on_effect=None):
        self.hero = hero
        self.field = field
        self.on_block_break = on_block_break
        self.on_effect = on_effect

    def hurt_block(self, blk, amount):
        blk.take_damage(amount)
        if blk.dead:
            self.destroy(blk, amount)

    def destroy(self, blk, damage):
        """Remove a dead block; `damage` is the hit that killed it (for the colour)."""
        if self.on_block_break:
            ratio = min(1.0, (blk.hp + damage) / max(1, blk.max_hp))
            self.on_block_break(blk.rect.center, block_color(ratio))
        if blk in self.field.blocks:
            self.field.blocks.remove(blk)

    def effect(self, kind, **data):
        if self.on_effect:
            self.on_effect(kind, **data)


class Skill:
    kind = ""
    name = ""
    desc = ""
    color = WHITE

    def on_block_hit(self, ball, blk, ctx):
        """Called after the ball damaged `blk` (check blk.dead: it may be gone)."""

    def on_boss_hit(self, ball, boss, ctx):
        """Called after the ball damaged the boss. Return True to keep the ball alive."""
        return False

    def on_turn_end(self, field, hero):
        """Called once per turn after the volley. Return [(center, hp_ratio)] of kills."""
        return []

    def draw_glyph(self, surface, cx, cy, k):
        """White symbol drawn inside the round icon. k = icon radius / 26."""

    # ---- shared helpers
    def draw_icon(self, surface, cx, cy, r):
        pygame.draw.circle(surface, self.color, (cx, cy), r)
        pygame.draw.circle(surface, WHITE, (cx, cy), r, 3)
        self.draw_glyph(surface, cx, cy, r / 26.0)

    @staticmethod
    def _pts(cx, cy, k, points):
        return [(cx + x * k, cy + y * k) for x, y in points]


SKILLS = {}                       # kind -> Skill instance, in registration order


def register(cls):
    SKILLS[cls.kind] = cls()
    return cls


def run_turn_end(field, hero):
    """Run every skill's on_turn_end; returns all blocks they killed."""
    killed = []
    for skill in SKILLS.values():
        killed.extend(skill.on_turn_end(field, hero))
    return killed


# ----------------------------------------------------------------- skills
@register
class FireBall(Skill):
    kind = SKILL_FIRE
    name = "Fire Ball"
    desc = f"Sets the block on fire. It burns for {BURN_TURNS} turns and takes damage every turn."
    color = (255, 110, 40)

    def on_block_hit(self, ball, blk, ctx):
        if not blk.dead:
            blk.ignite(BURN_TURNS, max(1, math.ceil(ctx.hero.damage * BURN_DAMAGE_RATIO)))

    def on_turn_end(self, field, hero):
        killed = []
        for blk in field.blocks[:]:
            if blk.burn_turns <= 0:
                continue
            ratio = min(1.0, blk.hp / max(1, blk.max_hp))
            blk.take_damage(blk.burn_dmg)
            blk.burn_turns -= 1
            if blk.dead:
                killed.append((blk.rect.center, ratio))
                field.blocks.remove(blk)
        return killed

    def draw_glyph(self, surface, cx, cy, k):
        pygame.draw.polygon(surface, WHITE, self._pts(cx, cy, k, [
            (0, -15), (8, -4), (11, 6), (0, 14), (-11, 6), (-8, -3), (-3, -7)]))


@register
class IceBall(Skill):
    kind = SKILL_ICE
    name = "Ice Ball"
    desc = f"Freezes the block it hits. It will not move down for {FREEZE_TURNS} turns."
    color = (90, 190, 255)

    def on_block_hit(self, ball, blk, ctx):
        if not blk.dead:
            blk.freeze(FREEZE_TURNS)      # Field.move_down honours blk.frozen

    def draw_glyph(self, surface, cx, cy, k):
        for i in range(3):
            a = math.radians(i * 60 + 90)
            dx, dy = math.cos(a) * 14 * k, math.sin(a) * 14 * k
            pygame.draw.line(surface, WHITE, (cx - dx, cy - dy), (cx + dx, cy + dy), 3)


@register
class LightningBall(Skill):
    kind = SKILL_LIGHTNING
    name = "Lightning Ball"
    desc = "Also damages every block around the block it hits."
    color = (240, 200, 30)

    def on_block_hit(self, ball, blk, ctx):
        around = [o for o in ctx.field.blocks
                  if o is not blk
                  and abs(o.col - blk.col) <= 1 and abs(o.row - blk.row) <= 1]
        if not around:
            return
        ctx.effect("bolt", src=blk.rect.center, targets=[o.rect.center for o in around])
        for o in around:
            ctx.hurt_block(o, ctx.hero.damage)

    def draw_glyph(self, surface, cx, cy, k):
        pygame.draw.polygon(surface, WHITE, self._pts(cx, cy, k, [
            (5, -15), (-8, 2), (0, 2), (-5, 15), (9, -4), (1, -4)]))


@register
class BossBounceBall(Skill):
    kind = SKILL_BOUNCE
    name = "Boss Bounce Ball"
    desc = "Bounces off the boss every time it touches it. Only disappears when it hits the floor."
    color = (190, 110, 255)

    def on_boss_hit(self, ball, boss, ctx):
        ball.vy = abs(ball.vy)            # send it back down, as many times as it comes back
        # (the floor is the only thing that removes this ball)
        ball.y = boss.rect.bottom + BALL_R
        ctx.effect("bounce", pos=(ball.x, boss.rect.bottom))
        return True

    def draw_glyph(self, surface, cx, cy, k):
        pygame.draw.line(surface, WHITE, (cx - 14 * k, cy - 13 * k), (cx + 14 * k, cy - 13 * k), 4)
        pygame.draw.lines(surface, WHITE, False,
                          self._pts(cx, cy, k, [(-12, 12), (0, -5), (12, 12)]), 3)
