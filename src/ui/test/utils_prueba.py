import pygame
from ui.utils import Boton, ScrollManager, mostrar_texto_adaptativo, dibujar_barra_scroll

pygame.init()
ANCHO, ALTO = 500, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Prueba de utils.py")

# Crear muchos botones para probar el scroll
botones = []
for i in range(20):
    btn = Boton(
        f"Botón {i+1}",
        50, 60 + i * 60, 400, 50,
        color_normal=(220, 230, 245),
        color_hover=(180, 210, 255),
        estilo="apple"
    )
    botones.append(btn)

scroll_mgr = ScrollManager()
clock = pygame.time.Clock()
running = True

while running:
    pantalla.fill((240, 245, 255))
    max_scroll = max(0, len(botones) * 60 + 20 - (ALTO - 40))
    visible_height = ALTO - 40
    total_height = len(botones) * 60 + 20
    scroll_y = scroll_mgr.update(max_scroll, smooth=True)

    thumb_rect = dibujar_barra_scroll(
        pantalla, 0, 60, ANCHO, visible_height,
        scroll_y, total_height, visible_height,
        highlight=scroll_mgr.dragging
    )
    bar_rect = pygame.Rect(0 + ANCHO - 10, 60, 10, visible_height)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        scroll_mgr.handle_event(event, wheel_speed=40, thumb_rect=thumb_rect, max_scroll=max_scroll, h=visible_height, y=60, bar_rect=bar_rect)

    # Dibujar los botones desplazados
    for i, btn in enumerate(botones):
        btn.rect.y = 60 + i * 60 - scroll_y
        btn.y = btn.rect.y
        if -60 < btn.rect.y < ALTO:
            btn.draw(pantalla)

    # Dibujar texto adaptativo en la parte superior
    mostrar_texto_adaptativo(
        pantalla,
        "Prueba de ScrollManager y Boton\nDesplaza con la rueda del mouse",
        0, 0, ANCHO, 50,
        color=(30, 30, 80),
        centrado=True
    )

    pygame.display.flip()
    clock.tick(60)

pygame.quit()