# main.py
import pygame
import setup.Carga_Configs
from setup.Fondo import estrellas_animadas

def main():
    pygame.init()

    pantalla = pygame.display.set_mode((setup.Carga_Configs.ANCHO, setup.Carga_Configs.ALTO), pygame.RESIZABLE)
    pygame.display.set_caption("Jugando con Dino")
    # Llama al fondo animado
    estrellas_animadas(pantalla)
    

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()

if __name__ == "__main__":
    main()
