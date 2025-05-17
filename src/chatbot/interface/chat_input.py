import pygame
from ui.components.utils import Boton

class ChatInputManager:
    def __init__(self, scaler, input_rect, font, on_send_callback):
        self.texto_usuario = ""
        self.color_input = pygame.Color('lightskyblue3')
        self.cursor_visible = True
        self.font = font
        self.scaler = scaler
        self.input_rect = input_rect
        self.boton_enviar = Boton(
            texto="Enviar",
            x=self.input_rect.right + self.scaler.scale_x_value(10),
            y=self.input_rect.y,
            ancho=self.scaler.scale_x_value(80),
            alto=self.input_rect.height,
            color_normal=(70, 130, 180),
            color_hover=(100, 160, 210),
            border_radius=12,
            on_click=on_send_callback
        )
        self.esperando_respuesta = False

    def handle_event(self, event, esperando_respuesta):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return 'send'
            if event.key == pygame.K_BACKSPACE:
                self.texto_usuario = self.texto_usuario[:-1]
            elif event.unicode and event.unicode.isprintable():
                self.texto_usuario += event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN and not esperando_respuesta:
            self.boton_enviar.handle_event(event)
        return None

    def draw(self, pantalla, esperando_respuesta):
        pygame.draw.rect(pantalla, self.color_input, self.input_rect, 2)
        texto_display = self.texto_usuario or "Escribe tu mensaje..."
        color = (0, 0, 0) if self.texto_usuario else (180, 180, 180)
        superficie = self.font.render(texto_display, True, color)
        pantalla.blit(superficie, (self.input_rect.x + 10, self.input_rect.y + 10))

        if self.cursor_visible and self.texto_usuario and not esperando_respuesta:
            cursor_x = self.input_rect.x + 10 + superficie.get_width() + 2
            cursor_y = self.input_rect.y + 10
            cursor_h = superficie.get_height()
            pygame.draw.line(pantalla, (0, 0, 0), (cursor_x, cursor_y),
                             (cursor_x, cursor_y + cursor_h), 2)

        if self.texto_usuario.strip() and not esperando_respuesta:
            self.boton_enviar.draw(pantalla)
        else:
            rect = self.boton_enviar.rect
            pygame.draw.rect(pantalla, (200, 200, 200), rect, border_radius=12)
            texto_btn = self.font.render("Enviar", True, (220, 220, 220))
            text_rect = texto_btn.get_rect(center=rect.center)
            pantalla.blit(texto_btn, text_rect)

    def update_layout(self, input_rect, font):
        self.input_rect = input_rect
        self.font = font
        self.boton_enviar.x = self.input_rect.right + self.scaler.scale_x_value(10)
        self.boton_enviar.y = self.input_rect.y
        self.boton_enviar.ancho = self.scaler.scale_x_value(80)
        self.boton_enviar.alto = self.input_rect.height

    def clear_input(self):
        self.texto_usuario = ""

    def get_text(self):
        return self.texto_usuario

    def set_cursor_visible(self, visible):
        self.cursor_visible = visible
