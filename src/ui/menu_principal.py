"""
Menú principal del juego Dino, con barra de navegación, fondo dinámico y transiciones.
"""
import pygame
import time
import random
from ui.navigation_bar import NavigationBar
from ui.animations import animar_dinos, dibujar_caja_juegos
from ui.components.utils import Boton, dibujar_caja_texto, mostrar_texto_adaptativo,TooltipManager
from ui.components.emoji import mostrar_alternativo_adaptativo
from core.game_state import *
from games import JUEGOS_DISPONIBLES
from ui.screen_manager import (
    ScreenManager, HomeScreen, JuegosScreen, ChatBotScreen, GameInstanceScreen,
    set_screen, handle_event_screen, update_screen, draw_screen
)

class MenuPrincipal:
    def __init__(self, pantalla, fondo, images, sounds, config, screen_manager=None):
        # --- Inicialización de pantalla y dimensiones base ---
        self.pantalla = pantalla
        self.base_width = pantalla.get_width()
        self.base_height = pantalla.get_height()

        # --- Recursos principales ---
        self.fondo = fondo                # Fondo animado
        self.images = images              # Diccionario de imágenes
        self.sounds = sounds              # Diccionario de sonidos
        self.config = config              # Configuración general

        # --- Barra de navegación y niveles ---
        self.niveles = ["Home", "Fácil", "Normal", "Difícil", "ChatBot"]
        tooltips = [
            "Ir a la pantalla principal",
            "Juegos para principiantes",
            "Juegos intermedios",
            "Juegos avanzados",
            "Habla con el ChatBot"
        ]
        self.navbar = NavigationBar(self.niveles, down=False, tooltips=tooltips)
        self.logo = self.images.get("dino_logo") if self.images else None

        # --- Recursos gráficos de dinosaurios ---
        self.imagenes_dinos = [self.images.get(f"dino{i+1}") for i in range(5)] if self.images else []
        self.dinos_actuales = [0, 1, 2]   # Índices de los dinos mostrados actualmente
        self.ultimo_cambio_dinos = time.time()  # Para animación de dinos

        # --- Tipografías principales ---
        self.font_titulo = pygame.font.SysFont("Segoe UI", 54, bold=True)
        self.font_texto = pygame.font.SysFont("Segoe UI", 28)

        # --- Reloj para control de FPS ---
        self.clock = pygame.time.Clock()

        # --- Screen manager ---
        if screen_manager is None:
            self.screen_manager = ScreenManager()
        else:
            self.screen_manager = screen_manager

        # --- Tooltip manager ---
        self.tooltip_manager = TooltipManager()

    def sx(self, x):
        return int(x * self.pantalla.get_width() / self.base_width)
    def sy(self, y):
        return int(y * self.pantalla.get_height() / self.base_height)

    def mostrar_home(self):
        # Dimensiones base
        base_w, base_h = 900, 700
        esc_x = self.pantalla.get_width() / base_w
        esc_y = self.pantalla.get_height() / base_h
        esc = min(esc_x, esc_y)
        # Caja título centrada
        w_t, h_t = int(640 * esc), int(60 * esc)
        x_t = (self.pantalla.get_width() - w_t) // 2
        y_t = int(110 * esc_y)
        dibujar_caja_texto(self.pantalla, x_t, y_t, w_t, h_t, (70, 130, 180))
        font_titulo = pygame.font.SysFont("Segoe UI", int(54 * esc), bold=True)
        mostrar_texto_adaptativo(
            self.pantalla,
            "¡Bienvenido a Jugando con Dino!",
            x_t, y_t, w_t, h_t,
            font_titulo,
            (255,255,255),
            centrado=True
        )
        # Caja instrucciones centrada
        w_c, h_c = int(600 * esc), int(320 * esc)
        x_c = (self.pantalla.get_width() - w_c) // 2
        y_c = int(180 * esc_y)
        dibujar_caja_texto(self.pantalla, x_c, y_c, w_c, h_c, (255,255,255,220))
        instrucciones = (
            "¡Aprende matemáticas jugando con Dino y sus amigos!\n\n"
            "Selecciona una opción en la barra superior:\n\n"
            "- Fácil: Juegos para principiantes\n"
            "- Normal: Juegos para quienes ya conocen los conceptos básicos\n"
            "- Difícil: Juegos para expertos en matemáticas\n"
            "- ChatBot: Habla directamente con Dino y pregúntale sobre matemáticas\n\n"
            "¡Diviértete y aprende mientras juegas!"
        )
        font_texto = pygame.font.SysFont("Segoe UI", int(28 * esc))
        mostrar_texto_adaptativo(
            self.pantalla,
            instrucciones,
            x_c, y_c, w_c, h_c,
            font_texto,
            (30,30,30),
            centrado=True
        )
        # Animación de dinos centrada
        if time.time() - self.ultimo_cambio_dinos >= 3.0:
            self.dinos_actuales = random.sample(range(len(self.imagenes_dinos)), 3)
            self.ultimo_cambio_dinos = time.time()
        dino_y = int(520 * esc_y)
        dino_w = int(120 * esc)
        dino_h = int(80 * esc)
        espacio = int(80 * esc)
        total_w = 3 * dino_w + 2 * espacio
        x_ini = (self.pantalla.get_width() - total_w) // 2
        dino_positions = [
            (x_ini + i * (dino_w + espacio), dino_y) for i in range(3)
        ]
        
        animar_dinos(
            self.pantalla,
            [self.imagenes_dinos[idx] for idx in self.dinos_actuales],
            dino_positions,
            esc,
            pygame.time.get_ticks()
        )
        
        

    def mostrar_chatbot(self):
        ancho, alto = self.pantalla.get_width(), self.pantalla.get_height()
        dibujar_caja_texto(self.pantalla, self.sx(80), self.sy(120), ancho - self.sx(160), alto - self.sy(180), (245, 245, 255), radius=24)
        mostrar_texto_adaptativo(
            self.pantalla,
            "ChatBot Dino",
            self.sx(100), self.sy(140), ancho - self.sx(200), self.sy(60),
            pygame.font.SysFont("Segoe UI", 48, bold=True),
            (70, 130, 180),
            centrado=True
        )
        mostrar_alternativo_adaptativo(
            self.pantalla,
            "¡Hola! Soy Dino. Pregúntame cualquier cosa sobre matemáticas.Σ 🧠 π 🦖",
            self.sx(120), self.sy(220), ancho - self.sx(240), self.sy(60),
            self.font_texto,
            (30, 30, 30),
            centrado=True
        )

    def mostrar_juegos(self, dificultad):
        x_t, y_t, w_t, h_t = self.sx(130), self.sy(110), self.sx(640), self.sy(60)
        dibujar_caja_texto(self.pantalla, x_t, y_t, w_t, h_t, (70, 130, 180))
        # --- Estado de dificultad seleccionada ---
        self.dificultad_seleccionada = dificultad
        mostrar_texto_adaptativo(
            self.pantalla,
            f"Juegos de nivel {dificultad}",
            x_t, y_t, w_t, h_t,
            self.font_titulo,
            (255,255,255),
            centrado=True
        )
        # Aquí podrías mostrar botones de juegos según la dificultad
        # Ejemplo: dibujar_caja_texto(...), mostrar_texto_adaptativo(...)
        # Área para la grilla de juegos (ajusta estos valores según tu diseño)
        x = self.sx(100)
        y = self.sy(200)
        w = self.pantalla.get_width() - self.sx(200)
        h = self.pantalla.get_height() - self.sy(260)
        margen = 24
        tam_caja = 160
        self.juego_rects = dibujar_caja_juegos(
            self.pantalla,
            x, y, w, h,
            juegos=JUEGOS_DISPONIBLES,
            recursos=self.images,
            color=(255,255,255),
            alpha=30,
            radius=24,
            margen=margen,
            tam_caja=tam_caja,
            fuente=self.font_texto
        )
        
    def handle_juegos_eventos(self, event):
        """Handle events for the games screen."""
        if event.type == pygame.MOUSEBUTTONDOWN and hasattr(self, "juego_rects"):
            for idx, rect in enumerate(self.juego_rects):
                if idx < len(JUEGOS_DISPONIBLES) and rect.collidepoint(event.pos):
                    print(f"Click en juego {idx}: {JUEGOS_DISPONIBLES[idx]['nombre']}")
                    juego = JUEGOS_DISPONIBLES[idx]
                    if callable(juego["clase"]):
                        instancia = juego["clase"](
                            self.pantalla,
                            self.config,
                            self.dificultad_seleccionada,
                            self.fondo,
                            self.navbar,
                            self.images,
                            self.sounds,
                            return_to_menu=lambda: set_screen(self.screen_manager, JuegosScreen(self, self.dificultad_seleccionada))
                        )
                        game_screen = GameInstanceScreen(instancia)
                        set_screen(self.screen_manager, game_screen)
                        return True
        return False

    def run(self):
        running = True
        last_time = time.time()
        set_screen(self.screen_manager, HomeScreen(self))
        Fps = 60

        while running:
            now = time.time()
            dt = now - last_time
            last_time = now

            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    # Solo actualiza si cambia el tamaño
                    if (event.w, event.h) != (self.base_width, self.base_height):
                        self.base_width, self.base_height = event.w, event.h
                        self.pantalla = pygame.display.set_mode((self.base_width, self.base_height), pygame.RESIZABLE)
                        self.fondo.resize(self.base_width, self.base_height)
                # Barra de navegación
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    nav_result = self.navbar.handle_event(event, self.logo)
                    if nav_result is not None:
                        vista = self.niveles[nav_result]
                        if vista == "Home":
                            set_screen(self.screen_manager, HomeScreen(self))
                        elif vista in ("Fácil", "Normal", "Difícil"):
                            set_screen(self.screen_manager, JuegosScreen(self, vista))
                        elif vista == "ChatBot":
                            set_screen(self.screen_manager, ChatBotScreen(self))

            # Actualiza tooltips globales si usas botones personalizados
            self.tooltip_manager.update(pygame.mouse.get_pos())

            # Delega eventos a la pantalla activa
            handle_event_screen(self.screen_manager, events)

            # Fondo dinámico
            self.fondo.update(dt * Fps)
            self.fondo.draw(self.pantalla)

            # Elementos de la pantalla según selección usando el screen manager
            update_screen(self.screen_manager, dt)
            draw_screen(self.screen_manager, self.pantalla)

            # Barra de navegación con logo (siempre encima de todo)
            self.navbar.draw(self.pantalla, self.logo)

            pygame.display.flip()
            self.clock.tick(Fps)

def run_menu_principal(pantalla, fondo, images, sounds, config):
    # Crear el screen manager
    screen_manager = ScreenManager()

    # Al iniciar el menú principal
    menu = MenuPrincipal(pantalla, fondo, images, sounds, config, screen_manager)
    screen_manager.set_screen(HomeScreen(menu))
    menu.run()
