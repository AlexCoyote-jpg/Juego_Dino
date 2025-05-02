# main.py
import pygame
import setup.Carga_Configs
from setup.Fondo import estrellas_animadas, crear_fondo, crear_estrellas

def main():
    pygame.init()

    ancho, alto = setup.Carga_Configs.ANCHO, setup.Carga_Configs.ALTO
    pantalla = pygame.display.set_mode((ancho, alto), pygame.RESIZABLE)
    pygame.display.set_caption("Jugando con Dino")

    fondo = crear_fondo(ancho, alto)
    estrellas = crear_estrellas(ancho, alto)

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                ancho, alto = event.w, event.h
                pantalla = pygame.display.set_mode((ancho, alto), pygame.RESIZABLE)
                fondo = crear_fondo(ancho, alto)
                estrellas = crear_estrellas(ancho, alto)

        estrellas_animadas(pantalla, estrellas, fondo, ancho, alto)
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
