# Ejemplo para menu.py
import pygame

class MenuPrincipal:
    def __init__(self, pantalla, estrellas, fondo, estrellas_animadas, crear_fondo, crear_estrellas):
        self.pantalla = pantalla
        self.estrellas = estrellas
        self.fondo = fondo
        self.estrellas_animadas = estrellas_animadas
        self.crear_fondo = crear_fondo
        self.crear_estrellas = crear_estrellas

    def ejecutar(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    ancho, alto = event.w, event.h
                    self.pantalla = pygame.display.set_mode((ancho, alto), pygame.RESIZABLE)
                    self.fondo = self.crear_fondo(ancho, alto)
                    self.estrellas = self.crear_estrellas(ancho, alto)
            self.estrellas_animadas(self.pantalla, self.estrellas, self.fondo, self.pantalla.get_width(), self.pantalla.get_height())
            # Aquí dibuja los elementos del menú encima del fondo
            pygame.display.flip()
            clock.tick(30)