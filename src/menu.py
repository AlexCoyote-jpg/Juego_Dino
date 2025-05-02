# Ejemplo para menu.py
import pygame
import time
import random
import math
from pygame.locals import MOUSEBUTTONDOWN
from setup.navegacion import JuegoBase, BarraNavegacion

class MenuPrincipal:
    def __init__(self, pantalla, estrellas, fondo, estrellas_animadas, crear_fondo, crear_estrellas):
        self.juegos = [
            {"nombre": "Dino Suma/Resta", "imagen": "assets/imagenes/dino1.png"},
            {"nombre": "DinoCazador", "imagen": "assets/imagenes/dino2.png"},
            {"nombre": "DinoLógico", "imagen": "assets/imagenes/dino3.png"},
            {"nombre": "Memoria Jurásica", "imagen": "assets/imagenes/dino4.png"},
            {"nombre": "Rescate Jurásico", "imagen": "assets/imagenes/dino5.png"}
        ]
        self.pantalla = pantalla
        self.estrellas = estrellas
        self.fondo = fondo
        self.estrellas_animadas = estrellas_animadas
        self.crear_fondo = crear_fondo
        self.crear_estrellas = crear_estrellas

        self.juego_base = JuegoBase(self.pantalla, self.pantalla.get_width(), self.pantalla.get_height())
        self.barra_nav = BarraNavegacion(self.juego_base, niveles=["Home", "Fácil", "Normal", "Difícil", "ChatBot"])

        self.base_width = 900
        self.base_height = 700
        self.scale = self.pantalla.get_width() / self.base_width
        self.imagenes_dinos = [pygame.image.load(j["imagen"]) for j in self.juegos]
        self.dinos_actuales = [0, 1, 2]
        self.ultimo_cambio_dinos = time.time()
        self.dificultad_seleccionada = "Fácil"
        self.juego_seleccionado = None
        self.botones_juegos = []

    def sx(self, x):
        return int(x * self.pantalla.get_width() / self.base_width)
    def sy(self, y):
        return int(y * self.pantalla.get_height() / self.base_height)

    def mostrar_home(self):
        azul = (70, 130, 180)
        blanco_trans = (255, 255, 255, 220)
        # Título centrado
        JuegoBase.dibujar_caja_texto(self, self.sx(self.base_width//2 - 320), self.sy(110), self.sx(640), self.sy(60), azul)
        JuegoBase.mostrar_texto_adaptativo(
            self.pantalla,
            "¡Bienvenido a Jugando con Dino!",
            self.sx(self.base_width//2 - 320), self.sy(110),
            self.sx(640), self.sy(60),
            pygame.font.SysFont("Segoe UI", 54, bold=True),
            (255,255,255),
            centrado=True
        )
        # Caja de instrucciones centrada
        caja_x = self.sx(self.base_width//2 - 300)
        caja_y = self.sy(180)
        caja_w = self.sx(600)
        caja_h = self.sy(320)
        JuegoBase.dibujar_caja_texto(self, caja_x, caja_y, caja_w, caja_h, blanco_trans)
        instrucciones = (
            "¡Aprende matemáticas jugando con Dino y sus amigos!\n\n"
            "Selecciona una opción en la barra superior:\n\n"
            "- Fácil: Juegos para principiantes\n"
            "- Normal: Juegos para quienes ya conocen los conceptos básicos\n"
            "- Difícil: Juegos para expertos en matemáticas\n"
            "- ChatBot: Habla directamente con Dino y pregúntale sobre matemáticas\n\n"
            "¡Diviértete y aprende mientras juegas!"
        )
        # Instrucciones perfectamente centradas en la caja
        JuegoBase.mostrar_texto_adaptativo(
            self.pantalla,
            instrucciones,
            caja_x, caja_y,
            caja_w, caja_h,
            pygame.font.SysFont("Segoe UI", 28),
            (30,30,30),
            centrado=True
        )
        # Animación de dinosaurios
        if time.time() - self.ultimo_cambio_dinos >= 3.0:
            self.dinos_actuales = random.sample(range(len(self.imagenes_dinos)), min(3, len(self.imagenes_dinos))
            )
            self.ultimo_cambio_dinos = time.time()
        dino_positions = [(self.sx(200), self.sy(520)), (self.sx(400), self.sy(520)), (self.sx(600), self.sy(520))]
        tiempo_ms = pygame.time.get_ticks()
        self.juego_base.animar_dinos(self.pantalla, [self.imagenes_dinos[idx] for idx in self.dinos_actuales], dino_positions, self.scale, tiempo_ms)

    def dibujar_pantalla_juegos(self):
        azul = (70, 130, 180)
        hover = (100, 149, 237)
        gris = (245,245,245)
        sx = self.sx
        sy = self.sy
        JuegoBase.dibujar_caja_texto(self, sx(self.base_width//2 - 320), sy(110), sx(640), sy(60), azul)
        JuegoBase.mostrar_texto_adaptativo(
            self.pantalla,
            f"Juegos de nivel {self.dificultad_seleccionada}",
            sx(self.base_width//2 - 320), sy(110),
            sx(640), sy(60),
            pygame.font.SysFont("Segoe UI", 54, bold=True),
            (255,255,255),
            centrado=True
        )
        self.botones_juegos = []
        juegos_por_fila = 3
        espacio_h, espacio_v = sx(40), sy(40)
        ancho_juego, alto_juego = sx(170), sy(170)
        ancho_total = juegos_por_fila * ancho_juego + (juegos_por_fila - 1) * espacio_h
        inicio_x = (self.pantalla.get_width() - ancho_total) // 2
        for i, (juego, imagen) in enumerate(zip(self.juegos, self.imagenes_dinos)):
            x = inicio_x + (ancho_juego + espacio_h) * (i % juegos_por_fila)
            y = sy(200) + (alto_juego + espacio_v) * (i // juegos_por_fila)
            JuegoBase.dibujar_caja_texto(self, x, y, ancho_juego, alto_juego, gris, radius=22)
            img = pygame.transform.smoothscale(imagen, (ancho_juego-20, alto_juego-20))
            self.pantalla.blit(img, (x+10, y+10))
            boton_rect = self.juego_base.dibujar_boton(
                juego["nombre"], x, y + alto_juego + sy(12), ancho_juego, sy(48),
                azul, hover
            )
            self.botones_juegos.append((boton_rect, juego))

    def manejar_eventos_menu(self, evento):
        if evento.type == MOUSEBUTTONDOWN:
            for boton, juego in self.botones_juegos:
                if boton.collidepoint(evento.pos):
                    self.juego_seleccionado = juego
                    # Aquí podrías lanzar el juego real
                    # self.cargar_juego(juego)
                    return True
        return False

    def ejecutar(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    ancho, alto = event.w, event.h
                    self.pantalla = pygame.display.set_mode((ancho, alto), pygame.RESIZABLE)
                    self.fondo = self.crear_fondo(ancho, alto)
                    self.estrellas = self.crear_estrellas(ancho, alto)
                    self.juego_base.pantalla = self.pantalla
                    self.juego_base.ANCHO = ancho
                    self.juego_base.ALTO = alto
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for nivel, rect in self.barra_nav.botones.items():
                        if rect.collidepoint(event.pos):
                            self.juego_base.nivel_actual = nivel
                            break
                    if self.juego_base.nivel_actual in ["Fácil", "Normal", "Difícil"]:
                        self.manejar_eventos_menu(event)
            self.estrellas_animadas(self.pantalla, self.estrellas, self.fondo, self.pantalla.get_width(), self.pantalla.get_height())
            self.barra_nav.dibujar(x_inicial=self.sx(80), y=self.sy(30), ancho=self.sx(120), alto=self.sy(50), espacio=self.sx(30))
            if self.juego_base.nivel_actual == "Home":
                self.mostrar_home()
            elif self.juego_base.nivel_actual in ["Fácil", "Normal", "Difícil"]:
                self.dificultad_seleccionada = self.juego_base.nivel_actual
                self.dibujar_pantalla_juegos()
            pygame.display.flip()
            clock.tick(60)