"""
Funciones utilitarias para la interfaz visual: botones, textos y cajas.
"""
import pygame
import emoji

class Boton:
    def __init__(
        self, texto, x, y, ancho, alto,
        color_normal=(220, 230, 245), color_hover=None,
        color_texto=(30, 30, 30), fuente=None,
        border_radius=12, estilo="apple", color_top=None, color_bottom=None,
        borde_blanco=True  # Nuevo parámetro opcional
    ):
        self.texto = texto
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.color_normal = color_normal
        self.color_hover = color_hover
        self.color_texto = color_texto
        self.fuente = fuente or pygame.font.SysFont("Segoe UI", 28)
        self.border_radius = border_radius
        self.estilo = estilo  # "apple", "flat", "round"
        self.color_top = color_top or (90, 180, 255)
        self.color_bottom = color_bottom or (0, 120, 255)
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.borde_blanco = borde_blanco  # Guarda la opción

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
        # Sombra suave y difusa para dar profundidad
        shadow_offset = 3
        shadow_surf = pygame.Surface((self.ancho + 6, self.alto + 6), pygame.SRCALPHA)
        pygame.draw.rect(
            shadow_surf,
            (0, 0, 0, 38),
            (shadow_offset, shadow_offset, self.ancho, self.alto),
            border_radius=self.border_radius + 4
        )
        pantalla.blit(shadow_surf, (self.x - 3, self.y - 3))

        # Degradado vertical sutil y elegante
        temp_surf = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        for i in range(self.alto):
            ratio = i / (self.alto - 1)
            r = int(self.color_top[0] * (1 - ratio) + self.color_bottom[0] * ratio)
            g = int(self.color_top[1] * (1 - ratio) + self.color_bottom[1] * ratio)
            b = int(self.color_top[2] * (1 - ratio) + self.color_bottom[2] * ratio)
            pygame.draw.rect(temp_surf, (r, g, b, 255), (0, i, self.ancho, 1))

        # Bordes suavemente redondeados y máscara para el degradado
        mask = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, self.ancho, self.alto), border_radius=self.border_radius)
        temp_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        pantalla.blit(temp_surf, (self.x, self.y))

        # Borde blanco sutil (opcional, para resaltar el botón seleccionado)
        if self.borde_blanco:
            pygame.draw.rect(
                pantalla,
                (255, 255, 255, 90),
                (self.x, self.y, self.ancho, self.alto),
                width=2,
                border_radius=self.border_radius
            )

       

        mostrar_texto_adaptativo(
            pantalla, self.texto, self.x, self.y, self.ancho, self.alto, self.fuente, self.color_texto, centrado=True
        )

    def _draw_flat(self, pantalla, hovered):
        color = self.color_hover if hovered and self.color_hover else self.color_normal
        pygame.draw.rect(pantalla, color, self.rect, border_radius=self.border_radius)
        mostrar_texto_adaptativo(
            pantalla, self.texto, self.x, self.y, self.ancho, self.alto, self.fuente, self.color_texto, centrado=True
        )

    def _draw_round(self, pantalla, hovered):
        color = self.color_hover if hovered and self.color_hover else self.color_normal
        radius = min(self.ancho, self.alto) // 2
        center = (self.x + self.ancho // 2, self.y + self.alto // 2)
        pygame.draw.circle(pantalla, color, center, radius)
        mostrar_texto_adaptativo(
            pantalla, self.texto, self.x, self.y, self.ancho, self.alto, self.fuente, self.color_texto, centrado=True
        )

    def collidepoint(self, pos):
        if self.estilo == "round":
            center = (self.x + self.ancho // 2, self.y + self.alto // 2)
            radius = min(self.ancho, self.alto) // 2
            return (pos[0] - center[0]) ** 2 + (pos[1] - center[1]) ** 2 <= radius ** 2
        return self.rect.collidepoint(pos)

def mostrar_texto_adaptativo(
    pantalla, texto, x, y, w, h, fuente_base=None, color=(30,30,30), centrado=False
):
    fuente_base = fuente_base or pygame.font.SysFont("Segoe UI", 28)
    font_name = "Segoe UI"
    max_font_size = fuente_base.get_height()
    min_font_size = 12
    parrafos = texto.split('\n\n')
    font_size = max_font_size
    while font_size >= min_font_size:
        fuente = pygame.font.SysFont(font_name, font_size, bold=fuente_base.get_bold())
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
    for i, line in enumerate(lines):
        # Soporte para emojis: usa emoji.emojize para convertir alias a unicode
        line = emoji.emojize(line, language='alias')
        try:
            render = fuente.render(line, True, color)
        except Exception:
            # Si la fuente no soporta el emoji, reemplaza por un espacio
            render = fuente.render(''.join([c if ord(c) < 100000 else ' ' for c in line]), True, color)
        rect = render.get_rect()
        if centrado:
            rect.centerx = x + w // 2
        else:
            rect.x = x
        rect.y = start_y + i * fuente.get_height()
        pantalla.blit(render, rect)

def dibujar_caja_texto(pantalla, x, y, w, h, color, radius=18, texto=None, fuente=None, color_texto=(30,30,30)):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(s, color, (0, 0, w, h), border_radius=radius)
    pantalla.blit(s, (x, y))
    if texto:
        mostrar_texto_adaptativo(
            pantalla, texto, x, y, w, h, fuente, color_texto, centrado=True
        )


'''
boton = Boton(
    "Música", 100, 100, 120, 48,
    color_texto=(255,255,255),
    border_radius=16,
    estilo="apple",
    color_top=(255, 94, 98),      # Apple Music top
    color_bottom=(255, 153, 102), # Apple Music bottom
    color_hover=(255, 120, 120)
)

# Botón plano con hover
boton2 = Boton("Flat", 100, 200, 200, 60, color_normal=(200,200,200), color_hover=(150,150,255), estilo="flat")
boton2.draw(pantalla)

# Botón redondo
boton3 = Boton("🔔", 400, 100, 60, 60, color_normal=(255,200,0), color_hover=(255,150,0), estilo="round")
boton3.draw(pantalla)

# Detectar clic
if boton1.collidepoint(pygame.mouse.get_pos()):
    # Acción
    pass
    
# Botón con borde blanco sutil (por defecto)
boton1 = Boton(
    "Música", 100, 100, 120, 48,
    color_texto=(255,255,255),
    border_radius=16,
    estilo="apple",
    color_top=(255, 94, 98),
    color_bottom=(255, 153, 102)
)
boton1.draw(pantalla)

# Botón SIN borde blanco
boton2 = Boton(
    "Sin borde", 250, 100, 120, 48,
    color_texto=(255,255,255),
    border_radius=16,
    estilo="apple",
    color_top=(60, 140, 255),
    color_bottom=(0, 120, 255),
    borde_blanco=False  # <--- Desactiva el borde blanco
)
boton2.draw(pantalla)    
    
'''