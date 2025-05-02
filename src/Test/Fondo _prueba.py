import pygame
import random
import math


def dibujar_gradiente(surf, color1, color2, vertical=True):
    """Dibuja un gradiente suave en toda la superficie."""
    width, height = surf.get_size()
    if vertical:
        for y in range(height):
            factor = y / (height - 1)
            color = (
                int(color1[0] + (color2[0] - color1[0]) * factor),
                int(color1[1] + (color2[1] - color1[1]) * factor),
                int(color1[2] + (color2[2] - color1[2]) * factor)
            )
            pygame.draw.line(surf, color, (0, y), (width, y))
    else:
        for x in range(width):
            factor = x / (width - 1)
            color = (
                int(color1[0] + (color2[0] - color1[0]) * factor),
                int(color1[1] + (color2[1] - color1[1]) * factor),
                int(color1[2] + (color2[2] - color1[2]) * factor)
            )
            pygame.draw.line(surf, color, (x, 0), (x, height))

def dibujar_estrella(surface, color, center, radius, points=5):
    """Dibuja una estrella simple en la superficie."""
    angle = math.pi / points
    vertices = []
    for i in range(2 * points):
        r = radius if i % 2 == 0 else radius // 2
        theta = i * angle
        x = center[0] + int(r * math.sin(theta))
        y = center[1] - int(r * math.cos(theta))
        vertices.append((x, y))
    pygame.draw.polygon(surface, color, vertices)

def no_superpone(rect, ocupados):
    """Evita superposición de figuras."""
    for r in ocupados:
        if rect.colliderect(r):
            return False
    return True

def estrellas_animadas(
    pantalla,
    color_fondo1=(255, 250, 240),
    color_fondo2=(255, 235, 205),
    max_estrellas=20
):
    """
    Dibuja y anima estrellas infantiles en el fondo.
    Ahora las estrellas se mueven suavemente y parpadean.
    """
    clock = pygame.time.Clock()
    corriendo = True
    ancho, alto = pantalla.get_size()

    class Estrella:
        def __init__(self, ancho, alto):
            self.radio = random.randint(16, 32)
            self.x = random.uniform(self.radio, ancho - self.radio)
            self.y = random.uniform(self.radio, alto - self.radio)
            self.color = random.choice([
                (255, 255, 255), (255, 255, 200), (255, 240, 180), (255, 235, 255)
            ])
            self.puntos = random.choice([5, 6, 7])
            # Movimiento
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(10, 40) / 60.0  # píxeles por frame
            self.dx = math.cos(angle) * speed
            self.dy = math.sin(angle) * speed
            # Parpadeo
            self.base_radio = self.radio
            self.fase = random.uniform(0, 2 * math.pi)
            self.parpadeo_vel = random.uniform(1.5, 2.5)
        def update(self, ancho, alto):
            # Movimiento
            self.x += self.dx
            self.y += self.dy
            # Rebote en bordes
            if self.x < self.radio or self.x > ancho - self.radio:
                self.dx *= -1
            if self.y < self.radio or self.y > alto - self.radio:
                self.dy *= -1
            # Parpadeo
            self.fase += self.parpadeo_vel * 0.03
            self.radio = int(self.base_radio * (0.85 + 0.15 * math.sin(self.fase)))
        def draw(self, surface):
            dibujar_estrella(surface, self.color, (int(self.x), int(self.y)), self.radio, points=self.puntos)

    def crear_fondo(ancho, alto):
        surf = pygame.Surface((ancho, alto))
        dibujar_gradiente(surf, color_fondo1, color_fondo2, vertical=True)
        return surf

    def crear_estrellas(ancho, alto):
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

    fondo = crear_fondo(ancho, alto)
    estrellas = crear_estrellas(ancho, alto)

    while corriendo:
        redimensionar = False
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            elif evento.type == pygame.VIDEORESIZE:
                ancho, alto = evento.w, evento.h
                pantalla = pygame.display.set_mode((ancho, alto), pygame.RESIZABLE)
                fondo = crear_fondo(ancho, alto)
                estrellas = crear_estrellas(ancho, alto)
                redimensionar = True

        # Actualiza y dibuja
        frame = fondo.copy()
        for estrella in estrellas:
            estrella.update(ancho, alto)
            estrella.draw(frame)
        pantalla.blit(frame, (0, 0))
        pygame.display.flip()
        clock.tick(30)  # 30 FPS para animación suave

# Ejemplo de uso:
'''
if __name__ == "__main__":
    pygame.init()
    # Puedes cambiar el tamaño inicial aquí (ejemplo: 900x600)
    pantalla = pygame.display.set_mode((900, 600))  # O usa (0, 0) para ventana máxima sin bordes
    
    pygame.display.set_caption("Fondo Infantil Animado")
    # Detecta el tamaño real de la ventana en cualquier modo
    ancho, alto = pantalla.get_size()
    print("Tamaño real de la ventana:", ancho, "x", alto)
    estrellas_animadas(pantalla)
    pygame.quit()
'''