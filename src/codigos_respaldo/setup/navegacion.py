# navegacion.py
"""
Módulo base funcional para lógica de navegación y utilidades de UI.
Refactorizado para integración directa en navigation_bar y menu_principal.
"""
import pygame
import math
import time
from setup.core import PALETA_COLORES

colores = PALETA_COLORES

def create_juego_base(pantalla, ancho, alto):
    return {
        "pantalla": pantalla,
        "ANCHO": ancho,
        "ALTO": alto,
        "botones_presionados": {},
        "animacion_nivel": 0,
        "nivel_actual": "Home",
        "fuente_botones": pygame.font.SysFont("Segoe UI", 32),
        "transicion_alpha": 0,
        "transicion_en_progreso": False,
        "transicion_color": (255, 255, 255),
        "transicion_velocidad": 18
    }

def actualizar_botones_presionados(juego_base):
    expirados = [k for k, v in juego_base["botones_presionados"].items() if v <= 1]
    for k in expirados:
        del juego_base["botones_presionados"][k]
    for k in juego_base["botones_presionados"]:
        juego_base["botones_presionados"][k] -= 1
    return juego_base

def iniciar_transicion(juego_base, color=(255,255,255), velocidad=18):
    juego_base["transicion_en_progreso"] = True
    juego_base["transicion_alpha"] = 0
    juego_base["transicion_color"] = color
    juego_base["transicion_velocidad"] = velocidad
    return juego_base

def manejar_transicion(juego_base):
    if juego_base["transicion_en_progreso"]:
        overlay = pygame.Surface((juego_base["ANCHO"], juego_base["ALTO"]), pygame.SRCALPHA)
        overlay.fill((*juego_base["transicion_color"], int(juego_base["transicion_alpha"])))
        juego_base["pantalla"].blit(overlay, (0, 0))
        juego_base["transicion_alpha"] += juego_base["transicion_velocidad"]
        if juego_base["transicion_alpha"] >= 255:
            juego_base["transicion_en_progreso"] = False
            juego_base["transicion_alpha"] = 0
    return juego_base

def dibujar_boton(pantalla, texto, x, y, ancho, alto, color_normal, color_hover, fuente=None):
    mouse_pos = pygame.mouse.get_pos()
    rect = pygame.Rect(x, y, ancho, alto)
    color = color_hover if rect.collidepoint(mouse_pos) else color_normal
    pygame.draw.rect(pantalla, color, rect, border_radius=10)
    if fuente:
        render = fuente.render(texto, True, (255,255,255))
        text_rect = render.get_rect(center=rect.center)
        pantalla.blit(render, text_rect)
    return rect

def animar_dinos(pantalla, imagenes_dinos, posiciones, escala, tiempo_ms):
    for i, (img, pos) in enumerate(zip(imagenes_dinos, posiciones)):
        escala_dino = escala * (1.0 + 0.1 * abs(math.sin((tiempo_ms + i*1000) / 800)))
        tamaño = int(100 * escala_dino)
        img_scaled = pygame.transform.smoothscale(img, (tamaño, tamaño))
        pos_x = pos[0] - (tamaño - int(100 * escala)) // 2
        pos_y = pos[1] - offset_y - (tamaño - int(100 * escala)) // 2
        pantalla.blit(img_scaled, (pos_x, pos_y))

def mostrar_texto_adaptativo(pantalla, texto, x, y, w, h, fuente_base=None, color=(30,30,30), centrado=False):
    fuente_base = fuente_base or pygame.font.SysFont("Segoe UI", 28)
    font_name = "Segoe UI"
    max_font_size = fuente_base.get_height()
    min_font_size = 12
    parrafos = texto.split('\n\n')
    font_size = max_font_size
    while font_size >= min_font_size:
        fuente = pygame.font.SysFont(font_name, font_size, bold=fuente_base.get_bold())
        lines = []
        for parrafo in parrafos:
            for raw_line in parrafo.split('\n'):
                words = raw_line.split()
                line = ""
                for word in words:
                    test_line = f"{line} {word}".strip()
                    if fuente.size(test_line)[0] <= w:
                        line = test_line
                    else:
                        lines.append(line)
                        line = word
                if line:
                    lines.append(line)
            if parrafo != parrafos[-1]:
                lines.append("")
        total_height = len(lines) * fuente.get_height()
        if total_height <= h:
            break
        font_size -= 1
    start_y = y + (h - total_height) // 2 if centrado else y
    for i, line in enumerate(lines):
        render = fuente.render(line, True, color)
        rect = render.get_rect()
        if centrado:
            rect.centerx = x + w // 2
        else:
        if centrado:
            rect.centerx = x + w // 2
        else:
            rect.x = x
        rect.y = start_y + i * fuente.get_height()
        pantalla.blit(render, rect)

