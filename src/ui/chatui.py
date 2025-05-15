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
            if event.key == pygame.K_RETURN and self.texto_usuario.strip():
                self.enviar_mensaje()
            elif event.key == pygame.K_BACKSPACE:
                self.texto_usuario = self.texto_usuario[:-1]
            else:
                self.texto_usuario += event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.texto_usuario.strip():
                self.boton_enviar.handle_event(event)

    def update(self, dt):
        pass  # No se requiere lógica de actualización por ahora

    def draw(self, pantalla):
        pantalla.fill((255, 255, 255))  # Fondo blanco

        # Título del chatbot
        mostrar_texto_adaptativo(
            pantalla, "🦖 DinoBot", self.menu.sx(100), self.menu.sy(40),
            pantalla.get_width() - self.menu.sx(200), self.menu.sy(60),
            pygame.font.SysFont("Segoe UI", 42, bold=True),
            (70, 130, 180), centrado=True)

        # Área de chat limitada
        chat_area_x = self.menu.sx(100)
        chat_area_y = self.menu.sy(120)
        chat_area_w = pantalla.get_width() - self.menu.sx(200)
        chat_area_h = self.menu.sy(380)
        dibujar_caja_texto(
            pantalla, chat_area_x, chat_area_y, chat_area_w, chat_area_h,
            (245, 245, 255, 220), radius=18)

        # Mensajes del chat (solo los que caben en el área)
        y = chat_area_y + 10
        line_height = self.menu.sy(45)
        max_lines = max(1, (chat_area_h - 20) // line_height)
        mensajes = []
        ancho_texto = chat_area_w - 20
        historial = self.chatbot.obtener_historial()
        # Solo procesar los últimos N mensajes para eficiencia
        for autor, texto in historial[-10:]:
            color = (70, 130, 180) if autor == "bot" else (0, 0, 0)
            for linea in wrap_text(texto, self.font, ancho_texto):
                mensajes.append((linea, color))
        # Solo mostrar las últimas líneas que caben
        for linea, color in mensajes[-max_lines:]:
            mostrar_texto_adaptativo(
                pantalla, linea,
                chat_area_x + 10, y,
                ancho_texto, line_height,
                self.font, color)
            y += line_height

        # Input box
        pygame.draw.rect(pantalla, self.color_input, self.input_rect, 2)
        texto = self.texto_usuario if self.texto_usuario else "Escribe tu mensaje..."
        color = (0, 0, 0) if self.texto_usuario else (180, 180, 180)
        texto_surface = self.font.render(texto, True, color)
        pantalla.blit(texto_surface, (self.input_rect.x + 10, self.input_rect.y + 10))

        # Botón enviar (deshabilitado si input vacío)
        if self.texto_usuario.strip():
            self.boton_enviar.color_normal = (70, 130, 180)
            self.boton_enviar.color_hover = (100, 160, 210)
            self.boton_enviar.draw(pantalla)
        else:
            boton_color = (200, 200, 200)
            pygame.draw.rect(pantalla, boton_color, self.boton_enviar.rect, border_radius=12)
            texto_btn = self.font.render("Enviar", True, (220, 220, 220))
            pantalla.blit(texto_btn, (self.boton_enviar.rect.x + 10, self.boton_enviar.rect.y + 10))
