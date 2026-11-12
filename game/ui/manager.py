"""UIManager: owns every button and draws the menu, pause, win/lose and skill-pick screens."""
import pygame

from .widgets import GlossyButton, IconButton, SkillCard


class UIManager:
    def __init__(self, width, height, game_instance):
        self.width = width
        self.height = height
        self.game = game_instance
        
        cx, cy = width // 2, height // 2
        self.title_font = pygame.font.SysFont('impact', 64)
        self.body_font = pygame.font.SysFont('tahoma', 16, bold=True)
        
        # ปุมกดทุกอันยังใช้ระบบโค้ดวาดที่สวยๆ เหมือนเดิมเป๊ะ ไม่ต้องทำรูป
        self.btn_start = GlossyButton(cx - 100, cy + 80, 200, 50, "START", (255, 180, 0), self.game.start_from_menu)
        self.btn_info = IconButton(50, 50, 25, 'info', self.game.open_info)
        self.btn_settings = IconButton(width - 50, 50, 25, 'settings', self.game.open_settings)
        
        self.btn_pause = IconButton(40, 40, 22, 'pause', self.game.pause_game)
        
        self.btn_next = GlossyButton(cx - 100, cy + 20, 200, 50, "NEXT STAGE", (0, 180, 255), self.game.next_stage)
        self.btn_retry = GlossyButton(cx - 100, cy + 20, 200, 50, "RETRY", (255, 100, 50), self.game.retry_game)
        self.btn_home = GlossyButton(cx - 100, cy + 90, 200, 50, "HOME", (150, 160, 170), self.game.go_home)
        self.btn_resume = GlossyButton(cx - 100, cy + 20, 200, 50, "RESUME", (100, 200, 100), self.game.resume_game)
        
        self.btn_close = IconButton(cx + 140, cy - 130, 20, 'close', self.game.close_modal)

        self.card_name_font = pygame.font.SysFont('tahoma', 20, bold=True)
        self.card_desc_font = pygame.font.SysFont('tahoma', 14, bold=True)
        self.skill_title_font = pygame.font.SysFont('impact', 40)

        # panel background: navy gradient with rounded corners, built once
        panel_size = (width - 48, 505)
        grad = pygame.Surface(panel_size, pygame.SRCALPHA)
        for y in range(panel_size[1]):
            t = y / panel_size[1]
            col = tuple(int(a + (b - a) * t) for a, b in zip((46, 50, 82), (22, 24, 42)))
            pygame.draw.line(grad, col + (255,), (0, y), (panel_size[0], y))
        mask = pygame.Surface(panel_size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=20)
        grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)    # clips the corners
        self._skill_panel = grad
        self.skill_cards = []

    def handle_event(self, event, state):
        if state == 'MENU':
            self.btn_start.handle_event(event)
            self.btn_info.handle_event(event)
            self.btn_settings.handle_event(event)
        elif state in ('INFO_SCREEN', 'SETTINGS_SCREEN'):
            self.btn_close.handle_event(event)
        elif state == 'WIN_SCREEN':
            self.btn_next.handle_event(event)
            self.btn_home.handle_event(event)
        elif state == 'LOSE_SCREEN':
            self.btn_retry.handle_event(event)
            self.btn_home.handle_event(event)
        elif state == 'PAUSE_SCREEN':
            self.btn_resume.handle_event(event)
            self.btn_home.handle_event(event)
        elif state == 'SKILL_SELECT':
            if event.type == pygame.KEYDOWN and pygame.K_1 <= event.key <= pygame.K_9:
                idx = event.key - pygame.K_1
                if idx < len(self.skill_cards):
                    self.skill_cards[idx].action()
                return
            for card in self.skill_cards[:]:
                if card.handle_event(event):
                    break

    def draw_menu(self, surface):
        cx, cy = self.width//2, self.height//2
        title_surf = self.title_font.render("WHANJEAB", True, (255, 255, 255))
        title_shadow = self.title_font.render("WHANJEAB", True, (0, 0, 100))
        t_rect = title_surf.get_rect(center=(cx, cy - 80))
        surface.blit(title_shadow, (t_rect.x + 5, t_rect.y + 6))
        surface.blit(title_surf, t_rect)
        
        self.btn_start.draw(surface)
        self.btn_info.draw(surface)
        self.btn_settings.draw(surface)

    def set_skill_choices(self, kinds):
        """Build the cards for the skill-pick screen."""
        card_w, card_h, gap = 400, 118, 14
        x = (self.width - card_w) // 2
        y0 = 222
        self.skill_cards = []
        for i, kind in enumerate(kinds):
            self.skill_cards.append(SkillCard(
                (x, y0 + i * (card_h + gap), card_w, card_h), kind, i + 1,
                lambda k=kind: self.game.choose_skill(k)))

    def draw_skill_select(self, surface, hero):
        cx = self.width // 2
        veil = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 190))
        surface.blit(veil, (0, 0))

        panel = pygame.Rect(24, 130, self.width - 48, 505)
        surface.blit(self._skill_panel, panel.topleft)
        pygame.draw.rect(surface, (10, 10, 22), panel.inflate(6, 6), 3, border_radius=22)   # dark outer line
        pygame.draw.rect(surface, (110, 120, 170), panel, 3, border_radius=20)             # light border
        pygame.draw.rect(surface, (78, 86, 130), (panel.x + 30, panel.y + 8, panel.w - 60, 4),
                        border_radius=2)                                                   # gloss strip

        text = "CHOOSE A SKILL"
        shadow = self.skill_title_font.render(text, True, (90, 50, 0))
        title = self.skill_title_font.render(text, True, (255, 190, 40))
        surface.blit(shadow, shadow.get_rect(center=(cx, 174)))
        surface.blit(title, title.get_rect(center=(cx, 170)))
        sub = self.body_font.render("You get +1 of that ball in every volley", True, (160, 172, 205))
        surface.blit(sub, sub.get_rect(center=(cx, 204)))

        for card in self.skill_cards:
            card.draw(surface, self.card_name_font, self.card_desc_font,
                    hero.skills.get(card.kind, 0), self.game.display.mouse_pos())

        hint = self.card_desc_font.render("Click a card or press 1 / 2 / 3", True, (140, 152, 185))
        surface.blit(hint, hint.get_rect(center=(cx, 617)))

    def draw_overlay(self, surface):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        surface.blit(overlay, (0, 0))
        
        cx, cy = self.width//2, self.height//2
        panel = pygame.Rect(cx - 140, cy - 150, 280, 320)
        pygame.draw.rect(surface, (250, 250, 250), panel, border_radius=20)
        pygame.draw.rect(surface, (200, 210, 220), panel, 4, border_radius=20)
        return cx, cy

    def draw_info_modal(self, surface):
        cx, cy = self.draw_overlay(surface)
        
        title = self.title_font.render("CONTROLS", True, (50, 150, 255))
        title = pygame.transform.scale(title, (int(title.get_width()*0.5), int(title.get_height()*0.5)))
        surface.blit(title, title.get_rect(center=(cx, cy - 100)))
        
        lines = [
            "Mouse Drag : Aim & Shoot",
            "A / D : Move Hero",
            "Spacebar : Fast Forward",
            "Gold star : Pick a skill",
            "Clear blocks & defeat Boss!"
        ]
        for i, text in enumerate(lines):
            t_surf = self.body_font.render(text, True, (80, 90, 100))
            surface.blit(t_surf, (cx - 100, cy - 40 + i*30))
            
        self.btn_close.draw(surface)

    def draw_settings_modal(self, surface):
        cx, cy = self.draw_overlay(surface)
        
        title = self.title_font.render("SETTINGS", True, (100, 100, 100))
        title = pygame.transform.scale(title, (int(title.get_width()*0.5), int(title.get_height()*0.5)))
        surface.blit(title, title.get_rect(center=(cx, cy - 100)))
        
        t_surf = self.body_font.render("SFX & Music coming soon!", True, (100, 100, 100))
        surface.blit(t_surf, t_surf.get_rect(center=(cx, cy)))
            
        self.btn_close.draw(surface)

    def draw_pause_modal(self, surface):
        cx, cy = self.draw_overlay(surface)
        
        title = self.title_font.render("PAUSED", True, (100, 100, 100))
        title = pygame.transform.scale(title, (int(title.get_width()*0.6), int(title.get_height()*0.6)))
        surface.blit(title, title.get_rect(center=(cx, cy - 80)))
        
        self.btn_resume.draw(surface)
        self.btn_home.draw(surface)

    def draw_modal(self, surface, title_text, title_color, subtitle_text):
        cx, cy = self.draw_overlay(surface)
        
        title_surf = self.title_font.render(title_text, True, title_color)
        title_surf = pygame.transform.scale(title_surf, (int(title_surf.get_width()*0.6), int(title_surf.get_height()*0.6)))
        title_shadow = self.title_font.render(title_text, True, (50, 50, 50))
        title_shadow = pygame.transform.scale(title_shadow, (int(title_shadow.get_width()*0.6), int(title_shadow.get_height()*0.6)))
        
        t_rect = title_surf.get_rect(center=(cx, cy - 80))
        surface.blit(title_shadow, (t_rect.x+3, t_rect.y+3))
        surface.blit(title_surf, t_rect)
        
        sub_surf = self.body_font.render(subtitle_text, True, (120, 130, 140))
        surface.blit(sub_surf, sub_surf.get_rect(center=(cx, cy - 30)))
        
        if "CLEARED" in title_text:
            self.btn_next.draw(surface)
        else:
            self.btn_retry.draw(surface)
        self.btn_home.draw(surface)
