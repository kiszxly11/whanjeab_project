import math

from ..settings import HERO_R, HERO_Y, MIN_AIM_ANGLE


def aim_angle(hero_x, mouse_pos):
    """Angle (radians) from the hero to the mouse, clamped to point upward.

    0 = right, pi/2 = straight up, pi = left.
    """
    mx, my = mouse_pos
    dx, dy = mx - hero_x, my - (HERO_Y - HERO_R)
    ang = math.atan2(-dy, dx)
    return max(MIN_AIM_ANGLE, min(math.pi - MIN_AIM_ANGLE, ang))
