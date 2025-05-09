import pygame
import random
import math
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

class FondoAnimado:
    def __init__(self, pantalla, ancho, alto, navbar_height=0, sx=lambda x: x, sy=lambda y: y):
        self.pantalla = pantalla
        self.ANCHO = ancho
        self.ALTO = alto
        self.navbar_height = navbar_height
        self.sx = sx
        self.sy = sy
        self.nubes = self.generar_nubes(5)
        self.burbujas = []
        self.tiempo_burbuja = 0

    def resize(self, ancho, alto):
        self.ANCHO = ancho
        self.ALTO = alto
        self.nubes = self.generar_nubes(len(self.nubes))

    def generar_nubes(self, cantidad):
        nubes = []
        for _ in range(cantidad):
            x = random.randint(0, self.ANCHO)
            y = random.randint(self.navbar_height, self.ALTO // 3)
            velocidad = random.uniform(0.2, 0.8)
            tamaño = random.uniform(0.7, 1.3)
            nubes.append({
                'x': x, 'y': y,
                'velocidad': velocidad,
                'tamaño': tamaño,
                'color': (255, 255, 255, random.randint(150, 200))
            })
        return nubes

    def actualizar_nubes(self):
        for nube in self.nubes:
            nube['x'] += nube['velocidad']
            if nube['x'] > self.ANCHO + self.sx(100):
                nube['x'] = -self.sx(100)
                nube['y'] = random.randint(self.navbar_height, self.ALTO // 3)

    def dibujar_nubes(self):
        for nube in self.nubes:
            radio_base = self.sx(40) * nube['tamaño']
            centros = [
                (nube['x'], nube['y']),
                (nube['x'] + radio_base * 0.7, nube['y'] - radio_base * 0.2),
                (nube['x'] + radio_base * 1.4, nube['y']),
                (nube['x'] + radio_base * 0.4, nube['y'] + radio_base * 0.3),
                (nube['x'] + radio_base, nube['y'] + radio_base * 0.4)
            ]
            ancho_nube = radio_base * 2.5
            alto_nube = radio_base * 1.5
            nube_surf = pygame.Surface((ancho_nube, alto_nube), pygame.SRCALPHA)
            for cx, cy in centros:
                rel_x = cx - (nube['x'] - radio_base * 0.5)
                rel_y = cy - (nube['y'] - radio_base * 0.5)
                pygame.draw.circle(nube_surf, nube['color'], (rel_x, rel_y), radio_base * 0.6)
            for i in range(10):
                pygame.draw.circle(nube_surf, (*nube['color'][:3], 30),
                                  (ancho_nube//2, alto_nube//2),
                                  radio_base * (0.8 + i*0.05))
            self.pantalla.blit(nube_surf, (nube['x'] - radio_base * 0.5, nube['y'] - radio_base * 0.5))

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
            'radio': random.randint(self.sy(10), self.sy(30)),
            'velocidad': random.uniform(0.5, 2.0),
            'color': (*color[:3], 100),
            'oscilacion': random.uniform(0.5, 1.5),
            'fase': random.uniform(0, 2 * math.pi)
        })

    def actualizar_burbujas(self):
        self.tiempo_burbuja -= 1
        if self.tiempo_burbuja <= 0:
            self.crear_burbuja()
            self.tiempo_burbuja = random.randint(30, 120)
        for burbuja in self.burbujas[:]:
            burbuja['y'] -= burbuja['velocidad']
            burbuja['x'] += math.sin(pygame.time.get_ticks() / 500 + burbuja['fase']) * burbuja['oscilacion']
            if burbuja['y'] < -burbuja['radio']:
                self.burbujas.remove(burbuja)

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
                (255, 255, 255, 150),
                (int(burbuja['x'] - brillo_offset), int(burbuja['y'] - brillo_offset)),
                brillo_radio
            )

    def dibujar_fondo(self, fondo=None):
        if fondo:
            if isinstance(fondo, pygame.Surface):
                fondo_escalado = pygame.transform.scale(fondo, (self.ANCHO, self.ALTO))
                self.pantalla.blit(fondo_escalado, (0, 0))
            elif isinstance(fondo, tuple) and len(fondo) >= 3:
                self.pantalla.fill(fondo)
            elif isinstance(fondo, tuple) and len(fondo) == 2:
                gradiente = get_gradient(self.ANCHO, self.ALTO, fondo[0], fondo[1])
                self.pantalla.blit(gradiente, (0, 0))
        else:
            gradiente = get_gradient(
                self.ANCHO, self.ALTO,
                (240, 248, 255),
                (230, 240, 250)
            )
            self.pantalla.blit(gradiente, (0, 0))
            self.dibujar_nubes()
            self.dibujar_burbujas()
