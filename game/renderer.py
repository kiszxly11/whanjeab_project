import math
import random

import pygame
from pygame import surface

import game

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
        self._block_shadow = pygame.Surface((CELL - 4, CELL - 4), pygame.SRCALPHA)
        pygame.draw.rect(self._block_shadow, (10, 20, 50, 90),
                         self._block_shadow.get_rect(), border_radius=10)
        self.big = pygame.font.SysFont("arial", 44, bold=True)
        self._boss_panel = pygame.Surface((W, BOSS_H))
        for y in range(BOSS_H):
            pygame.draw.line(self._boss_panel, mix((150, 42, 66), (92, 24, 48), y / BOSS_H),
                     (0, y), (W, y))
            pygame.draw.line(self._boss_panel, (205, 95, 110), (0, 0), (W, 0), 1)                 # top light edge
            pygame.draw.line(self._boss_panel, (55, 12, 28), (0, BOSS_H - 2), (W, BOSS_H - 2), 3)  # bottom dark edge
        self._hero_shadow = pygame.Surface((HERO_R * 2 + 10, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(self._hero_shadow, (0, 0, 0, 110), self._hero_shadow.get_rect())
        bar_h = H - FLOOR_Y
        self._bar_bg = pygame.Surface((W, bar_h))
        for y in range(bar_h):
            pygame.draw.line(self._bar_bg, mix((40, 40, 60), (18, 18, 30), y / bar_h), (0, y), (W, y))
        self._gem_shadows = {}
        self._boss_tint = pygame.Surface((W, BOSS_H))                                        # red flash when it attacks
        self._boss_tint.fill((255, 60, 40))
        self.small = pygame.font.SysFont("arial", 14, bold=True)
        self.mid = pygame.font.SysFont("arial", 30, bold=True)
        self.tiny = pygame.font.SysFont("arial", 11, bold=True)
        self.bar_font = pygame.font.SysFont("arial", 15, bold=True)     # HP numbers on the bars
        self.title_font = pygame.font.SysFont("arial", 17, bold=True)   # "BOSS Stage ..." line
        self._outline_cache = {}
        self._aim_cache = {}

    def _text(self, surface, value, font, color, center=None, topleft=None):
        image = font.render(value, True, color)
        rect = image.get_rect()
        if center is not None:
            rect.center = center
        if topleft is not None:
            rect.topleft = topleft
        surface.blit(image, rect)

    def _outlined(self, surface, value, font, color, center, outline=(12, 8, 20), width=2):
        """Text with a dark outline so it stays readable on any bar or background."""
        key = (value, id(font), color, outline, width)
        image = self._outline_cache.get(key)
        if image is None:
            body = font.render(value, True, color)
            edge = font.render(value, True, outline)
            image = pygame.Surface((body.get_width() + 2 * width, body.get_height() + 2 * width),
                                   pygame.SRCALPHA)
            for dx in range(-width, width + 1):
                for dy in range(-width, width + 1):
                    if dx * dx + dy * dy <= width * width + 1:
                        image.blit(edge, (width + dx, width + dy))
            image.blit(body, (width, width))
            if len(self._outline_cache) > 300:
                self._outline_cache.clear()
            self._outline_cache[key] = image
        surface.blit(image, image.get_rect(center=center))

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

    def aim_color(self, game):
        key = game.current_theme
        if key not in self._aim_cache:
            bg = game.assets.get(key)
            if bg is None:                                   # code-drawn fallback background
                self._aim_cache[key] = (200, 200, 220)
            else:
                area = pygame.Rect(0, GRID_TOP, W, FLOOR_Y - GRID_TOP)   # only the play area
                r, g, b = pygame.transform.average_color(bg, area)[:3]
                lum = 0.299 * r + 0.587 * g + 0.114 * b
                self._aim_cache[key] = (30, 30, 50) if lum > 140 else (235, 235, 250)
        return self._aim_cache[key]

    def _draw_block(self, s, block, color):
        r = block.rect
        s.blit(self._block_shadow, (r.x, r.y + 5))                        # soft drop shadow

        edge = mix(color, (0, 0, 0), 0.55)
        base = mix(color, (0, 0, 0), 0.30)
        pygame.draw.rect(s, base, r, border_radius=10)                    # darker bottom edge
        face = pygame.Rect(r.x, r.y, r.w, r.h - 6)
        pygame.draw.rect(s, color, face, border_radius=10)                # main face
        shine = pygame.Rect(r.x + 7, r.y + 5, r.w - 14, 6)
        pygame.draw.rect(s, mix(color, WHITE, 0.45), shine, border_radius=3)   # gloss strip
        pygame.draw.rect(s, edge, r, width=2, border_radius=10)           # outline

        cx, cy = face.center[0], face.center[1] + 3
        self._text(s, str(block.hp), self.font, (40, 30, 50), center=(cx + 1, cy + 2))  # text shadow
        self._text(s, str(block.hp), self.font, WHITE, center=(cx, cy))

    def _draw_hero(self, s, game, hurt_blink):
        x, y = int(game.hero.x), HERO_Y
        R = HERO_R
        body = (255, 80, 80) if hurt_blink else (80, 200, 255)

        sh = self._hero_shadow
        s.blit(sh, (x - sh.get_width() // 2, FLOOR_Y - sh.get_height() + 1))    # floor shadow

        pygame.draw.circle(s, (15, 25, 50), (x, y), R + 2)                      # dark halo: readable on busy backgrounds
        pygame.draw.circle(s, mix(body, (0, 0, 0), 0.35), (x, y + 2), R)        # lower edge
        pygame.draw.circle(s, body, (x, y), R)                                  # body
        pygame.draw.ellipse(s, mix(body, WHITE, 0.65),
                            (x - int(R * 0.64), y - int(R * 0.72), int(R * 0.64), int(R * 0.36)))   # gloss
        pygame.draw.circle(s, WHITE, (x, y), R, 2)                              # white rim

        # eyes look toward the aim direction (straight up outside the aim phase)
        angle = aim_angle(game.hero.x, game.display.mouse_pos()) if game.state == State.AIM else math.pi / 2
        px, py = math.cos(angle) * R * 0.12, -math.sin(angle) * R * 0.12
        ex, ey, er = int(R * 0.36), int(R * 0.08), max(3, int(R * 0.29))
        for sign in (-1, 1):
            cx, cy = x + sign * ex, y + ey
            pygame.draw.circle(s, WHITE, (cx, cy), er)
            pygame.draw.circle(s, (20, 20, 40), (cx + int(round(px * 2)), cy + int(round(py * 2))),
                            max(2, er // 2))

    def _draw_heart(self, s, cx, cy, color):
        pygame.draw.circle(s, color, (cx - 3, cy - 2), 4)
        pygame.draw.circle(s, color, (cx + 3, cy - 2), 4)
        pygame.draw.polygon(s, color, [(cx - 7, cy - 1), (cx + 7, cy - 1), (cx, cy + 7)])

    def _draw_chip(self, s, x, cy, icon, value):
        chip = pygame.Rect(x, cy - 11, 62, 22)
        pygame.draw.rect(s, (14, 14, 24), chip, border_radius=11)
        pygame.draw.rect(s, (70, 70, 95), chip, width=1, border_radius=11)
        ix = x + 13
        if icon == "ball":
            pygame.draw.circle(s, WHITE, (ix, cy), 5)
            pygame.draw.circle(s, (150, 150, 175), (ix, cy), 5, 1)
        elif icon == "dmg":                                      # little sword
            pygame.draw.line(s, (235, 240, 255), (ix - 1, cy + 1), (ix + 5, cy - 5), 3)
            pygame.draw.line(s, (255, 200, 80), (ix - 4, cy - 1), (ix, cy + 3), 2)
            pygame.draw.line(s, (200, 140, 60), (ix - 5, cy + 5), (ix - 2, cy + 2), 2)
        else:                                                    # clock
            pygame.draw.circle(s, (180, 190, 225), (ix, cy), 6, 2)
            pygame.draw.line(s, (180, 190, 225), (ix, cy), (ix, cy - 3), 1)
            pygame.draw.line(s, (180, 190, 225), (ix, cy), (ix + 3, cy), 1)
        self._text(s, str(value), self.small, WHITE, center=(x + 40, cy))

    def _draw_bottom_bar(self, s, game):
        s.blit(self._bar_bg, (0, FLOOR_Y))
        pygame.draw.line(s, (120, 120, 140), (0, FLOOR_Y), (W, FLOOR_Y), 2)
        cy = FLOOR_Y + (H - FLOOR_Y) // 2 + 1
        hero = game.hero

        # health: heart + bar (orange "ghost" shows recent damage, fill colour follows health)
        hurt = game.hurt_fx > 0
        self._draw_heart(s, 20, cy, (255, 100, 110))
        bar = pygame.Rect(36, cy - 10, 200, 20)
        pygame.draw.rect(s, (35, 35, 48), bar, border_radius=8)
        ratio = max(0.0, hero.hp / hero.max_hp)
        ghost = max(0.0, game.hp_ghost / hero.max_hp)
        inner = bar.w - 4
        if ghost > 0:
            pygame.draw.rect(s, (255, 170, 60),
                            (bar.x + 2, bar.y + 2, int(inner * ghost), bar.h - 4), border_radius=6)
        fill_w = int(inner * ratio)
        if fill_w > 0:
            col = (90, 220, 120) if ratio > 0.5 else (245, 190, 70) if ratio > 0.25 else (240, 80, 80)
            pygame.draw.rect(s, col, (bar.x + 2, bar.y + 2, fill_w, bar.h - 4), border_radius=6)
            if fill_w > 8:
                pygame.draw.rect(s, mix(col, WHITE, 0.5),
                                (bar.x + 5, bar.y + 3, fill_w - 6, 3), border_radius=2)
        pygame.draw.rect(s, (10, 10, 18), bar, width=2, border_radius=8)
        txt = f"{hero.hp}/{hero.max_hp}"
        self._outlined(s, txt, self.bar_font, (255, 150, 150) if hurt else WHITE, bar.center)

        # stat pills
        x = W - 3 * 62 - 2 * 6 - 10
        self._draw_chip(s, x, cy, "ball", hero.balls)
        self._draw_chip(s, x + 68, cy, "dmg", hero.damage)
        self._draw_chip(s, x + 136, cy, "turn", game.turn)

    def _gem(self, s, x, y, color, R):
        """Glossy round pickup: soft shadow, dark halo, lower edge, body, gloss, white rim."""
        cx, cy = int(x), int(y)
        sh = self._gem_shadows.get(R)
        if sh is None:
            sh = pygame.Surface((2 * R + 6, 2 * R + 6), pygame.SRCALPHA)
            pygame.draw.circle(sh, (10, 20, 50, 90), (sh.get_width() // 2, sh.get_height() // 2), R + 1)
            self._gem_shadows[R] = sh
        s.blit(sh, (cx - sh.get_width() // 2, cy - sh.get_height() // 2 + 4))

        pygame.draw.circle(s, (15, 25, 50), (cx, cy), R + 2)                  # dark halo
        pygame.draw.circle(s, mix(color, (0, 0, 0), 0.35), (cx, cy + 2), R)   # lower edge
        pygame.draw.circle(s, color, (cx, cy), R)                             # body
        pygame.draw.ellipse(s, mix(color, WHITE, 0.65),
                            (cx - int(R * 0.6), cy - int(R * 0.74), int(R * 0.7), int(R * 0.34)))  # gloss
        pygame.draw.circle(s, WHITE, (cx, cy), R, 2)                          # white rim

    def draw(self, game):
        s = game.canvas
        #s.fill(BG)

        #for col in range(1, COLS):
            #pygame.draw.line(s, GRID_LINE, (col * CELL, GRID_TOP), (col * CELL, FLOOR_Y))

        self._draw_boss(s, game)
        self._draw_fast_forward(s, game)

        for block in game.field.blocks:
            ratio = block.hp / max(1, block.max_hp)
            color = block_color(ratio)
            if block.frozen > 0:
                color = mix(color, (170, 225, 255), 0.6)
            if block.flash > 0:
                color = mix(color, WHITE, 0.85 * block.flash / BLOCK_FLASH)
            self._draw_block(s, block, color)
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
        self._draw_hero(s, game, hurt_blink)

        if game.state == State.AIM:
            angle = aim_angle(game.hero.x, game.display.mouse_pos())
            aim_col = self.aim_color(game)
            for i in range(1, 16):
                px = game.hero.x + math.cos(angle) * i * 26
                py = HERO_Y - HERO_R - math.sin(angle) * i * 26
                if 0 < px < W and py > BOSS_H:
                    pygame.draw.circle(s, aim_col, (int(px), int(py)), 2)
            #pygame.draw.rect(s, (40, 40, 56), (0, BOTTOM_STRIP_Y, W, 2))

        for ball in game.balls.balls:
            pos = (int(ball.x), int(ball.y))
            if ball.kind == BALL_NORMAL:
                pygame.draw.circle(s, WHITE, pos, BALL_R)
            else:                                    # special ball: coloured body, white core
                pygame.draw.circle(s, ball_color(ball.kind), pos, BALL_R + 1)
                pygame.draw.circle(s, WHITE, pos, BALL_R + 1, 1)
                pygame.draw.circle(s, WHITE, pos, 2)

        self._draw_bottom_bar(s, game)

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
        boss = game.boss
        atk = boss.atk_fx / ATTACK_FX_TIME

        surface.blit(self._boss_panel, (0, 0))
        if atk > 0:                                              # whole panel flushes red on attack
            self._boss_tint.set_alpha(int(90 * atk))
            surface.blit(self._boss_tint, (0, 0))

        self._draw_boss_face(surface, W // 2, 38, boss.flash > 0, atk)

        title = f"BOSS  Stage {game.stage}   ATK {boss.attack}"
        self._outlined(surface, title, self.title_font, WHITE, (W // 2, 77), outline=(40, 10, 25))

        # health bar: dark track, red fill with a shine, outline
        bar = pygame.Rect(20, 88, W - 40, 19)
        pygame.draw.rect(surface, (35, 12, 24), bar, border_radius=8)
        ratio = max(0.0, boss.hp / boss.max_hp)
        fill_w = int((bar.w - 4) * ratio)
        if fill_w > 0:
            fill = pygame.Rect(bar.x + 2, bar.y + 2, fill_w, bar.h - 4)
            pygame.draw.rect(surface, (255, 85, 85), fill, border_radius=6)
            if fill_w > 8:
                pygame.draw.rect(surface, mix((255, 85, 85), WHITE, 0.5),
                                (fill.x + 3, fill.y + 1, fill_w - 6, 3), border_radius=2)
        pygame.draw.rect(surface, (15, 5, 12), bar, width=2, border_radius=8)
        hp_text = f"{boss.hp}/{boss.max_hp}"
        self._outlined(surface, hp_text, self.bar_font, WHITE, (W // 2, bar.centery), outline=(40, 10, 25))

    def _draw_boss_face(self, s, cx, cy, flash, atk):
        skin = WHITE if flash else (84, 40, 78)                  # whole head flashes white when hit
        outline = (30, 12, 30)
        bone, bone_edge = (238, 228, 200), (150, 135, 110)

        for sign in (-1, 1):                                     # horns
            horn = [(cx + sign * 44, cy - 10), (cx + sign * 56, cy - 34), (cx + sign * 24, cy - 26)]
            pygame.draw.polygon(s, bone, horn)
            pygame.draw.polygon(s, bone_edge, horn, 2)

        head = pygame.Rect(0, 0, 104, 56)
        head.center = (cx, cy)
        pygame.draw.rect(s, mix(skin, (0, 0, 0), 0.45), head.move(0, 3), border_radius=16)  # lower edge
        pygame.draw.rect(s, skin, head, border_radius=16)
        pygame.draw.rect(s, mix(skin, WHITE, 0.3),
                        (head.x + 12, head.y + 4, head.w - 24, 4), border_radius=2)        # gloss
        pygame.draw.rect(s, outline, head, width=2, border_radius=16)

        eye = mix((255, 220, 0), (255, 40, 40), atk)             # eyes turn red when attacking
        for sign in (-1, 1):
            ex, ey = cx + sign * 22, cy - 4
            pygame.draw.circle(s, (20, 8, 20), (ex, ey), 11)
            pygame.draw.circle(s, eye, (ex, ey), 7)
            pygame.draw.circle(s, (20, 8, 20), (ex, ey), 3)
            pygame.draw.line(s, outline, (ex + sign * 12, ey - 14), (ex - sign * 10, ey - 7), 4)  # angry brow

        mouth = pygame.Rect(cx - 24, cy + 12, 48, 11 + int(6 * atk))   # opens wider when attacking
        pygame.draw.rect(s, (30, 10, 25), mouth, border_radius=4)
        for i in range(4):                                       # teeth
            x = mouth.x + 4 + i * 11
            pygame.draw.polygon(s, bone, [(x, mouth.y), (x + 9, mouth.y), (x + 4, mouth.y + 6)])

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