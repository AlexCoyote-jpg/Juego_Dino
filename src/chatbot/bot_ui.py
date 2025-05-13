import pygame
import sys
import textwrap
import logging
from chatbot.Configs import LLAMA
from chatbot.Conexion import obtener_respuesta_async
from chatbot.voz import hablar, detener
from ui.components.utils import obtener_fuente, render_text_cached, Boton
from ui.components.scroll import ScrollManager, dibujar_barra_scroll
from ui.components.emoji import mostrar_alternativo_adaptativo
from chatbot.event_handlers import (
    hay_respuesta_bot,
    manejar_voz,
    procesar_mensaje_async,
    respuesta_callback,
    handle_key_event,
    handle_mouse_event,
    process_events
)
from core.scale.responsive_scaler_basic import ResponsiveScaler
from chatbot.chatbot_state import ChatbotStateManager

pygame.init()
pygame.mixer.init()

scaler = ResponsiveScaler(base_width=900, base_height=600)

_avatar_cache = {}

def set_render_area(width, height):
    scaler.update(width, height)

def get_visual_constants():
    current_width = scaler.current_width
    current_height = scaler.current_height
    return {
        "ANCHO": current_width,
        "ALTO": current_height,
        "FUENTE": pygame.font.SysFont("Segoe UI Emoji", scaler.scale_font_size(25)),
        "COLOR_FONDO": (248, 249, 250),
        "COLOR_TEXTO": (33, 37, 41),
        "COLOR_ENTRADA": (255, 255, 255),
        "COLOR_BOT": (240, 242, 245),
        "COLOR_USER": (0, 123, 255),
        "COLOR_USER_TEXT": (255, 255, 255),
        "COLOR_BOT_TEXT": (33, 37, 41),
        "LINE_HEIGHT": scaler.scale_y_value(32),
        "MAX_LINE_WIDTH": 60,
        "BORDER_RADIUS": scaler.scale_x_value(18),
        "MENSAJE_SOMBRA": scaler.scale_x_value(3),
        "SCROLL_WIDTH": scaler.scale_x_value(8),
        "SCROLL_MARGIN": scaler.scale_x_value(2),
    }

def get_avatar_surface(label, color):
    key = (label, color)
    if key in _avatar_cache:
        return _avatar_cache[key]

    size = scaler.scale_x_value(32)
    radius = size // 2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(surf, color, (radius, radius), radius)
    emoji = render_text_cached(label, scaler.scale_font_size(16), False, (255, 255, 255))
    surf.blit(emoji, emoji.get_rect(center=(radius, radius)))
    _avatar_cache[key] = surf
    return surf

state = {
    'entrada_usuario': "",
    'esperando_respuesta': False
}
historial = ChatbotStateManager(max_visible=15)

logging.basicConfig(level=logging.INFO)
scroll_manager = ScrollManager()

def get_botones():
    c = get_visual_constants()
    sx = scaler.scale_x_value
    sy = scaler.scale_y_value
    ANCHO, ALTO = c["ANCHO"], c["ALTO"]
    return [
        Boton(
            texto="",
            x=ANCHO - sx(210), y=ALTO - sy(55), ancho=sx(48), alto=sy(48),
            id="enviar",
            imagen=render_text_cached("📤", scaler.scale_font_size(40), False, (28, 28, 30)),
            imagen_pos="center",
            color_normal=(240, 240, 255),
            color_hover=(200, 220, 255),
            color_top=(180, 210, 255),
            color_bottom=(120, 170, 255),
            border_color=(180, 200, 255, 180),
            border_width=sx(2),
            border_radius=sx(30),
            estilo="apple",
            tooltip="Enviar mensaje",
            on_click=lambda: procesar_mensaje_async(state, historial, lambda r: respuesta_callback(r, historial, state))
        ),
        Boton(
            texto="",
            x=ANCHO - sx(160), y=ALTO - sy(55), ancho=sx(48), alto=sy(48),
            id="voz",
            imagen=render_text_cached("🔊", scaler.scale_font_size(40), False, (28, 28, 30)),
            imagen_pos="center",
            color_normal=(240, 255, 240),
            color_hover=(200, 255, 200),
            color_top=(180, 255, 210),
            color_bottom=(120, 170, 255),
            border_color=(180, 220, 180, 180),
            border_width=sx(2),
            border_radius=sx(18),
            estilo="apple",
            tooltip="Reproducir voz",
            on_click=lambda: manejar_voz(historial)
        ),
        Boton(
            texto="",
            x=ANCHO - sx(110), y=ALTO - sy(55), ancho=sx(48), alto=sy(48),
            id="limpiar",
            imagen=render_text_cached("🧹", scaler.scale_font_size(40), False, (28, 28, 30)),
            tooltip="Limpiar historial",
            estilo="apple",
            on_click=lambda: historial.clear()
        ),
    ]

