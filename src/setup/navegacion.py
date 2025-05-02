import pygame
import math
import time

# Colores globales
BLANCO = (255, 255, 255)
BOTON_NORMAL = (70, 130, 180)
BOTON_HOVER = (100, 149, 237)
BOTON_ACTIVO = (30, 144, 255)
TEXTO_CLARO = (255, 255, 255)
TEXTO_OSCURO = (30, 30, 30)

class JuegoBase:
    def __init__(self, pantalla, ancho, alto):
        self.pantalla = pantalla
        self.ANCHO = ancho
        self.ALTO = alto
        self.botones_presionados = {}
        self.animacion_nivel = 0
        self.nivel_actual = "Home"
        self.fuente_botones = pygame.font.SysFont("Segoe UI", 32)
        self.transicion_alpha = 0
        self.transicion_en_progreso = False
        self.transicion_color = (255, 255, 255)
        self.transicion_velocidad = 18  # mayor = más rápido

    def actualizar_botones_presionados(self):
        """Reduce el contador de botones presionados y elimina los expirados."""
        expirados = [k for k, v in self.botones_presionados.items() if v <= 1]
        for k in expirados:
            del self.botones_presionados[k]
        for k in self.botones_presionados:
            self.botones_presionados[k] -= 1

    def manejar_transicion(self):
        """
        Fundido visual suave configurable, cómodo y ligero.
        Llama a self.iniciar_transicion() para comenzar.
        """
        if self.transicion_en_progreso:
            overlay = pygame.Surface((self.ANCHO, self.ALTO), pygame.SRCALPHA)
            overlay.fill((*self.transicion_color, int(self.transicion_alpha)))
            self.pantalla.blit(overlay, (0, 0))
            self.transicion_alpha += self.transicion_velocidad
            if self.transicion_alpha >= 255:
                self.transicion_en_progreso = False
                self.transicion_alpha = 0

    def iniciar_transicion(self, color=(255,255,255), velocidad=18):
        self.transicion_en_progreso = True
        self.transicion_alpha = 0
        self.transicion_color = color
        self.transicion_velocidad = velocidad

    def dibujar_boton(self, texto, x, y, ancho, alto, color_normal, color_hover):
        """Dibuja un botón y acomoda el texto adaptativamente en su interior, retorna su rect."""
        mouse_pos = pygame.mouse.get_pos()
        rect = pygame.Rect(x, y, ancho, alto)
        color = color_hover if rect.collidepoint(mouse_pos) else color_normal
        pygame.draw.rect(self.pantalla, color, rect, border_radius=10)
        # Usar mostrar_texto_adaptativo para centrar y ajustar el texto dentro del botón
        JuegoBase.mostrar_texto_adaptativo(
            self.pantalla,
            texto,
            x, y,
            ancho, alto,
            self.fuente_botones,
            TEXTO_CLARO,
            centrado=True
        )
        return rect

    @staticmethod
    def animar_dinos(pantalla, imagenes_dinos, posiciones, escala, tiempo_ms):
        """Anima dinosaurios en posiciones dadas."""
        for i, (img, pos) in enumerate(zip(imagenes_dinos, posiciones)):
            offset_y = int(10 * escala * abs(math.sin((tiempo_ms + i*1000) / 500)))
            escala_dino = escala * (1.0 + 0.1 * abs(math.sin((tiempo_ms + i*1000) / 800)))
            tamaño = int(100 * escala_dino)
            img_scaled = pygame.transform.smoothscale(img, (tamaño, tamaño))
            pos_x = pos[0] - (tamaño - int(100 * escala)) // 2
            pos_y = pos[1] - offset_y - (tamaño - int(100 * escala)) // 2
            pantalla.blit(img_scaled, (pos_x, pos_y))

    @staticmethod
    def mostrar_logros_y_puntuaciones(pantalla, fuente, logros, puntuaciones, ancho):
        """Muestra logros y puntuaciones en la pantalla."""
        y = 20
        JuegoBase.mostrar_texto_static(pantalla, "Logros:", ancho - 200, y, fuente)
        for logro in sorted(logros):
            y += 30
            JuegoBase.mostrar_texto_static(pantalla, f"- {logro}", ancho - 200, y, fuente)
        y += 40
        JuegoBase.mostrar_texto_static(pantalla, "Puntuaciones:", ancho - 200, y, fuente)
        for juego, puntos in puntuaciones.items():
            y += 30
            JuegoBase.mostrar_texto_static(pantalla, f"{juego}: {puntos}", ancho - 200, y, fuente)

    @staticmethod
    def mostrar_texto_adaptativo(
        pantalla, texto, x, y, w, h, fuente_base=None, color=(30,30,30), centrado=False
    ):
        """
        Dibuja texto adaptativo (autoajusta tamaño y salto de línea) en un área dada.
        El texto queda perfectamente centrado vertical y horizontalmente si centrado=True.
        Soporta saltos de párrafo (\n\n) y saltos de línea (\n).
        Devuelve una lista de rects de las líneas dibujadas.
        """
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
        # Centrado vertical
        start_y = y + (h - total_height) // 2 if centrado else y
        rects = []
        for i, line in enumerate(lines):
            render = fuente.render(line, True, color)
            rect = render.get_rect()
            if centrado:
                rect.centerx = x + w // 2
            else:
                rect.x = x
            rect.y = start_y + i * fuente.get_height()
            pantalla.blit(render, rect)
            rects.append(rect)
        return rects

    @staticmethod
    def dibujar_caja_texto(self, x, y, w, h, color, radius=18):
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(s, color, (0, 0, w, h), border_radius=radius)
        self.pantalla.blit(s, (x, y))

class BarraNavegacion:
    def __init__(self, juego, niveles=None):
        self.juego = juego
        self.niveles = niveles or ["Home", "Básico", "Medio", "Avanzado", "ChatBot"]
        self.botones = {}
        self.animacion_t0 = time.time()

    def dibujar(self, x_inicial=200, y=30, ancho=100, alto=40, espacio=10):
        """Dibuja la barra de navegación con animación sutil en el texto activo."""
        x = x_inicial
        mouse_pos = pygame.mouse.get_pos()
        nivel_actual = self.juego.nivel_actual
        fuente = self.juego.fuente_botones
        t = pygame.time.get_ticks() / 1000.0  # segundos

        for i, nivel in enumerate(self.niveles):
            boton_ancho = ancho + 20 if nivel == "ChatBot" else ancho
            rect = pygame.Rect(x, y, boton_ancho, alto)
            self.botones[nivel] = rect

            # Determina color según estado
            if nivel == nivel_actual:
                color = BOTON_ACTIVO
            elif rect.collidepoint(mouse_pos):
                color = BOTON_HOVER
            else:
                color = BOTON_NORMAL

            pygame.draw.rect(self.juego.pantalla, color, rect, border_radius=10)
            texto_render = fuente.render(nivel, True, TEXTO_CLARO)
            texto_rect = texto_render.get_rect(center=rect.center)

            # Animación sutil para el texto activo (bouncing vertical)
            if nivel == nivel_actual:
                offset = int(4 * math.sin(t * 4))  # rápido pero sutil
                texto_rect.y += offset

            self.juego.pantalla.blit(texto_render, texto_rect)

            # Efecto de presionado (opcional, si se usa)
            if i in self.juego.botones_presionados and self.juego.botones_presionados[i] > 0:
                pygame.draw.rect(self.juego.pantalla, BOTON_ACTIVO, rect, 0, border_radius=10)
                self.juego.pantalla.blit(texto_render, texto_rect)

            x += (boton_ancho + espacio)