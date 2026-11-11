"""Reusable UI pieces: buttons, text wrapping and the skill choice card."""
import math

import pygame

from ..skills import SKILLS


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
