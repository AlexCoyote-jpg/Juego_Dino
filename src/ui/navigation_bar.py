# navigation_bar.py
import pygame
from .utils import Boton
from .animations import get_surface

"""
Barra de navegación: componente para mostrar y gestionar la navegación entre secciones del juego.
"""

class NavigationBar:
    def __init__(self, options, down=True):
        self.options = options
        self.selected = 0
        self.down = down
        self._anim_size = 0

    def draw(self, surface, logo=None, logo_height=None):
        ancho = surface.get_width()
        alto = surface.get_height()
        num_opciones = len(self.options)

        # Tamaños adaptativos
        base_boton_alto = max(36, min(60, int(alto * 0.07)))
        base_boton_ancho = max(90, min(180, int(ancho * 0.12)))
        boton_ancho_sel = int(base_boton_ancho * 1.15)
        boton_alto_sel = int(base_boton_alto * 1.15)
        espacio_entre_botones = max(10, int(base_boton_ancho * 0.18))
        border_radius = max(14, int(base_boton_alto * 0.38))
        barra_alto = int(base_boton_alto * 2.1)
        margen_superior = max(10, int(alto * 0.04))
        margen_lateral = max(18, int(ancho * 0.03))
        logo_margin = max(10, int(ancho * 0.01))

        # Logo adaptativo
        max_logo_width = int(ancho * 0.16)
        min_logo_width = 32
        if logo is not None:
            logo_w = logo.get_width()
            logo_h = logo.get_height()
            logo_height = min(int(alto * 0.10), int(barra_alto * 1.1)) if logo_height is None else logo_height
            scale = logo_height / logo_h
            logo_width = int(logo_w * scale)
            if logo_width > max_logo_width:
                logo_width = max_logo_width
                scale = logo_width / logo_w
                logo_height = int(logo_h * scale)
            if logo_width < min_logo_width:
                logo_width = min_logo_width
                scale = logo_width / logo_w
                logo_height = int(logo_h * scale)
        else:
            logo_width = 0
            logo_height = 0

        # Calcula ancho total de la barra de botones
        barra_ancho = (num_opciones - 1) * espacio_entre_botones
        for i in range(num_opciones):
            if i == self.selected:
                barra_ancho += boton_ancho_sel
            else:
                barra_ancho += base_boton_ancho

        # Calcula la posición de la barra: deja margen para el logo
        min_x_barra = margen_lateral + logo_width + logo_margin
        barra_x = max((ancho - barra_ancho) // 2, min_x_barra)
        barra_y = margen_superior

        # Sombra suave para la barra
        shadow = get_surface(barra_rect_width := (barra_ancho + 2 * max(10, int(base_boton_ancho * 0.12))),
                             barra_alto, alpha=True)
        pygame.draw.rect(
            shadow, (0, 0, 0, 38),
            (6, 6, barra_rect_width - 12, barra_alto - 12),
            border_radius=border_radius + 8
        )
        surface.blit(shadow, (barra_x - max(10, int(base_boton_ancho * 0.12)), barra_y + 4))

        # Dibuja el logo alineado a la izquierda, ajustado y centrado verticalmente
        if logo is not None:
            logo_scaled = pygame.transform.smoothscale(logo, (logo_width, logo_height))
            logo_y = barra_y + (barra_alto - logo_height) // 2
            logo_x = margen_lateral
            surface.blit(logo_scaled, (logo_x, logo_y))

        # Fuente adaptativa y amigable
        try:
            fuente = pygame.font.SysFont("Arial Rounded MT Bold", int(base_boton_alto * 0.60), bold=True)
        except:
            fuente = pygame.font.SysFont("Segoe UI", int(base_boton_alto * 0.60), bold=True)

        # Colores pastel modernos y agradables
        colores = [
            ((120, 170, 255), (80, 120, 255)),    # Azul
            ((255, 170, 170), (255, 120, 120)),   # Rojo pastel
            ((140, 220, 180), (100, 200, 160)),   # Verde agua
            ((255, 210, 120), (255, 180, 80)),    # Amarillo pastel
            ((200, 160, 255), (160, 120, 255)),   # Lila pastel
        ]
        color_texto = (30, 30, 50)

        # Animación de transición para el botón seleccionado
        ANIM_SPEED = 0.18
        if not hasattr(self, "_anim_size"):
            self._anim_size = 0
        self._anim_size += ANIM_SPEED * ((1 if self.selected else 0) - self._anim_size)

        # Dibuja los botones
        self.botones = []
        x_actual = barra_x
        for i, opcion in enumerate(self.options):
            if i == self.selected:
                boton_ancho = int(base_boton_ancho + (boton_ancho_sel - base_boton_ancho) * min(1, self._anim_size))
                boton_alto = int(base_boton_alto + (boton_alto_sel - base_boton_alto) * min(1, self._anim_size))
                color_top, color_bottom = colores[i % len(colores)]
                borde_blanco = True
            else:
                boton_ancho = base_boton_ancho
                boton_alto = base_boton_alto
                color_top, color_bottom = colores[i % len(colores)]
                borde_blanco = False

            y = barra_y + (barra_alto - boton_alto) // 2

            boton = Boton(
                opcion, x_actual, y, boton_ancho, boton_alto,
                color_texto=color_texto, fuente=fuente,
                border_radius=border_radius, estilo="apple",
                color_top=color_top, color_bottom=color_bottom,
                borde_blanco=borde_blanco
            )
            boton.draw(surface)
            self.botones.append(boton)
            x_actual += boton_ancho + espacio_entre_botones

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

