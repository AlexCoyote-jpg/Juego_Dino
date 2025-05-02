import pygame
import random


def dibujar_gradiente(surf: pygame.Surface, color1: tuple, color2: tuple, vertical: bool = True) -> None:
    """
    Dibuja un gradiente de color en toda la superficie proporcionada.

    Args:
        surf: Superficie de Pygame donde se dibuja el gradiente.
        color1: Color inicial (R, G, B).
        color2: Color final (R, G, B).
        vertical: Si es True, el gradiente es vertical; si es False, es horizontal.
    """
    width, height = surf.get_size()
    if vertical:
        for y in range(height):
            factor = y / float(height - 1)
            color = (
                int(color1[0] + (color2[0] - color1[0]) * factor),
                int(color1[1] + (color2[1] - color1[1]) * factor),
                int(color1[2] + (color2[2] - color1[2]) * factor)
            )
            pygame.draw.line(surf, color, (0, y), (width, y))
    else:
        for x in range(width):
            factor = x / float(width - 1)
            color = (
                int(color1[0] + (color2[0] - color1[0]) * factor),
                int(color1[1] + (color2[1] - color1[1]) * factor),
                int(color1[2] + (color2[2] - color1[2]) * factor)
            )
            pygame.draw.line(surf, color, (x, 0), (x, height))


def _dibujar_figura_aleatoria(overlay: pygame.Surface, width: int, height: int) -> None:
    """
    Dibuja una figura geométrica aleatoria (círculo, rectángulo, elipse o triángulo) en la superficie overlay.

    Args:
        overlay: Superficie con canal alfa donde se dibuja la figura.
        width: Ancho máximo del área para posicionar la figura.
        height: Alto máximo del área para posicionar la figura.
    """
    shapes = ['circle', 'rect', 'ellipse', 'triangle']
    shape = random.choice(shapes)
    color = (255, 255, 255, 128)  # Blanco semi-transparente

    if shape == 'circle':
        x = random.randint(0, width)
        y = random.randint(0, height)
        radius = random.randint(5, 20)
        pygame.draw.circle(overlay, color, (x, y), radius)

    elif shape == 'rect':
        w = random.randint(10, 40)
        h = random.randint(10, 40)
        x = random.randint(0, width - w)
        y = random.randint(0, height - h)
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(overlay, color, rect)

    elif shape == 'ellipse':
        w = random.randint(10, 40)
        h = random.randint(10, 40)
        x = random.randint(0, width - w)
        y = random.randint(0, height - h)
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.ellipse(overlay, color, rect)

    elif shape == 'triangle':
        pt1 = (random.randint(0, width), random.randint(0, height))
        pt2 = (random.randint(0, width), random.randint(0, height))
        pt3 = (random.randint(0, width), random.randint(0, height))
        pygame.draw.polygon(overlay, color, [pt1, pt2, pt3])


def dibujar_fondo(surf: pygame.Surface, num_elementos: int = 10) -> None:
    """
    Dibuja un fondo con degradado y formas geométricas aleatorias semi-transparentes.

    Args:
        surf: Superficie de Pygame donde se dibuja el fondo.
        num_elementos: Número de formas aleatorias a dibujar.
    """
    # Colores base del degradado (puedes ajustarlos según tu tema)
    color_inicio = (255, 250, 240)
    color_fin = (255, 235, 205)
    dibujar_gradiente(surf, color_inicio, color_fin, vertical=True)

    width, height = surf.get_size()
    overlay = pygame.Surface((width, height), flags=pygame.SRCALPHA)

    for _ in range(num_elementos):
        _dibujar_figura_aleatoria(overlay, width, height)

    # Superpone las figuras sobre el fondo
    surf.blit(overlay, (0, 0))


# Ejemplo de uso:
#
# pygame.init()
# screen = pygame.display.set_mode((800, 600))
# dibujar_fondo(screen, num_elementos=15)
# pygame.display.flip()
