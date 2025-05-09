import pygame
from ui.components.utils import get_gradient

def dibujar_fondo(juego):
    """
    Dibuja el fondo con gradiente o imagen, respetando la barra de navegación.
    Versión mejorada con estilo Apple para niños.
    """
    if juego.fondo:
        if isinstance(juego.fondo, pygame.Surface):
            fondo_escalado = pygame.transform.scale(juego.fondo, (juego.ANCHO, juego.ALTO))
            juego.pantalla.blit(fondo_escalado, (0, 0))
        elif isinstance(juego.fondo, tuple) and len(juego.fondo) >= 3:
            juego.pantalla.fill(juego.fondo)
        elif isinstance(juego.fondo, tuple) and len(juego.fondo) == 2:
            gradiente = get_gradient(juego.ANCHO, juego.ALTO, juego.fondo[0], juego.fondo[1])
            juego.pantalla.blit(gradiente, (0, 0))
    else:
        gradiente = get_gradient(
            juego.ANCHO, juego.ALTO, 
            (240, 248, 255),
            (230, 240, 250)
        )
        juego.pantalla.blit(gradiente, (0, 0))
        juego.dibujar_nubes()
        juego.dibujar_burbujas()