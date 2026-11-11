import math
import random

import pygame

from .settings import (
    ATTACK_FX_TIME, BALL_R, BG, BOSS_H, BOTTOM_STRIP_Y,
    CELL, COLS, FLOOR_Y, GRID_LINE, GRID_TOP, H, HERO_R, HERO_Y,
    State, W, WHITE, BLOCK_FLASH, BALL_NORMAL, SKILL_LIGHTNING,
    block_color
)
from .items import ITEMS
from .skills import SKILLS
from .systems import aim_angle


def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def ball_color(kind):
    return SKILLS[kind].color if kind in SKILLS else WHITE


class Renderer:
    """Draws the game from its current state."""

    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("arial", 18, bold=True)
        self.big = pygame.font.SysFont("arial", 44, bold=True)
        self.small = pygame.font.SysFont("arial", 14, bold=True)
        self.mid = pygame.font.SysFont("arial", 30, bold=True)
        self.tiny = pygame.font.SysFont("arial", 11, bold=True)

    def _text(self, surface, value, font, color, center=None, topleft=None):
        image = font.render(value, True, color)
        rect = image.get_rect()
        if center is not None:
            rect.center = center
        if topleft is not None:
            rect.topleft = topleft
        surface.blit(image, rect)

    def _bar(self, surface, x, y, w, h, ratio, color, back=True):
        if back:
            pygame.draw.rect(surface, (50, 50, 60), (x, y, w, h), border_radius=4)
        pygame.draw.rect(surface, color, (x, y, int(w * max(0, ratio)), h),
                         border_radius=4)

    def _star(self, surface, x, y, outer, inner, color):
        pts = []
        for i in range(10):
            r = outer if i % 2 == 0 else inner
            a = -math.pi / 2 + i * math.pi / 5
            pts.append((x + math.cos(a) * r, y + math.sin(a) * r))
        pygame.draw.polygon(surface, color, pts)

    def _badge(self, surface, center, color, value):
        pygame.draw.circle(surface, color, center, 8)
        pygame.draw.circle(surface, WHITE, center, 8, 1)
        self._text(surface, str(value), self.tiny, (20, 20, 20), center=center)

    @staticmethod
    def _zigzag(a, b, segments=5, amp=7):
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy) or 1
        nx, ny = -dy / length, dx / length
        pts = [a]
        for i in range(1, segments):
            t = i / segments
            off = random.uniform(-amp, amp)
            pts.append((a[0] + dx * t + nx * off, a[1] + dy * t + ny * off))
        pts.append(b)
        return pts

    def _draw_block_status(self, s, block):
        r = block.rect
        if block.frozen > 0:
            pygame.draw.rect(s, (225, 246, 255), r, 2, border_radius=6)
            self._badge(s, (r.right - 9, r.top + 9), (150, 215, 255), block.frozen)
        if block.burn_turns > 0:
            pygame.draw.rect(s, (255, 140, 40), r, 2, border_radius=6)
            for i in range(3):                       # flickering flames
                fx = r.left + 12 + i * 16 + random.randint(-2, 2)
                fy = r.top + 2 - random.randint(0, 6)
                pygame.draw.circle(s, (255, 170, 50), (fx, fy), random.randint(3, 5))
                pygame.draw.circle(s, (255, 235, 120), (fx, fy + 1), 2)
            self._badge(s, (r.left + 9, r.top + 9), (255, 150, 60), block.burn_turns)

    def _draw_skill_badges(self, s, game):
        pending = game.pending_skills + game.balls.skills_collected
        if not game.hero.skills and not pending:
            return
        x = 8
        for kind, count in game.hero.skills.items():
            pygame.draw.rect(s, (20, 20, 30), (x, 111, 50, 18), border_radius=9)
            pygame.draw.circle(s, ball_color(kind), (x + 10, 120), 6)
            pygame.draw.circle(s, WHITE, (x + 10, 120), 6, 1)
            self._text(s, f"x{count}", self.small, WHITE, center=(x + 33, 120))
            x += 54
        if pending:                                  # skill picks waiting
            pygame.draw.rect(s, (20, 20, 30), (x, 111, 50, 18), border_radius=9)
            self._star(s, x + 10, 120, 7, 3, (255, 205, 60))
            self._text(s, f"x{pending}", self.small, (255, 215, 70), center=(x + 33, 120))

    def draw(self, game):
        s = game.canvas
        #s.fill(BG)

        for col in range(1, COLS):
            pygame.draw.line(s, GRID_LINE, (col * CELL, GRID_TOP), (col * CELL, FLOOR_Y))

        self._draw_boss(s, game)
        self._draw_fast_forward(s, game)

        for block in game.field.blocks:
            ratio = block.hp / max(1, block.max_hp)
            color = block_color(ratio)
            if block.frozen > 0:
                color = mix(color, (170, 225, 255), 0.6)
            if block.flash > 0:
                color = mix(color, WHITE, 0.85 * block.flash / BLOCK_FLASH)
            pygame.draw.rect(s, color, block.rect, border_radius=6)
            self._text(s, str(block.hp), self.font, (20, 20, 20), center=block.rect.center)
        for block in game.field.blocks:              # second pass: nothing covers the status
            self._draw_block_status(s, block)

        for bolt in game.bolts:                      # lightning arcs
            k = 1 - bolt["t"] / bolt["life"]
            glow = mix(BG, SKILLS[SKILL_LIGHTNING].color, k)
            core = mix(BG, WHITE, k)
            for target in bolt["targets"]:
                pts = self._zigzag(bolt["src"], target)
                pygame.draw.lines(s, glow, False, pts, 5)
                pygame.draw.lines(s, core, False, pts, 2)

        for particle in game.particles:
            t = particle["life"] / particle["max"]
            size = max(1, int(particle["size"] * t))
            color = mix(BG, particle["color"], t)
            pygame.draw.rect(s, color, (int(particle["x"] - size / 2),
                                        int(particle["y"] - size / 2), size, size))

        for item in game.field.items:
            x, y = item.pos
            ITEMS[item.kind].draw(self, s, x, y)

        pygame.draw.line(s, (120, 120, 140), (0, FLOOR_Y), (W, FLOOR_Y), 2)
        atk = game.boss.atk_fx / ATTACK_FX_TIME
        if atk > 0:
            beam = mix(BG, (255, 70, 50), atk)
            pygame.draw.line(s, beam, (W // 2, BOSS_H), (int(game.hero.x), HERO_Y),
                             int(2 + 8 * atk))
            ring = mix(BG, (255, 120, 90), atk)
            pygame.draw.circle(s, ring, (int(game.hero.x), HERO_Y),
                               int(HERO_R + (1 - atk) * 30), 3)

        hurt_blink = game.hurt_fx > 0 and int(game.hurt_fx * 20) % 2 == 0
        hero_color = (255, 80, 80) if hurt_blink else (80, 200, 255)
        pygame.draw.circle(s, hero_color, (int(game.hero.x), HERO_Y), HERO_R)
        pygame.draw.circle(s, WHITE, (int(game.hero.x), HERO_Y), HERO_R, 2)

        if game.state == State.AIM:
            angle = aim_angle(game.hero.x, game.display.mouse_pos())
            for i in range(1, 16):
                px = game.hero.x + math.cos(angle) * i * 26
                py = HERO_Y - HERO_R - math.sin(angle) * i * 26
                if 0 < px < W and py > BOSS_H:
                    pygame.draw.circle(s, (200, 200, 220), (int(px), int(py)), 2)
            #pygame.draw.rect(s, (40, 40, 56), (0, BOTTOM_STRIP_Y, W, 2))

        for ball in game.balls.balls:
            pos = (int(ball.x), int(ball.y))
            if ball.kind == BALL_NORMAL:
                pygame.draw.circle(s, WHITE, pos, BALL_R)
            else:                                    # special ball: coloured body, white core
                pygame.draw.circle(s, ball_color(ball.kind), pos, BALL_R + 1)
                pygame.draw.circle(s, WHITE, pos, BALL_R + 1, 1)
                pygame.draw.circle(s, WHITE, pos, 2)

        hp_color = (255, 120, 120) if game.hurt_fx > 0 else WHITE
        self._text(s, f"HP {game.hero.hp}/{game.hero.max_hp}", self.small, hp_color,
                   topleft=(10, H - 22))
        self._bar(s, 100, H - 20, 140, 10,
                  game.hp_ghost / game.hero.max_hp, (255, 170, 60))
        self._bar(s, 100, H - 20, 140, 10,
                  game.hero.hp / game.hero.max_hp, (90, 220, 120), back=False)
        self._text(s, f"Balls {game.hero.balls}   Dmg {game.hero.damage}   Turn {game.turn}",
                   self.small, WHITE, topleft=(260, H - 22))

        self._draw_skill_badges(s, game)

        for floater in game.floaters:
            image = self.mid.render(floater["text"], True, floater["color"])
            image.set_alpha(int(255 * (1 - floater["t"] / floater["life"])))
            s.blit(image, image.get_rect(center=(floater["x"], floater["y"])))

        if game.state == State.WIN:
            self._overlay(s, "STAGE CLEAR!",
                          "Hero upgraded (+HP, +balls)\nSPACE / click for next stage",
                          (120, 255, 160))
        elif game.state == State.LOSE:
            self._overlay(s, "GAME OVER",
                          f"Reached stage {game.stage}\nPress R to restart",
                          (255, 100, 100))

        ox = oy = 0
        if game.shake > 0:
            power = int(game.shake_pow * game.shake / game.shake_len)
            ox, oy = random.randint(-power, power), random.randint(-power, power)
        #self.screen.fill((0, 0, 0))
        self.screen.blit(s, (ox, oy))
        #pygame.display.flip()

    def _draw_boss(self, surface, game):
        attack_ratio = game.boss.atk_fx / ATTACK_FX_TIME
        if game.boss.flash > 0:
            boss_color = WHITE
        else:
            boss_color = mix((170, 50, 70), (255, 60, 30), attack_ratio)
        eye_color = mix((255, 220, 0), (255, 40, 40), attack_ratio)
        pygame.draw.rect(surface, boss_color, game.boss.rect)
        for dx in (-50, 50):
            pygame.draw.circle(surface, (20, 20, 20), (W // 2 + dx, 45), 14)
            pygame.draw.circle(surface, eye_color, (W // 2 + dx, 45), 6)
        self._text(surface, f"BOSS  Stage {game.stage}   ATK {game.boss.attack}",
                   self.small, WHITE, center=(W // 2, 78))
        self._bar(surface, 20, 90, W - 40, 12,
                  game.boss.hp / game.boss.max_hp, (255, 90, 90))
        self._text(surface, f"{game.boss.hp}/{game.boss.max_hp}", self.small,
                   WHITE, center=(W // 2, 96))

    def _draw_fast_forward(self, surface, game):
        if game.state in (State.AIM, State.ATTACK):
            active = game.ff_active()
            pygame.draw.rect(surface, (90, 220, 120) if active else (50, 50, 66),
                             game.ff_button, border_radius=6)
            pygame.draw.rect(surface, (200, 200, 220), game.ff_button, 2,
                             border_radius=6)
            self._text(surface, "FAST >>", self.small,
                       (10, 40, 10) if active else (230, 230, 240),
                       center=game.ff_button.center)

    def _overlay(self, surface, title, subtitle, color):
        veil = pygame.Surface((W, H), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 170))
        surface.blit(veil, (0, 0))
        self._text(surface, title, self.big, color, center=(W // 2, H // 2 - 40))
        for i, line in enumerate(subtitle.split("\n")):
            self._text(surface, line, self.font, (240, 240, 240),
                       center=(W // 2, H // 2 + 10 + i * 28))
