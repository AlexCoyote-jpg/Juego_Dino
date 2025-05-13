import pygame
from chatbot.voz import detener

def handle_key_event(event, state, procesar_mensaje_async):
    # Actualiza el 'entrada_usuario' o invoca el envío del mensaje
    if event.key == pygame.K_RETURN:
        procesar_mensaje_async()
    elif event.key == pygame.K_BACKSPACE:
        state['entrada_usuario'] = state['entrada_usuario'][:-1]
    elif event.unicode.isprintable():
        state['entrada_usuario'] += event.unicode

def manejar_click(pos, botones, state):
    detener()
    if state['esperando_respuesta']:
        return
    for boton in botones:
        if boton.collidepoint(pos):
            boton.handle_event(
                pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': pos, 'button': 1})
            )
            break

def handle_mouse_event(event, scroll_manager, max_scroll, area_y, area_height, bar_rect, botones, state):
    if event.type == pygame.MOUSEBUTTONDOWN:
        manejar_click(event.pos, botones, state)
    scroll_manager.handle_event(
        event,
        wheel_speed=40,
        thumb_rect=None,  # Se podría calcular dinámicamente si se necesita
        max_scroll=max_scroll,
        h=area_height,
        y=area_y,
        bar_rect=bar_rect
    )
