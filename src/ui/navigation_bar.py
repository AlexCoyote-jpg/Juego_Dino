# navigation_bar.py
import pygame
"""
Barra de navegación: componente para mostrar y gestionar la navegación entre secciones del juego.
"""

class NavigationBar:
    def __init__(self, options, down=None):
        self.options = options
        self.selected = 0
        self.down = down

    def draw(self, surface):

        # Dibuja la barra de navegación horizontal

        ancho = surface.get_width()
        alto = surface.get_height()
        barra_alto = 60
        barra_color = (230, 230, 240)
        opcion_color = (100, 160, 220)
        opcion_color_sel = (30, 60, 120)
        fuente = pygame.font.SysFont("Segoe UI", 28)
        num_opciones = len(self.options)
        opcion_ancho = ancho // num_opciones
        # Determinar la posición de la barra
        if self.down:
            barra_y = alto - barra_alto
        else:
            barra_y = 0
        # Fondo de la barra
        pygame.draw.rect(surface, barra_color, (0, barra_y, ancho, barra_alto))
        for i, opcion in enumerate(self.options):
            x = i * opcion_ancho
            color = opcion_color_sel if i == self.selected else opcion_color
            rect = pygame.Rect(x + 10, barra_y + 8, opcion_ancho - 20, barra_alto - 16)
            pygame.draw.rect(surface, color, rect, border_radius=12)
            texto = fuente.render(opcion, True, (255, 255, 255) if i == self.selected else (30, 30, 30))
            text_rect = texto.get_rect(center=rect.center)
            surface.blit(texto, text_rect)

    def draw_with_logo(self, surface, logo, logo_height=None):
        import pygame
        ancho = surface.get_width()
        alto = surface.get_height()
        barra_alto = 60
        logo_margin = 16
        # Escalar el logo al alto de la barra si es necesario
        if logo is not None:
            if logo_height is None:
                logo_height = barra_alto - 16  # deja un pequeño margen
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
        # Fondo de la barra
        barra_color = (230, 230, 240)
        #pygame.draw.rect(surface, barra_color, (0, barra_y, ancho, barra_alto))
        # Dibuja el logo escalado
        if logo_scaled:
            surface.blit(logo_scaled, (logo_margin, barra_y + logo_y))
        # Calcula el espacio restante para las opciones
        opciones_x = logo_margin * 2 + logo_width
        opciones_ancho = ancho - opciones_x
        num_opciones = len(self.options)
        opcion_ancho = opciones_ancho // num_opciones
        fuente = pygame.font.SysFont("Segoe UI", 28)
        opcion_color = (100, 160, 220)
        opcion_color_sel = (30, 60, 120)
        for i, opcion in enumerate(self.options):
            x = opciones_x + i * opcion_ancho
            color = opcion_color_sel if i == self.selected else opcion_color
            rect = pygame.Rect(x + 10, barra_y + 8, opcion_ancho - 20, barra_alto - 16)
            pygame.draw.rect(surface, color, rect, border_radius=12)
            texto = fuente.render(opcion, True, (255, 255, 255) if i == self.selected else (30, 30, 30))
            text_rect = texto.get_rect(center=rect.center)
            surface.blit(texto, text_rect)

    def handle_event(self, event, logo=None, logo_height=None):
        import pygame
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_RIGHT:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                return self.selected
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            ancho = pygame.display.get_surface().get_width()
            alto = pygame.display.get_surface().get_height()
            barra_alto = 60
            num_opciones = len(self.options)
            # Ajuste para barra con logo
            logo_margin = 16
            logo_width = 0
            if logo is not None:
                if logo_height is None:
                    logo_height = barra_alto - 16
                scale = logo_height / logo.get_height()
                logo_width = int(logo.get_width() * scale)
            opciones_x = logo_margin * 2 + logo_width if logo is not None else 0
            opciones_ancho = ancho - opciones_x if logo is not None else ancho
            opcion_ancho = opciones_ancho // num_opciones
            mx, my = event.pos
            if self.down:
                barra_y = alto - barra_alto
            else:
                barra_y = 0
            if barra_y < my < barra_y + barra_alto:
                if logo is not None and mx < opciones_x:
                    return None  # Click en el logo, no en las opciones
                idx = (mx - opciones_x) // opcion_ancho if logo is not None else mx // opcion_ancho
                if 0 <= idx < num_opciones:
                    self.selected = idx
                    return self.selected
        return None

