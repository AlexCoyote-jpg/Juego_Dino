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
        input_bg_color = (255, 255, 255)
        shadow_color = (230, 230, 230)
        border_radius = self.input_rect.height // 2
        grad_color_left = (255, 120, 120)
        grad_color_right = (255, 170, 200)
        btn_margin = 0
        btn_width = self.scaler.scale_x_value(110)
        btn_height = self.input_rect.height - 2 * btn_margin
        btn_rect = pygame.Rect(
            self.input_rect.right - btn_width - btn_margin,
            self.input_rect.y + btn_margin,
            btn_width,
            btn_height
        )
        # Sombra neumórfica
        shadow_rect = self.input_rect.move(0, 6)
        pygame.draw.rect(pantalla, shadow_color, shadow_rect, border_radius=border_radius)
        # Fondo principal input
        pygame.draw.rect(pantalla, input_bg_color, self.input_rect, border_radius=border_radius)
        # --- Botón gradiente usando utils ---
        if self.texto_usuario.strip() and not esperando_respuesta:
            grad_surf = get_gradient(btn_rect.width, btn_rect.height, grad_color_left, grad_color_right)
            grad_mask = pygame.Surface((btn_rect.width, btn_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(grad_mask, (255, 255, 255, 255), grad_mask.get_rect(), border_radius=border_radius)
            grad_surf = grad_surf.copy()
            grad_surf.blit(grad_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            pantalla.blit(grad_surf, btn_rect.topleft)
        else:
            btn_disabled = pygame.Surface((btn_rect.width, btn_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(btn_disabled, (240, 240, 245), btn_disabled.get_rect(), border_radius=border_radius)
            pantalla.blit(btn_disabled, btn_rect.topleft)
        # --- Icono enviar ---
        icon_path = "A:/progetto/IHC/Juego_Dino/assets/imagenes/enviar.png"
        try:
            icon_img = pygame.image.load(icon_path).convert_alpha()
            icon_size = btn_height - 18
            icon_img = pygame.transform.smoothscale(icon_img, (icon_size, icon_size))
        except Exception:
            icon_img = None
        if icon_img:
            icon_rect = icon_img.get_rect(center=btn_rect.center)
            pantalla.blit(icon_img, icon_rect)
        # --- Texto del input (solo renderizado simple, no mostrar_texto_adaptativo) ---
        text_area_right = btn_rect.left - 16
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
            # Medir el ancho del texto renderizado para el cursor
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
