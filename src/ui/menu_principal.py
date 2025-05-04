"""
Menú principal del juego Dino, con barra de navegación, fondo dinámico y transiciones.
"""
import pygame
import time
import random
from ui.navigation_bar import NavigationBar
from ui.animations import dibujar_fondo_animado, animar_dinos
from ui.utils import dibujar_caja_texto, mostrar_texto_adaptativo
from core.game_state import create_juego_base, manejar_transicion

class MenuPrincipal:
    def __init__(self, pantalla, fondo, estrellas, images, sounds, config, fondo_thread=None):
        self.pantalla = pantalla
        self.fondo = fondo
        self.estrellas = estrellas
        self.images = images
        self.sounds = sounds
        self.config = config
        self.fondo_thread = fondo_thread
        self.base_width = pantalla.get_width()
        self.base_height = pantalla.get_height()
        # Acceso a recursos por nombre
        self.logo = self.images.get("dino_logo") if self.images else None
        self.niveles = ["Home", "Fácil", "Normal", "Difícil", "ChatBot"]
        self.navbar = NavigationBar(self.niveles)
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
        x_t, y_t, w_t, h_t = self.sx(130), self.sy(110), self.sx(640), self.sy(60)
        dibujar_caja_texto(self.pantalla, x_t, y_t, w_t, h_t, (70, 130, 180))
        mostrar_texto_adaptativo(
            self.pantalla,
            "¡Bienvenido a Jugando con Dino!",
            x_t, y_t, w_t, h_t,
            self.font_titulo,
            (255,255,255),
            centrado=True
        )
        caja_x, caja_y, caja_w, caja_h = self.sx(150), self.sy(180), self.sx(600), self.sy(320)
        dibujar_caja_texto(self.pantalla, caja_x, caja_y, caja_w, caja_h, (255,255,255,220))
        instrucciones = (
            "¡Aprende matemáticas jugando con Dino y sus amigos!\n\n"
            "Selecciona una opción en la barra superior:\n\n"
            "- Fácil: Juegos para principiantes\n"
            "- Normal: Juegos para quienes ya conocen los conceptos básicos\n"
            "- Difícil: Juegos para expertos en matemáticas\n"
            "- ChatBot: Habla directamente con Dino y pregúntale sobre matemáticas\n\n"
            "¡Diviértete y aprende mientras juegas!"
        )
        mostrar_texto_adaptativo(
            self.pantalla,
            instrucciones,
            caja_x, caja_y, caja_w, caja_h,
            self.font_texto,
            (30,30,30),
            centrado=True
        )
        # Animación de dinos
        if time.time() - self.ultimo_cambio_dinos >= 3.0:
            self.dinos_actuales = random.sample(range(len(self.imagenes_dinos)), 3)
            self.ultimo_cambio_dinos = time.time()
        dino_positions = [(self.sx(200), self.sy(520)), (self.sx(400), self.sy(520)), (self.sx(600), self.sy(520))]
        animar_dinos(
            self.pantalla,
            [self.imagenes_dinos[idx] for idx in self.dinos_actuales],
            dino_positions,
            self.pantalla.get_width() / self.base_width,
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
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    nav_result = self.navbar.handle_event(event)
                    if nav_result is not None:
                        self.juego_base["nivel_actual"] = self.niveles[nav_result]
            
            # Fondo dinámico
            self.pantalla.blit(self.fondo, (0, 0))
            for estrella in self.estrellas:
                estrella.update(self.base_width, self.base_height)
                estrella.draw(self.pantalla)
            '''
            dibujar_fondo_animado(
                self.pantalla,
                self.pantalla.get_width(),
                self.pantalla.get_height(),
                self.fondo_thread,
                self.estrellas,
                self.fondo,
                self.estrellas
            )
            '''
            # Transición visual si aplica
            manejar_transicion(self.juego_base)
            # Barra de navegación con logo
            '''
            if self.logo:
                self.pantalla.blit(self.logo, (self.sx(20), self.sy(10)))
            self.navbar.draw(self.pantalla)
            '''
            # Pantalla según selección
            nivel = self.juego_base["nivel_actual"]
            if nivel == "Home":
                self.mostrar_home()
            elif nivel in ("Fácil", "Normal", "Difícil"):
                self.mostrar_juegos(nivel)
            elif nivel == "ChatBot":
                self.mostrar_chatbot()
            pygame.display.flip()
            self.clock.tick(60)

def run_menu_principal(pantalla, fondo, estrellas, images, sounds, config, fondo_thread=None):
    menu = MenuPrincipal(pantalla, fondo, estrellas, images, sounds, config, fondo_thread)
    menu.run()
