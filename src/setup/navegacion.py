import pygame

BLANCO = (255, 255, 255)
BOTON_NORMAL = (70, 130, 180)
BOTON_HOVER = (100, 149, 237)
BOTON_ACTIVO = (30, 144, 255)
TEXTO_CLARO = (255, 255, 255)

class JuegoBase:
    def __init__(self, pantalla, ancho, alto):
        self.pantalla = pantalla
        self.ANCHO = ancho
        self.ALTO = alto
        self.botones_presionados = {}
        self.animacion_nivel = 0
        self.nivel_actual = "Home"
        self.fuente_botones = pygame.font.SysFont(None, 32)

    def actualizar_botones_presionados(self):
        """Actualiza el estado de los botones presionados"""
        for boton_id in list(self.botones_presionados.keys()):
            self.botones_presionados[boton_id] -= 1
            if self.botones_presionados[boton_id] <= 0:
                del self.botones_presionados[boton_id]

    def manejar_transicion(self):
        """Maneja la transición entre niveles"""
        if self.animacion_nivel > 0:
            alpha = min(255, int(255 * (self.animacion_nivel / 30)))
            overlay = pygame.Surface((self.ANCHO, self.ALTO))
            overlay.set_alpha(alpha)
            overlay.fill(BLANCO)
            self.pantalla.blit(overlay, (0, 0))
            self.animacion_nivel -= 1

    def dibujar_boton(self, texto, x, y, ancho, alto, color_normal, color_hover):
        mouse_pos = pygame.mouse.get_pos()
        rect = pygame.Rect(x, y, ancho, alto)
        color = color_hover if rect.collidepoint(mouse_pos) else color_normal
        pygame.draw.rect(self.pantalla, color, rect, border_radius=10)
        fuente = self.fuente_botones
        texto_render = fuente.render(texto, True, TEXTO_CLARO)
        texto_rect = texto_render.get_rect(center=rect.center)
        self.pantalla.blit(texto_render, texto_rect)
        return rect

    def ejecutar(self):
        """Método principal para ejecutar el juego, debe ser implementado por cada juego"""
        pass

class BarraNavegacion:
    def __init__(self, juego, niveles=None):
        self.juego = juego
        self.niveles = niveles or ["Home", "Básico", "Medio", "Avanzado", "ChatBot"]
        self.botones = {}

    def dibujar(self, x_inicial=200, y=30, ancho=100, alto=40, espacio=10):
        """Dibuja la barra de navegación con los botones de nivel"""
        x = x_inicial

        for i, nivel in enumerate(self.niveles):
            boton_ancho = ancho + 20 if nivel == "ChatBot" else ancho

            self.botones[nivel] = self.juego.dibujar_boton(
                nivel, x, y, boton_ancho, alto,
                BOTON_NORMAL, BOTON_HOVER
            )

            # Resaltar el botón del nivel actual
            if nivel == self.juego.nivel_actual:
                pygame.draw.rect(self.juego.pantalla, BOTON_ACTIVO, self.botones[nivel], 0, border_radius=10)
                texto_render = self.juego.fuente_botones.render(nivel, True, TEXTO_CLARO)
                texto_rect = texto_render.get_rect(center=self.botones[nivel].center)
                self.juego.pantalla.blit(texto_render, texto_rect)

            # Aplicar efecto de presionado
            if i in self.juego.botones_presionados and self.juego.botones_presionados[i] > 0:
                pygame.draw.rect(self.juego.pantalla, BOTON_ACTIVO, self.botones[nivel], 0, border_radius=10)
                texto_render = self.juego.fuente_botones.render(nivel, True, TEXTO_CLARO)
                texto_rect = texto_render.get_rect(center=self.botones[nivel].center)
                self.juego.pantalla.blit(texto_render, texto_rect)

            x += (boton_ancho + espacio)