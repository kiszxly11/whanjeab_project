"""Loads the background images from the assets/ folder."""
import os

import pygame


def load_assets(w, h):
    assets = {}
    base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'assets')
    
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
