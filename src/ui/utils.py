import pygame



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
        shadow_offset = 3
        shadow_rect = pygame.Rect(self.x - 3, self.y - 3, self.ancho + 6, self.alto + 6)
        shadow_surf = pygame.Surface((shadow_rect.w, shadow_rect.h), pygame.SRCALPHA)
        pygame.draw.rect(
            shadow_surf, (0, 0, 0, 38),
            (shadow_offset, shadow_offset, self.ancho, self.alto),
            border_radius=self.border_radius + 4
        )
        pantalla.blit(shadow_surf, shadow_rect.topleft)

        if self._gradiente_cache is None:
            grad = pygame.Surface((1, self.alto), pygame.SRCALPHA)
            for i in range(self.alto):
                ratio = i / (self.alto - 1) if self.alto > 1 else 0
                r = int(self.color_top[0] * (1 - ratio) + self.color_bottom[0] * ratio)
                g = int(self.color_top[1] * (1 - ratio) + self.color_bottom[1] * ratio)
                b = int(self.color_top[2] * (1 - ratio) + self.color_bottom[2] * ratio)
                grad.set_at((0, i), (r, g, b, 255))
            self._gradiente_cache = pygame.transform.scale(grad, (self.ancho, self.alto))

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


def mostrar_texto_adaptativo(pantalla, texto, x, y, w, h, fuente_base=None, color=(30, 30, 30), centrado=False):
    fuente_base = fuente_base or get_default_font()
    font_name = FUENTE_NOMBRE
    max_font_size = fuente_base.get_height()
    min_font_size = 12
    parrafos = texto.split('\n\n')
    font_size = max_font_size

    while font_size >= min_font_size:
        fuente = obtener_fuente(font_size, fuente_base.get_bold())
        lines = []
        for parrafo in parrafos:
            for raw_line in parrafo.split('\n'):
                words = raw_line.split()
                line = ""
                for word in words:
                    test_line = f"{line} {word}".strip()
                    if fuente.size(test_line)[0] <= w:
                        line = test_line
                    else:
                        lines.append(line)
                        line = word
                if line:
                    lines.append(line)
            if parrafo != parrafos[-1]:
                lines.append("")
        total_height = len(lines) * fuente.get_height()
        if total_height <= h:
            break
        font_size -= 1

    start_y = y + (h - total_height) // 2 if centrado else y
    fuente = obtener_fuente(font_size, fuente_base.get_bold())

    for i, line in enumerate(lines):
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
