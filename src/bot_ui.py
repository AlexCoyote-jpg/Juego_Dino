import pygame
import sys
import textwrap
import logging
from chatbot.Configs import LLAMA
from chatbot.Conexion import obtener_respuesta_async
from chatbot.voz import hablar, detener
from ui.components.utils import obtener_fuente, render_text_cached, Boton
from ui.components.scroll import ScrollManager, dibujar_barra_scroll
import event_handlers

# Inicialización
pygame.init()
pygame.mixer.init()

# Constantes visuales actualizadas
ANCHO, ALTO = 900, 600
FUENTE = pygame.font.SysFont("San Francisco", 22)
COLOR_FONDO = (248, 249, 250)  # Fondo más claro y moderno
COLOR_TEXTO = (33, 37, 41)
COLOR_ENTRADA = (255, 255, 255)
COLOR_BOT = (240, 242, 245)  # Gris más suave para mensajes del bot
COLOR_USER = (0, 123, 255)    # Azul moderno para mensajes del usuario
COLOR_USER_TEXT = (255, 255, 255)
COLOR_BOT_TEXT = (33, 37, 41)
LINE_HEIGHT = 32
MAX_LINE_WIDTH = 60
BORDER_RADIUS = 18  # Bordes más redondeados
MENSAJE_SOMBRA = 3  # Añadir efecto de sombra a los mensajes

# Inicializar ventana
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("🤖 Chat Amigable")

# Diccionario de estado
state = {
    'entrada_usuario': "",
    'esperando_respuesta': False
}
historial = []

logging.basicConfig(level=logging.INFO)

# Crear botones usando la clase Boton
botones = [
    Boton(
        texto="",
        x=ANCHO - 210, y=ALTO - 55, ancho=48, alto=48,
        id="enviar",
        imagen=render_text_cached("📤", 36, False, (28, 28, 30)),
        imagen_pos="center",
        color_normal=(240, 240, 255),
        color_hover=(200, 220, 255),
        color_top=(180, 210, 255),
        color_bottom=(120, 170, 255),
        border_color=(180, 200, 255, 180),
        border_width=2,
        border_radius=30,
        estilo="apple",
        tooltip="Enviar mensaje",
        on_click=lambda: procesar_mensaje_async()
    ),
    Boton(
        texto="",
        x=ANCHO - 160, y=ALTO - 55, ancho=48, alto=48,
        id="voz",
        imagen=render_text_cached("🔊", 36, False, (28, 28, 30)),
        imagen_pos="center",
        color_normal=(240, 255, 240),
        color_hover=(200, 255, 200),
        color_top=(180, 255, 210),
        color_bottom=(120, 255, 170),
        border_color=(180, 220, 180, 180),
        border_width=2,
        border_radius=18,
        estilo="apple",
        tooltip="Reproducir voz",
        on_click=lambda: manejar_voz()
    ),
    Boton(
        texto="",
        x=ANCHO - 110, y=ALTO - 55, ancho=48, alto=48,
        id="limpiar",
        imagen=render_text_cached("🧹", 36, False, (28, 28, 30)),
        tooltip="Limpiar historial",
        estilo="apple",
        on_click=lambda: historial.clear()
    ),
    Boton(
        texto="",
        x=ANCHO - 60, y=ALTO - 55, ancho=48, alto=48,
        id="salir",
        imagen=render_text_cached("❌", 36, False, (220, 0, 0)),
        tooltip="Salir",
        estilo="apple",
        on_click=lambda: (pygame.quit(), sys.exit())
    ),
]

# Pre-caché de superficies estáticas
entrada_rect = pygame.Rect(20, ALTO - 55, 700, 48)
border_color = (200, 200, 205)
# Superficie gris para botones cuando se espera respuesta (su tamaño es fijo)
grey_surface_cache = pygame.Surface((48, 48), pygame.SRCALPHA)
grey_surface_cache.fill((180, 180, 180, 128))

scroll_manager = ScrollManager()
SCROLL_AREA = pygame.Rect(20, 20, 700, 420)  # Ajusta tamaño y posición según tu UI

def hay_respuesta_bot():
    return any(msg.startswith("Bot: ") for msg in historial)

