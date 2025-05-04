"""
Menú principal del juego Dino, con barra de navegación, fondo dinámico y transiciones.
"""
import pygame
import time
import random
from ui.navigation_bar import NavigationBar
from ui.animations import animar_dinos
from ui.utils import dibujar_caja_texto, mostrar_texto_adaptativo
from core.game_state import create_juego_base, manejar_transicion

class MenuPrincipal:
    def __init__(self, pantalla, fondo, images, sounds, config):
        self.pantalla = pantalla
        self.fondo = fondo
        self.images = images
        self.sounds = sounds
        self.config = config
        self.base_width = pantalla.get_width()
        self.base_height = pantalla.get_height()
        # Acceso a recursos por nombre
        self.logo = self.images.get("dino_logo") if self.images else None
        self.niveles = ["Home", "Fácil", "Normal", "Difícil", "ChatBot"]
        self.navbar = NavigationBar(self.niveles, down=False)
        self.juego_base = create_juego_base(pantalla, pantalla.get_width(), pantalla.get_height())
        self.imagenes_dinos = [self.images.get(f"dino{i+1}") for i in range(5)] if self.images else []
        self.font_titulo = pygame.font.SysFont("Segoe UI", 54, bold=True)
        self.font_texto = pygame.font.SysFont("Segoe UI", 28)
        self.ultimo_cambio_dinos = time.time()
        self.dinos_actuales = [0, 1, 2]
        self.dificultad_seleccionada = "Fácil"
        self.clock = pygame.time.Clock()

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
        mostrar_texto_adaptativo(
            self.pantalla,
            "¡Hola! Soy Dino. Pregúntame cualquier cosa sobre matemáticas.",
            self.sx(120), self.sy(220), ancho - self.sx(240), self.sy(60),
            self.font_texto,
            (30, 30, 30),
            centrado=True
        )

    def mostrar_juegos(self, dificultad):
        x_t, y_t, w_t, h_t = self.sx(130), self.sy(110), self.sx(640), self.sy(60)
        dibujar_caja_texto(self.pantalla, x_t, y_t, w_t, h_t, (70, 130, 180))
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

    def run(self):
        running = True
        last_time = time.time()
        while running:
            now = time.time()
            dt = now - last_time
            last_time = now

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.base_width, ALTO = event.w, event.h
                    self.pantalla = pygame.display.set_mode((self.base_width, ALTO), pygame.RESIZABLE)
                    self.fondo.resize(self.base_width, ALTO)
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    nav_result = self.navbar.handle_event(event, self.logo)
                    if nav_result is not None:
                        self.juego_base["nivel_actual"] = self.niveles[nav_result]

            # 1. Fondo dinámico
            self.fondo.update(dt * 60)  # Multiplica por 60 para mantener velocidad similar
            # Redibujar el fondo y las estrellas
            self.fondo.draw(self.pantalla)
            # 2. Elementos de la pantalla según selección
            nivel = self.juego_base["nivel_actual"]
            if nivel == "Home":
                self.mostrar_home()
            elif nivel in ("Fácil", "Normal", "Difícil"):
                self.mostrar_juegos(nivel)
            elif nivel == "ChatBot":
                self.mostrar_chatbot()
            # 3. Barra de navegación con logo (siempre encima de todo)
            self.navbar.draw_with_logo(self.pantalla, self.logo)
            # 4. Transición visual si aplica
            manejar_transicion(self.juego_base)
            pygame.display.flip()
            self.clock.tick(60)

def run_menu_principal(pantalla, fondo, images, sounds, config):
    menu = MenuPrincipal(pantalla, fondo, images, sounds, config)
    menu.run()
