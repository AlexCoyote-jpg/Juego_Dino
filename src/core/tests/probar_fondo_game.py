import pygame
import sys
from core.decoration.background_game import FondoAnimado

def main():
    pygame.init()
    ANCHO, ALTO = 900, 700
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Prueba FondoAnimado")

    fondo = FondoAnimado(pantalla, ANCHO, ALTO)

    clock = pygame.time.Clock()
    running = True
    frames = 0

    while running and frames < 6000:  # Corre la prueba por ~5 segundos a 60 FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        fondo.actualizar_nubes()
        fondo.actualizar_burbujas()
        fondo.dibujar_fondo()

        pygame.display.flip()
        clock.tick(60)
        frames += 1

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()