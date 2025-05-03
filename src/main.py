# main.py
import pygame
import logging
from setup.core import (
    Recursos,
    crear_fondo,
    crear_estrellas,
    FondoAnimadoThread,
    estrellas_animadas_threadsafe,
    ALTO,
    ANCHO,
)
from menu import MenuPrincipal

def inicializar_pygame(ancho, alto):
    pygame.init()
    pantalla = pygame.display.set_mode((ancho, alto), pygame.RESIZABLE)
    pygame.display.set_caption("Jugando con Dino")
    return pantalla

def cargar_recursos():
    Recursos.cargar_imagenes()
    Recursos.cargar_sonidos()

def crear_fondo_y_estrellas(ancho, alto):
    fondo = crear_fondo(ancho, alto)
    estrellas = crear_estrellas(ancho, alto)
    return fondo, estrellas

def main():
    logging.basicConfig(level=logging.INFO)
    ancho, alto = ANCHO, ALTO
    pantalla = inicializar_pygame(ancho, alto)
    cargar_recursos()
    fondo, estrellas = crear_fondo_y_estrellas(ancho, alto)
    fondo_thread = FondoAnimadoThread(estrellas, ancho, alto)
    fondo_thread.start()

    menu = MenuPrincipal(
        pantalla,
        estrellas,
        fondo,
        estrellas_animadas_threadsafe,
        crear_fondo,
        crear_estrellas,
        Recursos,
        fondo_thread
    )
    try:
        menu.ejecutar()
    except Exception as e:
        logging.exception("Error inesperado en el menú principal")
    finally:
        fondo_thread.stop()
        fondo_thread.join()
        pygame.quit()

if __name__ == "__main__":
    main()
