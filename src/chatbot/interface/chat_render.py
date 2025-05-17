import pygame
from ui.components.utils import dibujar_caja_texto
from ui.components.scroll import dibujar_barra_scroll
from ui.components.emoji_utils import render_texto_emojis

BUBBLE_PADDING = 14

# Renderizado de burbujas y chat

def draw_burbuja(pantalla, font, chat_x, chat_w, linea, color, bg, ali, y):
    text_surf, (w, h) = render_texto_emojis(linea, font.get_height(), color)
    text_rect = text_surf.get_rect()
    line_height = h
    vertical_padding = max(8, int(line_height * 0.25))
    bubble_rect = text_rect.inflate(BUBBLE_PADDING * 2, vertical_padding * 2)
    if ali == "der":
        bubble_rect.topright = (chat_x + chat_w - 10, y)
        text_rect.topright = (chat_x + chat_w - 10 - BUBBLE_PADDING, y + vertical_padding)
    else:
        bubble_rect.topleft = (chat_x + 10, y)
        text_rect.topleft = (chat_x + 10 + BUBBLE_PADDING, y + vertical_padding)
    pygame.draw.rect(pantalla, bg, bubble_rect, border_radius=12)
    pantalla.blit(text_surf, text_rect)

def render_chat(pantalla, chat_x, chat_y, chat_w, chat_h, font, _scroll_offset, _render_cache, _total_chat_height, _thumb_rect_ref):
    dibujar_caja_texto(pantalla, chat_x, chat_y, chat_w, chat_h,
                       (245, 245, 255, 220), radius=18)
    chat_area_h = chat_h
    chat_clip_rect = pygame.Rect(chat_x, chat_y, chat_w - 20, chat_h)
    pantalla.set_clip(chat_clip_rect)
    y = chat_y + 10 - _scroll_offset
    thumb_rect = None
    # Calcular alturas reales de cada burbuja
    bubble_heights = []
    for linea, color, bg, ali in _render_cache:
        _, (w, h) = render_texto_emojis(linea, font.get_height())
        vertical_padding = max(8, int(h * 0.25))
        bubble_heights.append(h + vertical_padding * 2)
    # Renderizar solo las burbujas visibles
    y_cursor = y
    for idx, (linea, color, bg, ali) in enumerate(_render_cache):
        bubble_h = bubble_heights[idx]
        if y_cursor + bubble_h < chat_y:
            y_cursor += bubble_h
            continue
        if y_cursor > chat_y + chat_h:
            break
        if hasattr(render_chat, 'draw_burbuja_cb'):
            render_chat.draw_burbuja_cb(pantalla, linea, color, bg, ali, y_cursor)
        else:
            draw_burbuja(pantalla, font, chat_x, chat_w, linea, color, bg, ali, y_cursor)
        y_cursor += bubble_h
    pantalla.set_clip(None)
    # Calcular altura total real del chat
    total_height = sum(bubble_heights)
    if _total_chat_height is not None:
        _total_chat_height = total_height
    if total_height > chat_area_h:
        barra_x = chat_x + chat_w - 18
        barra_y = chat_y
        barra_w = 16
        barra_h = chat_h
        thumb_h = max(30, int(barra_h * (chat_area_h / total_height)))
        max_scroll = total_height - chat_area_h
        scroll_offset = _scroll_offset
        thumb_y = barra_y + int(scroll_offset * (barra_h - thumb_h) / max_scroll) if max_scroll > 0 else barra_y
        thumb_rect = pygame.Rect(barra_x, thumb_y, barra_w, thumb_h)
        dibujar_barra_scroll(
            pantalla, barra_x, barra_y, barra_w, barra_h,
            scroll_offset, total_height, chat_area_h,
            color=(120, 180, 255), highlight=False, modern=True
        )
    _thumb_rect_ref[0] = thumb_rect
