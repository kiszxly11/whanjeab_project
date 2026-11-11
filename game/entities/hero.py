import random

from ..settings import BALL_DAMAGE, HERO_MAX_HP, START_BALLS, W, HERO_R
from ..skills import SKILLS


class Hero:
    def __init__(self):
        self.x = W / 2
        self.max_hp = HERO_MAX_HP
        self.hp = self.max_hp
        self.balls = START_BALLS
        self.damage = BALL_DAMAGE
        self.skills = {}                  # skill kind -> how many special balls

    @property
    def alive(self):                      # Hero Defeat Detection
        return self.hp > 0

    def move_to(self, x):                 # Hero Position Selection
        self.x = max(HERO_R, min(W - HERO_R, x))

    def take_damage(self, amount):        # Hero Damage System
        self.hp = max(0, self.hp - amount)

    def level_up(self):                   # Hero Progression
        self.max_hp += 10
        self.hp = min(self.max_hp, self.hp + 30)
        self.balls += 2
        #if random.random() < 0.5:
          #  self.damage += 1

    def add_skill(self, kind):            # Skill pick: +1 special ball every volley
        self.skills[kind] = self.skills.get(kind, 0) + 1

    def special_balls(self):
        """Kinds of the special balls added to every volley, e.g. ['fire', 'fire', 'ice']."""
        out = []
        for kind in SKILLS:               # stable order
            out.extend([kind] * self.skills.get(kind, 0))
        return out
