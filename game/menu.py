import pygame
import math
import random
import os

from .skills import SKILLS


def load_assets(w, h):
    assets = {}
    base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
    
    if not os.path.exists(base_path):
        try:
            os.makedirs(base_path)
            print(f"Created assets folder at: {base_path}")
        except Exception:
            pass
        return assets
            
    for filename in os.listdir(base_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            name = os.path.splitext(filename)[0]
            # โหลดเฉพาะภาพที่เป็นพื้นหลังเท่านั้น เพื่อไม่ให้ไปกวนระบบปุ่ม
            if name.startswith('bg_'):
                path = os.path.join(base_path, filename)
                try:
                    img = pygame.image.load(path).convert_alpha()
                    assets[name] = pygame.transform.scale(img, (w, h))
                except Exception:
                    pass
    return assets

THEMES = {
    'Garden': {'floor1': (160, 210, 100), 'floor2': (140, 190, 80), 'bg': (100, 180, 80)},
    'Volcano': {'floor1': (70, 40, 40), 'floor2': (50, 25, 25), 'bg': (40, 15, 10)},
    'Snow': {'floor1': (230, 245, 255), 'floor2': (210, 230, 245), 'bg': (160, 190, 220)},
    'Forest': {'floor1': (40, 90, 40), 'floor2': (30, 75, 30), 'bg': (20, 50, 20)},
    'City': {'floor1': (90, 90, 100), 'floor2': (75, 75, 85), 'bg': (30, 30, 45)}
}

def draw_main_menu_bg(surface):
    w, h = surface.get_size()
    for y in range(h):
        r = max(0, 40 - int((y/h)*40))
        g = max(0, 140 - int((y/h)*60))
        b = max(0, 240 - int((y/h)*80))
        pygame.draw.line(surface, (r, g, b), (0, y), (w, y))
    
    pygame.draw.ellipse(surface, (255, 255, 255, 200), (-30, h*0.7, w*0.6, 200))
    pygame.draw.ellipse(surface, (240, 245, 255, 200), (w*0.4, h*0.65, w*0.8, 250))
    pygame.draw.circle(surface, (255, 255, 255), (w*0.2, h*0.2), 40)
    pygame.draw.circle(surface, (255, 255, 255), (w*0.2 + 40, h*0.2 - 20), 50)
    pygame.draw.circle(surface, (255, 255, 255), (w*0.2 + 80, h*0.2 + 10), 35)

def draw_scenery(surface, theme, w, h):
    sky_rect = pygame.Rect(0, 0, w, h)
    if theme == 'Forest':
        surface.fill((135, 206, 235), sky_rect)
        pygame.draw.circle(surface, (255, 220, 50), (w*0.8, h*0.4), 40) 
        pygame.draw.polygon(surface, (80, 140, 80), [(0, h), (w*0.3, h*0.2), (w*0.7, h)]) 
        pygame.draw.polygon(surface, (60, 120, 60), [(w*0.4, h), (w*0.8, h*0.3), (w, h)]) 
        for x in range(10, w, 80): 
            pygame.draw.polygon(surface, (34, 139, 34), [(x, h), (x+25, h-70), (x+50, h)])
            pygame.draw.rect(surface, (139, 69, 19), (x+20, h-10, 10, 10))
    elif theme == 'City':
        surface.fill((20, 25, 45), sky_rect)
        pygame.draw.circle(surface, (220, 220, 230), (w*0.8, h*0.4), 30) 
        b_widths, b_heights = [80, 100, 60, 120, 90], [120, 220, 160, 250, 180]
        cur_x = 0
        for bw, bh in zip(b_widths, b_heights):
            if cur_x > w: break
            pygame.draw.rect(surface, (30, 35, 50), (cur_x, h - bh, bw, bh))
            for wx in range(cur_x + 15, cur_x + bw - 15, 25): 
                for wy in range(h - bh + 20, h - 20, 35):
                    if (wx + wy) % 3 != 0:
                        pygame.draw.rect(surface, (255, 255, 120), (wx, wy, 12, 18))
            cur_x += bw
    elif theme == 'Snow':
        surface.fill((176, 224, 230), sky_rect)
        pygame.draw.ellipse(surface, (240, 248, 255), (-50, h-80, w*0.7, 160)) 
        pygame.draw.ellipse(surface, (255, 255, 255), (w*0.3, h-100, w*0.8, 180)) 
        pygame.draw.circle(surface, (255, 255, 255), (w*0.8, h-40), 25)
        pygame.draw.circle(surface, (255, 255, 255), (w*0.8, h-80), 18)
        pygame.draw.circle(surface, (0, 0, 0), (w*0.8 - 6, h-85), 3) 
        pygame.draw.circle(surface, (0, 0, 0), (w*0.8 + 6, h-85), 3)
        pygame.draw.polygon(surface, (255, 140, 0), [(w*0.8, h-80), (w*0.8-20, h-75), (w*0.8, h-70)]) 
    elif theme == 'Volcano':
        surface.fill((80, 20, 20), sky_rect)
        pygame.draw.polygon(surface, (30, 10, 10), [(w*0.1, h), (w*0.4, h*0.2), (w*0.6, h*0.2), (w*0.9, h)])
        pygame.draw.polygon(surface, (255, 80, 0), [(w*0.45, h*0.2), (w*0.48, h*0.5), (w*0.55, h*0.2)])
        pygame.draw.polygon(surface, (255, 120, 0), [(w*0.4, h*0.2), (w*0.6, h*0.2), (w*0.5, h*0.15)])
        for i in range(20): 
            pygame.draw.circle(surface, (255, 150, 50), ((i*41)%w, (i*27)%h), 3)
    else: 
        surface.fill((135, 206, 235), sky_rect)
        pygame.draw.ellipse(surface, (124, 252, 0), (-50, h-60, w*0.7, 120))
        pygame.draw.ellipse(surface, (173, 255, 47), (w*0.3, h-80, w*0.8, 140))
        for fx in [60, 150, 280, 380, 500]:
            if fx < w:
                pygame.draw.line(surface, (34, 139, 34), (fx, h-10), (fx, h-40), 4) 
                pygame.draw.circle(surface, (255, 105, 180), (fx, h-45), 12) 
                pygame.draw.circle(surface, (255, 255, 0), (fx, h-45), 5) 

def draw_game_field(surface, theme_name):
    w, h = surface.get_size()
    horizon_y = int(h * 0.22)
    
    draw_scenery(surface, theme_name, w, horizon_y)
    
    theme = THEMES.get(theme_name, THEMES['Garden'])
    pygame.draw.rect(surface, theme['bg'], (0, horizon_y, w, h - horizon_y))
    
    grid_size = 45
    rows = (h - horizon_y) // grid_size + 1
    cols = w // grid_size + 1
    
    for row in range(rows):
        for col in range(cols):
            color = theme['floor1'] if (row + col) % 2 == 0 else theme['floor2']
            rect_x = col * grid_size
            rect_y = horizon_y + row * grid_size
            pygame.draw.rect(surface, color, (rect_x, rect_y, grid_size, grid_size))
            
    pygame.draw.line(surface, (255, 255, 255), (0, horizon_y), (w, horizon_y), 4)

class GlossyButton:
    def __init__(self, x, y, width, height, text, bg_color, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.bg_color = bg_color
        self.hover_color = (min(255, bg_color[0]+40), min(255, bg_color[1]+40), min(255, bg_color[2]+40))
        self.font = pygame.font.SysFont('tahoma', 22, bold=True)
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.bg_color
        r, g, b = color
        dark_color = (max(0, r-60), max(0, g-60), max(0, b-60))
        
        shadow_rect = self.rect.copy()
        shadow_rect.y += 6
        pygame.draw.rect(surface, dark_color, shadow_rect, border_radius=20)
        
        pygame.draw.rect(surface, color, self.rect, border_radius=20)
        
        highlight = pygame.Rect(self.rect.x + 8, self.rect.y + 4, self.rect.width - 16, self.rect.height // 2 - 2)
        highlight_surf = pygame.Surface((highlight.width, highlight.height), pygame.SRCALPHA)
        pygame.draw.rect(highlight_surf, (255, 255, 255, 70), highlight_surf.get_rect(), border_radius=12)
        surface.blit(highlight_surf, highlight)
        
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 3, border_radius=20)
        
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_shadow = self.font.render(self.text, True, dark_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_shadow, (text_rect.x, text_rect.y + 2))
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered and self.action:
                self.action()

class IconButton:
    def __init__(self, x, y, radius, icon_type, action):
        self.x = x
        self.y = y
        self.radius = radius
        self.action = action
        self.icon_type = icon_type 
        self.is_hovered = False

    def draw(self, surface):
        color = (220, 220, 220) if self.is_hovered else (255, 255, 255)
        if self.icon_type == 'close':
            color = (255, 100, 100) if self.is_hovered else (220, 60, 60)
            
        pygame.draw.circle(surface, (50, 50, 50), (self.x, self.y + 4), self.radius) 
        pygame.draw.circle(surface, color, (self.x, self.y), self.radius)
        pygame.draw.circle(surface, (255, 255, 255) if self.icon_type == 'close' else (100,100,100), (self.x, self.y), self.radius, 3) 
        
        if self.icon_type == 'info':
            font = pygame.font.SysFont('impact', 24)
            text = font.render('i', True, (50, 150, 255))
            surface.blit(text, text.get_rect(center=(self.x, self.y)))
        elif self.icon_type == 'settings':
            pygame.draw.circle(surface, (100, 100, 100), (self.x, self.y), self.radius - 8, 4)
            for i in range(0, 360, 45):
                rad = math.radians(i)
                end_x = self.x + math.cos(rad) * (self.radius - 2)
                end_y = self.y + math.sin(rad) * (self.radius - 2)
                pygame.draw.line(surface, (100, 100, 100), (self.x, self.y), (end_x, end_y), 4)
            pygame.draw.circle(surface, color, (self.x, self.y), self.radius - 12)
        elif self.icon_type == 'close':
            offset = 8
            line_color = (255, 255, 255)
            pygame.draw.line(surface, line_color, (self.x-offset, self.y-offset), (self.x+offset, self.y+offset), 4)
            pygame.draw.line(surface, line_color, (self.x-offset, self.y+offset), (self.x+offset, self.y-offset), 4)
        elif self.icon_type == 'pause':
            offset = 6
            line_color = (100, 100, 100)
            pygame.draw.rect(surface, line_color, (self.x - offset - 2, self.y - offset, 4, offset*2))
            pygame.draw.rect(surface, line_color, (self.x + offset - 2, self.y - offset, 4, offset*2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            dist = math.hypot(event.pos[0] - self.x, event.pos[1] - self.y)
            self.is_hovered = dist <= self.radius
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered and self.action:
                self.action()

def wrap_text(text, font, max_width):
    lines, line = [], ""
    for word in text.split():
        trial = (line + " " + word).strip()
        if font.size(trial)[0] <= max_width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


class SkillCard:
    """One clickable skill choice."""

    def __init__(self, rect, kind, number, action):
        self.rect = pygame.Rect(rect)
        self.kind = kind
        self.number = number
        self.action = action

    def handle_event(self, event):
        # uses the click position directly, so it never depends on a stale hover flag
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                and self.rect.collidepoint(event.pos)):
            self.action()
            return True
        return False

    def draw(self, surface, name_font, desc_font, owned, mouse_pos):
        info = SKILLS[self.kind]
        hovered = self.rect.collidepoint(mouse_pos)

        shadow = self.rect.copy()
        shadow.y += 5
        pygame.draw.rect(surface, (190, 198, 208), shadow, border_radius=16)
        pygame.draw.rect(surface, (255, 246, 222) if hovered else (255, 255, 255),
                         self.rect, border_radius=16)
        pygame.draw.rect(surface, info.color, self.rect, 4, border_radius=16)

        info.draw_icon(surface, self.rect.x + 52, self.rect.centery, 28)

        text_x = self.rect.x + 100
        name = name_font.render(info.name, True, (40, 45, 60))
        surface.blit(name, (text_x, self.rect.y + 14))
        for i, line in enumerate(wrap_text(info.desc, desc_font, self.rect.right - text_x - 16)):
            surface.blit(desc_font.render(line, True, (90, 100, 115)),
                         (text_x, self.rect.y + 46 + i * 20))

        key = desc_font.render(f"[{self.number}]", True, (150, 160, 175))
        surface.blit(key, (self.rect.right - key.get_width() - 14, self.rect.y + 14))
        if owned:
            own = desc_font.render(f"owned x{owned}", True, info.color)
            surface.blit(own, (self.rect.right - own.get_width() - 14, self.rect.bottom - 26))


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
        pygame.draw.rect(surface, (250, 250, 250), panel, border_radius=20)
        pygame.draw.rect(surface, (200, 210, 220), panel, 4, border_radius=20)

        title = self.title_font.render("CHOOSE A SKILL", True, (255, 170, 0))
        title = pygame.transform.scale(title, (int(title.get_width() * 0.6), int(title.get_height() * 0.6)))
        surface.blit(title, title.get_rect(center=(cx, 170)))
        sub = self.body_font.render("You get +1 of that ball in every volley", True, (110, 120, 135))
        surface.blit(sub, sub.get_rect(center=(cx, 202)))

        for card in self.skill_cards:
            card.draw(surface, self.card_name_font, self.card_desc_font,
                      hero.skills.get(card.kind, 0), self.game.display.mouse_pos())

        hint = self.card_desc_font.render("Click a card or press 1 / 2 / 3", True, (140, 150, 165))
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
