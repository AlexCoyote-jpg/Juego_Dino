"""
Pantalla de victoria y botón para avanzar de nivel.
"""
import pygame
from ..ui.utils import mostrar_texto_adaptativo, dibujar_boton

def mostrar_victoria(
    pantalla, sx, sy, ancho, alto, fuente_titulo, fuente_texto, juego_base, carta_rects,
    color_panel=(255, 255, 224), color_borde=(255, 215, 0)
):
    ancho_panel = sx(500)
    alto_panel = sy(200)
    x_panel = (ancho - ancho_panel) // 2
    y_panel = (alto - alto_panel) // 2
    panel = pygame.Surface((ancho_panel, alto_panel), pygame.SRCALPHA)
    for i in range(alto_panel):
        factor = i / alto_panel
        r = int(255 - factor * 50)
        g = int(250 - factor * 20)
        b = int(150 + factor * 50)
        pygame.draw.line(panel, (r, g, b, 240), (0, i), (ancho_panel, i))
    pantalla.blit(panel, (x_panel, y_panel))
    pygame.draw.rect(pantalla, color_borde, (x_panel, y_panel, ancho_panel, alto_panel), 4, border_radius=20)
    mostrar_texto_adaptativo(
        pantalla, "¡FELICIDADES! 🎉",
        x_panel, y_panel + sy(20), ancho_panel, sy(60),
        fuente_titulo, (100, 160, 220), centrado=True
    )
    mostrar_texto_adaptativo(
        pantalla, "¡Has completado el nivel!",
        x_panel, y_panel + sy(80), ancho_panel, sy(40),
        fuente_texto, (30, 30, 30), centrado=True
    )
    boton_rect = dibujar_boton(
        juego_base["pantalla"],
        "¡Siguiente nivel! 👉",
        x_panel + (ancho_panel - sx(300)) // 2,
        y_panel + sy(130),
        sx(300), sy(50),
        (100, 160, 220), (30, 60, 120), fuente_texto
    )
    carta_rects.append((boton_rect, {'id': 'siguiente'}))
