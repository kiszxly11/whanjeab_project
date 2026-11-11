import math

from ..entities import Ball
from ..settings import (BALL_NORMAL, BALL_R, BALL_SPEED, FIRE_INTERVAL,
                        FLOOR_Y, HERO_R, HERO_Y, ITEM_PLUS, ITEM_R, ITEM_SKILL,
                        W, block_color)
from ..skills import SKILLS, HitContext


class BallManager:
    """Fires volleys and handles ball movement and every ball collision.

    Optional callbacks (all passed to update()):
      on_boss_hit()                 a ball damaged the boss
      on_block_break(pos, color)    a block was destroyed
      on_effect(kind, **data)       visual-only events: 'bolt', 'bounce', 'skill_item'
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self.balls = []
        self.queue = []                   # kinds still waiting to be fired
        self.fire_timer = 0.0
        self.fire_x = 0.0
        self.angle = math.pi / 2
        self.extra_balls = 0              # collected '+1' items, applied next round
        self.skills_collected = 0         # collected skill items, offered after the volley

    # ----------------------------------------------------------- shooting
    def start_volley(self, hero, angle):  # Ball Shooting
        self.balls = []
        self.angle = angle
        # special balls go first, then the normal ones
        self.queue = hero.special_balls() + [BALL_NORMAL] * hero.balls
        self.fire_x = hero.x
        self.fire_timer = 0.0

    @property
    def to_fire(self):
        return len(self.queue)

    @property
    def finished(self):
        """True when every ball has been fired and has hit the floor."""
        return not self.queue and not self.balls

    def _spawn_ball(self):
        kind = self.queue.pop(0)
        vx = math.cos(self.angle) * BALL_SPEED
        vy = -math.sin(self.angle) * BALL_SPEED
        self.balls.append(Ball(self.fire_x, HERO_Y - HERO_R, vx, vy, kind))

    # ------------------------------------------------------------- update
    def update(self, dt, hero, boss, field, on_boss_hit=None, on_block_break=None,
               on_effect=None):
        if self.queue:
            self.fire_timer -= dt
            while self.queue and self.fire_timer <= 0:
                self._spawn_ball()
                self.fire_timer += FIRE_INTERVAL

        for ball in self.balls[:]:        # Multiple Ball Management
            self._step_ball(ball, dt, hero, boss, field,
                            on_boss_hit, on_block_break, on_effect)
        self.balls = [b for b in self.balls if b.active]

    def _step_ball(self, ball, dt, hero, boss, field,
                   on_boss_hit=None, on_block_break=None, on_effect=None):
        dist = BALL_SPEED * dt
        steps = max(1, int(dist // 3) + 1)        # sub-steps avoid tunnelling
        h = dt / steps
        for _ in range(steps):
            ball.x += ball.vx * h                 # Ball Movement
            ball.y += ball.vy * h
            self._collide_walls(ball)
            self._collide_boss(ball, hero, boss, on_boss_hit, on_effect)
            if not ball.active:
                return
            self._collide_floor(ball)
            if not ball.active:
                return
            self._collect_items(ball, field, on_effect)
            self._collide_blocks(ball, hero, field, on_block_break, on_effect)

    # --------------------------------------------------------- collisions
    @staticmethod
    def _collide_walls(b):                # Wall Collision Detection and Bounce
        if b.x - BALL_R < 0:
            b.x = BALL_R
            b.vx = abs(b.vx)
        elif b.x + BALL_R > W:
            b.x = W - BALL_R
            b.vx = -abs(b.vx)

    @staticmethod
    def _collide_boss(b, hero, boss, on_boss_hit=None, on_effect=None):
        """Boss Collision Detection and Damage.

        The ball is absorbed unless its skill's on_boss_hit keeps it alive (bounce).
        """
        if b.y - BALL_R >= boss.rect.bottom:
            return
        boss.take_damage(hero.damage)
        if on_boss_hit:
            on_boss_hit()
        skill = SKILLS.get(b.kind)
        if not (skill and skill.on_boss_hit(b, boss, HitContext(hero, None, None, on_effect))):
            b.active = False

    @staticmethod
    def _collide_floor(b):                # Floor Collision / Ball Removal
        if b.y + BALL_R >= FLOOR_Y:
            b.active = False

    def _collide_blocks(self, b, hero, field, on_block_break=None, on_effect=None):
        """Block Collision Detection and Damage (+ skill-ball effects)."""
        for blk in field.blocks:
            r = blk.rect
            cx = max(r.left, min(b.x, r.right))
            cy = max(r.top, min(b.y, r.bottom))
            dx, dy = b.x - cx, b.y - cy
            d2 = dx * dx + dy * dy
            if d2 >= BALL_R * BALL_R:
                continue
            if d2 == 0:                           # centre is inside the block
                ox = min(b.x - r.left, r.right - b.x)
                oy = min(b.y - r.top, r.bottom - b.y)
                if ox < oy:
                    nx, ny = (-1 if b.x < r.centerx else 1), 0
                else:
                    nx, ny = 0, (-1 if b.y < r.centery else 1)
            else:
                d = math.sqrt(d2)
                nx, ny = dx / d, dy / d
            dot = b.vx * nx + b.vy * ny
            if dot < 0:                           # reflect velocity
                b.vx -= 2 * dot * nx
                b.vy -= 2 * dot * ny
            b.x = cx + nx * (BALL_R + 0.1)
            b.y = cy + ny * (BALL_R + 0.1)

            ctx = HitContext(hero, field, on_block_break, on_effect)
            blk.take_damage(hero.damage)
            if blk.dead:
                ctx.destroy(blk, hero.damage)
            skill = SKILLS.get(b.kind)
            if skill:                             # fire / ice / lightning ... effects
                skill.on_block_hit(b, blk, ctx)
            break                                 # one block per sub-step

    def _collect_items(self, b, field, on_effect=None):   # Special items
        for it in field.items[:]:
            ix, iy = it.pos
            if math.hypot(b.x - ix, b.y - iy) < BALL_R + ITEM_R:
                field.items.remove(it)
                if it.kind == ITEM_PLUS:
                    self.extra_balls += 1
                elif it.kind == ITEM_SKILL:
                    self.skills_collected += 1
                    if on_effect:
                        on_effect("skill_item", pos=(ix, iy))
                else:                             # multiply the ball (children keep its kind)
                    ang = math.atan2(b.vy, b.vx)
                    for off in (-0.35, 0.35):
                        a = ang + off
                        self.balls.append(Ball(b.x, b.y,
                                               math.cos(a) * BALL_SPEED,
                                               math.sin(a) * BALL_SPEED,
                                               b.kind))
