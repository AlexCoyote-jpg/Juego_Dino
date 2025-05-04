"""
Animaciones visuales para el juego (dinos, fondo animado, etc).
"""
import pygame
import math

def animar_dinos(pantalla, imagenes_dinos, posiciones, escala, tiempo_ms):
    for i, (img, pos) in enumerate(zip(imagenes_dinos, posiciones)):
        offset_y = int(10 * escala * abs(math.sin((tiempo_ms + i*1000) / 500)))
        escala_dino = escala * (1.0 + 0.1 * abs(math.sin((tiempo_ms + i*1000) / 800)))
        tamaño = int(100 * escala_dino)
        img_scaled = pygame.transform.smoothscale(img, (tamaño, tamaño))
        pos_x = pos[0] - (tamaño - int(100 * escala)) // 2
        pos_y = pos[1] - offset_y - (tamaño - int(100 * escala)) // 2
        pantalla.blit(img_scaled, (pos_x, pos_y))

def get_surface(ancho, alto, alpha=False):
    if alpha:
        return pygame.Surface((ancho, alto), pygame.SRCALPHA)
    return pygame.Surface((ancho, alto))

def dibujar_fondo_animado(pantalla, ancho, alto, fondo_thread, estrellas_animadas, fondo, estrellas):
    try:
        if fondo_thread:
            estrellas_animadas(pantalla, fondo or get_surface(ancho, alto), fondo_thread)
        else:
            estrellas = estrellas or get_surface(ancho, alto, alpha=True)
            fondo = fondo or get_surface(ancho, alto)
            estrellas_animadas(pantalla, estrellas, fondo, ancho, alto)
    except Exception:
        pantalla.fill((135, 206, 250))  # Azul cielo por defecto
