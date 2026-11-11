"""All user-interface code (menus, modals, buttons, backgrounds)."""
from .assets import load_assets
from .backgrounds import draw_game_field, draw_main_menu_bg
from .manager import UIManager

__all__ = ["UIManager", "load_assets", "draw_game_field", "draw_main_menu_bg"]
