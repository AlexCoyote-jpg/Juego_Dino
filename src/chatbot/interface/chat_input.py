import pygame
import tkinter as tk
import math

from ui.components.utils import Boton

class ChatInputManager:
    def __init__(self, scaler, input_rect, font, on_send_callback):
        self.texto_usuario = ""
        self.font = font
        self.scaler = scaler
        self.input_rect = input_rect

        self.cursor_visible = True
        self.last_cursor_toggle = 0
        self.cursor_interval = 500  # ms

        self.last_backspace_time = 0
        self.backspace_delay = 50  # ms

        self.esperando_respuesta = False

        # Icono de enviar
        icon_path = "A:/progetto/IHC/Juego_Dino/assets/imagenes/enviar.png"
        try:
            icon_img = pygame.image.load(icon_path).convert_alpha()
        except Exception:
            icon_img = None

        btn_size = min(self.input_rect.height - 2, self.scaler.scale_x_value(48))
        self.btn_size = btn_size
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

    def handle_event(self, event, esperando_respuesta):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return 'send'
            elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:
                try:
                    r = tk.Tk()
                    r.withdraw()
                    self.texto_usuario += r.clipboard_get()
                    r.destroy()
                except Exception:
                    pass
            elif event.key == pygame.K_BACKSPACE:
                self.texto_usuario = self.texto_usuario[:-1]
                self.last_backspace_time = pygame.time.get_ticks()
            elif event.unicode and event.unicode.isprintable():
                self.texto_usuario += event.unicode

        elif event.type == pygame.MOUSEBUTTONDOWN and not esperando_respuesta:
            self.boton_enviar.handle_event(event)

        return None

    def update(self):
        # Repetición de backspace
        keys = pygame.key.get_pressed()
        if keys[pygame.K_BACKSPACE]:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_backspace_time >= self.backspace_delay:
                self.texto_usuario = self.texto_usuario[:-1]
                self.last_backspace_time = current_time

        # Parpadeo del cursor
        now = pygame.time.get_ticks()
        if now - self.last_cursor_toggle > self.cursor_interval:
            self.cursor_visible = not self.cursor_visible
            self.last_cursor_toggle = now

    def draw(self, pantalla, esperando_respuesta):
        input_bg_color = (255, 255, 255)
        shadow_color = (230, 230, 230)
        border_radius = self.input_rect.height // 2

        shadow_rect = self.input_rect.move(0, 6)
        pygame.draw.rect(pantalla, shadow_color, shadow_rect, border_radius=border_radius)
        pygame.draw.rect(pantalla, input_bg_color, self.input_rect, border_radius=border_radius)

        # Actualizar botón
        self.boton_enviar.x = self.input_rect.right - self.btn_size
        self.boton_enviar.y = self.input_rect.y + (self.input_rect.height - self.btn_size) // 2
        self.boton_enviar.ancho = self.btn_size
        self.boton_enviar.alto = self.btn_size
        self.boton_enviar.texto_visible = False
        activo = self.texto_usuario.strip() and not esperando_respuesta
        color = (255, 120, 120) if activo else (240, 240, 245)
        self.boton_enviar.color_top = self.boton_enviar.color_bottom = self.boton_enviar.color_hover = color
        self.boton_enviar.draw(pantalla)

        # Dibujar texto
        text_area_right = self.boton_enviar.x - 16
        texto_display = self.texto_usuario or "Escribe tu mensaje..."
        color_texto = (120, 120, 120) if self.texto_usuario else (180, 180, 185)
        superficie = self.font.render(texto_display, True, color_texto)
        text_x = self.input_rect.x + 28
        text_y = self.input_rect.y + (self.input_rect.height - superficie.get_height()) // 2
        max_text_width = text_area_right - text_x

        if superficie.get_width() > max_text_width:
            for i in range(len(texto_display), 0, -1):
                recortado = texto_display[:i] + '...'
                superficie = self.font.render(recortado, True, color_texto)
                if superficie.get_width() <= max_text_width:
                    break
        pantalla.blit(superficie, (text_x, text_y))

        # Cursor
        if self.cursor_visible and self.texto_usuario and not esperando_respuesta:
            superficie = self.font.render(self.texto_usuario, True, color_texto)
            cursor_x = text_x + superficie.get_width() + 2
            if cursor_x < text_area_right:
                cursor_y = text_y
                cursor_h = superficie.get_height()
                pygame.draw.line(pantalla, (255, 120, 120), (cursor_x, cursor_y),
                                 (cursor_x, cursor_y + cursor_h), 2)

    def draw_loading_bar(self, pantalla):
        # Barra de carga que rodea todo el input area (borde exterior animado, siguiendo el borde redondeado)
        border_radius = self.input_rect.height // 2
        bar_thickness = 4
        time_ms = pygame.time.get_ticks()
        w, h = self.input_rect.width, self.input_rect.height
        # Perímetro real: lados rectos + arcos de esquinas
        arc_len = 0.5 * 3.1416 * border_radius * 4  # 4 esquinas
        line_len = 2 * (w - 2 * border_radius) + 2 * (h - 2 * border_radius)
        perimeter = arc_len + line_len
        # Animación: segmento móvil
        progress = (time_ms // 3) % int(perimeter)
        chunk_len = int(perimeter * 0.18)
        # Dibuja fondo del borde
        pygame.draw.rect(pantalla, (230, 230, 230), self.input_rect.inflate(bar_thickness*2, bar_thickness*2),
                         width=bar_thickness, border_radius=border_radius+2)
        # Prepara puntos a lo largo del borde redondeado
        n_segments = int(perimeter // 2)
        points = []
        rect = self.input_rect.inflate(bar_thickness*2, bar_thickness*2)
        r = border_radius + 2
        # Top line
        for i in range(int(w - 2*r)):
            x = rect.left + r + i
            y = rect.top
            points.append((x, y))
        # Top-right arc
        for i in range(0, 91, 2):
            angle = (i / 180) * math.pi
            x = rect.right - r + r * math.cos(angle)
            y = rect.top + r - r * math.sin(angle)
            points.append((x, y))
        # Right line
        for i in range(int(h - 2*r)):
            x = rect.right
            y = rect.top + r + i
            points.append((x, y))
        # Bottom-right arc
        for i in range(0, 91, 2):
            angle = (i / 180) * math.pi
            x = rect.right - r + r * math.cos(angle)
            y = rect.bottom - r + r * math.sin(angle)
            points.append((x, y))
        # Bottom line
        for i in range(int(w - 2*r)):
            x = rect.right - r - i
            y = rect.bottom
            points.append((x, y))
        # Bottom-left arc
        for i in range(0, 91, 2):
            angle = (i / 180) * math.pi
            x = rect.left + r - r * math.cos(angle)
            y = rect.bottom - r + r * math.sin(angle)
            points.append((x, y))
        # Left line
        for i in range(int(h - 2*r)):
            x = rect.left
            y = rect.bottom - r - i
            points.append((x, y))
        # Top-left arc
        for i in range(0, 91, 2):
            angle = (i / 180) * math.pi
            x = rect.left + r - r * math.cos(angle)
            y = rect.top + r - r * math.sin(angle)
            points.append((x, y))
        # Dibuja segmento animado
        for i in range(len(points)):
            seg_pos = (progress + i) % len(points)
            if seg_pos < chunk_len:
                x, y = points[i]
                pygame.draw.circle(pantalla, (255, 120, 120), (int(x), int(y)), bar_thickness//2+1)

    def update_layout(self, input_rect, font):
        self.input_rect = input_rect
        self.font = font
        self.btn_size = min(self.input_rect.height - 2, self.scaler.scale_x_value(48))

    def clear_input(self):
        self.texto_usuario = ""

    def get_text(self):
        return self.texto_usuario

    def set_cursor_visible(self, visible):
        self.cursor_visible = visible
