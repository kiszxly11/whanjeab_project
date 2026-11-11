import pygame

from ..settings import BLOCK_FLASH, CELL, GRID_TOP


class Block:
    def __init__(self, col, row, hp):
        self.col, self.row = col, row
        self.hp = hp
        self.max_hp = hp
        self.flash = 0.0
        self.burn_turns = 0           # fire ball: burn ticks left
        self.burn_dmg = 0             # damage dealt per burn tick
        self.frozen = 0               # ice ball: move-down turns it will skip

    @property
    def rect(self):
        return pygame.Rect(self.col * CELL + 2,
                           GRID_TOP + self.row * CELL + 2,
                           CELL - 4, CELL - 4)

    @property
    def dead(self):
        return self.hp <= 0

    def take_damage(self, amount):
        self.hp -= amount
        self.flash = BLOCK_FLASH

    def ignite(self, turns, damage):
        self.burn_turns = turns       # re-igniting refreshes the timer
        self.burn_dmg = damage

    def freeze(self, turns):
        self.frozen = max(self.frozen, turns)