def renderizar_historial():
    # Renderiza todo el historial en una superficie aparte
    mensajes = historial[-100:]  # Limita para evitar superficies enormes
    ancho = SCROLL_AREA.width
    y_offset = 0
    surfaces = []
    for mensaje in mensajes:
        if mensaje.startswith("Bot: "):
            color, text_color = COLOR_BOT, COLOR_BOT_TEXT
            display_msg = "🤖 " + mensaje[5:]
            align = "left"
            # Añadir avatar para el bot (círculo con ícono)
            avatar = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.circle(avatar, (120, 120, 220), (16, 16), 16)
            avatar_text = render_text_cached("🤖", 16, False, (255, 255, 255))
            avatar.blit(avatar_text, avatar_text.get_rect(center=(16, 16)))
        else:
            color, text_color = COLOR_USER, COLOR_USER_TEXT
            display_msg = mensaje
            align = "right"
            # Avatar para el usuario
            avatar = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.circle(avatar, (52, 199, 89), (16, 16), 16)
            avatar_text = render_text_cached("👤", 16, False, (255, 255, 255))
            avatar.blit(avatar_text, avatar_text.get_rect(center=(16, 16)))
            
        # Procesar texto y calcular tamaño
        lineas = textwrap.wrap(display_msg, MAX_LINE_WIDTH)
        renders = [FUENTE.render(linea, True, text_color) for linea in lineas]
        total_height = len(renders) * (LINE_HEIGHT + 4) - 4
        max_width = max(r.get_width() for r in renders) if renders else 0
        
        # Crear superficie para el mensaje con sombra
        padding = 12  # Espacio alrededor del texto
        msg_width = max_width + padding * 2
        msg_height = total_height + padding
        fondo = pygame.Surface((msg_width + MENSAJE_SOMBRA, msg_height + MENSAJE_SOMBRA), pygame.SRCALPHA)
        
        # Dibujar sombra
        shadow_rect = pygame.Rect(MENSAJE_SOMBRA, MENSAJE_SOMBRA, msg_width, msg_height)
        pygame.draw.rect(fondo, (0, 0, 0, 40), shadow_rect, border_radius=BORDER_RADIUS)
        
        # Dibujar mensaje
        msg_rect = pygame.Rect(0, 0, msg_width, msg_height)
        pygame.draw.rect(fondo, color, msg_rect, border_radius=BORDER_RADIUS)
        
        # Añadir texto
        y_line = 0
        for r in renders:
            fondo.blit(r, (padding, y_line + padding//2))
            y_line += LINE_HEIGHT + 4
            
        # Calcular posición (con espacio para avatar)
        avatar_margin = 40
        if align == "left":
            x = avatar_margin
        else:
            x = ancho - fondo.get_width() - avatar_margin
            
        # Añadir avatar y mensaje a la lista
        surfaces.append((avatar, 
                        0 if align == "left" else ancho - 32, 
                        y_offset + (total_height - 32)//2, 32))
        surfaces.append((fondo, x, y_offset, total_height + padding))
        y_offset += total_height + padding + 10  # Espacio entre mensajes

    # Crea la superficie de scroll
    total_height = y_offset
    scroll_surface = pygame.Surface((ancho, max(SCROLL_AREA.height, total_height)), pygame.SRCALPHA)
    for fondo, x, y, _ in surfaces:
        scroll_surface.blit(fondo, (x, y))

    # Calcula el scroll actual
    max_scroll = max(0, total_height - SCROLL_AREA.height)
    scroll_y = scroll_manager.update(max_scroll)

    # Dibuja la parte visible
    pantalla.blit(scroll_surface, (SCROLL_AREA.x, SCROLL_AREA.y), area=pygame.Rect(0, scroll_y, ancho, SCROLL_AREA.height))

    # Dibuja la barra de scroll
    dibujar_barra_scroll(
        pantalla, SCROLL_AREA.x, SCROLL_AREA.y, SCROLL_AREA.width, SCROLL_AREA.height,
        scroll_y, total_height, SCROLL_AREA.height, color=(150, 180, 255), highlight=True
    )
    return surfaces, total_height

def manejar_click(pos):
    detener()
    if state['esperando_respuesta']:
        return
    for boton in botones:
        if boton.collidepoint(pos):
            boton.handle_event(
                pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': pos, 'button': 1})
            )
            break

def manejar_voz():
    sonido_voz = pygame.mixer.Sound("assets/sonidos/acierto.wav")
    sonido_voz.play()
    for msg in reversed(historial):
        if msg.startswith("Bot: "):
            hablar(msg[5:])
            break

def procesar_mensaje_async():
    mensaje = state['entrada_usuario'].strip()
    if mensaje and not state['esperando_respuesta']:
        state['esperando_respuesta'] = True
        historial.append("Tú: " + "🧑‍💬 " + mensaje)
        state['entrada_usuario'] = ""
        obtener_respuesta_async(mensaje, LLAMA.model, LLAMA.api_key, callback=respuesta_callback)

def respuesta_callback(respuesta):
    historial.append("Bot: " + respuesta)
    state['esperando_respuesta'] = False

def dibujar_entrada():
    color_entrada = (230, 230, 235) if state['esperando_respuesta'] else COLOR_ENTRADA
    pygame.draw.rect(pantalla, color_entrada, entrada_rect, border_radius=BORDER_RADIUS)
    pygame.draw.rect(pantalla, border_color, entrada_rect, 1, border_radius=BORDER_RADIUS)
    texto_render = FUENTE.render(state['entrada_usuario'], True, COLOR_TEXTO)
    pantalla.blit(texto_render, (entrada_rect.x + 12, entrada_rect.y + 12))

def dibujar_botones():
    for boton in botones:
        if boton.id == "voz" and not hay_respuesta_bot():
            continue
        if boton.id in ("enviar", "voz") and state['esperando_respuesta']:
            boton.color_normal = (180, 180, 180)
            boton.color_hover = (180, 180, 180)
        else:
            boton.color_normal = (255, 255, 255)
            boton.color_hover = (230, 230, 235)
        boton.draw(pantalla)

def main():
    clock = pygame.time.Clock()
    # Variables para efectos visuales
    fade_alpha = 0
    mensaje_animado = -1
    
    while True:
        pantalla.fill(COLOR_FONDO)
        
        # Renderizar fondo con patrón sutil
        for y in range(0, ALTO, 20):
            for x in range(0, ANCHO, 20):
                pygame.draw.circle(pantalla, (240, 240, 240), (x, y), 1)
        
        surfaces, total_height = renderizar_historial()
        max_scroll = max(0, total_height - SCROLL_AREA.height)
        bar_rect = pygame.Rect(SCROLL_AREA.right - 16, SCROLL_AREA.y, 16, SCROLL_AREA.height)
        
        # Efecto de transición cuando se envía un mensaje
        if state['esperando_respuesta']:
            fade_alpha = min(fade_alpha + 5, 30)
            fade_surf = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            fade_surf.fill((100, 100, 255, fade_alpha))
            pantalla.blit(fade_surf, (0, 0))
            
            # Animación de espera
            t = pygame.time.get_ticks() % 1000 / 1000
            r = 5 + 2 * abs(t - 0.5)  # Radio que varía entre 5 y 7
            pygame.draw.circle(pantalla, (52, 152, 219), 
                              (SCROLL_AREA.centerx, SCROLL_AREA.bottom + 20), r)
        else:
            fade_alpha = max(fade_alpha - 15, 0)
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                detener()
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                event_handlers.handle_key_event(evento, state, procesar_mensaje_async)
            elif evento.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                event_handlers.handle_mouse_event(evento, scroll_manager, max_scroll, SCROLL_AREA.y, SCROLL_AREA.height, bar_rect, botones, state)
        
        # Separador visual entre área de chat y entrada
        pygame.draw.line(pantalla, (220, 220, 220), 
                        (20, ALTO - 70), (ANCHO - 20, ALTO - 70), 2)
        
        dibujar_entrada()
        dibujar_botones()
        pygame.display.flip()
        clock.tick(60)  # Aumentar FPS para animaciones más suaves

if __name__ == "__main__":
    main()
