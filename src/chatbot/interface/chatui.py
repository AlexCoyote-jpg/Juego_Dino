import pygame
import threading
from ui.components.utils import dibujar_caja_texto
from chatbot.chat import ChatBot
from ui.components.scroll import ScrollManager, dibujar_barra_scroll
from core.scale.responsive_scaler_basic import ResponsiveScaler
from chatbot.interface.chat_utils import wrap_text
from chatbot.interface.chat_render import draw_burbuja, render_chat
from chatbot.interface.chat_scroll import calcular_offset_ultimo_usuario
from chatbot.interface.chat_input import ChatInputManager

BUBBLE_PADDING = 14
MIN_THUMB_HEIGHT = 30
LINE_SPACING = 0  # El espaciado vertical lo controlamos con el alto de línea real

class BotScreen:
    def __init__(self, menu):
        self.menu = menu
        self.chatbot = ChatBot()
        
        # Inicializar el lock para acceso seguro al historial
        self._hist_lock = threading.Lock()
        
        # Inicializar el escalador responsivo con las dimensiones base
        self.scaler = ResponsiveScaler(
            base_width=self.menu.pantalla.get_width(),
            base_height=self.menu.pantalla.get_height()
        )
        
        self.last_screen_size = (0, 0)  # Almacenar el último tamaño conocido

        # Inicializar input_rect y font ANTES de crear input_manager
        screen_width = self.menu.pantalla.get_width()
        screen_height = self.menu.pantalla.get_height()
        self.input_rect = pygame.Rect(
            self.scaler.scale_x_value(100),
            self.scaler.scale_y_value(520),
            screen_width - self.scaler.scale_x_value(200),
            self.scaler.scale_y_value(50)
        )
        self.font = pygame.font.Font(None, 28)
        self.titulo_surface = self.font.render("🦖 DinoBot", True, (70, 130, 180))
        self._last_typing_index = -1

        # Scroll
        self.scroll_manager = ScrollManager()
        self._mensajes_altos = []
        self._total_chat_height = 0
        self._thumb_rect = None
        self._render_cache = []
        self._scroll_offset = 0  # Initialize scroll offset
        self.typing_animation_index = 0
        self.esperando_respuesta = False

        # Configuración de scroll
        self.auto_scroll_enabled = True  # Activar auto-scroll por defecto
        self.smooth_scroll = True  # Usar scroll suave por defecto

        # Inicializar ChatInputManager
        self.input_manager = ChatInputManager(
            self.scaler, self.input_rect, self.font, self.enviar_mensaje
        )

        self._layout_dirty = True  # Marca si el layout necesita actualizarse
        self._render_cache_dirty = True  # Marca si la caché de renderizado necesita actualizarse
        self._update_layout(force=True)

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

            self.input_manager.update_layout(self.input_rect, self.font)
            self._layout_dirty = True  # Marca que el layout cambió
            self._render_cache_dirty = True  # Marca que la caché de renderizado cambió

    def enviar_mensaje(self):
        mensaje = self.input_manager.get_text().strip()
        if mensaje and not self.esperando_respuesta:
            self.esperando_respuesta = True
            self.input_manager.clear_input()
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
        historial = self.chatbot.obtener_historial()
        return calcular_offset_ultimo_usuario(
            historial,
            self.font,
            self.chat_w,
            self._total_chat_height,
            self.chat_h
        )

    def _actualizar_render_cache(self):
        """
        Reconstruye la caché de renderizado del chat basándose en el historial, optimizado para mayor ligereza y eficiencia.
        """
        with self._hist_lock:
            historial = self.chatbot.obtener_historial()[-100:]
        if not historial:
            self._render_cache = []
            self._mensajes_altos = []
            self._total_chat_height = 0
            self._layout_dirty = False
            self._render_cache_dirty = False
            return

        mensajes = []
        alturas = []
        ancho_texto = self.chat_w - 40
        font = self.font
        line_height = font.get_linesize() + max(8, int(font.get_linesize() * 0.25)) * 2
        esperando = self.esperando_respuesta
        typing_index = self.typing_animation_index

        for autor, texto in historial:
            if not isinstance(texto, str):
                continue
            if autor == "bot":
                color_texto = (70, 130, 180)
                bg_color = (230, 240, 255)
                alineacion = "izq"
                if texto == "" and esperando:
                    texto = f"Escribiendo{'.' * typing_index}"
            else:
                color_texto = (0, 0, 0)
                bg_color = (255, 255, 255)
                alineacion = "der"
            for linea in wrap_text(texto, font, ancho_texto):
                mensajes.append((linea, color_texto, bg_color, alineacion))
                alturas.append(line_height)
        self._render_cache = mensajes
        self._mensajes_altos = alturas
        self._total_chat_height = sum(alturas)
        self._layout_dirty = False
        self._render_cache_dirty = False

    def handle_event(self, event):
        result = self.input_manager.handle_event(event, self.esperando_respuesta)
        if result == 'send':
            self.enviar_mensaje()
            return
        # Scroll
        bar_rect = pygame.Rect(self.chat_x + self.chat_w - 18, self.chat_y, 16, self.chat_h)
        self.scroll_manager.handle_event(event, 40, self._thumb_rect,
                                           max(0, self._total_chat_height - self.chat_h),
                                           self.chat_h, self.chat_y, bar_rect)

    def update(self, dt):
        now = pygame.time.get_ticks()
        # Solo actualiza el cursor cada 500ms
        if now % 1000 < 500:
            if not self.input_manager.cursor_visible:
                self.input_manager.set_cursor_visible(True)
        else:
            if self.input_manager.cursor_visible:
                self.input_manager.set_cursor_visible(False)
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
        self._update_layout()
        if self._layout_dirty or self._render_cache_dirty:
            self._actualizar_render_cache()
        pantalla.blit(self.titulo_surface, (self.chat_x, self.scaler.scale_y_value(40)))
        # Usar render_chat modularizado
        def draw_burbuja_cb(pantalla, linea, color, bg, ali, y):
            self._draw_burbuja(pantalla, linea, color, bg, ali, y)
        render_chat.draw_burbuja_cb = draw_burbuja_cb
        thumb_rect_ref = [self._thumb_rect]
        render_chat(
            pantalla,
            self.chat_x,
            self.chat_y,
            self.chat_w,
            self.chat_h,
            self.font,
            self._scroll_offset,
            self._render_cache,
            self._total_chat_height,
            thumb_rect_ref
        )
        self._thumb_rect = thumb_rect_ref[0]
        self.input_manager.draw(pantalla, self.esperando_respuesta)

    def _draw_burbuja(self, pantalla, linea, color, bg, ali, y):
        """
        Dibuja la burbuja de mensaje.
        """
        draw_burbuja(pantalla, self.font, self.chat_x, self.chat_w, linea, color, bg, ali, y)
