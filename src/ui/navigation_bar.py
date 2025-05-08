# navigation_bar.py
import pygame
from .utils import Boton
from .animations import get_surface

class NavigationBar:
    def __init__(self, options, down=True, icons=None, tooltips=None):
        self.options = options
        self.selected = 0
        self.down = down
        self._anim_sizes = [0.0 for _ in options]
        self._anim_opacity = [1.0 for _ in options]
        self.botones = []
        self.icons = icons or [None] * len(options)
        self.tooltips = tooltips or [None] * len(options)
        self._tooltip_idx = None
        self._tooltip_alpha = 0

    def get_height(self):
        alto = pygame.display.get_surface().get_height() if pygame.display.get_surface() else 700
        return max(36, min(60, int(alto * 0.07))) + max(6, int(alto * 0.01)) * 2

    def draw(self, surface, logo=None, logo_height=None):
        ancho, alto = surface.get_size()
        num = len(self.options)

        # Responsividad: tamaño de fuente y botones
        b_alto = max(36, min(60, int(alto * 0.07)))
        b_ancho = max(90, min(180, int(ancho * 0.12)))
        b_ancho_sel = int(b_ancho * 1.15)
        b_alto_sel = int(b_alto * 1.15)
        sep = max(2, int(b_ancho * 0.04))
        radius = max(24, int(b_alto * 0.48))
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

        # Sombra pegada a los botones (sin espacio)
        pad_x, pad_y = 0, 0
        sombra = get_surface(bar_w + pad_x * 2, b_alto + pad_y * 2, alpha=True)
        pygame.draw.rect(sombra, (0, 0, 0, 48), sombra.get_rect(), border_radius=radius + 10)
        surface.blit(sombra, (bar_x - pad_x, bar_y - pad_y))

        if logo:
            logo_scaled = pygame.transform.smoothscale(logo, (lw, lh))
            surface.blit(logo_scaled, (margin_x, lmy))

        # Responsividad: tamaño de fuente
        font_size = int(b_alto * 0.60)
        try:
            fuente = pygame.font.SysFont("Arial Rounded MT Bold", font_size, bold=True)
        except:
            fuente = pygame.font.SysFont("Segoe UI", font_size, bold=True)

        colores = [
            ((120, 170, 255), (80, 120, 255)),
            ((140, 220, 180), (100, 200, 160)),
            ((255, 210, 120), (255, 180, 80)),
            ((255, 170, 170), (255, 120, 120)),
            ((200, 160, 255), (160, 120, 255)),
        ]
        txt_color_sel = (30, 30, 50)
        txt_color_unsel = (255, 255, 255)
        anim_speed = 0.22
        opacity_speed = 0.18

        mouse_pos = pygame.mouse.get_pos()
        self._tooltip_idx = None

        for i in range(num):
            tgt = 1.0 if i == self.selected else 0.0
            self._anim_sizes[i] += (tgt - self._anim_sizes[i]) * anim_speed
            # Animación de opacidad para texto no seleccionado
            tgt_op = 1.0 if i == self.selected else 0.5
            self._anim_opacity[i] += (tgt_op - self._anim_opacity[i]) * opacity_speed

        self.botones.clear()
        x = bar_x

        for i, txt in enumerate(self.options):
            a = min(1.0, max(0.0, self._anim_sizes[i]))
            ancho = int(b_ancho + (b_ancho_sel - b_ancho) * a)
            alto = int(b_alto + (b_alto_sel - b_alto) * a)
            y = bar_y + (b_alto - alto) // 2
            icon = self.icons[i] if i < len(self.icons) else None
            if i == self.selected:
                color_top, color_bottom = colores[i % len(colores)]
                color_texto = txt_color_sel
                border_color = (68, 68, 78, 255)  # Negro grisáceo translúcido tipo sombra
                estilo = "apple"
                text_alpha = 255
            else:
                color_top = color_bottom = (0, 0, 0, 0)
                color_texto = txt_color_unsel
                border_color = False
                estilo = "flat"
                text_alpha = int(255 * self._anim_opacity[i])
            boton = Boton(
                txt, x, y, ancho, alto,
                color_texto=color_texto, fuente=fuente,
                border_radius=radius, estilo=estilo,
                color_top=color_top, color_bottom=color_bottom,
                border_color=border_color,
                texto_visible=True,
            )
            # Soporte para iconos: dibuja el icono si existe
            if icon:
                icon_size = int(alto * 0.6)
                icon_img = pygame.transform.smoothscale(icon, (icon_size, icon_size))
                icon_x = x + (ancho - icon_size) // 2
                icon_y = y + (alto - icon_size) // 2 - (font_size // 3)
                surface.blit(icon_img, (icon_x, icon_y))
                # Ajusta la posición del texto para dejar espacio al icono
                boton.texto_espaciado = icon_size // 4

            # Animación de opacidad en el texto
            if boton.texto and not i == self.selected:
                # Renderiza el texto con opacidad animada
                text_surf = fuente.render(boton.texto, True, color_texto)
                text_surf.set_alpha(text_alpha)
                text_rect = text_surf.get_rect(center=(x + ancho // 2, y + alto // 2 + (icon_size // 2 if icon else 0)))
                surface.blit(text_surf, text_rect)
            else:
                boton.draw(surface)

            self.botones.append(boton)
            # Tooltip: detecta si el mouse está sobre el botón
            if boton.rect.collidepoint(mouse_pos):
                self._tooltip_idx = i
            x += ancho + sep

        # Tooltip: dibuja el tooltip si corresponde
        if self._tooltip_idx is not None and self.tooltips[self._tooltip_idx]:
            self._tooltip_alpha = min(self._tooltip_alpha + 20, 255)
            tooltip_text = self.tooltips[self._tooltip_idx]
            tooltip_font = pygame.font.SysFont("Segoe UI", max(16, font_size // 2))
            tooltip_surf = tooltip_font.render(tooltip_text, True, (255, 255, 255))
            tooltip_surf.set_alpha(self._tooltip_alpha)
            tw, th = tooltip_surf.get_size()
            mx, my = mouse_pos
            tooltip_bg = pygame.Surface((tw + 16, th + 10), pygame.SRCALPHA)
            pygame.draw.rect(tooltip_bg, (30, 30, 30, 220), tooltip_bg.get_rect(), border_radius=8)
            tooltip_bg.blit(tooltip_surf, (8, 5))
            surface.blit(tooltip_bg, (mx + 12, my - th - 18))
        else:
            self._tooltip_alpha = 0

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
