# Clase base para juegos: define la interfaz y utilidades comunes para todos los juegos.

import pygame

class JuegoBase:
    def __init__(self, nombre="Juego"):
        self.nombre = nombre
        self.pantalla = None
        self.nivel_actual = "Home"
        self.logo_img = None
        self.fuente_titulo = pygame.font.SysFont("Segoe UI", 48, bold=True)
        self.fuente = pygame.font.SysFont("Segoe UI", 28)
        self.ANCHO = 900
        self.ALTO = 700
        self.reloj = pygame.time.Clock()

    def cargar_imagenes(self):
        # Para ser sobrescrito por cada juego si necesita cargar imágenes
        pass

    def dibujar_fondo(self):
        # Para ser sobrescrito si el juego tiene fondo personalizado
        if self.pantalla:
            self.pantalla.fill((255, 255, 255))

    def mostrar_texto(self, texto, x, y, fuente=None, centrado=False):
        fuente = fuente or self.fuente
        txt = fuente.render(texto, True, (30, 30, 30))
        rect = txt.get_rect()
        if centrado:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        if self.pantalla:
            self.pantalla.blit(txt, rect)

    def mostrar_texto_multilinea(self, texto, x, y, fuente=None, centrado=False):
        fuente = fuente or self.fuente
        lineas = texto.split("\n")
        for i, linea in enumerate(lineas):
            self.mostrar_texto(linea, x, y + i * 36, fuente, centrado)

    def handle_event(self, evento):
        # Maneja el redimensionamiento de la ventana
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            if self.return_to_menu:
                self.return_to_menu()
        if evento.type == pygame.VIDEORESIZE:
            self.ANCHO, self.ALTO = evento.w, evento.h
            self.pantalla = pygame.display.set_mode((self.ANCHO, self.ALTO), pygame.RESIZABLE)
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
