# Clase base para juegos: define la interfaz y utilidades comunes para todos los juegos.

import pygame

class JuegoBase:
    def __init__(self, pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu):
        # --- Integración con el menú principal ---
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
        self.fuente_titulo = pygame.font.SysFont("Segoe UI", max(36, int(0.04 * pantalla.get_height())), bold=True)
        self.fuente = pygame.font.SysFont("Segoe UI", max(20, int(0.025 * pantalla.get_height())))
        self.reloj = pygame.time.Clock()
        self.navbar_height = 0
        self._update_navbar_height()

    def _update_navbar_height(self):
        if self.navbar and hasattr(self.navbar, "get_height"):
            self.navbar_height = self.navbar.get_height()
        elif self.navbar and hasattr(self.navbar, "height"):
            self.navbar_height = self.navbar.height
        else:
            self.navbar_height = 60  # Valor por defecto si no se puede obtener

    def cargar_imagenes(self):
        # Para ser sobrescrito por cada juego si necesita cargar imágenes
        pass

    def dibujar_fondo(self):
        # Dibuja el fondo respetando la barra de navegación (no dibuja sobre ella)
        if self.pantalla:
            self.pantalla.fill((255, 255, 255))
            # Si quieres un área reservada visual para la navbar, puedes dibujar una franja aquí si lo deseas

    def mostrar_texto(self, texto, x, y, fuente=None, centrado=False):
        fuente = fuente or self.fuente
        txt = fuente.render(texto, True, (30, 30, 30))
        rect = txt.get_rect()
        # Ajusta la posición Y para no solaparse con la barra de navegación
        y_ajustado = max(y, self.navbar_height + rect.height // 2 if centrado else self.navbar_height)
        if centrado:
            rect.center = (x, y_ajustado)
        else:
            rect.topleft = (x, y_ajustado)
        if self.pantalla:
            self.pantalla.blit(txt, rect)

    def mostrar_texto_multilinea(self, texto, x, y, fuente=None, centrado=False):
        fuente = fuente or self.fuente
        lineas = texto.split("\n")
        y_actual = max(y, self.navbar_height)
        for i, linea in enumerate(lineas):
            self.mostrar_texto(linea, x, y_actual + i * 36, fuente, centrado)

    def handle_event(self, evento):
        # Maneja el redimensionamiento de la ventana y actualiza la altura de la navbar
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            if self.return_to_menu:
                self.return_to_menu()
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
