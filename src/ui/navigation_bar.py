# navigation_bar.py
import pygame
from .utils import Boton

"""
Barra de navegación: componente para mostrar y gestionar la navegación entre secciones del juego.
"""

class NavigationBar:
    def __init__(self, options, down=None):
        self.options = options
        self.selected = 0
        self.down = down

    def draw(self, surface):
        ancho = surface.get_width()
        alto = surface.get_height()
        barra_alto = 60
        margen_lateral = 40  # margen a los lados
        espacio_entre_botones = 16
        num_opciones = len(self.options)
        boton_ancho = min(180, (ancho - 2 * margen_lateral - (num_opciones - 1) * espacio_entre_botones) // num_opciones)
        boton_alto = barra_alto - 16
        barra_ancho = num_opciones * boton_ancho + (num_opciones - 1) * espacio_entre_botones
        barra_x = (ancho - barra_ancho) // 2
        barra_y = alto - barra_alto if self.down else 0

        # Fondo de la barra solo detrás de los botones, con bordes redondeados
        barra_rect = pygame.Rect(barra_x - 16, barra_y + 4, barra_ancho + 32, barra_alto - 8)
        pygame.draw.rect(surface, (230, 230, 240), barra_rect, border_radius=barra_alto // 2)

        fuente = pygame.font.SysFont("Segoe UI", 28)
        self.botones = []
        for i, opcion in enumerate(self.options):
            x = barra_x + i * (boton_ancho + espacio_entre_botones)
            y = barra_y + 8
            if i == self.selected:
                estilo = "apple"
                color_top = (90, 180, 255)
                color_bottom = (0, 120, 255)
                color_texto = (255, 255, 255)
            else:
                estilo = "apple"
                color_top = (220, 230, 245)
                color_bottom = (180, 200, 230)
                color_texto = (30, 30, 30)
            boton = Boton(
                opcion, x, y, boton_ancho, boton_alto,
                color_texto=color_texto, fuente=fuente,
                border_radius=18, estilo=estilo,
                color_top=color_top, color_bottom=color_bottom
            )
            boton.draw(surface)
            self.botones.append(boton)

    def draw_with_logo(self, surface, logo, logo_height=None):
        ancho = surface.get_width()
        alto = surface.get_height()
        barra_alto = 60
        logo_margin = 16

        # Escalar el logo al alto de la barra si es necesario
        if logo is not None:
            if logo_height is None:
                logo_height = barra_alto - 16
            scale = logo_height / logo.get_height()
            logo_width = int(logo.get_width() * scale)
            logo_scaled = pygame.transform.smoothscale(logo, (logo_width, logo_height))
            logo_y = (barra_alto - logo_height) // 2
        else:
            logo_scaled = None
            logo_width = 0
            logo_y = 0

        if self.down:
            barra_y = alto - barra_alto
        else:
            barra_y = 0

        num_opciones = len(self.options)
        margen_lateral = 40
        espacio_entre_botones = 16
        boton_ancho = min(180, (ancho - logo_width - 2 * logo_margin - 2 * margen_lateral - (num_opciones - 1) * espacio_entre_botones) // num_opciones)
        boton_alto = barra_alto - 16
        barra_ancho = logo_width + 2 * logo_margin + num_opciones * boton_ancho + (num_opciones - 1) * espacio_entre_botones
        barra_x = (ancho - barra_ancho) // 2 + logo_width + logo_margin if logo else (ancho - barra_ancho) // 2
        barra_rect = pygame.Rect(barra_x - 16, barra_y + 4, barra_ancho - logo_width - logo_margin + 32, barra_alto - 8)
        pygame.draw.rect(surface, (230, 230, 240), barra_rect, border_radius=barra_alto // 2)

        fuente = pygame.font.SysFont("Segoe UI", 28)

        # Dibuja el logo escalado
        if logo_scaled:
            surface.blit(logo_scaled, (barra_x - logo_width - logo_margin, barra_y + logo_y))

        self.botones = []
        for i, opcion in enumerate(self.options):
            x = barra_x + i * (boton_ancho + espacio_entre_botones)
            y = barra_y + 8
            if i == self.selected:
                estilo = "apple"
                color_top = (90, 180, 255)
                color_bottom = (0, 120, 255)
                color_texto = (255, 255, 255)
            else:
                estilo = "apple"
                color_top = (220, 230, 245)
                color_bottom = (180, 200, 230)
                color_texto = (30, 30, 30)
            boton = Boton(
                opcion, x, y, boton_ancho, boton_alto,
                color_texto=color_texto, fuente=fuente,
                border_radius=18, estilo=estilo,
                color_top=color_top, color_bottom=color_bottom
            )
            boton.draw(surface)
            self.botones.append(boton)

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

