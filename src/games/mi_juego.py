# src/games/mi_juego.py
from core.game_state import JuegoBase
import pygame

class MiJuego(JuegoBase):
    def __init__(self, pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu=None):
        super().__init__('MiJuego', pantalla, config, dificultad, fondo, navbar, images, sounds)
        self.return_to_menu = return_to_menu

    def update(self):
        pass

    def draw(self, surface=None):
        pantalla = surface if surface else self.pantalla
        pantalla.fill((200, 220, 255))  # Color de fondo visible
        self.mostrar_texto("¡Hola desde MiJuego!", self.ANCHO // 2, self.ALTO // 2, centrado=True)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.return_to_menu:
                self.return_to_menu()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_1:
            print("Opción 1 seleccionada")