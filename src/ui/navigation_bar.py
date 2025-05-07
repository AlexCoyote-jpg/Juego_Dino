# navigation_bar.py
import pygame
from .utils import Boton
from .animations import get_surface

class NavigationBar:
    def __init__(self, options, down=True):
        self.options = options
        self.selected = 0
        self.down = down
        self._anim_sizes = [0.0 for _ in options]
        self.botones = []
    
    def get_height(self):
        # Devuelve la altura actual de la barra de navegación (útil para juegos)
        alto = pygame.display.get_surface().get_height() if pygame.display.get_surface() else 700
        return max(36, min(60, int(alto * 0.07))) + max(6, int(alto * 0.01)) * 2


    def draw(self, surface, logo=None, logo_height=None):
        ancho, alto = surface.get_size()
        num = len(self.options)

        b_alto = max(36, min(60, int(alto * 0.07)))
        b_ancho = max(90, min(180, int(ancho * 0.12)))
        b_ancho_sel = int(b_ancho * 1.15)
        b_alto_sel = int(b_alto * 1.15)
        sep = max(10, int(b_ancho * 0.18))
        radius = max(14, int(b_alto * 0.26))
        margin_y = max(20, int(alto * 0.04))
        margin_x = max(18, int(ancho * 0.03))
        logo_margin = max(10, int(ancho * 0.01))

        # Logo
        lw = lh = lmy = 0
        if logo:
            lw0, lh0 = logo.get_size()
            lw = int(min(int(ancho * 0.20), lw0))
            max_lh = int(alto * 0.25 if logo_height is None else min(alto * 0.25, logo_height))
            scale = min(lw / lw0, max_lh / lh0, 1.5)
            lw = int(lw0 * scale)
            lh = int(lh0 * scale)
            lmy = max(6, (b_alto - lh) // 2 + margin_y)

        bar_w = (num - 1) * sep
        for i in range(num):
            bar_w += b_ancho_sel if i == self.selected else b_ancho
        bar_x = max((ancho - bar_w) // 2, margin_x + lw + logo_margin)
        bar_y = margin_y

        # Sombra
        pad_x, pad_y = max(12, int(b_ancho * 0.13)), max(12, int(b_alto * 0.30))
        sombra = get_surface(bar_w + pad_x * 2, b_alto + pad_y * 2, alpha=True)
        pygame.draw.rect(sombra, (0, 0, 0, 32), sombra.get_rect(), border_radius=radius + 8)
        surface.blit(sombra, (bar_x - pad_x, bar_y - pad_y))

        if logo:
            logo_scaled = pygame.transform.smoothscale(logo, (lw, lh))
            surface.blit(logo_scaled, (margin_x, lmy))

        try:
            fuente = pygame.font.SysFont("Arial Rounded MT Bold", int(b_alto * 0.60), bold=True)
        except:
            fuente = pygame.font.SysFont("Segoe UI", int(b_alto * 0.60), bold=True)

        colores = [
            ((120, 170, 255), (80, 120, 255)),
            ((255, 170, 170), (255, 120, 120)),
            ((140, 220, 180), (100, 200, 160)),
            ((255, 210, 120), (255, 180, 80)),
            ((200, 160, 255), (160, 120, 255)),
        ]
        txt_color = (30, 30, 50)
        anim_speed = 0.22

        for i in range(num):
            tgt = 1.0 if i == self.selected else 0.0
            self._anim_sizes[i] += (tgt - self._anim_sizes[i]) * anim_speed

        self.botones.clear()
        x = bar_x
        for i, txt in enumerate(self.options):
            a = min(1.0, max(0.0, self._anim_sizes[i]))
            ancho = int(b_ancho + (b_ancho_sel - b_ancho) * a)
            alto = int(b_alto + (b_alto_sel - b_alto) * a)
            y = bar_y + (b_alto - alto) // 2
            color_top, color_bottom = colores[i % len(colores)]
            borde_blanco = (i == self.selected)
            boton = Boton(
                txt, x, y, ancho, alto,
                color_texto=txt_color, fuente=fuente,
                border_radius=radius, estilo="apple",
                color_top=color_top, color_bottom=color_bottom,
                border_color=borde_blanco
            )
            boton.draw(surface)
            self.botones.append(boton)
            x += ancho + sep

    def handle_event(self, event, logo=None, logo_height=None):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_RIGHT:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                return self.selected
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            for idx, boton in enumerate(self.botones):
                if boton.collidepoint(mouse_pos):
                    self.selected = idx
                    return self.selected
        return None
