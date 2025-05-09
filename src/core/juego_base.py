# Clase base para juegos: define la interfaz y utilidades comunes para todos los juegos.

import pygame
import random
from ui.utils import (
    mostrar_texto_adaptativo, Boton, obtener_fuente, render_text_cached,
    dibujar_caja_texto, TooltipManager
)
from ui.Emojis import mostrar_alternativo_adaptativo

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

class JuegoBase:
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
        self.fuente_titulo = obtener_fuente(max(36, int(0.04 * self.ALTO)), negrita=True)
        self.fuente = obtener_fuente(max(20, int(0.025 * self.ALTO)))
        self.reloj = pygame.time.Clock()
        self.navbar_height = 0
        self._update_navbar_height()

        # --- Tooltip manager (opcional para juegos con tooltips) ---
        self.tooltip_manager = TooltipManager(delay=1.0)

        # --- Actualiza el título de la ventana ---
        pygame.display.set_caption(f"{self.nombre} - {self.dificultad}")

        # --- Inicializa lista de botones de opciones ---
        self.opcion_botones = []

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
            self.navbar_height = 60  # Valor por defecto

    def cargar_imagenes(self):
        """Para ser sobrescrito por cada juego si necesita cargar imágenes."""
        pass

    def dibujar_fondo(self):
        """Dibuja el fondo respetando la barra de navegación."""
        if self.pantalla:
            self.pantalla.fill((255, 255, 255))
            # Puedes dibujar aquí un área reservada para la navbar si lo deseas

    def mostrar_texto(self, texto, x, y, w, h, fuente=None, color=(30,30,30), centrado=False):
        """Muestra texto adaptativo en pantalla."""
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
        mostrar_texto_adaptativo(
            pantalla=self.pantalla,
            texto=f"{self.nombre} - Nivel {self.dificultad}",
            x=0,
            y=self.navbar_height + 30,
            w=self.ANCHO,
            h=60,
            fuente_base=self.fuente_titulo,
            color=(70, 130, 180),
            centrado=True
        )

    def mostrar_puntaje(self, juegos_ganados, juegos_totales, frase="¡Puntaje!"):
        """
        Muestra el puntaje en la parte inferior izquierda en una caja bonita con emojis.
        """
        ancho_caja = max(180, int(self.ANCHO * 0.18))
        alto_caja = max(48, int(self.ALTO * 0.07))
        x = 18
        y = self.ALTO - alto_caja - 18

        texto = f"🏆 {frase}: {juegos_ganados}/{juegos_totales} 🎮"

        dibujar_caja_texto(
            self.pantalla,
            x, y, ancho_caja, alto_caja,
            color=(240, 250, 255, 230),
            radius=18,
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
        border_radius=12,
        x0=None,
        y0=None,
        espacio=20
    ):
        """
        Dibuja botones de opciones de forma responsiva, colorida y reutilizable.
        """
        opciones = opciones if opciones is not None else getattr(self, "opciones", [])
        if not opciones:
            return  # No dibujar si no hay opciones
        cnt = len(opciones)
        w = max(100, min(180, self.ANCHO // (cnt * 2)))
        h = max(50, min(80, self.ALTO // 12))
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

    @staticmethod
    def mostrar_victoria(
        pantalla, sx, sy, ancho, alto, fuente_titulo, fuente_texto, juego_base, carta_rects,
        color_panel=(255, 255, 224), color_borde=(255, 215, 0)
    ):
        ancho_panel = sx(500)
        alto_panel = sy(200)
        x_panel = (ancho - ancho_panel) // 2
        y_panel = (alto - alto_panel) // 2
        panel = pygame.Surface((ancho_panel, alto_panel), pygame.SRCALPHA)
        for i in range(alto_panel):
            factor = i / alto_panel
            r = int(255 - factor * 50)
            g = int(250 - factor * 20)
            b = int(150 + factor * 50)
            pygame.draw.line(panel, (r, g, b, 240), (0, i), (ancho_panel, i))
        pantalla.blit(panel, (x_panel, y_panel))
        pygame.draw.rect(pantalla, color_borde, (x_panel, y_panel, ancho_panel, alto_panel), 4, border_radius=20)
        mostrar_alternativo_adaptativo(
            pantalla, "¡FELICIDADES! 🎉",
            x_panel, y_panel + sy(20), ancho_panel, sy(60),
            fuente_titulo, (100, 160, 220), centrado=True
        )
        mostrar_texto_adaptativo(
            pantalla, "¡Has completado el memorama!",
            x_panel, y_panel + sy(80), ancho_panel, sy(40),
            fuente_texto, (30, 30, 30), centrado=True
        )
        # Botón de reinicio
        boton = Boton(
            "¡Reiniciar! 🔄",
            x_panel + (ancho_panel - sx(300)) // 2,
            y_panel + sy(130),
            sx(300), sy(50),
            color_normal=(100, 160, 220),
            color_hover=(30, 60, 120),
            fuente=pygame.font.SysFont("Segoe UI Emoji", 28),
            texto_adaptativo=True
        )
        boton.draw(pantalla)
        carta_rects.append((boton.rect, {'id': 'siguiente'}))
        dibujar_caja_texto(
            pantalla, x_panel, y_panel, ancho_panel, alto_panel,
            color=(220, 240, 255, 220),
            radius=16,
            texto="¡Victoria! 🎉",
            fuente=fuente_titulo,
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
            self.on_resize(self.ANCHO, self.ALTO)
        # Para ser sobrescrito por cada juego
        pass

    def on_resize(self, ancho, alto):
        # Método opcional para que los juegos hijos ajusten elementos al redimensionar
        pass

    def update(self, dt=None):
        # Para ser sobrescrito por cada juego
        pass

    def draw(self, surface):
        # Para ser sobrescrito por cada juego
        pass

    def mostrar_feedback(self, es_correcto, respuesta_correcta=None):
        if es_correcto:
            mensaje = random.choice(mensajes_correcto)
        else:
            mensaje = random.choice(mensajes_incorrecto).format(respuesta=respuesta_correcta)
        self.mostrar_mensaje_temporal(mensaje)
