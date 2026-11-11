import pygame

from ..settings import BOSS_H, W


class Boss:
    def __init__(self, stage):
        self.stage = stage
        self.max_hp = 40 + 30 * stage
        self.hp = self.max_hp
        self.attack = 3 + stage
        self.rect = pygame.Rect(0, 0, W, BOSS_H)
        self.flash = 0.0
        self.atk_fx = 0.0

    @property
    def dead(self):
        return self.hp <= 0

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)
        self.flash = 0.1

    def update(self, dt):
        self.flash = max(0.0, self.flash - dt)
