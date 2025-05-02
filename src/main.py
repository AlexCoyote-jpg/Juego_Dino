# main.py
import pygame
import setup.Carga_Configs
from setup.Fondo import estrellas_animadas, crear_fondo, crear_estrellas, FondoAnimadoThread, estrellas_animadas_threadsafe
from setup.Carga_Recursos import Recursos
from menu import MenuPrincipal

def main():
    pygame.init()
    # Usa configuración óptima para pantalla y evita recalcular tamaños
    ancho, alto = setup.Carga_Configs.ANCHO, setup.Carga_Configs.ALTO
    pantalla = pygame.display.set_mode((ancho, alto), pygame.RESIZABLE)
    pygame.display.set_caption("Jugando con Dino")

    # Carga imágenes después de display.set_mode()
    Recursos.cargar_imagenes()

    # Crea fondo y estrellas una sola vez, se actualizan en el menú
    fondo = crear_fondo(ancho, alto)
    estrellas = crear_estrellas(ancho, alto)
    # Inicia el hilo para el fondo animado
    fondo_thread = FondoAnimadoThread(estrellas, ancho, alto)
    fondo_thread.start()

    menu = MenuPrincipal(
        pantalla,
        estrellas,
        fondo,
        estrellas_animadas_threadsafe,  # Usar la versión threadsafe
        crear_fondo,
        crear_estrellas,
        Recursos,
        fondo_thread  # Pasa el hilo al menú
    )
    try:
        menu.ejecutar()
    finally:
        fondo_thread.stop()
        fondo_thread.join()
        pygame.quit()

if __name__ == "__main__":
    main()
