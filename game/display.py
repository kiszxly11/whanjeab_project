"""Window handling: the game always draws at W x H and is scaled to fit the screen."""
import pygame

SCREEN_MARGIN_Y = 110     # room for the title bar + taskbar/dock
SCREEN_MARGIN_X = 20


def desktop_size():
    try:
        return pygame.display.get_desktop_sizes()[0]
    except Exception:
        info = pygame.display.Info()
        return info.current_w, info.current_h


class Display:
    """Owns the real window. Everything else draws on `self.surface` (W x H) and
    calls present(); mouse positions are converted back with to_logical()."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        dw, dh = desktop_size()
        scale = min(1.0, (dh - SCREEN_MARGIN_Y) / h, (dw - SCREEN_MARGIN_X) / w)
        scale = max(0.3, scale)
        size = (int(w * scale), int(h * scale))
        self.window = pygame.display.set_mode(size, pygame.RESIZABLE)
        self.surface = pygame.Surface((w, h))

    def _view(self):
        """(x, y, w, h) of the game inside the window, keeping the aspect ratio."""
        ww, wh = pygame.display.get_surface().get_size()
        s = min(ww / self.w, wh / self.h)
        vw, vh = max(1, int(self.w * s)), max(1, int(self.h * s))
        return (ww - vw) // 2, (wh - vh) // 2, vw, vh

    def present(self):
        window = pygame.display.get_surface()
        ww, wh = window.get_size()
        s = min(ww / self.w, wh / self.h)
        if s >= 1:
            s = int(s)                      # whole-number scale = crisp pixels
            scaled = pygame.transform.scale(self.surface, (self.w * s, self.h * s))
        else:
            s = max(s, 0.1)                 # smaller than 1 -> smooth shrink looks better
            scaled = pygame.transform.smoothscale(self.surface, (int(self.w * s), int(self.h * s)))
        window.fill((0, 0, 0))
        window.blit(scaled, ((ww - scaled.get_width()) // 2, (wh - scaled.get_height()) // 2))
        pygame.display.flip()

    def to_logical(self, pos):
        x, y, vw, vh = self._view()
        return ((pos[0] - x) * self.w / vw, (pos[1] - y) * self.h / vh)

    def mouse_pos(self):
        return self.to_logical(pygame.mouse.get_pos())
