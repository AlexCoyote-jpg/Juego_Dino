# main.py
import pygame
from setup.Fondo import dibujar_fondo

def main():
    pygame.init()
    # Define el tamaño de la ventana que quieras
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Llama a tu función de fondo en cada frame
        dibujar_fondo(screen, num_elementos=15)

        pygame.display.flip()
        clock.tick(30)  # limita a 30 FPS

    pygame.quit()

if __name__ == "__main__":
    main()
