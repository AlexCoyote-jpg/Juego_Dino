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
    El número de estrellas y el refresco se adaptan automáticamente.
    Se adapta en tiempo real al redimensionar la ventana.
    """
    clock = pygame.time.Clock()
    corriendo = True
    tiempo_cambio = 0
    intervalo_ms = 1000  # Cambia cada segundo

    ancho, alto = pantalla.get_size()

    while corriendo:
        redimensionar = False
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            elif evento.type == pygame.VIDEORESIZE:
                ancho, alto = evento.w, evento.h
                pantalla = pygame.display.set_mode((ancho, alto), pygame.RESIZABLE)
                redimensionar = True

        # Solo cambia las estrellas si ha pasado el intervalo o si se redimensionó
        tiempo_cambio += clock.get_time()
        if tiempo_cambio >= intervalo_ms or redimensionar:
            ancho, alto = pantalla.get_size()
            area = ancho * alto
            num_estrellas = min(max(area // 30000, 6), max_estrellas)
            dibujar_gradiente(pantalla, color_fondo1, color_fondo2, vertical=True)
            ocupados = []
            for _ in range(num_estrellas):
                for _ in range(10):
                    radio = random.randint(16, 32)
                    x = random.randint(radio, ancho - radio)
                    y = random.randint(radio, alto - radio)
                    rect = pygame.Rect(x - radio, y - radio, radio * 2, radio * 2)
                    if no_superpone(rect, ocupados):
                        color = random.choice([
                            (255, 255, 255), (255, 255, 200), (255, 240, 180), (255, 235, 255)
                        ])
                        dibujar_estrella(pantalla, color, (x, y), radio, points=random.choice([5,6,7]))
                        ocupados.append(rect)
                        break
            pygame.display.flip()
            tiempo_cambio = 0

        clock.tick()  # Se adapta automáticamente a los FPS

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