def renderizar_historial(pantalla):
    c = get_visual_constants()
    sx, sy = scaler.scale_x_value, scaler.scale_y_value
    FUENTE = c["FUENTE"]
    LINE_HEIGHT, MAX_LINE_WIDTH = c["LINE_HEIGHT"], c["MAX_LINE_WIDTH"]
    BORDER_RADIUS = c["BORDER_RADIUS"]
    MENSAJE_SOMBRA = c["MENSAJE_SOMBRA"]
    SCROLL_WIDTH = c["SCROLL_WIDTH"]
    SCROLL_MARGIN = c["SCROLL_MARGIN"]
    ANCHO, ALTO = c["ANCHO"], c["ALTO"]

    margin_horiz = sx(20)
    spacing = sy(10)
    avatar_margin = sx(40)

    SCROLL_AREA = pygame.Rect(margin_horiz, sy(20), ANCHO - margin_horiz * 2 - SCROLL_WIDTH - SCROLL_MARGIN, int(ALTO * 0.7))
    mensajes = historial.all_messages if hasattr(historial, 'all_messages') else historial

    # --- Calcular altura de cada mensaje (para scroll pixel-perfect) ---
    alturas = []
    mensajes_renders = []
    for mensaje in mensajes:
        is_bot = mensaje.startswith("Bot: ")
        display_msg = ("🤖 " + mensaje[5:]) if is_bot else mensaje
        color, text_color = (c["COLOR_BOT"], c["COLOR_BOT_TEXT"]) if is_bot else (c["COLOR_USER"], c["COLOR_USER_TEXT"])
        avatar = get_avatar_surface("🤖" if is_bot else "👤", (120,120,220) if is_bot else (52,199,89))

        lineas = textwrap.wrap(display_msg, MAX_LINE_WIDTH)
        renders = [FUENTE.render(linea, True, text_color) for linea in lineas]
        total_height = len(renders) * (LINE_HEIGHT + sy(4)) - sy(4)
        max_width = max((r.get_width() for r in renders), default=0)
        padding = sx(12)
        msg_width, msg_height = max_width + padding * 2, total_height + padding
        alturas.append(msg_height + spacing)
        mensajes_renders.append((mensaje, is_bot, renders, color, text_color, avatar, msg_width, msg_height, padding))

    # Sincronizar alturas con ChatbotStateManager
    if hasattr(historial, 'set_mensajes_altos'):
        historial.set_mensajes_altos(alturas)

    # --- Scroll visual: obtener mensajes y offset según scroll_offset_px ---
    scroll_offset = int(getattr(historial, 'scroll_offset_px', 0))
    area_height = SCROLL_AREA.height
    visibles, offset_inicial = [], 0
    if hasattr(historial, 'get_visible_messages_by_scroll'):
        visibles, offset_inicial = historial.get_visible_messages_by_scroll(area_height)
    else:
        visibles = mensajes_renders
        offset_inicial = 0

    # --- Renderizar solo los mensajes visibles ---
    y_offset = offset_inicial
    surfaces = []
    for idx, (mensaje, alto) in enumerate(visibles):
        try:
            i = mensajes.index(mensaje)
            _, is_bot, renders, color, text_color, avatar, msg_width, msg_height, padding = mensajes_renders[i]
        except Exception:
            continue
        # Renderiza el avatar
        x = avatar_margin if is_bot else SCROLL_AREA.width - avatar.get_width()
        surfaces.append((avatar, 0 if is_bot else SCROLL_AREA.width - avatar.get_width(), y_offset + (msg_height - avatar.get_height()) // 2, avatar.get_height()))
        # Renderiza el mensaje con emojis y símbolos
        # Ajusta el tamaño mínimo y máximo de fuente usando el escalador ResponsiveScaler
        font_size_min = max(14, scaler.scale_font_size(18))
        font_size_max = max(20, scaler.scale_font_size(32))
        msg_surface = pygame.Surface((msg_width + MENSAJE_SOMBRA, msg_height + MENSAJE_SOMBRA), pygame.SRCALPHA)
        pygame.draw.rect(msg_surface, (0, 0, 0, 40), pygame.Rect(MENSAJE_SOMBRA, MENSAJE_SOMBRA, msg_width, msg_height), border_radius=BORDER_RADIUS)
        pygame.draw.rect(msg_surface, color, pygame.Rect(0, 0, msg_width, msg_height), border_radius=BORDER_RADIUS)
        mostrar_alternativo_adaptativo(
            msg_surface,
            ("🤖 " + mensaje[5:]) if is_bot else mensaje,
            padding,
            padding // 2,
            msg_width,
            msg_height,
            color=text_color,
            centrado=False,
            fuente_base=pygame.font.SysFont("Segoe UI Emoji", font_size_max)
        )
        x_msg = avatar_margin if is_bot else SCROLL_AREA.width - msg_surface.get_width() - avatar_margin
        surfaces.append((msg_surface, x_msg, y_offset, msg_height))
        y_offset += alto

    total_height = sum(alturas)
    scroll_surface = pygame.Surface((SCROLL_AREA.width, max(SCROLL_AREA.height, total_height)), pygame.SRCALPHA)
    for surface, x, y, _ in surfaces:
        scroll_surface.blit(surface, (x, y))

    pantalla.blit(scroll_surface, (SCROLL_AREA.x, SCROLL_AREA.y), area=pygame.Rect(0, 0, SCROLL_AREA.width, SCROLL_AREA.height))

    # --- Barra de scroll visual ---
    scroll_manager = globals().get('scroll_manager', None)
    if scroll_manager and hasattr(historial, 'get_total_height'):
        # Sincronizar scroll visual con scroll_offset_px
        max_scroll = max(0, historial.get_total_height() - area_height)
        historial.set_scroll_offset_px(scroll_manager.update(max_scroll))
        scroll_pos = historial.scroll_offset_px
    else:
        scroll_pos = 0
        max_scroll = 0
    dibujar_barra_scroll(
        pantalla,
        ANCHO - SCROLL_WIDTH - SCROLL_MARGIN,
        SCROLL_AREA.y,
        SCROLL_WIDTH,
        SCROLL_AREA.height,
        scroll_pos,
        total_height,
        SCROLL_AREA.height,
        color=(150, 180, 255),
        highlight=True,
        modern=True
    )
    return surfaces, total_height

def dibujar_entrada(pantalla):
    c = get_visual_constants()
    sx, sy = scaler.scale_x_value, scaler.scale_y_value
    x, y = sx(20), c["ALTO"] - sy(55)
    w, h = sx(700), sy(48)
    rect = pygame.Rect(x, y, w, h)
    color_fill = (230, 230, 235) if state['esperando_respuesta'] else c["COLOR_ENTRADA"]
    pygame.draw.rect(pantalla, color_fill, rect, border_radius=c["BORDER_RADIUS"])
    pygame.draw.rect(pantalla, (200, 200, 205), rect, 1, border_radius=c["BORDER_RADIUS"])
    pantalla.blit(c["FUENTE"].render(state['entrada_usuario'], True, c["COLOR_TEXTO"]), (rect.x + sx(12), rect.y + sy(12)))

def dibujar_botones(pantalla):
    botones = get_botones()
    for boton in botones:
        if boton.id == "voz" and not hay_respuesta_bot(historial):
            continue
        if boton.id in ("enviar", "voz") and state['esperando_respuesta']:
            boton.color_normal = (180, 180, 180)
            boton.color_hover = (180, 180, 180)
        else:
            boton.color_normal = (255, 255, 255)
            boton.color_hover = (230, 230, 235)
        boton.draw(pantalla)

__all__ = [
    "dibujar_entrada",
    "dibujar_botones",
    "renderizar_historial",
    "state",
    "historial",
    "scroll_manager",
    "get_visual_constants",
    "set_render_area",
    "get_botones"
]