def dibujar_caja_texto(pantalla, x, y, w, h, color, radius=18, texto=None, fuente=None, color_texto=(30,30,30)):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(s, color, (0, 0, w, h), border_radius=radius)
    pantalla.blit(s, (x, y))
    if texto:
        mostrar_texto_adaptativo(
            pantalla, texto, x, y, w, h, fuente, color_texto, centrado=True
        )

def dibujar_carta_generica(pantalla, carta, x, y, ancho, alto, fuente, color_texto, color_acierto, color_error, color_borde, img_reverso, color_borde_reverso):
    escala = 1.0 + carta.get('animacion', 0.0) * 0.1
    ancho_real = int(ancho * escala)
    alto_real = int(alto * escala)
    x_offset = (ancho_real - ancho) // 2
    y_offset = (alto_real - alto) // 2
    rect = pygame.Rect(x - x_offset, y - y_offset, ancho_real, alto_real)
    if carta.get('id') in carta.get('cartas_emparejadas', set()) or carta.get('volteada', False):
        color_fondo = (60, 60, 100) if carta.get('tipo') == 'operacion' else (100, 60, 60)
        dibujar_caja_texto(pantalla, rect.x, rect.y, rect.width, rect.height, color_fondo, radius=10)
        mostrar_texto_adaptativo(
            pantalla, carta.get('valor', ''), rect.x, rect.y, rect.width, rect.height, fuente, color_texto, centrado=True
        )
        if carta.get('bordes') == 'acierto':
            pygame.draw.rect(pantalla, color_acierto, rect, 4, border_radius=10)
        elif carta.get('bordes') == 'error':
            pygame.draw.rect(pantalla, color_error, rect, 4, border_radius=10)
        else:
            pygame.draw.rect(pantalla, color_borde, rect, 3, border_radius=10)
    else:
        img = pygame.transform.scale(img_reverso, (ancho_real, alto_real))
        pantalla.blit(img, rect)
        pygame.draw.rect(pantalla, color_borde_reverso, rect, 2, border_radius=10)
    return rect

def mostrar_victoria(pantalla, sx, sy, ancho, alto, fuente_titulo, fuente_texto, juego_base, carta_rects):
    ancho_panel = sx(500)
    alto_panel = sy(200)
    x_panel = (ancho - ancho_panel) // 2
    y_panel = (alto - alto_panel) // 2
    panel = get_surface(ancho_panel, alto_panel, alpha=True)
    for i in range(alto_panel):
        factor = i / alto_panel
        r = int(255 - factor * 50)
        g = int(250 - factor * 20)
        b = int(150 + factor * 50)
        pygame.draw.line(panel, (r, g, b, 240), (0, i), (ancho_panel, i))
    pantalla.blit(panel, (x_panel, y_panel))
    pygame.draw.rect(pantalla, (255, 215, 0), (x_panel, y_panel, ancho_panel, alto_panel), 4, border_radius=20)
    mostrar_texto_adaptativo(
        pantalla, "¡FELICIDADES! 🎉",
        x_panel, y_panel + sy(20), ancho_panel, sy(60),
        fuente_titulo, colores["AZUL_CIELO"], centrado=True
    )
    mostrar_texto_adaptativo(
        pantalla, "¡Has completado el nivel!",
        x_panel, y_panel + sy(80), ancho_panel, sy(40),
        fuente_texto, colores["GRIS_OSCURO"], centrado=True
    )
    boton_rect = dibujar_boton(
        pantalla,
        "¡Siguiente nivel! 👉",
        x_panel + (ancho_panel - sx(300)) // 2,
        y_panel + sy(130),
        sx(300), sy(50),
        colores["AZUL_CIELO"], colores["GRIS_OSCURO"]
    )
    carta_rects.append((boton_rect, {'id': 'siguiente'}))

