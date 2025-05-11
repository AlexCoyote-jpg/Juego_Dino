import pygame
import random
from ui.components.utils import (
    mostrar_texto_adaptativo, Boton, obtener_fuente, render_text_cached,
    dibujar_caja_texto, TooltipManager
)
from ui.components.emoji import mostrar_alternativo_adaptativo
from core.decoration.effects import EffectsMixin  # Asegúrate de que la ruta sea correcta
from core.decoration.background_game import FondoAnimado  # <--- agregado

# Ejemplos para mostrar en mostrar_mensaje_temporal o donde corresponda

# Cuando la respuesta es correcta:
mensajes_correcto = [
    "¡Excelente! 🦕✨",
    "¡Muy bien, Dino está feliz! 🥚🎉",
    "¡Correcto! ¡Sigue así! 🌟",
    "¡Genial! ¡Eres un crack de las mates! 🦖"
]

# Cuando la respuesta es incorrecta:
mensajes_incorrecto = [
    "¡Ups! Intenta de nuevo, tú puedes 🦕",
    "¡No te rindas! La respuesta era {respuesta} 🥚",
    "¡Casi! Sigue practicando 💪",
    "¡Ánimo! Dino confía en ti 🦖"
]
PALETA = [
    (244, 67, 54),    # rojo
    (233, 30, 99),    # rosa
    (156, 39, 176),   # púrpura
    (63, 81, 181),    # índigo
    (33, 150, 243),   # azul claro
    (0, 188, 212),    # cian
    (0, 150, 136),    # teal
    (76, 175, 80),    # verde
    (255, 235, 59),   # amarillo
    (255, 152, 0),    # naranja
]

# --- Sistema de Escalado Responsivo ---
class ResponsiveScaler:
    """
    Sistema de escalado responsivo que mantiene proporciones consistentes
    en diferentes resoluciones de pantalla.
    """
    def __init__(self, base_width=1280, base_height=720):
        """
        Inicializa el escalador con dimensiones base de referencia.
        
        Args:
            base_width: Ancho base de diseño (por defecto 1280)
            base_height: Alto base de diseño (por defecto 720)
        """
        self.base_width = base_width
        self.base_height = base_height
        self.current_width = base_width
        self.current_height = base_height
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.aspect_ratio = base_width / base_height
        self.cached_values = {}
        
    def update(self, width, height):
        """
        Actualiza los factores de escala basados en las nuevas dimensiones.
        
        Args:
            width: Ancho actual de la pantalla
            height: Alto actual de la pantalla
        """
        self.current_width = width
        self.current_height = height
        self.scale_x = width / self.base_width
        self.scale_y = height / self.base_height
        self.aspect_ratio = width / height
        # Limpiar caché cuando cambian las dimensiones
        self.cached_values = {}
        
    def scale_x_value(self, value):
        """Escala un valor horizontal."""
        cache_key = f"x_{value}"
        if cache_key not in self.cached_values:
            self.cached_values[cache_key] = int(value * self.scale_x)
        return self.cached_values[cache_key]
        
    def scale_y_value(self, value):
        """Escala un valor vertical."""
        cache_key = f"y_{value}"
        if cache_key not in self.cached_values:
            self.cached_values[cache_key] = int(value * self.scale_y)
        return self.cached_values[cache_key]
    
    def scale_font_size(self, size):
        """Escala un tamaño de fuente de manera balanceada."""
        cache_key = f"font_{size}"
        if cache_key not in self.cached_values:
            # Usar un promedio ponderado para que la fuente no sea demasiado grande o pequeña
            scale_factor = (self.scale_x * 0.6 + self.scale_y * 0.4)
            self.cached_values[cache_key] = max(12, int(size * scale_factor))
        return self.cached_values[cache_key]
    
    def scale_rect(self, x, y, width, height):
        """Escala un rectángulo completo."""
        return (
            self.scale_x_value(x),
            self.scale_y_value(y),
            self.scale_x_value(width),
            self.scale_y_value(height)
        )
    
    def get_centered_rect(self, width, height, vertical_offset=0):
        """
        Obtiene un rectángulo centrado en la pantalla con dimensiones escaladas.
        
        Args:
            width: Ancho base del rectángulo
            height: Alto base del rectángulo
            vertical_offset: Desplazamiento vertical desde el centro (positivo = hacia abajo)
        
        Returns:
            Tupla (x, y, width, height) con valores escalados
        """
        scaled_width = self.scale_x_value(width)
        scaled_height = self.scale_y_value(height)
        x = (self.current_width - scaled_width) // 2
        y = (self.current_height - scaled_height) // 2 + self.scale_y_value(vertical_offset)
        return (x, y, scaled_width, scaled_height)
    
    def maintain_aspect_ratio(self, width, height):
        """
        Ajusta dimensiones para mantener la relación de aspecto.
        Útil para imágenes y elementos visuales que no deben distorsionarse.
        """
        target_ratio = width / height
        if target_ratio > self.aspect_ratio:
            # Limitar por ancho
            new_width = self.scale_x_value(width)
            new_height = int(new_width / target_ratio)
        else:
            # Limitar por alto
            new_height = self.scale_y_value(height)
            new_width = int(new_height * target_ratio)
        return new_width, new_height

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

