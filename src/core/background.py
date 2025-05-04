# background.py
"""
Módulo para lógica de fondo animado y gestión de estrellas.
"""
import pygame
import random
import math
import threading

# Gradiente de fondo

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

def crear_fondo(ancho, alto, color_fondo1=(255, 250, 240), color_fondo2=(255, 235, 205)):
    surf = pygame.Surface((ancho, alto))
    dibujar_gradiente(surf, color_fondo1, color_fondo2, vertical=True)
    return surf

def crear_estrellas(ancho, alto, max_estrellas=20):
    area = ancho * alto
    num_estrellas = min(max(area // 30000, 6), max_estrellas)
    estrellas = []
    intentos = 0
    while len(estrellas) < num_estrellas and intentos < num_estrellas * 20:
        nueva = Estrella(ancho, alto)
        rect_nueva = pygame.Rect(nueva.x - nueva.radio, nueva.y - nueva.radio, nueva.radio * 2, nueva.radio * 2)
        if all(not rect_nueva.colliderect(
            pygame.Rect(e.x - e.radio, e.y - e.radio, e.radio * 2, e.radio * 2)
        ) for e in estrellas):
            estrellas.append(nueva)
        intentos += 1
    return estrellas

def actualizar_estrellas(estrellas, ancho, alto):
    for estrella in estrellas:
        estrella.update(ancho, alto)
    return estrellas

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

def dibujar_estrellas_animadas(pantalla, fondo, estrellas):
    pantalla.blit(fondo, (0, 0))
    for estrella in estrellas:
        area_rect = pygame.Rect(
            int(estrella.x - estrella.radio - 1),
            int(estrella.y - estrella.radio - 1),
            estrella.radio * 2 + 2,
            estrella.radio * 2 + 2
        )
        pantalla.blit(fondo, area_rect, area_rect)
        estrella.draw(pantalla)

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

# Opcional: animación de estrellas con hilos
class FondoAnimadoThread(threading.Thread):
    def __init__(self, estrellas, ancho, alto, update_interval=0.008):
        super().__init__()
        self.estrellas = estrellas
        self.ancho = ancho
        self.alto = alto
        self.update_interval = update_interval
        self._running = threading.Event()
        self._running.set()
        self._lock = threading.Lock()

    def run(self):
        while self._running.is_set():
            with self._lock:
                for estrella in self.estrellas:
                    estrella.update(self.ancho, self.alto)
            pygame.time.wait(int(self.update_interval * 1000))

    def stop(self):
        self._running.clear()

    def update_size(self, ancho, alto):
        with self._lock:
            self.ancho = ancho
            self.alto = alto

    def get_estrellas(self):
        with self._lock:
            return list(self.estrellas)

def estrellas_animadas_threadsafe(pantalla, fondo, estrellas_thread):
    pantalla.blit(fondo, (0, 0))
    estrellas = estrellas_thread.get_estrellas()
    for estrella in estrellas:
        area_rect = pygame.Rect(
            int(estrella.x - estrella.radio - 1),
            int(estrella.y - estrella.radio - 1),
            estrella.radio * 2 + 2,
            estrella.radio * 2 + 2
        )
        pantalla.blit(fondo, area_rect, area_rect)
        estrella.draw(pantalla)
