import pygame
import time


FUENTES_CACHE = {}
FUENTE_NOMBRE = "Segoe UI"
FUENTE_BASE = None  # Eliminated the direct SysFont creation here

def get_default_font():
    global FUENTE_BASE
    # Initialize the font subsystem if needed
    if not pygame.font.get_init():
        pygame.font.init()
    # Create the default font lazily
    if FUENTE_BASE is None:
        FUENTE_BASE = pygame.font.SysFont(FUENTE_NOMBRE, 28)
    return FUENTE_BASE

def obtener_fuente(tamaño, negrita=False):
    clave = (tamaño, negrita)
    if clave not in FUENTES_CACHE:
        # Ensure font subsystem is initialized before creating
        if not pygame.font.get_init():
            pygame.font.init()
        FUENTES_CACHE[clave] = pygame.font.SysFont(FUENTE_NOMBRE, tamaño, bold=negrita)
    return FUENTES_CACHE[clave]

class Boton:
    def __init__(self, texto, x, y, ancho, alto,
                 color_normal=(220, 230, 245), color_hover=None,
                 color_texto=(30, 30, 30), fuente=None,
                 border_radius=12, estilo="apple",
                 color_top=None, color_bottom=None,
                 borde_blanco=True):
        self.texto = texto
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.color_normal = color_normal
        self.color_hover = color_hover
        self.color_texto = color_texto
        self.fuente = fuente or get_default_font()
        self.border_radius = border_radius
        self.estilo = estilo
        self.color_top = color_top or (90, 180, 255)
        self.color_bottom = color_bottom or (0, 120, 255)
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.borde_blanco = borde_blanco
        self._gradiente_cache = None
        self._last_hovered = None

    def draw(self, pantalla):
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mouse_pos)
        if self.estilo == "apple":
            self._draw_apple(pantalla)
        elif self.estilo == "round":
            self._draw_round(pantalla, hovered)
        else:
            self._draw_flat(pantalla, hovered)

    def _draw_apple(self, pantalla):
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mouse_pos)
        shadow_offset = 3
        shadow_rect = pygame.Rect(self.x - 3, self.y - 3, self.ancho + 6, self.alto + 6)
        shadow_surf = pygame.Surface((shadow_rect.w, shadow_rect.h), pygame.SRCALPHA)
        pygame.draw.rect(
            shadow_surf, (0, 0, 0, 38),
            (shadow_offset, shadow_offset, self.ancho, self.alto),
            border_radius=self.border_radius + 4
        )
        pantalla.blit(shadow_surf, shadow_rect.topleft)

        # Cambia el gradiente si está hovered
        color_top = self.color_hover if hovered and self.color_hover else self.color_top
        color_bottom = self.color_hover if hovered and self.color_hover else self.color_bottom

        if self._gradiente_cache is None or hovered != getattr(self, "_last_hovered", None):
            grad = pygame.Surface((1, self.alto), pygame.SRCALPHA)
            for i in range(self.alto):
                ratio = i / (self.alto - 1) if self.alto > 1 else 0
                r = int(color_top[0] * (1 - ratio) + color_bottom[0] * ratio)
                g = int(color_top[1] * (1 - ratio) + color_bottom[1] * ratio)
                b = int(color_top[2] * (1 - ratio) + color_bottom[2] * ratio)
                grad.set_at((0, i), (r, g, b, 255))
            self._gradiente_cache = pygame.transform.scale(grad, (self.ancho, self.alto))
            self._last_hovered = hovered

        gradiente = self._gradiente_cache.copy()
        mask = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, self.ancho, self.alto), border_radius=self.border_radius)
        gradiente.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        pantalla.blit(gradiente, (self.x, self.y))

        if self.borde_blanco:
            pygame.draw.rect(
                pantalla, (255, 255, 255, 90),
                (self.x, self.y, self.ancho, self.alto),
                width=2, border_radius=self.border_radius
            )

        mostrar_texto_adaptativo(
            pantalla, self.texto, self.x, self.y, self.ancho, self.alto,
            self.fuente, self.color_texto, centrado=True
        )

    def _draw_flat(self, pantalla, hovered):
        color = self.color_hover if hovered and self.color_hover else self.color_normal
        pygame.draw.rect(pantalla, color, self.rect, border_radius=self.border_radius)
        mostrar_texto_adaptativo(
            pantalla, self.texto, self.x, self.y, self.ancho, self.alto,
            self.fuente, self.color_texto, centrado=True
        )

    def _draw_round(self, pantalla, hovered):
        color = self.color_hover if hovered and self.color_hover else self.color_normal
        radius = min(self.ancho, self.alto) // 2
        center = (self.x + self.ancho // 2, self.y + self.alto // 2)
        pygame.draw.circle(pantalla, color, center, radius)
        mostrar_texto_adaptativo(
            pantalla, self.texto, self.x, self.y, self.ancho, self.alto,
            self.fuente, self.color_texto, centrado=True
        )

    def collidepoint(self, pos):
        if self.estilo == "round":
            center = (self.x + self.ancho // 2, self.y + self.alto // 2)
            radius = min(self.ancho, self.alto) // 2
            return (pos[0] - center[0]) ** 2 + (pos[1] - center[1]) ** 2 <= radius ** 2
        return self.rect.collidepoint(pos)


def mostrar_texto_adaptativo(
    pantalla: pygame.Surface,
    texto: str,
    x: int,
    y: int,
    w: int,
    h: int,
    fuente_base: pygame.font.Font = None,
    color: tuple = (30, 30, 30),
    centrado: bool = False
):
    """
    Dibuja texto adaptando el tamaño de fuente para que quepa en el área dada.
    Usa búsqueda binaria para optimizar el ajuste.
    """
    fuente_base = fuente_base or get_default_font()
    max_font_size = fuente_base.get_height()
    min_font_size = 12
    parrafos = texto.split('\n\n')

    def get_lines(font):
        lines = []
        for parrafo in parrafos:
            for raw_line in parrafo.split('\n'):
                words = raw_line.split()
                line = ""
                for word in words:
                    test_line = f"{line} {word}".strip()
                    if font.size(test_line)[0] <= w:
                        line = test_line
                    else:
                        if line:
                            lines.append(line)
                        line = word
                if line:
                    lines.append(line)
            if parrafo != parrafos[-1]:
                lines.append("")
        return lines

    # Búsqueda binaria para el tamaño de fuente
    left, right = min_font_size, max_font_size
    best_size = min_font_size
    best_lines = []
    while left <= right:
        mid = (left + right) // 2
        fuente = obtener_fuente(mid, fuente_base.get_bold())
        lines = get_lines(fuente)
        total_height = len(lines) * fuente.get_height()
        if total_height <= h:
            best_size = mid
            best_lines = lines
            left = mid + 1
        else:
            right = mid - 1

    fuente = obtener_fuente(best_size, fuente_base.get_bold())
    total_height = len(best_lines) * fuente.get_height()
    start_y = y + (h - total_height) // 2 if centrado else y

    for i, line in enumerate(best_lines):
        try:
            render = fuente.render(line, True, color)
        except Exception:
            render = fuente.render(''.join([c if ord(c) < 100000 else ' ' for c in line]), True, color)
        rect = render.get_rect()
        rect.centerx = x + w // 2 if centrado else x
        rect.y = start_y + i * fuente.get_height()
        pantalla.blit(render, rect)


def dibujar_caja_texto(pantalla, x, y, w, h, color, radius=18, texto=None, fuente=None, color_texto=(30, 30, 30)):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(s, color, (0, 0, w, h), border_radius=radius)
    pantalla.blit(s, (x, y))
    if texto:
        mostrar_texto_adaptativo(
            pantalla, texto, x, y, w, h, fuente or get_default_font(), color_texto, centrado=True
        )


def dibujar_barra_scroll(surface, x, y, w, h, scroll_pos, total_height, visible_height, color=(200, 200, 200), highlight=False):
    """
    Dibuja una barra de desplazamiento vertical.
    Oculta la barra si no es necesaria.
    Permite saltar al hacer click en la barra.
    """
    if total_height <= visible_height or h <= 0:
        return None  # No necesita scroll ni barra

    bar_width = 10
    # Optimización: calcula proporción solo una vez
    vis_ratio = visible_height / total_height
    thumb_height = max(30, int(visible_height * vis_ratio))
    max_scroll = total_height - visible_height
    # Evita división por cero
    if max_scroll == 0:
        thumb_pos = y
    else:
        thumb_pos = y + int(scroll_pos * (h - thumb_height) / max_scroll)

    # Fondo de la barra
    bar_rect = pygame.Rect(x + w - bar_width, y, bar_width, h)
    pygame.draw.rect(surface, (100, 100, 100, 100), bar_rect, border_radius=5)

    # Thumb con feedback visual
    thumb_color = (150, 180, 255) if highlight else color
    thumb_rect = pygame.Rect(x + w - bar_width, thumb_pos, bar_width, thumb_height)
    pygame.draw.rect(surface, thumb_color, thumb_rect, border_radius=5)

    return thumb_rect  # Devuelve el rectángulo del thumb para detección de drag


# Clase para gestionar el scroll
class ScrollManager:
    def __init__(self, initial_pos=0):
        self.scroll_pos = initial_pos
        self.target_scroll = initial_pos
        self.last_update = time.time()
        self.dragging = False
        self.drag_offset = 0

    def update(self, max_scroll, smooth=True):
        current_time = time.time()
        dt = current_time - self.last_update
        self.last_update = current_time

        if smooth:
            diff = self.target_scroll - self.scroll_pos
            # Optimización: solo actualiza si hay diferencia significativa
            if abs(diff) > 0.5:
                self.scroll_pos += diff * min(1.0, dt * 10)
            else:
                self.scroll_pos = self.target_scroll
        else:
            self.scroll_pos = self.target_scroll

        self.scroll_pos = max(0, min(self.scroll_pos, max_scroll))
        self.target_scroll = max(0, min(self.target_scroll, max_scroll))
        return int(self.scroll_pos)

    def scroll_to(self, pos):
        self.target_scroll = pos

    def scroll_by(self, delta):
        self.target_scroll += delta

    def handle_event(self, event, wheel_speed=40, thumb_rect=None, max_scroll=0, h=0, y=0, bar_rect=None):
        """
        Maneja eventos de rueda, drag del mouse y click en la barra para saltar.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll hacia arriba
                self.scroll_by(-wheel_speed)
                return True
            elif event.button == 5:  # Scroll hacia abajo
                self.scroll_by(wheel_speed)
                return True
            elif event.button == 1:
                # Drag del thumb
                if thumb_rect and thumb_rect.collidepoint(event.pos):
                    self.dragging = True
                    self.drag_offset = event.pos[1] - thumb_rect.y
                    return True
                # Click en la barra fuera del thumb para saltar
                elif bar_rect and bar_rect.collidepoint(event.pos):
                    # Saltar el scroll al centro del thumb donde se hizo click
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
            # Calcular nueva posición de scroll basada en el movimiento del mouse
            new_thumb_y = event.pos[1] - self.drag_offset
            bar_height = h
            thumb_height = thumb_rect.height
            max_thumb_y = y + bar_height - thumb_height
            new_thumb_y = max(y, min(new_thumb_y, max_thumb_y))
            # Convertir posición del thumb a scroll_pos
            if max_scroll > 0 and bar_height > thumb_height:
                self.target_scroll = int((new_thumb_y - y) * max_scroll / (bar_height - thumb_height))
            return True
        return False