# Ejemplo de uso para un juego específico
class JuegoEjemplo(JuegoBase):
    def __init__(self, nombre, pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu):
        super().__init__(nombre, pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu)
        
        # Inicializar elementos específicos del juego
        self.puntuacion = 0
        self.total_preguntas = 10
        self.pregunta_actual = 1
        self.respuesta_correcta = 42
        self.opciones = self.generar_opciones(self.respuesta_correcta, 4)
        
        # Elementos UI específicos de este juego
        self.init_responsive_ui()
        
    def init_responsive_ui(self):
        """Inicializa elementos UI específicos de este juego."""
        super().init_responsive_ui()  # Llamar al método de la clase base primero
        
        # Añadir elementos específicos de este juego
        self.ui_elements.update({
            "pregunta_rect": (self.sx(100), self.navbar_height + self.sy(100), 
                             self.ANCHO - self.sx(200), self.sy(100)),
            "opciones_y": self.ALTO // 2 + self.sy(50),
            "instrucciones_rect": (self.sx(50), self.ALTO - self.sy(100), 
                                  self.ANCHO - self.sx(100), self.sy(50))
        })
        
    def on_resize(self, ancho, alto):
        """Maneja el redimensionamiento específico para este juego."""
        # Actualizar posiciones de elementos específicos
        self.init_responsive_ui()
        
    def draw(self, surface=None):
        """Dibuja la interfaz del juego."""
        surface = surface or self.pantalla
        
        # Dibujar fondo
        self.dibujar_fondo()
        
        # Dibujar título
        self.mostrar_titulo()
        
        # Dibujar pregunta
        pregunta_rect = self.ui_elements["pregunta_rect"]
        self.mostrar_texto(
            f"Pregunta {self.pregunta_actual}/{self.total_preguntas}: ¿Cuál es la respuesta a la vida, el universo y todo lo demás?",
            pregunta_rect[0], pregunta_rect[1], pregunta_rect[2], pregunta_rect[3],
            self.fuente, (30, 30, 90), centrado=True
        )
        
        # Dibujar opciones
        self.dibujar_opciones(
            opciones=self.opciones,
            y0=self.ui_elements["opciones_y"]
        )
        
        # Dibujar puntaje
        self.mostrar_puntaje(self.puntuacion, self.total_preguntas)
        
        # Dibujar racha
        self.mostrar_racha()
        
        # Dibujar operación actual
        self.mostrar_operacion()
        
        # Dibujar instrucciones
        instrucciones_rect = self.ui_elements["instrucciones_rect"]
        self.mostrar_texto(
            "Haz clic en la opción correcta. Presiona ESC para volver al menú.",
            instrucciones_rect[0], instrucciones_rect[1], 
            instrucciones_rect[2], instrucciones_rect[3],
            fuente=obtener_fuente(self.sf(16)), 
            color=(100, 100, 100), 
            centrado=True
        )
        
    def handle_event(self, evento):
        """Maneja eventos específicos del juego."""
        super().handle_event(evento)  # Llamar al método de la clase base primero
        
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for i, btn in enumerate(self.opcion_botones):
                if btn.collidepoint(evento.pos):
                    self.verificar_respuesta(self.opciones[i])
                    break
    
    def verificar_respuesta(self, respuesta):
        """Verifica si la respuesta seleccionada es correcta."""
        es_correcta = respuesta == self.respuesta_correcta
        
        if es_correcta:
            self.puntuacion += 1
            
        # Generar nueva pregunta
        if self.pregunta_actual < self.total_preguntas:
            self.pregunta_actual += 1
            self.respuesta_correcta = random.randint(1, 100)
            self.opciones = self.generar_opciones(self.respuesta_correcta, 4)
        else:
            # Juego terminado
            print(f"¡Juego terminado! Puntuación final: {self.puntuacion}/{self.total_preguntas}")

# Función para probar el sistema responsivo
def test_responsive_game():
    pygame.init()
    pantalla = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
    pygame.display.set_caption("Test Responsivo")
    
    # Crear instancia del juego de ejemplo
    juego = JuegoEjemplo(
        nombre="Juego de Prueba",
        pantalla=pantalla,
        config={},
        dificultad="Normal",
        fondo=None,
        navbar=None,
        images={},
        sounds={},
        return_to_menu=lambda: print("Volviendo al menú")
    )
    
    ejecutando = True
    reloj = pygame.time.Clock()
    
    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                ejecutando = False
                
            juego.handle_event(evento)
            
        juego.update()
        juego.draw()
        
        pygame.display.flip()
        reloj.tick(60)
        
    pygame.quit()

if __name__ == "__main__":
    test_responsive_game()