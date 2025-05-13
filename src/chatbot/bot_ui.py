import pygame
import sys
import textwrap
import logging
from chatbot.Configs import LLAMA
from chatbot.Conexion import obtener_respuesta_async
from chatbot.voz import hablar, detener
from ui.components.utils import obtener_fuente, render_text_cached, Boton
from ui.components.scroll import ScrollManager, dibujar_barra_scroll
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

pygame.init()
pygame.mixer.init()

scaler = ResponsiveScaler(base_width=900, base_height=600)

def set_render_area(width, height):
    scaler.update(width, height)

def get_visual_constants():
    current_width = scaler.current_width
    current_height = scaler.current_height
    return {
        "ANCHO": current_width,
        "ALTO": current_height,
        "FUENTE": pygame.font.SysFont("San Francisco", scaler.scale_font_size(22)),
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

state = {
    'entrada_usuario': "",
    'esperando_respuesta': False
}
historial = []

logging.basicConfig(level=logging.INFO)

scroll_manager = ScrollManager()

def get_botones():
    constants = get_visual_constants()
    ANCHO = constants["ANCHO"]
    ALTO = constants["ALTO"]
    sx = scaler.scale_x_value
    sy = scaler.scale_y_value
    return [
        Boton(
            texto="",
            x=ANCHO - sx(210), y=ALTO - sy(55), ancho=sx(48), alto=sy(48),
            id="enviar",
            imagen=render_text_cached("📤", scaler.scale_font_size(36), False, (28, 28, 30)),
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
            imagen=render_text_cached("🔊", scaler.scale_font_size(36), False, (28, 28, 30)),
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
            imagen=render_text_cached("🧹", scaler.scale_font_size(36), False, (28, 28, 30)),
            tooltip="Limpiar historial",
            estilo="apple",
            on_click=lambda: historial.clear()
        ),
        Boton(
            texto="",
            x=ANCHO - sx(60), y=ALTO - sy(55), ancho=sx(48), alto=sy(48),
            id="salir",
            imagen=render_text_cached("❌", scaler.scale_font_size(36), False, (220, 0, 0)),
            tooltip="Salir",
            estilo="apple",
            on_click=lambda: (pygame.quit(), sys.exit())
        ),
    ]

def renderizar_historial(pantalla):
    constants = get_visual_constants()
    ANCHO = constants["ANCHO"]
    ALTO = constants["ALTO"]
    FUENTE = constants["FUENTE"]
    COLOR_BOT = constants["COLOR_BOT"]
    COLOR_BOT_TEXT = constants["COLOR_BOT_TEXT"]
    COLOR_USER = constants["COLOR_USER"]
    COLOR_USER_TEXT = constants["COLOR_USER_TEXT"]
    LINE_HEIGHT = constants["LINE_HEIGHT"]
    MAX_LINE_WIDTH = constants["MAX_LINE_WIDTH"]
    BORDER_RADIUS = constants["BORDER_RADIUS"]
    MENSAJE_SOMBRA = constants["MENSAJE_SOMBRA"]
    SCROLL_WIDTH = constants["SCROLL_WIDTH"]
    SCROLL_MARGIN = constants["SCROLL_MARGIN"]

    # Precalcular valores de escalado que se usan repetidamente
    sx = scaler.scale_x_value
    sy = scaler.scale_y_value
    margin_horiz = sx(20)
    avatar_size = sx(32)
    avatar_radius = sx(16)
    avatar_margin = sx(40)
    spacing_between_msgs = sy(10)

    SCROLL_AREA = pygame.Rect(
        margin_horiz, sy(20),
        ANCHO - margin_horiz * 2 - SCROLL_WIDTH - SCROLL_MARGIN,
        int(ALTO * 0.7)
    )

    mensajes = historial[-100:]
    ancho = SCROLL_AREA.width
    y_offset = 0
    surfaces = []
    for mensaje in mensajes:
        if mensaje.startswith("Bot: "):
            color, text_color = COLOR_BOT, COLOR_BOT_TEXT
            display_msg = "🤖 " + mensaje[5:]
            align = "left"
            avatar = pygame.Surface((avatar_size, avatar_size), pygame.SRCALPHA)
            pygame.draw.circle(avatar, (120, 120, 220), (avatar_radius, avatar_radius), avatar_radius)
            avatar_text = render_text_cached("🤖", scaler.scale_font_size(16), False, (255, 255, 255))
            avatar.blit(avatar_text, avatar_text.get_rect(center=(avatar_radius, avatar_radius)))
        else:
            color, text_color = COLOR_USER, COLOR_USER_TEXT
            display_msg = mensaje
            align = "right"
            avatar = pygame.Surface((avatar_size, avatar_size), pygame.SRCALPHA)
            pygame.draw.circle(avatar, (52, 199, 89), (avatar_radius, avatar_radius), avatar_radius)
            avatar_text = render_text_cached("👤", scaler.scale_font_size(16), False, (255, 255, 255))
            avatar.blit(avatar_text, avatar_text.get_rect(center=(avatar_radius, avatar_radius)))

        lineas = textwrap.wrap(display_msg, MAX_LINE_WIDTH)
        renders = [FUENTE.render(linea, True, text_color) for linea in lineas]
        total_height = len(renders) * (LINE_HEIGHT + sy(4)) - sy(4)
        max_width = max((r.get_width() for r in renders), default=0)

        padding = sx(12)
        msg_width = max_width + padding * 2
        msg_height = total_height + padding
        fondo = pygame.Surface((msg_width + MENSAJE_SOMBRA, msg_height + MENSAJE_SOMBRA), pygame.SRCALPHA)

        shadow_rect = pygame.Rect(MENSAJE_SOMBRA, MENSAJE_SOMBRA, msg_width, msg_height)
        pygame.draw.rect(fondo, (0, 0, 0, 40), shadow_rect, border_radius=BORDER_RADIUS)
        msg_rect = pygame.Rect(0, 0, msg_width, msg_height)
        pygame.draw.rect(fondo, color, msg_rect, border_radius=BORDER_RADIUS)

        y_line = 0
        for r in renders:
            fondo.blit(r, (padding, y_line + padding // 2))
            y_line += LINE_HEIGHT + sy(4)

        x = avatar_margin if align == "left" else ancho - fondo.get_width() - avatar_margin

        surfaces.append((avatar, 0 if align == "left" else ancho - avatar_size, y_offset + (total_height - avatar_size) // 2, avatar_size))
        surfaces.append((fondo, x, y_offset, total_height + padding))
        y_offset += total_height + padding + spacing_between_msgs

    total_height = y_offset
    scroll_surface = pygame.Surface((ancho, max(SCROLL_AREA.height, total_height)), pygame.SRCALPHA)
    for surface, x, y, _ in surfaces:
        scroll_surface.blit(surface, (x, y))

    max_scroll = max(0, total_height - SCROLL_AREA.height)
    scroll_y = scroll_manager.update(max_scroll)

    pantalla.blit(scroll_surface, (SCROLL_AREA.x, SCROLL_AREA.y), area=pygame.Rect(0, scroll_y, ancho, SCROLL_AREA.height))

    dibujar_barra_scroll(
        pantalla,
        ANCHO - SCROLL_WIDTH - SCROLL_MARGIN,
        SCROLL_AREA.y,
        SCROLL_WIDTH,
        SCROLL_AREA.height,
        scroll_y,
        total_height,
        SCROLL_AREA.height,
        color=(150, 180, 255),
        highlight=True,
        modern=True
    )
    return surfaces, total_height

def dibujar_entrada(pantalla):
    constants = get_visual_constants()
    FUENTE = constants["FUENTE"]
    COLOR_TEXTO = constants["COLOR_TEXTO"]
    COLOR_ENTRADA = constants["COLOR_ENTRADA"]
    BORDER_RADIUS = constants["BORDER_RADIUS"]
    ALTO = constants["ALTO"]
    sx = scaler.scale_x_value
    sy = scaler.scale_y_value
    x, y = sx(20), ALTO - sy(55)
    width, height = sx(700), sy(48)
    entrada_rect = pygame.Rect(x, y, width, height)
    border_color = (200, 200, 205)
    color_entrada = (230, 230, 235) if state['esperando_respuesta'] else COLOR_ENTRADA
    pygame.draw.rect(pantalla, color_entrada, entrada_rect, border_radius=BORDER_RADIUS)
    pygame.draw.rect(pantalla, border_color, entrada_rect, 1, border_radius=BORDER_RADIUS)
    pantalla.blit(FUENTE.render(state['entrada_usuario'], True, COLOR_TEXTO),
                  (entrada_rect.x + sx(12), entrada_rect.y + sy(12)))

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