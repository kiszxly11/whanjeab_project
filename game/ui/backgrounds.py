"""Code-drawn backgrounds: the main menu sky and the themed battlefields
(used when no bg_*.jpg image is available)."""
import pygame


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
