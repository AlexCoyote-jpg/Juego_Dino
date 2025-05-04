import pygame
import sys
import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'core')))
from core.background import crear_fondo, crear_estrellas, actualizar_estrellas

ANCHO, ALTO = 800, 600

pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption('Prueba de Fondo y Estrellas')
clock = pygame.time.Clock()

fondo = crear_fondo(ANCHO, ALTO)
estrellas = crear_estrellas(ANCHO, ALTO)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pantalla.blit(fondo, (0, 0))
    for estrella in estrellas:
        estrella.update(ANCHO, ALTO)
        estrella.draw(pantalla)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
