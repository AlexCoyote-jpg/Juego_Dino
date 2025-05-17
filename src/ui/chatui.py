import pygame
import threading
from ui.components.utils import dibujar_caja_texto, Boton
from chatbot.chat import ChatBot
from ui.components.scroll import ScrollManager, dibujar_barra_scroll
from core.scale.responsive_scaler_basic import ResponsiveScaler

BUBBLE_PADDING = 14
MIN_THUMB_HEIGHT = 30
LINE_SPACING = 0  # El espaciado vertical lo controlamos con el alto de línea real

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
        
        # Inicializar el lock para acceso seguro al historial
        self._hist_lock = threading.Lock()
        
        # Inicializar el escalador responsivo con las dimensiones base
        self.scaler = ResponsiveScaler(
            base_width=self.menu.pantalla.get_width(),
            base_height=self.menu.pantalla.get_height()
        )
        
        self.font = pygame.font.Font(None, 28)
        self.last_screen_size = (0, 0)  # Almacenar el último tamaño conocido
        self._layout_dirty = True  # Marca si el layout necesita actualizarse
        self._render_cache_dirty = True  # Marca si la caché de renderizado necesita actualizarse
        self._update_layout(force=True)
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

        # Configuración de scroll
        self.auto_scroll_enabled = True  # Activar auto-scroll por defecto
        self.smooth_scroll = True  # Usar scroll suave por defecto

    def _update_layout(self, force=False):
        """
        Actualiza el layout según el tamaño actual de pantalla.
        Solo recalcula si el tamaño cambió.
        """
        current_size = self.menu.pantalla.get_size()
        if force or current_size != self.last_screen_size:
            self.last_screen_size = current_size
            self.scaler.update(current_size[0], current_size[1])

            screen_width, screen_height = current_size
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

            font_size = self.scaler.scale_font_size(28)
            self.font = pygame.font.Font(None, font_size)

            self.titulo_surface = self.font.render("🦖 DinoBot", True, (70, 130, 180))

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
            self._layout_dirty = True  # Marca que el layout cambió
            self._render_cache_dirty = True  # Marca que la caché de renderizado cambió

    def enviar_mensaje(self):
        mensaje = self.texto_usuario.strip()
        if mensaje and not self.esperando_respuesta:
            self.esperando_respuesta = True
            self.texto_usuario = ""
            self._render_cache_dirty = True
            threading.Thread(target=self._procesar_en_hilo, args=(mensaje,), daemon=True).start()

    def _procesar_en_hilo(self, mensaje):
        """
        Procesa la respuesta del bot en un hilo separado.
        Actualiza el historial y fuerza el auto-scroll para que se muestre desde el
        inicio del último mensaje enviado por el usuario.
        """
        self.chatbot.procesar_input(mensaje)
        self.esperando_respuesta = False
        self._render_cache_dirty = True
        
        # Calcular el offset donde inicia el último mensaje del usuario
        target_offset = self._calcular_offset_ultimo_usuario()
        current_offset = self._scroll_offset
        umbral = 5
        if abs(target_offset - current_offset) > umbral:
            if getattr(self, "auto_scroll_enabled", True):
                # Usar la propiedad smooth_scroll para decidir el tipo de scroll
                instant = not getattr(self, "smooth_scroll", True)
                self.scroll_manager.scroll_to_bottom(target_offset, instant=instant)
            else:
                self.mostrar_indicador_nuevo_mensaje()

    def _calcular_offset_ultimo_usuario(self):
        """
        Calcula el offset en el que inicia el último mensaje enviado por el usuario.
        """
        offset = 0
        ancho_texto = self.chat_w - 40
        line_height = self.font.get_linesize() + max(8, int(self.font.get_linesize() * 0.25)) * 2
        ultimo_usuario_offset = 0
        historial = self.chatbot.obtener_historial()
        for autor, texto in historial:
            lineas = wrap_text(texto, self.font, ancho_texto)
            if autor == "usuario":
                ultimo_usuario_offset = offset
            offset += line_height * len(lineas)
        max_scroll = max(0, self._total_chat_height - self.chat_h)
        return min(ultimo_usuario_offset, max_scroll)

    def _actualizar_render_cache(self):
        """
        Reconstruye la caché de renderizado del chat basándose en el historial.
        """
        mensajes, alturas = [], []
        ancho_texto = self.chat_w - 40
        line_height = self.font.get_linesize() + max(8, int(self.font.get_linesize() * 0.25)) * 2
        with self._hist_lock:
            historial = self.chatbot.obtener_historial()[-100:]
        for autor, texto in historial:
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
        self._layout_dirty = False  # Layout actualizado
        self._render_cache_dirty = False  # Caché de renderizado actualizada

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
        self.scroll_manager.handle_event(event, 40, self._thumb_rect,
                                           max(0, self._total_chat_height - self.chat_h),
                                           self.chat_h, self.chat_y, bar_rect)

    def update(self, dt):
        now = pygame.time.get_ticks()
        # Solo actualiza el cursor cada 500ms
        if now % 1000 < 500:
            if not self.cursor_visible:
                self.cursor_visible = True
        else:
            if self.cursor_visible:
                self.cursor_visible = False

        self._scroll_offset = self.scroll_manager.update(
            max(0, self._total_chat_height - self.chat_h), smooth=True
        )

        if self.esperando_respuesta:
            typing_index = (now // 300) % 4
            if typing_index != self._last_typing_index:
                self.typing_animation_index = typing_index
                self._render_cache_dirty = True
                self._last_typing_index = typing_index

    def draw(self, pantalla):
        # Solo actualiza el layout y el caché si el tamaño cambió
        self._update_layout()
        if self._layout_dirty or self._render_cache_dirty:
            self._actualizar_render_cache()

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
            pygame.draw.line(pantalla, (0, 0, 0), (cursor_x, cursor_y),
                             (cursor_x, cursor_y + cursor_h), 2)

        if self.texto_usuario.strip() and not self.esperando_respuesta:
            self.boton_enviar.draw(pantalla)
        else:
            rect = self.boton_enviar.rect
            pygame.draw.rect(pantalla, (200, 200, 200), rect, border_radius=12)
            texto_btn = self.font.render("Enviar", True, (220, 220, 220))
            text_rect = texto_btn.get_rect(center=rect.center)
            pantalla.blit(texto_btn, text_rect)

    def _render_chat(self, pantalla):
        dibujar_caja_texto(pantalla, self.chat_x, self.chat_y, self.chat_w, self.chat_h,
                             (245, 245, 255, 220), radius=18)
        line_height = self.font.get_linesize() + max(8, int(self.font.get_linesize() * 0.25)) * 2
        chat_area_h = self.chat_h

        # Clipping del área de chat
        chat_clip_rect = pygame.Rect(self.chat_x, self.chat_y, self.chat_w - 20, self.chat_h)
        pantalla.set_clip(chat_clip_rect)

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

        if self._total_chat_height > chat_area_h:
            barra_x = self.chat_x + self.chat_w - 18
            barra_y = self.chat_y
            barra_w = 16
            barra_h = self.chat_h
            thumb_h = max(MIN_THUMB_HEIGHT, int(barra_h * (chat_area_h / self._total_chat_height)))
            max_scroll = self._total_chat_height - chat_area_h
            
            scroll_offset = self._scroll_offset
            thumb_y = barra_y + int(scroll_offset * (barra_h - thumb_h) / max_scroll) if max_scroll > 0 else barra_y
            self._thumb_rect = pygame.Rect(barra_x, thumb_y, barra_w, thumb_h)
            dibujar_barra_scroll(
                pantalla, barra_x, barra_y, barra_w, barra_h,
                scroll_offset, self._total_chat_height, chat_area_h,
                color=(120, 180, 255), highlight=False, modern=True
            )

    def _draw_burbuja(self, pantalla, linea, color, bg, ali, y):
        """
        Dibuja la burbuja de mensaje.
        
        Args:
            pantalla: Surface de Pygame donde se dibuja.
            linea (str): Texto a renderizar.
            color (tuple): Color del texto.
            bg (tuple): Color de fondo de la burbuja.
            ali (str): Alineación ("der" o "izq").
            y (int): Posición vertical.
        """
        text_surf = self.font.render(linea, True, color)
        text_rect = text_surf.get_rect()
        line_height = self.font.get_linesize()
        # Calcula el padding vertical para centrar el texto en la burbuja
        vertical_padding = max(8, int(line_height * 0.25))
        bubble_rect = text_rect.inflate(BUBBLE_PADDING * 2, vertical_padding * 2)
        if ali == "der":
            bubble_rect.topright = (self.chat_x + self.chat_w - 10, y)
            text_rect.topright = (self.chat_x + self.chat_w - 10 - BUBBLE_PADDING, y + vertical_padding)
        else:
            bubble_rect.topleft = (self.chat_x + 10, y)
            text_rect.topleft = (self.chat_x + 10 + BUBBLE_PADDING, y + vertical_padding)
        pygame.draw.rect(pantalla, bg, bubble_rect, border_radius=12)
        pantalla.blit(text_surf, text_rect)
