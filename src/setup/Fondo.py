import pygame
import random

def dibujar_gradiente(superficie, rect, color1, color2, vertical=True):
    """Dibuja un gradiente en la superficie dada."""
    if vertical:
        for y in range(rect.height):
            factor = y / rect.height
            color = (
                int(color1[0] + (color2[0] - color1[0]) * factor),
                int(color1[1] + (color2[1] - color1[1]) * factor),
                int(color1[2] + (color2[2] - color1[2]) * factor)
            )
            pygame.draw.line(superficie, color, (rect.left, rect.top + y), (rect.right, rect.top + y))
    else:
        for x in range(rect.width):
            factor = x / rect.width
            color = (
                int(color1[0] + (color2[0] - color1[0]) * factor),
                int(color1[1] + (color2[1] - color1[1]) * factor),
                int(color1[2] + (color2[2] - color1[2]) * factor)
            )
            pygame.draw.line(superficie, color, (rect.left + x, rect.top), (rect.left + x, rect.bottom))

def dibujar_fondo(pantalla, ancho, alto):
    """Dibuja el fondo con degradado y elementos decorativos."""
    rect_fondo = pygame.Rect(0, 0, ancho, alto)
    dibujar_gradiente(pantalla, rect_fondo, (255, 250, 240), (255, 235, 205))
    for i in range(10):
        x = random.randint(0, ancho)
        y = random.randint(0, alto)
        tamaño = random.randint(5, 15)
        pygame.draw.circle(pantalla, (255, 255, 255, 128), (x, y), tamaño)