def avanzar_nivel(juego):
    niveles = ["Básico", "Medio", "Avanzado"]
    idx = niveles.index(juego["nivel_actual"])
    juego["nivel_actual"] = niveles[(idx + 1) % len(niveles)]
    if "sonido_acierto" in juego and juego["sonido_acierto"] and not juego.get("silencio", False):
        juego["sonido_acierto"].play()
    if "inicializar_nivel" in juego:
        juego["inicializar_nivel"]()

def dibujar_fondo_animado(pantalla, ancho, alto, fondo_thread, estrellas_animadas, fondo, estrellas):
    try:
        if fondo_thread:
            estrellas_animadas(pantalla, fondo or get_surface(ancho, alto), fondo_thread)
        else:
            estrellas = estrellas or get_surface(ancho, alto, alpha=True)
            fondo = fondo or get_surface(ancho, alto)
            estrellas_animadas(pantalla, estrellas, fondo, ancho, alto)
    except Exception:
        pantalla.fill(colores["AZUL_CIELO"])

def sx(pantalla, x, base_width=900):
    return int(x * pantalla.get_width() / base_width)

def sy(pantalla, y, base_height=700):
    return int(y * pantalla.get_height() / base_height)

def get_surface(ancho, alto, alpha=False):
    if alpha:
        return pygame.Surface((ancho, alto), pygame.SRCALPHA)
    return pygame.Surface((ancho, alto))

class BarraNavegacion:
    def __init__(self, juego, niveles=None, logo_img=None):
        self.juego = juego
        self.niveles = niveles or ["Home", "Básico", "Medio", "Avanzado", "ChatBot"]
        self.botones = {}
        self.animacion_t0 = time.time()
        self.logo_img = logo_img

    def dibujar(self, x_inicial=200, y=30, ancho=100, alto=40, espacio=10):
        mouse_pos = pygame.mouse.get_pos()
        nivel_actual = self.juego["nivel_actual"]
        fuente = self.juego["fuente_botones"]
        t = pygame.time.get_ticks() / 1000.0

        x = x_inicial

        if self.logo_img:
            logo_size = alto
            logo_scaled = pygame.transform.smoothscale(self.logo_img, (logo_size, logo_size))
            logo_rect = logo_scaled.get_rect()
            logo_rect.x = x
            logo_rect.y = y
            self.juego["pantalla"].blit(logo_scaled, logo_rect)
            x += logo_size + espacio

        for i, nivel in enumerate(self.niveles):
            boton_ancho = ancho + 20 if nivel == "ChatBot" else ancho
            rect = pygame.Rect(x, y, boton_ancho, alto)
            self.botones[nivel] = rect

            if nivel == nivel_actual:
                color = colores["AZUL_CIELO"]
            elif rect.collidepoint(mouse_pos):
                color = colores["GRIS_OSCURO"]
            else:
                color = colores["GRIS_OSCURO"]

            pygame.draw.rect(self.juego["pantalla"], color, rect, border_radius=10)
            mostrar_texto_adaptativo(
                self.juego["pantalla"],
                nivel,
                rect.x, rect.y, rect.width, rect.height,
                fuente,
                colores["GRIS_OSCURO"],
                centrado=True
            )

            if i in self.juego["botones_presionados"] and self.juego["botones_presionados"][i] > 0:
                pygame.draw.rect(self.juego["pantalla"], colores["AZUL_CIELO"], rect, 0, border_radius=10)
                mostrar_texto_adaptativo(
                    self.juego["pantalla"],
                    nivel,
                    rect.x, rect.y, rect.width, rect.height,
                    fuente,
                    colores["GRIS_OSCURO"],
                    centrado=True
                )

            x += (boton_ancho + espacio)

    def manejar_eventos(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            for i, (nivel, boton) in enumerate(self.botones.items()):
                if boton.collidepoint(evento.pos):
                    if self.juego["nivel_actual"] != nivel:
                        self.juego["nivel_anterior"] = self.juego["nivel_actual"]
                        self.juego["nivel_actual"] = nivel
                        self.juego["animacion_nivel"] = 30
                        if "cambiar_nivel" in self.juego:
                            self.juego["cambiar_nivel"]()
                    self.juego["botones_presionados"][i] = 10
                    return True
        return False