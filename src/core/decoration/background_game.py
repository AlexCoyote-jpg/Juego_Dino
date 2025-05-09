import pygame
import random
import math
from collections import deque
from ui.components.utils import get_gradient

PALETA = {
    "rojo_manzana": (255, 59, 48),
    "naranja_zanahoria": (255, 149, 0),
    "amarillo_sol": (255, 204, 0),
    "verde_manzana": (76, 217, 100),
    "verde_lima": (186, 255, 86),
    "azul_cielo": (90, 200, 250),
    "azul_oceano": (0, 122, 255),
    "morado_uva": (175, 82, 222),
    "rosa_chicle": (255, 45, 85),
    "rosa_pastel": (255, 156, 189),
    "turquesa": (52, 199, 186),
    "coral": (255, 127, 80),
    "lavanda": (186, 156, 255),
    "melocoton": (255, 190, 152),
    "menta": (152, 255, 179)
}

def generar_nube_surface_eficiente(radio_base, color):
    # Aumenta el tamaño para permitir elipses que sobresalgan y suavicen bordes
    ancho_nube = radio_base * 3.0
    alto_nube = radio_base * 1.8
    surf = pygame.Surface((int(ancho_nube), int(alto_nube)), pygame.SRCALPHA)

    # Elipses principales (centro y lados)
    elipses = [
        # (cx, cy, scale_x, scale_y)
        (radio_base * 1.0, radio_base * 1.0, 1.3, 1.0),   # centro
        (radio_base * 1.7, radio_base * 0.8, 1.1, 0.9),   # arriba derecha
        (radio_base * 0.5, radio_base * 1.1, 1.0, 0.8),   # izquierda
        (radio_base * 1.5, radio_base * 1.3, 1.2, 1.0),   # abajo derecha
        (radio_base * 2.0, radio_base * 1.1, 1.0, 0.8),   # extremo derecho
        (radio_base * 1.2, radio_base * 1.5, 1.0, 0.7),   # abajo centro
    ]

    for cx, cy, scale_x, scale_y in elipses:
        pygame.draw.ellipse(
            surf,
            color,
            pygame.Rect(
                cx - radio_base * scale_x / 2,
                cy - radio_base * scale_y / 2,
                radio_base * scale_x,
                radio_base * scale_y
            )
        )

    # Brillo suave en la parte superior
    pygame.draw.ellipse(
        surf,
        (255, 255, 255, 60),
        pygame.Rect(
            radio_base * 0.9,
            radio_base * 0.5,
            radio_base * 1.0,
            radio_base * 0.4
        )
    )
    surf = surf.convert_alpha()
    return surf, (radio_base * 0.7, radio_base * 0.7)

class FondoAnimado:
    def __init__(self, pantalla, ancho, alto, navbar_height=0, sx=lambda x: x, sy=lambda y: y):
        self.pantalla = pantalla
        self.ANCHO = ancho
        self.ALTO = alto
        self.navbar_height = navbar_height
        self.sx = sx
        self.sy = sy
        self.nubes = self.generar_nubes(6)
        self.burbujas = deque()
        self.tiempo_burbuja = 0
        self.fondo_actual = None
        self.fondo_cache = None

    def generar_nubes(self, cantidad):
        # Pre-render nubes para máxima eficiencia
        return [{
            'x': random.randint(0, self.ANCHO),
            'y': random.randint(self.navbar_height, self.ALTO // 3),
            'velocidad': random.uniform(0.15, 0.45),
            'surf': surf,
            'offset': offset,
            'w': surf.get_width()
        } for _ in range(cantidad)
          for surf, offset in [generar_nube_surface_eficiente(self.sx(60) * random.uniform(1.0, 1.7),
                                                              (255, 255, 255, random.randint(90, 140)))]
        ]

    def resize(self, ancho, alto):
        self.ANCHO = ancho
        self.ALTO = alto
        self.nubes = self.generar_nubes(len(self.nubes))
        self.fondo_cache = None

    def actualizar_nubes(self):
        for nube in self.nubes:
            nube['x'] += nube['velocidad']
            if nube['x'] > self.ANCHO + self.sx(120):
                nube['x'] = -nube['w']
                nube['y'] = random.randint(self.navbar_height, self.ALTO // 3)

    def dibujar_nubes(self):
        for nube in self.nubes:
            self.pantalla.blit(nube['surf'], (nube['x'] - nube['offset'][0], nube['y'] - nube['offset'][1]))

    def crear_burbuja(self, x=None, y=None):
        if x is None:
            x = random.randint(self.sx(50), self.ANCHO - self.sx(50))
        if y is None:
            y = self.ALTO + self.sy(20)
        color = random.choice([
            PALETA["azul_cielo"],
            PALETA["rosa_pastel"],
            PALETA["verde_lima"],
            PALETA["lavanda"],
            PALETA["turquesa"]
        ])
        self.burbujas.append({
            'x': x, 'y': y,
            'radio': random.randint(self.sy(14), self.sy(32)),
            'velocidad': random.uniform(0.4, 1.3),
            'color': (*color[:3], 90),
            'oscilacion': random.uniform(0.7, 1.7),
            'fase': random.uniform(0, 2 * math.pi)
        })

    def actualizar_burbujas(self):
        self.tiempo_burbuja -= 1
        if self.tiempo_burbuja <= 0:
            self.crear_burbuja()
            self.tiempo_burbuja = random.randint(36, 110)

        ticks = pygame.time.get_ticks()
        self.burbujas = deque([
            dict(burbuja,
                 y=burbuja['y'] - burbuja['velocidad'],
                 x=burbuja['x'] + math.sin(ticks / 520 + burbuja['fase']) * burbuja['oscilacion']
                 )
            for burbuja in self.burbujas
            if burbuja['y'] - burbuja['velocidad'] > -burbuja['radio']
        ])

    def dibujar_burbujas(self):
        for burbuja in self.burbujas:
            pygame.draw.circle(
                self.pantalla,
                burbuja['color'],
                (int(burbuja['x']), int(burbuja['y'])),
                burbuja['radio']
            )
            brillo_radio = burbuja['radio'] // 3
            brillo_offset = burbuja['radio'] // 4
            pygame.draw.circle(
                self.pantalla,
                (255, 255, 255, 120),
                (int(burbuja['x'] - brillo_offset), int(burbuja['y'] - brillo_offset)),
                brillo_radio
            )

    def dibujar_fondo(self, fondo=None):
        fondo_cambio = fondo != self.fondo_actual or self.fondo_cache is None
        if fondo_cambio:
            if isinstance(fondo, pygame.Surface):
                self.fondo_cache = pygame.transform.smoothscale(fondo, (self.ANCHO, self.ALTO))
            elif isinstance(fondo, tuple) and len(fondo) >= 3:
                self.fondo_cache = pygame.Surface((self.ANCHO, self.ALTO))
                self.fondo_cache.fill(fondo)
            elif isinstance(fondo, tuple) and len(fondo) == 2:
                self.fondo_cache = get_gradient(self.ANCHO, self.ALTO, (230, 245, 255), (255, 255, 255))
            else:
                self.fondo_cache = get_gradient(self.ANCHO, self.ALTO, (230, 245, 255), (255, 255, 255))
            self.fondo_actual = fondo

        self.pantalla.blit(self.fondo_cache, (0, 0))
        self.dibujar_nubes()
        self.dibujar_burbujas()
