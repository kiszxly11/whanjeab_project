import math
import random
import sys
import pygame
import os

from .entities import Boss, Hero
from .renderer import Renderer
from .settings import (
    ATTACK_FX_TIME, BOTTOM_STRIP_Y, END_PHASE_DELAY, FF_SPEED, FPS, H,
    HERO_MOVE_SPEED, HERO_R, HERO_Y, HIT_SHAKE_POWER, HIT_SHAKE_TIME, MAX_PARTICLES,
    PARTICLE_COUNT, SHAKE_POWER, SHAKE_TIME, TITLE, W, State,
    BOLT_TIME, SKILL_BOUNCE, SKILL_CHOICES, SKILL_LIGHTNING, SKILL_PICK_DELAY,
    block_color
)
from .skills import SKILLS, run_turn_end
from .systems import BallManager, Field, aim_angle
from .display import Display
from .ui import UIManager, load_assets, draw_game_field, draw_main_menu_bg

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.display = Display(W, H)      # real window, scaled to fit the screen
        self.screen = self.display.surface
        self.canvas = pygame.Surface((W, H),pygame.SRCALPHA)
        self.clock = pygame.time.Clock()
        self.renderer = Renderer(self.screen)
        
        # โหลดเฉพาะภาพพื้นหลัง (ถ้ามี)
        self.assets = load_assets(W, H)
        
        self.ff_button = pygame.Rect(W - 80, 8, 72, 26)
        self.ff = False

        self.app_state = 'MENU'  
        self.ui = UIManager(W, H, self)

        self.field = Field()
        self.balls = BallManager()
        
        self.new_game()

    def go_home(self):
        self.app_state = 'MENU'
        
    def resume_game(self):
        self.app_state = 'PLAYING'
        
    def pause_game(self):
        if self.app_state == 'PLAYING':
            self.app_state = 'PAUSE_SCREEN'

    def next_stage(self):
        self.stage += 1
        self.hero.level_up()
        self.start_stage()
        self.app_state = 'PLAYING'
        self.open_skill_choice()          # a skill item collected on the winning volley

    def retry_game(self):
        self.new_game()
        self.app_state = 'PLAYING'

    def start_from_menu(self):
        self.new_game()
        self.app_state = 'PLAYING'

    def open_info(self):
        self.app_state = 'INFO_SCREEN'

    def open_settings(self):
        self.app_state = 'SETTINGS_SCREEN'

    def close_modal(self):
        self.app_state = 'MENU'

    def new_game(self):
        self.hero = Hero()
        self.hurt_fx = 0.0
        self.dragging = False
        self.shake = 0.0
        self.shake_len = 1.0
        self.shake_pow = 0
        self.particles = []
        self.floaters = []
        self.bolts = []                   # lightning visuals
        self.pending_skills = 0           # skill items collected, choices still owed
        self.skill_delay = 0.0
        self.hp_ghost = self.hero.hp
        self.stage = 1
        self.start_stage()

    def start_stage(self):
        self.boss = Boss(self.stage)
        self.field.reset()
        self.balls.reset()
        self.turn = 1
        self.end_timer = 0.0
        self.state = State.AIM
        self.ff = False
        for _ in range(3):
            self.field.move_down()
            self.field.spawn_row(self.turn, self.stage)
        
        # สุ่มภาพพื้นหลัง ถ้ามีไฟล์ภาพใน assets ก็ใช้ภาพ ถ้าไม่มีใช้แบบวาดโค้ด
        bg_keys = [k for k in self.assets.keys() if k.startswith('bg_') and k != 'bg_menu']
        if bg_keys:
            self.current_theme = random.choice(bg_keys)
        else:
            self.current_theme = random.choice(['Volcano', 'Snow', 'Garden', 'Forest', 'City'])

    # ------------------------------------------------------------- skills
    def open_skill_choice(self):
        """Show the pick-1-of-3 screen if a skill item was collected."""
        if self.pending_skills <= 0:
            return False
        self.pending_skills -= 1
        choices = random.sample(list(SKILLS), min(SKILL_CHOICES, len(SKILLS)))
        self.ui.set_skill_choices(choices)
        self.skill_delay = SKILL_PICK_DELAY
        self.app_state = 'SKILL_SELECT'
        return True

    def choose_skill(self, kind):
        if self.skill_delay > 0:
            return
        self.hero.add_skill(kind)
        if not self.open_skill_choice():  # more skill items collected? ask again
            self.app_state = 'PLAYING'

    def on_ball_effect(self, kind, **data):
        """Visual-only events coming from BallManager."""
        if kind == "bolt":
            self.bolts.append({"src": data["src"], "targets": data["targets"],
                               "t": 0.0, "life": BOLT_TIME})
            self.spawn_particles(data["src"], SKILLS[SKILL_LIGHTNING].color)
            self.add_shake(HIT_SHAKE_TIME, HIT_SHAKE_POWER)
        elif kind == "bounce":
            self.spawn_particles(data["pos"], SKILLS[SKILL_BOUNCE].color)
        elif kind == "heal":
            x, y = data["pos"]
            self.spawn_particles((x, y), (255, 110, 150))
            self.floaters.append({"text": f"+{data['amount']}", "x": x, "y": y,
                                  "t": 0.0, "life": 0.9, "color": (110, 240, 140)})
        elif kind == "skill_item":
            x, y = data["pos"]
            self.floaters.append({"text": "SKILL!", "x": x, "y": y,
                                  "t": 0.0, "life": 0.9, "color": (255, 215, 70)})

    def fire(self):
        angle = aim_angle(self.hero.x, self.display.mouse_pos())
        self.balls.start_volley(self.hero, angle)
        self.state = State.ATTACK

    def ff_active(self):
        held = self.state == State.ATTACK and pygame.key.get_pressed()[pygame.K_SPACE]
        return self.ff or held

    def update_attack(self, dt):
        self.balls.update(dt, self.hero, self.boss, self.field,
                          on_boss_hit=self.on_boss_hit,
                          on_block_break=self.spawn_particles,
                          on_effect=self.on_ball_effect)
        if self.boss.dead:
            self.hero.balls += self.balls.extra_balls
            self.pending_skills += self.balls.skills_collected
            self.balls.reset()
            self.state = State.WIN
            self.shake = 0.0
            self.app_state = 'WIN_SCREEN'
        elif self.balls.finished:
            self.end_phase()

    def end_phase(self):
        self.hero.balls += self.balls.extra_balls
        self.balls.extra_balls = 0
        self.pending_skills += self.balls.skills_collected
        self.balls.skills_collected = 0

        for center, ratio in run_turn_end(self.field, self.hero):   # e.g. fire burn damage
            self.spawn_particles(center, block_color(ratio))

        before = self.hero.hp
        self.hero.take_damage(self.boss.attack)
        self.trigger_boss_attack(before - self.hero.hp)
        if not self.hero.alive:
            self.state = State.LOSE
            self.shake = 0.0
            self.app_state = 'LOSE_SCREEN'
            return

        self.turn += 1
        self.field.move_down()
        self.field.spawn_row(self.turn, self.stage)
        if self.field.block_hit_hero():
            self.state = State.LOSE
            self.shake = 0.0
            self.app_state = 'LOSE_SCREEN'
            return

        self.end_timer = END_PHASE_DELAY
        self.state = State.END

    def add_shake(self, duration, power):
        current = self.shake_pow * self.shake / self.shake_len
        if power >= current:
            self.shake = duration
            self.shake_len = duration
            self.shake_pow = power

    def on_boss_hit(self):
        self.add_shake(HIT_SHAKE_TIME, HIT_SHAKE_POWER)

    def spawn_particles(self, pos, color):
        for _ in range(PARTICLE_COUNT):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(80, 260)
            life = random.uniform(0.35, 0.7)
            particle_color = (255, 255, 255) if random.random() < 0.25 else color
            self.particles.append({
                "x": pos[0], "y": pos[1],
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - 60,
                "life": life, "max": life,
                "size": random.randint(3, 6), "color": particle_color
            })
        del self.particles[:-MAX_PARTICLES]

    def trigger_boss_attack(self, damage):
        self.boss.atk_fx = ATTACK_FX_TIME
        self.hurt_fx = ATTACK_FX_TIME
        self.add_shake(SHAKE_TIME, SHAKE_POWER)
        self.floaters.append({
            "text": f"-{damage}", "x": self.hero.x, "y": HERO_Y - 30,
            "t": 0.0, "life": 0.9, "color": (255, 90, 90)
        })

    def update_effects(self, dt):
        self.boss.atk_fx = max(0.0, self.boss.atk_fx - dt)
        self.hurt_fx = max(0.0, self.hurt_fx - dt)
        self.shake = max(0.0, self.shake - dt)

        for floater in self.floaters:
            floater["t"] += dt
            floater["y"] -= 40 * dt
        self.floaters = [f for f in self.floaters if f["t"] < f["life"]]

        for bolt in self.bolts:
            bolt["t"] += dt
        self.bolts = [b for b in self.bolts if b["t"] < b["life"]]

        for particle in self.particles:
            particle["life"] -= dt
            particle["vy"] += 700 * dt
            particle["x"] += particle["vx"] * dt
            particle["y"] += particle["vy"] * dt
        self.particles = [p for p in self.particles if p["life"] > 0]

        for block in self.field.blocks:
            block.flash = max(0.0, block.flash - dt)

        if self.hp_ghost < self.hero.hp:
            self.hp_ghost = self.hero.hp
        elif self.hurt_fx <= 0.2:
            self.hp_ghost = max(self.hero.hp, self.hp_ghost - 50 * dt)

    def handle_event(self, e):
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if self.app_state != 'PLAYING':
            self.ui.handle_event(e, self.app_state)
            return

        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if math.hypot(e.pos[0] - 40, e.pos[1] - 40) <= 22:
                self.pause_game()
                return

        if (e.type == pygame.MOUSEBUTTONDOWN and e.button == 1
                and self.state in (State.AIM, State.ATTACK)
                and self.ff_button.collidepoint(e.pos)):
            self.ff = not self.ff
            return

        if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            self.dragging = False

        if self.state == State.AIM:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if e.pos[1] >= BOTTOM_STRIP_Y:
                    self.dragging = True
                    self.hero.move_to(e.pos[0])
                else:
                    self.fire()
            elif e.type == pygame.MOUSEMOTION and self.dragging:
                self.hero.move_to(e.pos[0])

    def update(self, dt):
        if self.app_state in ('PLAYING', 'WIN_SCREEN', 'LOSE_SCREEN', 'SKILL_SELECT'):
            self.update_effects(dt)

        if self.app_state == 'SKILL_SELECT':
            self.skill_delay = max(0.0, self.skill_delay - dt)

        if self.app_state != 'PLAYING':
            return

        self.boss.update(dt)

        if self.state == State.AIM:
            keys = pygame.key.get_pressed()
            move = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
            self.hero.move_to(self.hero.x + move * HERO_MOVE_SPEED * dt)
        elif self.state == State.ATTACK:
            for _ in range(FF_SPEED if self.ff_active() else 1):
                if self.state != State.ATTACK:
                    break
                self.update_attack(dt)
        elif self.state == State.END:
            self.end_timer -= dt
            if self.end_timer <= 0:
                self.state = State.AIM
                self.open_skill_choice()  # skill item collected this volley

    def draw_game_layer(self, target_surface):
        # ถ้ารูปภาพด่านมีอยู่ วาดรูปภาพ ถ้าไม่มีให้วาดด้วยโค้ด (draw_game_field)
        if self.current_theme in self.assets:
            target_surface.blit(self.assets[self.current_theme], (0, 0))
        else:
            draw_game_field(target_surface, self.current_theme)
            
        self.renderer.screen = target_surface
        self.renderer.draw(self)

    def run(self):
        while True:
            dt = min(self.clock.tick(FPS) / 1000, 1 / 30)
            for event in pygame.event.get():
                if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN,
                                  pygame.MOUSEBUTTONUP):
                    event.pos = self.display.to_logical(event.pos)   # window -> game coords
                self.handle_event(event)
            
            self.update(dt)

            if self.app_state == 'MENU':
                if 'bg_menu' in self.assets:
                    self.screen.blit(self.assets['bg_menu'], (0, 0))
                else:
                    draw_main_menu_bg(self.screen)
                self.ui.draw_menu(self.screen)
                
            elif self.app_state == 'INFO_SCREEN':
                if 'bg_menu' in self.assets:
                    self.screen.blit(self.assets['bg_menu'], (0, 0))
                else:
                    draw_main_menu_bg(self.screen)
                self.ui.draw_menu(self.screen)
                self.ui.draw_info_modal(self.screen)
                
            elif self.app_state == 'SETTINGS_SCREEN':
                if 'bg_menu' in self.assets:
                    self.screen.blit(self.assets['bg_menu'], (0, 0))
                else:
                    draw_main_menu_bg(self.screen)
                self.ui.draw_menu(self.screen)
                self.ui.draw_settings_modal(self.screen)
                
            elif self.app_state == 'WIN_SCREEN':
                self.draw_game_layer(self.canvas)
                self.screen.blit(self.canvas, (0,0))
                self.ui.draw_modal(self.screen, "STAGE CLEARED!", (100, 220, 100), f"Completed Stage {self.stage}")
                
            elif self.app_state == 'LOSE_SCREEN':
                self.draw_game_layer(self.canvas)
                self.screen.blit(self.canvas, (0,0))
                self.ui.draw_modal(self.screen, "GAME OVER", (255, 90, 90), f"Fell at Stage {self.stage}")
                
            elif self.app_state == 'SKILL_SELECT':
                self.draw_game_layer(self.canvas)
                self.screen.blit(self.canvas, (0,0))
                self.ui.draw_skill_select(self.screen, self.hero)

            elif self.app_state == 'PAUSE_SCREEN':
                self.draw_game_layer(self.canvas)
                self.screen.blit(self.canvas, (0,0))
                self.ui.draw_pause_modal(self.screen)
                
            elif self.app_state == 'PLAYING':
                self.draw_game_layer(self.canvas)
                self.screen.blit(self.canvas, (0,0))
                self.ui.btn_pause.draw(self.screen)
            
            self.display.present()
