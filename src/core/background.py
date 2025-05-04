# background.py
"""
Módulo para lógica de fondo animado y gestión de estrellas.
"""
import pygame
import random
import math
from collections import defaultdict

class FondoAnimado:
    """
    Clase que gestiona el fondo pre-renderizado y las estrellas animadas.
    Permite redimensionamiento dinámico y es eficiente en el redibujado.
    """
    def __init__(self, ancho, alto, color_fondo1=(255, 250, 240), color_fondo2=(255, 235, 205), max_estrellas=20):
        self.color_fondo1 = color_fondo1
        self.color_fondo2 = color_fondo2
        self.max_estrellas = max_estrellas
        self._make_background(ancho, alto)
        self._make_estrellas(ancho, alto)

    def _make_background(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto
        self.fondo = pygame.Surface((ancho, alto))
        dibujar_gradiente(self.fondo, self.color_fondo1, self.color_fondo2, vertical=True)

    def _make_estrellas(self, ancho, alto):
        self.estrellas = crear_estrellas(ancho, alto, self.max_estrellas)

    def resize(self, ancho, alto):
        self._make_background(ancho, alto)
        self._make_estrellas(ancho, alto)

    def update(self):
        for estrella in self.estrellas:
            estrella.update(self.ancho, self.alto)

    def draw(self, surface):
        surface.blit(self.fondo, (0, 0))
        for estrella in self.estrellas:
            estrella.draw(surface)

# --- Utilidades y funciones auxiliares ---
def dibujar_gradiente(surf, color1, color2, vertical=True):
    width, height = surf.get_size()
    for i in range(height if vertical else width):
        factor = i / ((height - 1) if vertical else (width - 1))
        color = tuple(
            int(color1[j] + (color2[j] - color1[j]) * factor) for j in range(3)
        )
        if vertical:
            pygame.draw.line(surf, color, (0, i), (width, i))
        else:
            pygame.draw.line(surf, color, (i, 0), (i, height))

# --- Colocación eficiente de estrellas usando cuadrícula ---
def crear_estrellas_pantalla(ancho, alto, max_estrellas=20):
    area = ancho * alto
    num_estrellas = min(max(area // 30000, 6), max_estrellas)
    cell_size = 48  # Tamaño de celda para evitar solapamientos
    grid = defaultdict(list)
    estrellas = []
    intentos = 0
    max_intentos = num_estrellas * 30
    while len(estrellas) < num_estrellas and intentos < max_intentos:
        nueva = Estrella(ancho, alto)
        cell_x = int(nueva.x // cell_size)
        cell_y = int(nueva.y // cell_size)
        colision = False
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for e in grid[(cell_x+dx, cell_y+dy)]:
                    if nueva.colisiona_con(e):
                        colision = True
                        break
                if colision:
                    break
            if colision:
                break
        if not colision:
            estrellas.append(nueva)
            grid[(cell_x, cell_y)].append(nueva)
        intentos += 1
    return estrellas

class Estrella:
    def __init__(self, ancho, alto):
        self.radio = random.randint(16, 32)
        self.x = random.uniform(self.radio, ancho - self.radio)
        self.y = random.uniform(self.radio, alto - self.radio)
        self.color = random.choice([
            (255, 255, 255), (255, 255, 200), (255, 240, 180), (255, 235, 255)
        ])
        self.puntos = random.choice([5, 6, 7])
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(20, 80) / 60.0
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.base_radio = self.radio
        self.fase = random.uniform(0, 2 * math.pi)
        self.parpadeo_vel = random.uniform(1.5, 2.5)

    def update(self, ancho, alto):
        self.x += self.dx
        self.y += self.dy
        if self.x < self.radio or self.x > ancho - self.radio:
            self.dx *= -1
        if self.y < self.radio or self.y > alto - self.radio:
            self.dy *= -1
        self.fase += self.parpadeo_vel * 0.03
        self.radio = int(self.base_radio * (0.85 + 0.15 * math.sin(self.fase)))

    def draw(self, surface):
        dibujar_estrella(surface, self.color, (int(self.x), int(self.y)), self.radio, points=self.puntos)

    def colisiona_con(self, otra):
        dist = math.hypot(self.x - otra.x, self.y - otra.y)
        return dist < (self.radio + otra.radio)

def dibujar_estrella(surface, color, center, radius, points=5):
    angle = math.pi / points
    vertices = []
    for i in range(2 * points):
        r = radius if i % 2 == 0 else radius // 2
        theta = i * angle
        x = center[0] + int(r * math.sin(theta))
        y = center[1] - int(r * math.cos(theta))
        vertices.append((x, y))
    pygame.draw.polygon(surface, color, vertices)

# --- API retrocompatible ---
def crear_fondo(ancho, alto, color_fondo1=(255, 250, 240), color_fondo2=(255, 235, 205)):
    surf = pygame.Surface((ancho, alto))
    dibujar_gradiente(surf, color_fondo1, color_fondo2, vertical=True)
    return surf

def crear_estrellas(ancho, alto, max_estrellas=20):
    return crear_estrellas_pantalla(ancho, alto, max_estrellas)

def actualizar_estrellas(estrellas, ancho, alto):
    for estrella in estrellas:
        estrella.update(ancho, alto)
    return estrellas
