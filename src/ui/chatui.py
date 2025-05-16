import pygame
import threading
from ui.components.utils import dibujar_caja_texto, Boton
from chatbot.chat import ChatBot
from ui.components.scroll import ScrollManager, dibujar_barra_scroll
from core.scale.responsive_scaler_basic import ResponsiveScaler

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
        
        # Inicializar el escalador responsivo con las dimensiones base
        self.scaler = ResponsiveScaler(
            base_width=self.menu.pantalla.get_width(),
            base_height=self.menu.pantalla.get_height()
        )
        
        self.font = pygame.font.Font(None, 28)
        self.last_screen_size = (0, 0)  # Almacenar el último tamaño conocido
        self._update_layout()
        self.color_input = pygame.Color('lightskyblue3')
        self.boton_enviar = Boton(
            texto="Enviar",
            x=self.input_rect.right + 10,
            y=self.input_rect.y,
            ancho=80,
            alto=self.input_rect.height,
            color_normal=(70, 130, 180),
            color_hover=(100, 160, 210),
            border_radius=12,
            on_click=self.enviar_mensaje
        )
        self.esperando_respuesta = False
        self.cursor_visible = True
        self.typing_animation_index = 0

        # Scroll
        self.scroll_manager = ScrollManager()
        self._mensajes_altos = []
        self._total_chat_height = 0
        self._thumb_rect = None
        self._render_cache = []
        self._scroll_offset = 0  # Initialize scroll offset
        self.titulo_surface = self.font.render("🦖 DinoBot", True, (70, 130, 180))
        self._last_typing_index = -1

    def _update_layout(self):
        # Actualizar el último tamaño conocido y el escalador
        current_size = self.menu.pantalla.get_size()
        self.last_screen_size = current_size
        self.scaler.update(current_size[0], current_size[1])
        
        # Usar el escalador para calcular dimensiones
        screen_width = current_size[0]
        screen_height = current_size[1]
        
        # Calcular dimensiones responsivas
        self.input_rect = pygame.Rect(
            self.scaler.scale_x_value(100),
            self.scaler.scale_y_value(520),
            screen_width - self.scaler.scale_x_value(200),
            self.scaler.scale_y_value(50)
        )
        
        self.chat_x = self.scaler.scale_x_value(100)
        self.chat_y = self.scaler.scale_y_value(120)
        self.chat_w = screen_width - self.scaler.scale_x_value(200)
        self.chat_h = self.scaler.scale_y_value(380)
        
        # Recalcular el tamaño de fuente basado en la escala
        font_size = self.scaler.scale_font_size(28)
        self.font = pygame.font.Font(None, font_size)
        
        # Actualizar el título
        self.titulo_surface = self.font.render("🦖 DinoBot", True, (70, 130, 180))
        
        # Actualizar el botón de enviar si ya está creado
        if hasattr(self, 'boton_enviar'):
            self.boton_enviar = Boton(
                texto="Enviar",
                x=self.input_rect.right + self.scaler.scale_x_value(10),
                y=self.input_rect.y,
                ancho=self.scaler.scale_x_value(80),
                alto=self.input_rect.height,
                color_normal=(70, 130, 180),
                color_hover=(100, 160, 210),
                border_radius=12,
                on_click=self.enviar_mensaje
            )
        
        # Forzar actualización del cache de renderizado
        if hasattr(self, '_render_cache') and self._render_cache:
            self._actualizar_render_cache()
    
    def enviar_mensaje(self):
        mensaje = self.texto_usuario.strip()
        if mensaje and not self.esperando_respuesta:
            self.esperando_respuesta = True
            self.chatbot.historial.append(("usuario", mensaje))
            self.chatbot.historial.append(("bot", ""))
            self.texto_usuario = ""
            self._actualizar_render_cache()
            threading.Thread(target=self._procesar_en_hilo, args=(mensaje,), daemon=True).start()

    def _procesar_en_hilo(self, mensaje):
        respuesta_ia = self.chatbot.procesar_input(mensaje)
        respuesta_display = str(respuesta_ia).strip() or "[Respuesta vacía del bot]"
        for i in range(len(self.chatbot.historial) - 1, -1, -1):
            autor, texto = self.chatbot.historial[i]
            if autor == "bot" and texto == "":
                self.chatbot.historial[i] = ("bot", respuesta_display)
                break
        self.esperando_respuesta = False
        self._actualizar_render_cache()

    def _actualizar_render_cache(self):
        mensajes, alturas = [], []
        ancho_texto = self.chat_w - 40
        line_height = self.scaler.scale_y_value(45)  # Usar el escalador
        for autor, texto in self.chatbot.obtener_historial()[-100:]:
            if not isinstance(texto, str):
                continue
            color_texto = (70, 130, 180) if autor == "bot" else (0, 0, 0)
            bg_color = (230, 240, 255) if autor == "bot" else (255, 255, 255)
            alineacion = "izq" if autor == "bot" else "der"
            if autor == "bot" and texto == "" and self.esperando_respuesta:
                texto = "Escribiendo" + "." * self.typing_animation_index
            for linea in wrap_text(texto, self.font, ancho_texto):
                mensajes.append((linea, color_texto, bg_color, alineacion))
                alturas.append(line_height)
        self._render_cache = mensajes
        self._mensajes_altos = alturas
        self._total_chat_height = sum(alturas)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.enviar_mensaje()
                return
            if event.key == pygame.K_BACKSPACE:
                self.texto_usuario = self.texto_usuario[:-1]
            elif event.unicode and event.unicode.isprintable():
                self.texto_usuario += event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN and not self.esperando_respuesta:
            self.boton_enviar.handle_event(event)

        # Scroll
        bar_rect = pygame.Rect(self.chat_x + self.chat_w - 18, self.chat_y, 16, self.chat_h)
        self.scroll_manager.handle_event(event, 40, self._thumb_rect, max(0, self._total_chat_height - self.chat_h), self.chat_h, self.chat_y, bar_rect)

    def update(self, dt):
        now = pygame.time.get_ticks()
        self.cursor_visible = (now // 500) % 2 == 0
        
        # Calculate scroll offset once per frame
        self._scroll_offset = self.scroll_manager.update(
            max(0, self._total_chat_height - self.chat_h), smooth=True
        )
        
        if self.esperando_respuesta:
            typing_index = (now // 300) % 4
            if typing_index != self._last_typing_index:
                self.typing_animation_index = typing_index
                self._actualizar_render_cache()
                self._last_typing_index = typing_index

    def draw(self, pantalla):
        # Verificar si cambió el tamaño con la referencia almacenada
        current_size = pantalla.get_size()
        if current_size != self.last_screen_size:
            self._update_layout()
        
        # Resto del código de dibujo
        pantalla.blit(self.titulo_surface, (self.chat_x, self.scaler.scale_y_value(40)))
        self._render_chat(pantalla)

        pygame.draw.rect(pantalla, self.color_input, self.input_rect, 2)
        texto_display = self.texto_usuario or "Escribe tu mensaje..."
        color = (0, 0, 0) if self.texto_usuario else (180, 180, 180)
        superficie = self.font.render(texto_display, True, color)
        pantalla.blit(superficie, (self.input_rect.x + 10, self.input_rect.y + 10))

        if self.cursor_visible and self.texto_usuario and not self.esperando_respuesta:
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
            text_rect = texto_btn.get_rect(center=rect.center)
            pantalla.blit(texto_btn, text_rect)

    def _render_chat(self, pantalla):
        dibujar_caja_texto(pantalla, self.chat_x, self.chat_y, self.chat_w, self.chat_h, (245, 245, 255, 220), radius=18)
        line_height = self.menu.sy(45)
        chat_area_h = self.chat_h

        # Clipping del área de chat para que nada se salga
        chat_clip_rect = pygame.Rect(self.chat_x, self.chat_y, self.chat_w - 20, self.chat_h)
        pantalla.set_clip(chat_clip_rect)

        # Use the pre-calculated scroll offset
        y = self.chat_y + 10 - self._scroll_offset

        self._thumb_rect = None
        for linea, color, bg, ali in self._render_cache:
            if y + line_height < self.chat_y:
                y += line_height
                continue
            if y > self.chat_y + self.chat_h:
                break
            self._draw_burbuja(pantalla, linea, color, bg, ali, y)
            y += line_height

        pantalla.set_clip(None)

        # Dibujar barra de scroll
        if self._total_chat_height > chat_area_h:
            barra_x = self.chat_x + self.chat_w - 18
            barra_y = self.chat_y
            barra_w = 16
            barra_h = self.chat_h
            thumb_h = max(30, int(barra_h * (chat_area_h / self._total_chat_height)))
            max_scroll = self._total_chat_height - chat_area_h
            
            # For clarity, use a local reference to self._scroll_offset
            scroll_offset = self._scroll_offset  # para mantener claridad
            
            thumb_y = barra_y + int(scroll_offset * (barra_h - thumb_h) / max_scroll) if max_scroll > 0 else barra_y
            self._thumb_rect = pygame.Rect(barra_x, thumb_y, barra_w, thumb_h)
            dibujar_barra_scroll(
                pantalla, barra_x, barra_y, barra_w, barra_h,
                scroll_offset, self._total_chat_height, chat_area_h,
                color=(120, 180, 255), highlight=False, modern=True
            )

    def _draw_burbuja(self, pantalla, linea, color, bg, ali, y):
        text_surf = self.font.render(linea, True, color)
        text_rect = text_surf.get_rect()
        bubble_padding = 14
        bubble_rect = text_rect.inflate(bubble_padding * 2, 20)
        if ali == "der":
            bubble_rect.topright = (self.chat_x + self.chat_w - 10, y)
            text_rect.topright = (self.chat_x + self.chat_w - 10 - bubble_padding, y + 10)
        else:
            bubble_rect.topleft = (self.chat_x + 10, y)
            text_rect.topleft = (self.chat_x + 10 + bubble_padding, y + 10)
        pygame.draw.rect(pantalla, bg, bubble_rect, border_radius=12)
        pantalla.blit(text_surf, text_rect)
