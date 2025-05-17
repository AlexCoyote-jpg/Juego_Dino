import pygame
from ui.components.utils import Boton, get_gradient

class ChatInputManager:
    def __init__(self, scaler, input_rect, font, on_send_callback):
        self.texto_usuario = ""
        self.color_input = pygame.Color('lightskyblue3')
        self.cursor_visible = True
        self.font = font
        self.scaler = scaler
        self.input_rect = input_rect
        # Cargar el icono de enviar
        icon_path = "A:/progetto/IHC/Juego_Dino/assets/imagenes/enviar.png"
        try:
            icon_img = pygame.image.load(icon_path).convert_alpha()
        except Exception:
            icon_img = None
        btn_size = min(self.input_rect.height - 2, self.scaler.scale_x_value(48))
        self.boton_enviar = Boton(
            texto="",
            x=self.input_rect.right - btn_size,
            y=self.input_rect.y + (self.input_rect.height - btn_size) // 2,
            ancho=btn_size,
            alto=btn_size,
            imagen=icon_img,
            imagen_pos="center",
            color_top=(255, 120, 120),
            color_bottom=(255, 170, 200),
            color_hover=(255, 140, 160),
            border_radius=btn_size // 2,
            estilo="round",
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
        input_bg_color = (255, 255, 255)
        shadow_color = (230, 230, 230)
        border_radius = self.input_rect.height // 2
        # Sombra neumórfica
        shadow_rect = self.input_rect.move(0, 6)
        pygame.draw.rect(pantalla, shadow_color, shadow_rect, border_radius=border_radius)
        # Fondo principal input
        pygame.draw.rect(pantalla, input_bg_color, self.input_rect, border_radius=border_radius)
        # --- Botón round usando Boton ---
        # Actualiza posición y tamaño del botón por si cambia el layout
        btn_size = self.boton_enviar.ancho
        self.boton_enviar.x = self.input_rect.right - btn_size
        self.boton_enviar.y = self.input_rect.y + (self.input_rect.height - btn_size) // 2
        self.boton_enviar.ancho = btn_size
        self.boton_enviar.alto = btn_size
        # Solo habilitado si hay texto y no esperando respuesta
        self.boton_enviar.texto_visible = False
        self.boton_enviar.imagen_pos = "center"
        self.boton_enviar.color_top = (255, 120, 120) if self.texto_usuario.strip() and not esperando_respuesta else (240, 240, 245)
        self.boton_enviar.color_bottom = (255, 170, 200) if self.texto_usuario.strip() and not esperando_respuesta else (240, 240, 245)
        self.boton_enviar.color_hover = (255, 140, 160) if self.texto_usuario.strip() and not esperando_respuesta else (240, 240, 245)
        self.boton_enviar.estilo = "round"
        self.boton_enviar.draw(pantalla)
        # --- Texto del input ---
        text_area_right = self.boton_enviar.x - 16
        texto_display = self.texto_usuario or "Escribe tu mensaje..."
        color = (120, 120, 120) if self.texto_usuario else (180, 180, 185)
        superficie = self.font.render(texto_display, True, color)
        text_x = self.input_rect.x + 28
        text_y = self.input_rect.y + (self.input_rect.height - superficie.get_height()) // 2
        max_text_width = text_area_right - text_x
        if superficie.get_width() > max_text_width:
            for i in range(len(texto_display), 0, -1):
                recortado = texto_display[:i] + '...'
                superficie = self.font.render(recortado, True, color)
                if superficie.get_width() <= max_text_width:
                    break
        pantalla.blit(superficie, (text_x, text_y))
        # --- Cursor elegante ---
        if self.cursor_visible and self.texto_usuario and not esperando_respuesta:
            superficie = self.font.render(self.texto_usuario, True, color)
            cursor_x = text_x + superficie.get_width() + 2
            if cursor_x < text_area_right:
                cursor_y = text_y
                cursor_h = superficie.get_height()
                pygame.draw.line(pantalla, (255, 120, 120), (cursor_x, cursor_y),
                                 (cursor_x, cursor_y + cursor_h), 2)

    def update_layout(self, input_rect, font):
        self.input_rect = input_rect
        self.font = font
        btn_size = min(self.input_rect.height - 2, self.scaler.scale_x_value(48))
        self.boton_enviar.x = self.input_rect.right - btn_size
        self.boton_enviar.y = self.input_rect.y + (self.input_rect.height - btn_size) // 2
        self.boton_enviar.ancho = btn_size
        self.boton_enviar.alto = btn_size

    def clear_input(self):
        self.texto_usuario = ""

    def get_text(self):
        return self.texto_usuario

    def set_cursor_visible(self, visible):
        self.cursor_visible = visible
