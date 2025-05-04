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
        # Animación individual por botón
        self._anim_sizes = [0.0 for _ in options]

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
        border_radius = max(14, int(base_boton_alto * 0.26))
        margen_superior = max(20, int(alto * 0.04))
        margen_lateral = max(18, int(ancho * 0.03))
        logo_margin = max(10, int(ancho * 0.01))

        # --- LOGO: Escalado flexible y seguro ---
        if logo is not None:
            logo_w, logo_h = logo.get_width(), logo.get_height()
            # Permite que el logo sea hasta el 25% del alto de la ventana o el 20% del ancho
            max_logo_width = int(ancho * 0.20)
            # Si se pasa logo_height, se usa como límite superior, si no, se calcula
            if logo_height is not None:
                max_logo_height = min(int(alto * 0.25), int(logo_height))
            else:
                max_logo_height = int(alto * 0.25)
            # Calcula el factor de escala sin deformar el logo
            scale = min(max_logo_width / logo_w, max_logo_height / logo_h, 1.5)
            logo_width = int(logo_w * scale)
            logo_height_final = int(logo_h * scale)
            # El margen superior del logo se ajusta para centrarlo respecto a la barra
            margen_superior_logo = max(6, (base_boton_alto - logo_height_final) // 2 + margen_superior)
        else:
            logo_width = 0
            logo_height_final = 0
            margen_superior_logo = 0

        # --- Barra de botones ---
        barra_ancho = (num_opciones - 1) * espacio_entre_botones
        for i in range(num_opciones):
            if i == self.selected:
                barra_ancho += boton_ancho_sel
            else:
                barra_ancho += base_boton_ancho

        min_x_barra = margen_lateral + logo_width + logo_margin
        barra_x = max((ancho - barra_ancho) // 2, min_x_barra)
        barra_y = margen_superior

        # --- Sombra de la barra ---
        shadow_pad_x = max(12, int(base_boton_ancho * 0.13)) 
        shadow_pad_y = max(12, int(base_boton_alto * 0.30))     
        shadow_width = barra_ancho + shadow_pad_x * 2
        shadow_height = base_boton_alto + shadow_pad_y * 2

        shadow = get_surface(shadow_width, shadow_height, alpha=True)
        pygame.draw.rect(
            shadow, (0, 0, 0, 32),
            (0, 0, shadow_width, shadow_height),
            border_radius=border_radius + 8
        )
        surface.blit(shadow, (barra_x - shadow_pad_x, barra_y - shadow_pad_y))

        # --- Dibuja el logo (puede sobresalir la sombra, pero no la barra) ---
        if logo is not None:
            logo_scaled = pygame.transform.smoothscale(logo, (logo_width, logo_height_final))
            logo_y = margen_superior_logo
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

        # Animación de transición para cada botón
        ANIM_SPEED = 0.22  # Ligeramente más rápido para mayor fluidez
        for i in range(len(self.options)):
            target = 1.0 if i == self.selected else 0.0
            # Interpolación lineal suave (lerp)
            self._anim_sizes[i] += (target - self._anim_sizes[i]) * ANIM_SPEED

        # Dibuja los botones
        self.botones = []
        x_actual = barra_x
        for i, opcion in enumerate(self.options):
            anim = min(1.0, max(0.0, self._anim_sizes[i]))
            if i == self.selected:
                boton_ancho = int(base_boton_ancho + (boton_ancho_sel - base_boton_ancho) * anim)
                boton_alto = int(base_boton_alto + (boton_alto_sel - base_boton_alto) * anim)
                color_top, color_bottom = colores[i % len(colores)]
                borde_blanco = True
            else:
                boton_ancho = int(base_boton_ancho + (boton_ancho_sel - base_boton_ancho) * anim)
                boton_alto = int(base_boton_alto + (boton_alto_sel - base_boton_alto) * anim)
                color_top, color_bottom = colores[i % len(colores)]
                borde_blanco = False

            y = barra_y + (base_boton_alto - boton_alto) // 2

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

