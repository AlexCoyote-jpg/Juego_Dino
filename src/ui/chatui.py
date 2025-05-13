# ui/chatbot_screen.py
import pygame
from ui.components.utils import dibujar_caja_texto, mostrar_texto_adaptativo, Boton
from chatbot.chat import ChatBot

class BotScreen:
    def __init__(self, menu):
        self.menu = menu
        self.chatbot = ChatBot()
        self.texto_usuario = ""
        self.font = pygame.font.SysFont("Segoe UI", 28)
        self.input_rect = pygame.Rect(menu.sx(100), menu.sy(520), menu.pantalla.get_width() - menu.sx(200), menu.sy(50))
        self.color_input = pygame.Color('lightskyblue3')

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                respuesta = self.chatbot.procesar_input(self.texto_usuario)
                self.texto_usuario = ""
            elif event.key == pygame.K_BACKSPACE:
                self.texto_usuario = self.texto_usuario[:-1]
            else:
                self.texto_usuario += event.unicode

    def update(self, dt):
        pass  # Nada que actualizar por ahora

    def draw(self, pantalla):
        pantalla.fill((255, 255, 255))  # Fondo blanco

        # Título
        mostrar_texto_adaptativo(pantalla, "🦖 DinoBot", self.menu.sx(100), self.menu.sy(40),
                                 pantalla.get_width() - self.menu.sx(200), self.menu.sy(60),
                                 pygame.font.SysFont("Segoe UI", 42, bold=True),
                                 (70, 130, 180), centrado=True)

        # Mensajes del chat
        y = self.menu.sy(120)
        for autor, texto in self.chatbot.obtener_historial():
            color = (70, 130, 180) if autor == "bot" else (0, 0, 0)
            mostrar_texto_adaptativo(pantalla, texto, self.menu.sx(100), y,
                                     pantalla.get_width() - self.menu.sx(200), self.menu.sy(40),
                                     self.font, color)
            y += self.menu.sy(50)

        # Input box
        pygame.draw.rect(pantalla, self.color_input, self.input_rect, 2)
        texto_surface = self.font.render(self.texto_usuario, True, (0, 0, 0))
        pantalla.blit(texto_surface, (self.input_rect.x + 10, self.input_rect.y + 10))
