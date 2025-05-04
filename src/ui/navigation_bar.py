# navigation_bar.py
"""
Barra de navegación: componente para mostrar y gestionar la navegación entre secciones del juego.
"""

class NavigationBar:
    def __init__(self, options):
        self.options = options
        self.selected = 0

    def draw(self, surface):
        # Dibuja la barra de navegación horizontal en la parte inferior
        import pygame
        ancho = surface.get_width()
        alto = surface.get_height()
        barra_alto = 60
        barra_color = (230, 230, 240)
        opcion_color = (100, 160, 220)
        opcion_color_sel = (30, 60, 120)
        fuente = pygame.font.SysFont("Segoe UI", 28)
        num_opciones = len(self.options)
        opcion_ancho = ancho // num_opciones
        # Fondo de la barra
        pygame.draw.rect(surface, barra_color, (0, alto - barra_alto, ancho, barra_alto))
        for i, opcion in enumerate(self.options):
            x = i * opcion_ancho
            color = opcion_color_sel if i == self.selected else opcion_color
            rect = pygame.Rect(x + 10, alto - barra_alto + 8, opcion_ancho - 20, barra_alto - 16)
            pygame.draw.rect(surface, color, rect, border_radius=12)
            texto = fuente.render(opcion, True, (255, 255, 255) if i == self.selected else (30, 30, 30))
            text_rect = texto.get_rect(center=rect.center)
            surface.blit(texto, text_rect)

    def handle_event(self, event):
        # Permite navegar con flechas izquierda/derecha y seleccionar con Enter
        import pygame
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_RIGHT:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                return self.selected  # Devuelve el índice seleccionado
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            ancho = pygame.display.get_surface().get_width()
            alto = pygame.display.get_surface().get_height()
            barra_alto = 60
            num_opciones = len(self.options)
            opcion_ancho = ancho // num_opciones
            mx, my = event.pos
            if alto - barra_alto < my < alto:
                idx = mx // opcion_ancho
                if 0 <= idx < num_opciones:
                    self.selected = idx
                    return self.selected
        return None

