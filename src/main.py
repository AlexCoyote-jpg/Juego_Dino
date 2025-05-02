# main.py
import pygame
import setup.Carga_Configs
from setup.Fondo import estrellas_animadas, crear_fondo, crear_estrellas
from menu import MenuPrincipal  # Asegúrate de importar tu menú

def main():
    pygame.init()

    ancho, alto = setup.Carga_Configs.ANCHO, setup.Carga_Configs.ALTO
    pantalla = pygame.display.set_mode((ancho, alto), pygame.RESIZABLE)
    pygame.display.set_caption("Jugando con Dino")

    fondo = crear_fondo(ancho, alto)
    estrellas = crear_estrellas(ancho, alto)

    # Pasa las variables y funciones necesarias al menú
    menu = MenuPrincipal(
        pantalla,
        estrellas,
        fondo,
        estrellas_animadas,
        crear_fondo,
        crear_estrellas
    )
    menu.ejecutar()

    pygame.quit()

if __name__ == "__main__":
    main()
