import pygame
from ui.components.utils import dibujar_caja_texto, mostrar_texto_adaptativo, Boton
from chatbot.chat import ChatBot

def wrap_text(texto, fuente, max_width):
    palabras, lineas, linea_actual = texto.split(), [], ""
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

        self.input_rect = pygame.Rect(menu.sx(100), menu.sy(520),
                                      menu.pantalla.get_width() - menu.sx(200),
                                      menu.sy(50))
        self.color_input = pygame.Color('lightskyblue3')

        boton_x = self.input_rect.right + menu.sx(10)
        self.boton_enviar = Boton(
            texto="Enviar",
            x=boton_x,
            y=self.input_rect.y,
            ancho=menu.sx(80),
            alto=self.input_rect.height,
            color_normal=(70, 130, 180),
            color_hover=(100, 160, 210),
            border_radius=12,
            on_click=self.enviar_mensaje
        )

    def enviar_mensaje(self):
        mensaje = self.texto_usuario.strip()
        if mensaje:
            self.chatbot.historial.append(("usuario", mensaje))
            respuesta = self.chatbot.procesar_input(mensaje)
            if respuesta and isinstance(respuesta, str):
                self.chatbot.historial.append(("bot", respuesta))
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

    def update(self, dt): pass  # Sin lógica dinámica por ahora

    def draw(self, pantalla):
        pantalla.fill((255, 255, 255))

        # Título superior
        mostrar_texto_adaptativo(
            pantalla, "🦖 DinoBot", self.menu.sx(100), self.menu.sy(40),
            pantalla.get_width() - self.menu.sx(200), self.menu.sy(60),
            pygame.font.SysFont("Segoe UI", 42, bold=True),
            (70, 130, 180), centrado=True)

        # Área de chat
        self._render_chat(pantalla)

        # Input box
        pygame.draw.rect(pantalla, self.color_input, self.input_rect, 2)
        texto = self.texto_usuario or "Escribe tu mensaje..."
        color = (0, 0, 0) if self.texto_usuario else (180, 180, 180)
        superficie = self.font.render(texto, True, color)
        pantalla.blit(superficie, (self.input_rect.x + 10, self.input_rect.y + 10))

        # Botón enviar
        if self.texto_usuario.strip():
            self.boton_enviar.draw(pantalla)
        else:
            rect = self.boton_enviar.rect
            pygame.draw.rect(pantalla, (200, 200, 200), rect, border_radius=12)
            texto_btn = self.font.render("Enviar", True, (220, 220, 220))
            pantalla.blit(texto_btn, (rect.x + 10, rect.y + 10))

    def _render_chat(self, pantalla):
        chat_x = self.menu.sx(100)
        chat_y = self.menu.sy(120)
        chat_w = pantalla.get_width() - self.menu.sx(200)
        chat_h = self.menu.sy(380)
        dibujar_caja_texto(pantalla, chat_x, chat_y, chat_w, chat_h,
                           (245, 245, 255, 220), radius=18)

        line_height = self.menu.sy(45)
        max_lines = (chat_h - 20) // line_height
        ancho_texto = chat_w - 20
        y = chat_y + 10
        mensajes = []

        for autor, texto in self.chatbot.obtener_historial()[-20:]:
            color = (70, 130, 180) if autor == "bot" else (0, 0, 0)
            for linea in wrap_text(texto, self.font, ancho_texto):
                mensajes.append((linea, color))

        for linea, color in mensajes[-max_lines:]:
            mostrar_texto_adaptativo(
                pantalla, linea, chat_x + 10, y,
                ancho_texto, line_height, self.font, color)
            y += line_height
