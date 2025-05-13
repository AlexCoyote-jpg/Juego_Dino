import pygame
import time
import unicodedata
from functools import lru_cache
from typing import Optional, Tuple, Dict, Any, List, Union, Callable

def dibujar_barra_scroll(superficie, x, y, ancho, alto, scroll_pos, contenido_alto, ventana_alto, 
                         color=(100, 100, 100), highlight=False, modern=False):
    """Dibuja una barra de desplazamiento moderna con efecto hover"""
    # Calcular dimensiones y posición de la barra
    if contenido_alto <= ventana_alto:
        return  # No hace falta barra de scroll
    
    barra_alto = max(30, ventana_alto * ventana_alto / contenido_alto)
    barra_pos = y + (scroll_pos * (alto - barra_alto) / (contenido_alto - ventana_alto))
    
    # Estilo moderno con barra minimalista
    if modern:
        # Dibujar fondo de la barra (casi invisible)
        bg_rect = pygame.Rect(x, y, ancho, alto)
        pygame.draw.rect(superficie, (220, 220, 220, 30), bg_rect, border_radius=ancho//2)
        
        # Dibujar la barra con borde suave y redondeado
        barra_rect = pygame.Rect(x, barra_pos, ancho, barra_alto)
        
        # Crear gradiente suave
        if highlight:
            color_top = (min(255, color[0]+15), min(255, color[1]+15), min(255, color[2]+15))
            color_bottom = (max(0, color[0]-15), max(0, color[1]-15), max(0, color[2]-15))
        else:
            color_top = color
            color_bottom = (max(0, color[0]-20), max(0, color[1]-20), max(0, color[2]-20))
        
        # Dibuja el gradiente manualmente asegurando colores válidos
        for i in range(int(barra_alto)):
            progress = i / barra_alto if barra_alto > 0 else 0
            r = int(max(0, min(255, color_top[0] * (1 - progress) + color_bottom[0] * progress)))
            g = int(max(0, min(255, color_top[1] * (1 - progress) + color_bottom[1] * progress)))
            b = int(max(0, min(255, color_top[2] * (1 - progress) + color_bottom[2] * progress)))
            pygame.draw.line(superficie, (r, g, b, 200), 
                            (barra_rect.x, barra_rect.y + i),
                            (barra_rect.right, barra_rect.y + i))
        
        # Añadir brillo en los bordes para efecto 3D sutil
        pygame.draw.rect(superficie, (255, 255, 255, 100), barra_rect, width=1, border_radius=ancho//2)
        
    else:
        # Estilo tradicional
        bg_rect = pygame.Rect(x, y, ancho, alto)
        pygame.draw.rect(superficie, (220, 220, 220), bg_rect, border_radius=ancho//2)
        
        barra_rect = pygame.Rect(x, barra_pos, ancho, barra_alto)
        pygame.draw.rect(superficie, color, barra_rect, border_radius=ancho//2)
        pygame.draw.rect(superficie, (255, 255, 255), barra_rect, width=1, border_radius=ancho//2)

# --- Inertial & Time-based Scroll Manager ---
class ScrollManager:
    def __init__(self, initial_pos=0):
        self.scroll_pos = initial_pos
        self.target_scroll = initial_pos
        self.last_update = time.time()
        self.dragging = False
        self.drag_offset = 0
        self.velocity = 0.0  # For inertial scrolling

    def update(self, max_scroll, smooth=True):
        current_time = time.time()
        dt = current_time - self.last_update
        self.last_update = current_time

        if smooth:
            diff = self.target_scroll - self.scroll_pos
            if abs(diff) > 0.5:
                self.velocity = diff * min(1.0, dt * 10)
                self.scroll_pos += self.velocity
            else:
                self.scroll_pos = self.target_scroll
                self.velocity = 0.0
        else:
            self.scroll_pos = self.target_scroll
            self.velocity = 0.0

        # Inertial effect
        if not self.dragging and abs(self.velocity) > 0.1:
            self.scroll_pos += self.velocity * dt * 10
            self.velocity *= 0.92  # Damping

        self.scroll_pos = max(0, min(self.scroll_pos, max_scroll))
        self.target_scroll = max(0, min(self.target_scroll, max_scroll))
        return int(self.scroll_pos)

    def scroll_to(self, pos):
        self.target_scroll = pos

    def scroll_by(self, delta):
        self.target_scroll += delta

    def handle_event(self, event, wheel_speed=40, thumb_rect=None, max_scroll=0, h=0, y=0, bar_rect=None):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                self.scroll_by(-wheel_speed)
                return True
            elif event.button == 5:
                self.scroll_by(wheel_speed)
                return True
            elif event.button == 1:
                if thumb_rect and thumb_rect.collidepoint(event.pos):
                    self.dragging = True
                    self.drag_offset = event.pos[1] - thumb_rect.y
                    return True
                elif bar_rect and bar_rect.collidepoint(event.pos):
                    click_y = event.pos[1]
                    bar_top = y
                    bar_height = h
                    thumb_height = thumb_rect.height if thumb_rect else 30
                    rel_y = click_y - bar_top - thumb_height // 2
                    max_thumb_y = bar_height - thumb_height
                    rel_y = max(0, min(rel_y, max_thumb_y))
                    if max_scroll > 0 and bar_height > thumb_height:
                        self.target_scroll = int(rel_y * max_scroll / (bar_height - thumb_height))
                    return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging and thumb_rect:
            new_thumb_y = event.pos[1] - self.drag_offset
            bar_height = h
            thumb_height = thumb_rect.height
            max_thumb_y = y + bar_height - thumb_height
            new_thumb_y = max(y, min(new_thumb_y, max_thumb_y))
            if max_scroll > 0 and bar_height > thumb_height:
                self.target_scroll = int((new_thumb_y - y) * max_scroll / (bar_height - thumb_height))
            return True
        return False
