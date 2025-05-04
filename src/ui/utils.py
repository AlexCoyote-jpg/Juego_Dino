"""
Funciones utilitarias para la interfaz visual: botones, textos y cajas.
"""
import pygame

def dibujar_boton(pantalla, texto, x, y, ancho, alto, color_normal, color_hover, fuente=None):
    mouse_pos = pygame.mouse.get_pos()
    rect = pygame.Rect(x, y, ancho, alto)
    color = color_hover if rect.collidepoint(mouse_pos) else color_normal
    pygame.draw.rect(pantalla, color, rect, border_radius=10)
    mostrar_texto_adaptativo(
        pantalla, texto, x, y, ancho, alto, fuente, (30, 30, 30), centrado=True
    )
    return rect

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
        render = fuente.render(line, True, color)
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
