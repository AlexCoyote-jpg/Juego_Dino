import pygame
import threading
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

        self.esperando_respuesta = False
        self.lock = threading.Lock()
        self.cursor_visible = True
        self.cursor_timer = 0

    def enviar_mensaje(self):
        mensaje = self.texto_usuario.strip()
        if mensaje and not self.esperando_respuesta:
            self.esperando_respuesta = True
            self.texto_usuario = ""
            with self.lock:
                self.chatbot.historial.append(("usuario", mensaje))
                self.chatbot.historial.append(("bot", "..."))
            threading.Thread(target=self._procesar_en_hilo, args=(mensaje,), daemon=True).start()

    def _procesar_en_hilo(self, mensaje):
        respuesta = self.chatbot.procesar_input(mensaje)
        with self.lock:
            for i in range(len(self.chatbot.historial)-1, -1, -1):
                if self.chatbot.historial[i] == ("bot", "..."):
                    self.chatbot.historial[i] = ("bot", respuesta)
                    break
        self.esperando_respuesta = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if not self.esperando_respuesta:
                    self.enviar_mensaje()
            elif event.key == pygame.K_BACKSPACE:
                self.texto_usuario = self.texto_usuario[:-1]
            else:
                if event.unicode and event.unicode.isprintable():
                    self.texto_usuario += event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not self.esperando_respuesta:
                self.boton_enviar.handle_event(event)

    def update(self, dt):
        self.cursor_timer += dt if dt else 0
        if self.cursor_timer > 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def draw(self, pantalla):
        mostrar_texto_adaptativo(
            pantalla, "🦖 DinoBot", self.menu.sx(100), self.menu.sy(40),
            pantalla.get_width() - self.menu.sx(200), self.menu.sy(60),
            self.font,
            (70, 130, 180), centrado=True)
        self._render_chat(pantalla)
        pygame.draw.rect(pantalla, self.color_input, self.input_rect, 2)
        texto = self.texto_usuario or "Escribe tu mensaje..."
        color = (0, 0, 0) if self.texto_usuario else (180, 180, 180)
        superficie = self.font.render(texto, True, color)
        pantalla.blit(superficie, (self.input_rect.x + 10, self.input_rect.y + 10))
        if self.cursor_visible and self.texto_usuario != "" and not self.esperando_respuesta:
            cursor_x = self.input_rect.x + 10 + superficie.get_width() + 2
            cursor_y = self.input_rect.y + 10
            cursor_h = superficie.get_height()
            pygame.draw.line(pantalla, (0, 0, 0), (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_h), 2)
        if self.texto_usuario.strip() and not self.esperando_respuesta:
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
        for autor, texto in self.chatbot.obtener_historial()[-40:]:
            if not isinstance(texto, str):
                continue
            color = (70, 130, 180) if autor == "bot" else (0, 0, 0)
            for linea in wrap_text(texto, self.font, ancho_texto):
                mensajes.append((linea, color))
        for linea, color in mensajes[-max_lines:]:
            superficie = self.font.render(linea, True, color)
            pantalla.blit(superficie, (chat_x + 10, y))
            y += line_height
