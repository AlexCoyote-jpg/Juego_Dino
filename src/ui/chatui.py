import pygame
from ui.components.utils import dibujar_caja_texto, mostrar_texto_adaptativo, Boton
from chatbot.chat import ChatBot

def wrap_text(texto, fuente, max_width):
    palabras = texto.split(' ')
    lineas = []
    linea_actual = ""

    for palabra in palabras:
        test_line = linea_actual + palabra + " "
        if fuente.size(test_line)[0] <= max_width:
            linea_actual = test_line
        else:
            lineas.append(linea_actual.strip())
            linea_actual = palabra + " "
    if linea_actual:
        lineas.append(linea_actual.strip())

    return lineas

class BotScreen:
    def __init__(self, menu):
        self.menu = menu
        self.chatbot = ChatBot()
        self.texto_usuario = ""
        self.font = pygame.font.SysFont("Segoe UI", 28)
        self.input_rect = pygame.Rect(menu.sx(100), menu.sy(520), menu.pantalla.get_width() - menu.sx(200), menu.sy(50))
        self.color_input = pygame.Color('lightskyblue3')

        # Botón enviar
        boton_ancho = menu.sx(80)
        boton_x = self.input_rect.x + self.input_rect.width + menu.sx(10)
        self.boton_enviar = Boton(
            texto="Enviar",
            x=boton_x,
            y=self.input_rect.y,
            ancho=boton_ancho,
            alto=self.input_rect.height,
            color_normal=(70, 130, 180),
            color_hover=(100, 160, 210),
            border_radius=12,
            on_click=self.enviar_mensaje
        )

    def enviar_mensaje(self):
        if self.texto_usuario.strip():
            self.chatbot.procesar_input(self.texto_usuario)
            self.texto_usuario = ""

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.enviar_mensaje()
            elif event.key == pygame.K_BACKSPACE:
                self.texto_usuario = self.texto_usuario[:-1]
            else:
                self.texto_usuario += event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.boton_enviar.handle_event(event)

    def update(self, dt):
        pass  # No se requiere lógica de actualización por ahora

    def draw(self, pantalla):
        pantalla.fill((255, 255, 255))  # Fondo blanco

        # Título del chatbot
        mostrar_texto_adaptativo(pantalla, "🦖 DinoBot", self.menu.sx(100), self.menu.sy(40),
                                 pantalla.get_width() - self.menu.sx(200), self.menu.sy(60),
                                 pygame.font.SysFont("Segoe UI", 42, bold=True),
                                 (70, 130, 180), centrado=True)

        # Mensajes del chat
        y = self.menu.sy(120)
        ancho_texto = pantalla.get_width() - self.menu.sx(200)

        for autor, texto in self.chatbot.obtener_historial():
            color = (70, 130, 180) if autor == "bot" else (0, 0, 0)
            lineas = wrap_text(texto, self.font, ancho_texto)
            for linea in lineas:
                mostrar_texto_adaptativo(
                    pantalla, linea,
                    self.menu.sx(100), y,
                    ancho_texto, self.menu.sy(40),
                    self.font, color
                )
                y += self.menu.sy(45)

        # Input box
        pygame.draw.rect(pantalla, self.color_input, self.input_rect, 2)
        texto_surface = self.font.render(self.texto_usuario, True, (0, 0, 0))
        pantalla.blit(texto_surface, (self.input_rect.x + 10, self.input_rect.y + 10))

        # Botón enviar
        self.boton_enviar.draw(pantalla)
