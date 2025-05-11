import pygame
import random
from ui.components.utils import (
    mostrar_texto_adaptativo, Boton, obtener_fuente, render_text_cached,
    dibujar_caja_texto, TooltipManager
)
from ui.components.emoji import mostrar_alternativo_adaptativo
from core.decoration.effects import EffectsMixin  # Asegúrate de que la ruta sea correcta
from core.decoration.background_game import FondoAnimado  # <--- agregado
from core.decoration.paleta import PALETA_LISTA as PALETA
from core.scale.responsive_scaler_basic import ResponsiveScaler

class JuegoBase(EffectsMixin):
    def __init__(self, nombre, pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu):
        """
        Clase base para juegos. Proporciona utilidades y estructura común.
        """
        self.nombre = nombre
        self.pantalla = pantalla
        self.config = config
        self.dificultad = dificultad
        self.fondo = fondo
        self.navbar = navbar
        self.images = images
        self.sounds = sounds
        self.return_to_menu = return_to_menu

        # --- Dimensiones y fuentes ---
        self.ANCHO = pantalla.get_width()
        self.ALTO = pantalla.get_height()
        
        # --- Sistema de escalado responsivo ---
        self.scaler = ResponsiveScaler(1280, 720)  # Dimensiones base de diseño
        self.scaler.update(self.ANCHO, self.ALTO)
        
        # Funciones de escalado para facilitar el uso
        self.sx = self.scaler.scale_x_value
        self.sy = self.scaler.scale_y_value
        self.sf = self.scaler.scale_font_size
        
        # Fuentes escaladas
        self.fuente_titulo = obtener_fuente(self.sf(36), negrita=True)
        self.fuente = obtener_fuente(self.sf(20))
        
        self.reloj = pygame.time.Clock()
        self.navbar_height = 0
        self._update_navbar_height()

        # --- Tooltip manager (opcional para juegos con tooltips) ---
        self.tooltip_manager = TooltipManager(delay=1.0)

        # --- Actualiza el título de la ventana ---
        pygame.display.set_caption(f"{self.nombre} - {self.dificultad}")

        # --- Inicializa lista de botones de opciones ---
        self.opcion_botones = []

        # --- Elementos UI responsivos ---
        self.ui_elements = {}
        self.init_responsive_ui()

        # --- Racha ---
        self.racha_correctas = 0
        self.mejor_racha = 0

        # --- Operación actual (para mostrar junto al problema) ---
        self.operacion_actual = ""

        # --- Efectos visuales ---
        self.mensaje = ""
        self.tiempo_mensaje = 0
        self.mensaje_color = (255, 255, 255, 220)
        self.mensaje_animacion = 1.0
        self.sonido_activado = True  # Puedes controlar esto según tu lógica

        # Inicializar listas de efectos si no existen
        self.estrellas = []
        self.particulas = []
        self.estrella_img = None
        self.animacion_activa = False
        self.tiempo_animacion = 0

        # --- Inicializar FondoAnimado ---
        self.fondo_animado = FondoAnimado(self.pantalla, self.navbar_height)
        self.fondo_animado.set_escaladores(self.sx, self.sy)
        self.fondo_animado.resize(self.ANCHO, self.ALTO)

    def mostrar_racha(self, rect=None):
        """Muestra la racha actual y la mejor racha en pantalla."""
        if rect is None:
            rect = (self.ANCHO - self.sx(200), self.ALTO - self.sy(70), self.sx(180), self.sy(50))
        dibujar_caja_texto(
            self.pantalla,
            rect[0], rect[1], rect[2], rect[3],
            color=(255, 240, 200, 220),
            radius=self.sy(10),
            texto=f"🔥 Racha: {self.racha_correctas} (Mejor: {self.mejor_racha})",
            fuente=obtener_fuente(self.sf(18)),
            color_texto=(100, 50, 0)
        )

    def mostrar_operacion(self, rect=None):
        """Muestra la operación matemática actual."""
        if not self.operacion_actual:
            return
        if rect is None:
            rect = (self.ANCHO - self.sx(200), self.navbar_height + self.sy(50), self.sx(180), self.sy(40))
        dibujar_caja_texto(
            self.pantalla,
            rect[0], rect[1], rect[2], rect[3],
            color=(240, 240, 255, 220),
            radius=self.sy(10),
            texto=self.operacion_actual,
            fuente=obtener_fuente(self.sf(20), negrita=True),
            color_texto=(50, 50, 120)
        )

    def init_responsive_ui(self):
        """
        Inicializa elementos de UI responsivos.
        Este método debe ser sobrescrito por cada juego para definir sus elementos específicos.
        """
        # Ejemplo de elementos base que podrían ser comunes a todos los juegos
        self.ui_elements = {
            "titulo_rect": (0, self.navbar_height + self.sy(30), self.ANCHO, self.sy(60)),
            "feedback_rect": self.scaler.get_centered_rect(500, 50, vertical_offset=self.ALTO//2 - 50),
            "puntaje_rect": (self.sx(18), self.ALTO - self.sy(48) - self.sy(18), 
                            self.sx(180), self.sy(48))
        }

    def _nivel_from_dificultad(self, dificultad):
        """
        Traduce la dificultad a un nivel textual.
        """
        if dificultad == "Fácil":
            return "Básico"
        elif dificultad == "Normal":
            return "Medio"
        else:
            return "Avanzado"

    def _update_navbar_height(self):
        """
        Actualiza la altura de la barra de navegación si existe.
        """
        if self.navbar and hasattr(self.navbar, "get_height"):
            self.navbar_height = self.navbar.get_height()
        elif self.navbar and hasattr(self.navbar, "height"):
            self.navbar_height = self.navbar.height
        else:
            self.navbar_height = self.sy(60)  # Valor por defecto escalado

    def cargar_imagenes(self):
        """Para ser sobrescrito por cada juego si necesita cargar imágenes."""
        pass

    def dibujar_fondo(self):
        """Dibuja el fondo animado respetando la barra de navegación."""
        if self.pantalla:
            # En lugar de un fill estático, uso FondoAnimado
            self.fondo_animado.update()
            self.fondo_animado.draw()

    def mostrar_texto(self, texto, x, y, w, h, fuente=None, color=(30,30,30), centrado=False):
        """Muestra texto adaptativo en pantalla con coordenadas escaladas."""
        fuente = fuente or self.fuente
        mostrar_texto_adaptativo(
            pantalla=self.pantalla,
            texto=texto,
            x=x,
            y=y,
            w=w,
            h=h,
            fuente_base=fuente,
            color=color,
            centrado=centrado
        )

    def mostrar_titulo(self):
        """Muestra el título del juego centrado debajo de la navbar."""
        titulo_rect = self.ui_elements.get("titulo_rect", 
                                          (0, self.navbar_height + self.sy(30), 
                                           self.ANCHO, self.sy(60)))
        
        mostrar_texto_adaptativo(
            pantalla=self.pantalla,
            texto=f"{self.nombre} - Nivel {self.dificultad}",
            x=titulo_rect[0],
            y=titulo_rect[1],
            w=titulo_rect[2],
            h=titulo_rect[3],
            fuente_base=self.fuente_titulo,
            color=(70, 130, 180),
            centrado=True
        )

    def mostrar_puntaje(self, juegos_ganados, juegos_totales, frase="¡Puntaje!"):
        """
        Muestra el puntaje en la parte inferior izquierda en una caja bonita con emojis.
        """
        puntaje_rect = self.ui_elements.get("puntaje_rect", 
                                           (self.sx(18), self.ALTO - self.sy(48) - self.sy(18), 
                                            self.sx(180), self.sy(48)))
        
        x, y, ancho_caja, alto_caja = puntaje_rect

        texto = f"🏆 {frase}: {juegos_ganados}/{juegos_totales} 🎮"

        dibujar_caja_texto(
            self.pantalla,
            x, y, ancho_caja, alto_caja,
            color=(240, 250, 255, 230),
            radius=self.sy(18),
            texto=texto,
            fuente=self.fuente,
            color_texto=(30, 60, 90)
        )

    def generar_opciones(self, respuesta: int, cantidad: int = 3) -> list[int]:
        """
        Genera opciones aleatorias alrededor de la respuesta correcta, sin duplicados ni negativos.
        Mejorada para evitar bucles infinitos y asegurar variedad.
        """
        opciones = {respuesta}
        posibles = set(range(max(0, respuesta - 10), respuesta + 11)) - {respuesta}
        while len(opciones) < cantidad and posibles:
            op = random.choice(list(posibles))
            opciones.add(op)
            posibles.remove(op)
        while len(opciones) < cantidad:
            op = respuesta + random.randint(1, 20)
            opciones.add(op)
        resultado = list(opciones)
        random.shuffle(resultado)
        return resultado

    def dibujar_opciones(
        self,
        opciones=None,
        tooltips=None,
        estilo="flat",
        border_radius=None,
        x0=None,
        y0=None,
        espacio=None
    ):
        """
        Dibuja botones de opciones de forma responsiva, colorida y reutilizable.
        """
        opciones = opciones if opciones is not None else getattr(self, "opciones", [])
        if not opciones:
            return  # No dibujar si no hay opciones
            
        # Valores escalados
        border_radius = border_radius or self.sy(12)
        espacio = espacio or self.sx(20)
        
        cnt = len(opciones)
        w = max(self.sx(100), min(self.sx(180), self.ANCHO // (cnt * 2)))
        h = max(self.sy(50), min(self.sy(80), self.ALTO // 12))
        
        if x0 is None:
            x0 = (self.ANCHO - (w * cnt + espacio * (cnt - 1))) // 2
        if y0 is None:
            y0 = self.ALTO // 2 - h // 2
            
        paleta = PALETA[:cnt] if cnt <= len(PALETA) else PALETA * (cnt // len(PALETA)) + PALETA[:cnt % len(PALETA)]

        self.opcion_botones.clear()
        for i, val in enumerate(opciones):
            color_bg = paleta[i % len(paleta)]
            color_hover = self.color_complementario(color_bg)
            lum = 0.299 * color_bg[0] + 0.587 * color_bg[1] + 0.114 * color_bg[2]
            color_texto = (0, 0, 0) if lum > 180 else (255, 255, 255)
            x = x0 + i * (w + espacio)
            btn = Boton(
                texto=str(val),
                x=x, y=y0, ancho=w, alto=h,
                fuente=self.fuente,
                color_normal=color_bg,
                color_hover=color_hover,
                color_texto=color_texto,
                border_radius=border_radius,
                estilo=estilo,
                tooltip=tooltips[i] if tooltips and i < len(tooltips) else None
            )
            btn.draw(self.pantalla, tooltip_manager=getattr(self, "tooltip_manager", None))
            self.opcion_botones.append(btn)

    @staticmethod
    def color_complementario(rgb):
        """Devuelve el color complementario."""
        return tuple(255 - c for c in rgb)

    def mostrar_victoria(
        self, carta_rects, color_panel=(255, 255, 224), color_borde=(255, 215, 0)
    ):
        """Muestra pantalla de victoria con escalado responsivo."""
        ancho_panel = self.sx(500)
        alto_panel = self.sy(200)
        x_panel = (self.ANCHO - ancho_panel) // 2
        y_panel = (self.ALTO - alto_panel) // 2
        
        # Crear panel con gradiente
        panel = pygame.Surface((ancho_panel, alto_panel), pygame.SRCALPHA)
        for i in range(alto_panel):
            factor = i / alto_panel
            r = int(255 - factor * 50)
            g = int(250 - factor * 20)
            b = int(150 + factor * 50)
            pygame.draw.line(panel, (r, g, b, 240), (0, i), (ancho_panel, i))
        self.pantalla.blit(panel, (x_panel, y_panel))
        
        # Borde del panel
        pygame.draw.rect(
            self.pantalla, 
            color_borde, 
            (x_panel, y_panel, ancho_panel, alto_panel), 
            4, 
            border_radius=self.sy(20)
        )
        
        # Título
        mostrar_alternativo_adaptativo(
            self.pantalla, "¡FELICIDADES! 🎉",
            x_panel, y_panel + self.sy(20), ancho_panel, self.sy(60),
            self.fuente_titulo, (100, 160, 220), centrado=True
        )
        
        # Subtítulo
        mostrar_texto_adaptativo(
            self.pantalla, "¡Has completado el memorama!",
            x_panel, y_panel + self.sy(80), ancho_panel, self.sy(40),
            self.fuente, (30, 30, 30), centrado=True
        )
        
        # Botón de reinicio
        boton = Boton(
            "¡Reiniciar! 🔄",
            x_panel + (ancho_panel - self.sx(300)) // 2,
            y_panel + self.sy(130),
            self.sx(300), self.sy(50),
            color_normal=(100, 160, 220),
            color_hover=(30, 60, 120),
            fuente=pygame.font.SysFont("Segoe UI Emoji", self.sf(28)),
            texto_adaptativo=True
        )
        boton.draw(self.pantalla)
        carta_rects.append((boton.rect, {'id': 'siguiente'}))
        
        # Caja de texto
        dibujar_caja_texto(
            self.pantalla, x_panel, y_panel, ancho_panel, alto_panel,
            color=(220, 240, 255, 220),
            radius=self.sy(16),
            texto="¡Victoria! 🎉",
            fuente=self.fuente_titulo,
            color_texto=(30, 30, 60)
        )

    def handle_event(self, evento):
        # Lógica base: salir, resize, etc.
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            if self.return_to_menu:
                self.return_to_menu()
                pygame.display.set_caption("jugando con dino")
        if evento.type == pygame.VIDEORESIZE:
            self.ANCHO, self.ALTO = evento.w, evento.h
            self.pantalla = pygame.display.set_mode((self.ANCHO, self.ALTO), pygame.RESIZABLE)
            self._update_navbar_height()
            
            # Actualizar el sistema de escalado
            self.scaler.update(self.ANCHO, self.ALTO)
            
            # Actualizar fuentes con nuevos tamaños escalados
            self.fuente_titulo = obtener_fuente(self.sf(36), negrita=True)
            self.fuente = obtener_fuente(self.sf(20))
            
            # Reinicializar elementos UI responsivos
            self.init_responsive_ui()
            
            # --- Actualizar FondoAnimado ---
            self.fondo_animado.set_escaladores(self.sx, self.sy)
            self.fondo_animado.resize(self.ANCHO, self.ALTO)
            
            # Llamar al método específico de cada juego
            self.on_resize(self.ANCHO, self.ALTO)
            
        # Manejar clicks en botones de opciones
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for btn in self.opcion_botones:
                if btn.handle_event(evento):
                    break
                    
        # Para ser sobrescrito por cada juego
        pass

    def on_resize(self, ancho, alto):
        # Método opcional para que los juegos hijos ajusten elementos al redimensionar
        pass

    def update(self, dt=None):
        # Actualizo fondo animado antes de la lógica específica
        self.fondo_animado.update()
        # Para ser sobrescrito por cada juego

    def draw(self, surface):
        # Dibujo fondo y luego dejo que cada juego dibuje lo suyo
        surface = surface or self.pantalla
        self.dibujar_fondo()
        # Para ser sobrescrito por cada juego

