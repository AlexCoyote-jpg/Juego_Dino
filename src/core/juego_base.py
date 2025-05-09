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

class JuegoBase:
    def __init__(self, nombre, pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu):
        # --- Integración con el menú principal ---
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

    def _nivel_from_dificultad(self, dificultad):
        if dificultad == "Fácil":
            return "Básico"
        elif dificultad == "Normal":
            return "Medio"
        else:
            return "Avanzado"    

    def _update_navbar_height(self):
        if self.navbar and hasattr(self.navbar, "get_height"):
            self.navbar_height = self.navbar.get_height()
        elif self.navbar and hasattr(self.navbar, "height"):
            self.navbar_height = self.navbar.height
        else:
            self.navbar_height = 60  # Valor por defecto

    def cargar_imagenes(self):
        # Para ser sobrescrito por cada juego si necesita cargar imágenes
        pass

    def dibujar_fondo(self):
        # Dibuja el fondo respetando la barra de navegación
        if self.pantalla:
            self.pantalla.fill((255, 255, 255))
            # Puedes dibujar aquí un área reservada para la navbar si lo deseas
            

    def mostrar_texto(self, texto, x, y, w, h, fuente=None, color=(30,30,30), centrado=False):
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
        # Dimensiones y posición responsiva
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
    @staticmethod    
    def color_complementario(rgb):
            # Complementario simple: 255 - componente
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
