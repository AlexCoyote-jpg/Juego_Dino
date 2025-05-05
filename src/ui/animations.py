import pygame
import math

scaled_imgs_cache = {}  # Cache global para imágenes escaladas
hover_anim_states = {}  # Estado de hover por índice (0.0 a 1.0)


def get_scaled_image(img, size):
    key = (id(img), size)
    if key not in scaled_imgs_cache:
        scaled_imgs_cache[key] = pygame.transform.smoothscale(img, (size, size))
    return scaled_imgs_cache[key]

def animar_dinos(pantalla, imagenes_dinos, posiciones, escala, tiempo_ms):
    for i, (img, pos) in enumerate(zip(imagenes_dinos, posiciones)):
        offset_y = int(10 * escala * abs(math.sin((tiempo_ms + i * 1000) / 500)))
        escala_dino = escala * (1.0 + 0.1 * abs(math.sin((tiempo_ms + i * 1000) / 800)))
        tamaño_base = int(100 * escala)
        tamaño = int(100 * escala_dino)
        img_scaled = get_scaled_image(img, tamaño)
        pos_x = pos[0] - (tamaño - tamaño_base) // 2
        pos_y = pos[1] - offset_y - (tamaño - tamaño_base) // 2
        pantalla.blit(img_scaled, (pos_x, pos_y))

def get_surface(ancho, alto, alpha=False):
    flags = pygame.SRCALPHA if alpha else 0
    return pygame.Surface((ancho, alto), flags)

def elementos(caja, juego, recursos, cx, cy, tam_caja, fuente):
    img = recursos.get(juego["imagen"])
    if img:
        padding = 16
        img_w = img_h = tam_caja - 2 * padding
        img_scaled = get_scaled_image(img, img_w)
        img_x = cx + (tam_caja - img_w) // 2
        img_y = cy + padding
        caja.blit(img_scaled, (img_x, img_y))
    from ui.utils import mostrar_texto_adaptativo
    mostrar_texto_adaptativo(
        caja,
        juego["nombre"],
        cx + 4, cy + tam_caja - 36,
        tam_caja - 8, 32,
        fuente,
        (30, 30, 60),
        centrado=True
    )

def dibujar_caja_juegos(surface, x, y, w, h, juegos, recursos,
                         color=(255, 255, 255), alpha=0, radius=0,
                         margen=20, tam_caja=120, fuente=None, on_hover=None):
    caja = get_surface(w, h, alpha=alpha > 0)
    caja.fill((*color, alpha) if alpha > 0 else color)
    pygame.draw.rect(caja, color, caja.get_rect(), border_radius=radius)

    num_cols = 3
    num_rows = 2
    margen = 24
    tam_caja_w = (w - (num_cols + 1) * margen) // num_cols
    tam_caja_h = (h - (num_rows + 1) * margen) // num_rows
    tam_caja = min(tam_caja_w, tam_caja_h)

    cols = max(1, (w + margen) // (tam_caja + margen))
    cols = min(cols, len(juegos))
    rows = max(1, math.ceil(len(juegos) / cols))

    max_juegos = min(cols * rows, len(juegos))

    total_w = cols * tam_caja + (cols - 1) * margen
    total_h = rows * tam_caja + (rows - 1) * margen
    offset_x = max(0, (w - total_w) // 2)
    offset_y = max(0, (h - total_h) // 2)

    if fuente is None:
        fuente = pygame.font.SysFont("Segoe UI", 22, bold=True)

    rects = []
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_rel_x, mouse_rel_y = mouse_x - x, mouse_y - y

    from ui.utils import dibujar_caja_texto

    for idx, juego in enumerate(juegos[:max_juegos]):
        col = idx % cols
        row = idx // cols
        cx = offset_x + col * (tam_caja + margen)
        cy = offset_y + row * (tam_caja + margen)
        rect = pygame.Rect(cx, cy, tam_caja, tam_caja)
        abs_rect = pygame.Rect(x + cx, y + cy, tam_caja, tam_caja)
        rects.append(abs_rect)

        is_hover = rect.collidepoint((mouse_rel_x, mouse_rel_y))

        # Interpolación suave para hover (entre 0 y 1)
        state = hover_anim_states.get(idx, 0.0)
        state += 0.1 if is_hover else -0.1
        state = max(0.0, min(1.0, state))
        hover_anim_states[idx] = state

        scale = 1.0 + 0.2 * state
        render_size = int(tam_caja * scale)
        render_cx = cx - (render_size - tam_caja) // 2
        render_cy = cy - (render_size - tam_caja) // 2

        if state > 0:
            color_hover = (200, 220, 255)
            radio = 18 if state > 0.9 else 16
            dibujar_caja_texto(caja, render_cx, render_cy, render_size, render_size,
                               color=color_hover, radius=radio)
            elementos(caja, juego, recursos, render_cx, render_cy, render_size, fuente)
            if is_hover and on_hover:
                on_hover(idx, abs_rect)
        else:
            dibujar_caja_texto(caja, cx, cy, tam_caja, tam_caja,
                               color=(230, 240, 255), radius=16)
            elementos(caja, juego, recursos, cx, cy, tam_caja, fuente)

    surface.blit(caja, (x, y))
    return rects
