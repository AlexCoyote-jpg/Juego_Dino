import pygame
from ui.components.utils import dibujar_caja_texto
from ui.components.scroll import dibujar_barra_scroll

BUBBLE_PADDING = 14

# Renderizado de burbujas y chat

def draw_burbuja(pantalla, font, chat_x, chat_w, linea, color, bg, ali, y):
    text_surf = font.render(linea, True, color)
    text_rect = text_surf.get_rect()
    line_height = font.get_linesize()
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
    line_height = font.get_linesize() + max(8, int(font.get_linesize() * 0.25)) * 2
    chat_area_h = chat_h
    chat_clip_rect = pygame.Rect(chat_x, chat_y, chat_w - 20, chat_h)
    pantalla.set_clip(chat_clip_rect)
    y = chat_y + 10 - _scroll_offset
    thumb_rect = None
    for linea, color, bg, ali in _render_cache:
        if y + line_height < chat_y:
            y += line_height
            continue
        if y > chat_y + chat_h:
            break
        # Se asume que la función draw_burbuja está disponible en el contexto de BotScreen
        # Por lo tanto, el llamador debe pasar una función draw_burbuja adecuada si se requiere
        # Aquí solo se deja el renderizado de la burbuja como callback opcional
        if hasattr(render_chat, 'draw_burbuja_cb'):
            render_chat.draw_burbuja_cb(pantalla, linea, color, bg, ali, y)
        y += line_height
    pantalla.set_clip(None)
    if _total_chat_height > chat_area_h:
        barra_x = chat_x + chat_w - 18
        barra_y = chat_y
        barra_w = 16
        barra_h = chat_h
        thumb_h = max(30, int(barra_h * (chat_area_h / _total_chat_height)))
        max_scroll = _total_chat_height - chat_area_h
        scroll_offset = _scroll_offset
        thumb_y = barra_y + int(scroll_offset * (barra_h - thumb_h) / max_scroll) if max_scroll > 0 else barra_y
        thumb_rect = pygame.Rect(barra_x, thumb_y, barra_w, thumb_h)
        dibujar_barra_scroll(
            pantalla, barra_x, barra_y, barra_w, barra_h,
            scroll_offset, _total_chat_height, chat_area_h,
            color=(120, 180, 255), highlight=False, modern=True
        )
    _thumb_rect_ref[0] = thumb_rect
