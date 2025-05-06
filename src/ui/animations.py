import pygame
import math

scaled_imgs_cache = {}  # Cache global para imágenes escaladas
hover_anim_states = {}  # Estado de hover por índice (0.0 a 1.0)

def get_scaled_image(img, size):
    if img is None:
        return None
    key = (id(img), size)
    if key not in scaled_imgs_cache:
        scaled_imgs_cache[key] = pygame.transform.smoothscale(img, (size, size))
    return scaled_imgs_cache[key]

def actualizar_hover_state(idx, is_hover, velocidad=0.1):
    state = hover_anim_states.get(idx, 0.0)
    state += velocidad if is_hover else -velocidad
    state = max(0.0, min(1.0, state))
    hover_anim_states[idx] = state
    return state

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

def renderizar_celda(caja, juego, recursos, fuente, x, y, tam, color, radio):
    from ui.utils import dibujar_caja_texto
    dibujar_caja_texto(caja, x, y, tam, tam, color=color, radius=radio)
    elementos(caja, juego, recursos, x, y, tam, fuente)

def animar_dinos(pantalla, imagenes_dinos, posiciones, escala, tiempo_ms, velocidad=1.0):
    """Versión mejorada con más parámetros de control y animaciones más suaves."""
    for i, (img_key, pos) in enumerate(zip(imagenes_dinos, posiciones)):
        # Parámetros de animación personalizados por dino
        fase = (tiempo_ms + i * 1000) / 500
        fase_escala = (tiempo_ms + i * 1000) / 800
        
        # Movimiento vertical más suave con easing
        t = abs(math.sin(fase * velocidad))
        t = t * t * (3 - 2 * t)  # Función de easing
        offset_y = int(10 * escala * t)
        
        # Escala con rebote suave
        t_escala = abs(math.sin(fase_escala * velocidad))
        t_escala = t_escala * t_escala * (3 - 2 * t_escala)
        escala_dino = escala * (1.0 + 0.1 * t_escala)
        
        # Calcular tamaños y posiciones
        tamaño_base = int(100 * escala)
        tamaño = int(100 * escala_dino)
        
        # Obtener imagen
        img = img_key  # Ahora img_key es directamente el objeto de imagen
        
        # Obtener imagen escalada
        img_scaled = get_scaled_image(img, tamaño)
        
        if img_scaled:
            # Calcular posición con centrado
            pos_x = pos[0] - (tamaño - tamaño_base) // 2
            pos_y = pos[1] - offset_y - (tamaño - tamaño_base) // 2
            
            # Añadir sombra debajo del dino
            sombra_size = int(tamaño * 0.8)
            sombra = get_surface(sombra_size, sombra_size // 3, alpha=True)
            pygame.draw.ellipse(sombra, (0, 0, 0, 80 - int(40 * t)), sombra.get_rect())
            sombra_x = pos_x + (tamaño - sombra_size) // 2
            sombra_y = pos[1] + tamaño_base - sombra_size // 3
            pantalla.blit(sombra, (sombra_x, sombra_y))
            
            # Dibujar el dino
            pantalla.blit(img_scaled, (pos_x, pos_y))

def dibujar_caja_juegos(surface, x, y, w, h, juegos, recursos,
                         color=(255, 255, 255), alpha=0, radius=0,
                         margen=24, tam_caja=120, fuente=None, on_hover=None,
                         num_cols=3, num_rows=2):

    caja = get_surface(w, h, alpha=alpha > 0)
    caja.fill((*color, alpha) if alpha > 0 else color)
    pygame.draw.rect(caja, color, caja.get_rect(), border_radius=radius)

    tam_caja_w = (w - (num_cols + 1) * margen) // num_cols
    tam_caja_h = (h - (num_rows + 1) * margen) // num_rows
    tam_caja = min(tam_caja_w, tam_caja_h)

    cols = min(num_cols, len(juegos))
    rows = min(num_rows, math.ceil(len(juegos) / cols))
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

    for idx, juego in enumerate(juegos[:max_juegos]):
        col = idx % cols
        row = idx // cols
        cx = offset_x + col * (tam_caja + margen)
        cy = offset_y + row * (tam_caja + margen)
        rect = pygame.Rect(cx, cy, tam_caja, tam_caja)
        abs_rect = pygame.Rect(x + cx, y + cy, tam_caja, tam_caja)
        rects.append(abs_rect)

        is_hover = rect.collidepoint((mouse_rel_x, mouse_rel_y))
        state = actualizar_hover_state(idx, is_hover)

        if state > 0:
            scale = 1.0 + 0.2 * state
            render_size = int(tam_caja * scale)
            render_cx = cx - (render_size - tam_caja) // 2
            render_cy = cy - (render_size - tam_caja) // 2
            radio = 18 if state > 0.9 else 16
            renderizar_celda(caja, juego, recursos, fuente, render_cx, render_cy, render_size, (200, 220, 255), radio)
            if is_hover and on_hover:
                on_hover(idx, abs_rect)
        else:
            renderizar_celda(caja, juego, recursos, fuente, cx, cy, tam_caja, (230, 240, 255), 16)

    surface.blit(caja, (x, y))
    return rects
