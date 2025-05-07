import pygame
from core.juego_base import JuegoBase

class MiJuego(JuegoBase):
    def __init__(self, pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu):
        super().__init__(pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu)
        self.circulo_color = (0, 120, 255)
        self.circulo_radio = 60

    def update(self, dt=None):
        # Aquí podrías actualizar la lógica del juego
        pass

    def draw(self, surface):
        self.pantalla = surface  # Asegura que self.pantalla no sea None
        self.dibujar_fondo()
        # Dibuja un círculo centrado
        centro = (self.ANCHO // 2, self.ALTO // 2)
        pygame.draw.circle(surface, self.circulo_color, centro, self.circulo_radio)
        self.mostrar_texto("Redimensiona la ventana", self.ANCHO // 2, 40, self.fuente_titulo, centrado=True)

    def on_resize(self, ancho, alto):
        # El círculo siempre se mantiene centrado, así que no es necesario hacer nada extra aquí
        pass