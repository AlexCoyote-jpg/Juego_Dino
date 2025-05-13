import pygame
import sys
import textwrap
import logging
from chatbot.Configs import LLAMA
from chatbot.Conexion import obtener_respuesta_async
from chatbot.voz import hablar, detener

# Configuración
pygame.init()
pygame.mixer.init()

# Constantes visuales
ANCHO, ALTO = 900, 600
FUENTE = pygame.font.SysFont("San Francisco", 22)
COLOR_FONDO = (242, 242, 247)
COLOR_TEXTO = (28, 28, 30)
COLOR_ENTRADA = (255, 255, 255)
COLOR_BOT = (229, 229, 234)
COLOR_USER = (52, 199, 89)
COLOR_USER_TEXT = (255, 255, 255)
COLOR_BOT_TEXT = (28, 28, 30)
LINE_HEIGHT = 32
MAX_LINE_WIDTH = 60
BORDER_RADIUS = 16

# Iconos
ICONOS = {
    "enviar": "assets/imagenes/user.png",
    "limpiar": "assets/imagenes/mapa.png",
    "salir": "assets/imagenes/roca.png",
    "voz": "assets/imagenes/scroll_down.png",
}

# Inicializar ventana
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("🤖 Chat Amigable")

# Variables globales
entrada_usuario = ""
historial = []
esperando_respuesta = False

logging.basicConfig(level=logging.INFO)

def cargar_iconos():
    """Carga y escala los iconos."""
    for nombre, ruta in ICONOS.items():
        icono = pygame.image.load(ruta).convert_alpha()
        ICONOS[nombre] = pygame.transform.smoothscale(icono, (40, 40))

cargar_iconos()

BOTONES = {
    "enviar": pygame.Rect(ANCHO - 160, ALTO - 55, 48, 48),
    "voz": pygame.Rect(ANCHO - 110, ALTO - 55, 48, 48),
    "limpiar": pygame.Rect(ANCHO - 60, ALTO - 55, 48, 48),
    "salir": pygame.Rect(ANCHO - 210, ALTO - 55, 48, 48),
}

def hay_respuesta_bot():
    return any(msg.startswith("Bot: ") for msg in historial)

def renderizar_historial():
    y_offset = 20
    for mensaje in historial[-20:]:
        if mensaje.startswith("Bot: "):
            color, text_color, prefix, align = COLOR_BOT, COLOR_BOT_TEXT, "🤖 ", "left"
        else:
            color, text_color, prefix, align = COLOR_USER, COLOR_USER_TEXT, "", "right"

        mensaje = prefix + mensaje[5:] if mensaje.startswith("Bot: ") else mensaje
        for linea in textwrap.wrap(mensaje, MAX_LINE_WIDTH):
            render = FUENTE.render(linea, True, text_color)
            fondo = pygame.Surface((render.get_width() + 24, LINE_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(fondo, color, fondo.get_rect(), border_radius=BORDER_RADIUS)
            x = 20 if align == "left" else ANCHO - fondo.get_width() - 20
            pantalla.blit(fondo, (x, y_offset))
            pantalla.blit(render, (x + 12, y_offset + 4))
            y_offset += LINE_HEIGHT + 4

def manejar_click(pos):
    detener()
    global entrada_usuario, historial, esperando_respuesta

    if esperando_respuesta:
        return

    if BOTONES["enviar"].collidepoint(pos):
        procesar_mensaje_async()
    elif BOTONES["voz"].collidepoint(pos):
        manejar_voz()
    elif BOTONES["limpiar"].collidepoint(pos):
        historial.clear()
    elif BOTONES["salir"].collidepoint(pos):
        pygame.quit()
        sys.exit()

def manejar_voz():
    sonido_voz = pygame.mixer.Sound("assets/sonidos/acierto.wav")
    sonido_voz.play()
    for msg in reversed(historial):
        if msg.startswith("Bot: "):
            hablar(msg[5:])
            break

def procesar_mensaje_async():
    global esperando_respuesta, entrada_usuario
    if entrada_usuario.strip() and not esperando_respuesta:
        esperando_respuesta = True
        historial.append("Tú: " + entrada_usuario.strip())
        entrada_usuario = ""
        obtener_respuesta_async(
            historial[-1][4:], LLAMA.model, LLAMA.api_key, callback=respuesta_callback
        )

def respuesta_callback(respuesta):
    global esperando_respuesta
    historial.append("Bot: " + respuesta)
    esperando_respuesta = False

def dibujar_entrada():
    color_entrada = (230, 230, 235) if esperando_respuesta else COLOR_ENTRADA
    entrada_rect = pygame.Rect(20, ALTO - 55, 700, 48)
    pygame.draw.rect(pantalla, color_entrada, entrada_rect, border_radius=BORDER_RADIUS)
    pygame.draw.rect(pantalla, (200, 200, 205), entrada_rect, 1, border_radius=BORDER_RADIUS)
    texto_render = FUENTE.render(entrada_usuario, True, COLOR_TEXTO)
    pantalla.blit(texto_render, (entrada_rect.x + 12, entrada_rect.y + 12))

def dibujar_botones():
    for nombre, rect in BOTONES.items():
        if nombre == "voz" and not hay_respuesta_bot():
            continue
        gris = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        gris.fill((180, 180, 180, 128)) if esperando_respuesta else None
        pygame.draw.rect(pantalla, (255, 255, 255), rect, border_radius=BORDER_RADIUS)
        pygame.draw.rect(pantalla, (200, 200, 205), rect, 1, border_radius=BORDER_RADIUS)
        pantalla.blit(ICONOS[nombre], rect.topleft)

def main():
    global entrada_usuario
    clock = pygame.time.Clock()

    while True:
        pantalla.fill(COLOR_FONDO)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                detener()
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    procesar_mensaje_async()
                elif evento.key == pygame.K_BACKSPACE:
                    entrada_usuario = entrada_usuario[:-1]
                elif evento.unicode.isprintable():
                    entrada_usuario += evento.unicode
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                manejar_click(evento.pos)

        renderizar_historial()
        dibujar_entrada()
        dibujar_botones()
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
