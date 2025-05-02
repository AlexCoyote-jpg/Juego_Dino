# main.py
import pygame
from setup.Fondo import estrellas_animadas

def main():
    pygame.init()
    # Define el tamaño de la ventana que quieras (o usa (0, 0) para tamaño máximo disponible)
    width, height = 800, 600
    pantalla = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption("Jugando con Dino")
    # Llama al fondo animado
    estrellas_animadas(pantalla)
    pygame.quit()

if __name__ == "__main__":
    main()
