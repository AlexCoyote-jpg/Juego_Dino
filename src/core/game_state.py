"""
Lógica y utilidades para el estado base del juego y transiciones.
"""
import pygame

class JuegoBase:
    """
    Clase base para todos los juegos.
    - Centraliza atributos comunes: pantalla, fuentes, imágenes, sonidos, etc.
    - Proporciona utilidades reutilizables: métodos para dibujar fondo, mostrar texto, mostrar mensajes temporales, etc.
    - Facilita la herencia: todos los juegos pueden heredar de JuegoBase y así evitar duplicar código.
    - Permite integración uniforme: el menú y el screen manager pueden tratar todos los juegos de la misma forma.
    """
    def __init__(self, nombre, pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu=None):
        self.nombre = nombre
        self.pantalla = pantalla
        self.config = config
        self.dificultad = dificultad
        self.fondo = fondo
        self.navbar = navbar
        self.images = images
        self.sounds = sounds
        self.return_to_menu = return_to_menu
        self.ANCHO = pantalla.get_width()
        self.ALTO = pantalla.get_height()
        self.fuente_titulo = pygame.font.SysFont("Segoe UI", 54, bold=True)
        self.fuente_texto = pygame.font.SysFont("Segoe UI", 28)
        self.logo_img = images.get("dino_logo") if images else None
        self.reloj = pygame.time.Clock()
        self.mensaje = ""
        self.tiempo_mensaje = 0
        self.puntuacion = 0
        self.jugadas_totales = 0

    def dibujar_fondo(self):
        """Dibuja el fondo del juego. Si el fondo tiene método draw, lo usa; si no, rellena con color base."""
        if hasattr(self.fondo, "draw"):
            self.fondo.draw(self.pantalla)
        else:
            self.pantalla.fill((245, 245, 255))

    def mostrar_texto(self, texto, x, y, fuente=None, color=(30,30,30), centrado=False):
        """Muestra texto en pantalla, con opción de centrado y fuente personalizada."""
        fuente = fuente or self.fuente_texto
        surf = fuente.render(texto, True, color)
        rect = surf.get_rect()
        if centrado:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        self.pantalla.blit(surf, rect)

    def mostrar_texto_multilinea(self, texto, x, y, fuente=None, color=(30,30,30), centrado=False):
        """Muestra texto multilínea en pantalla."""
        fuente = fuente or self.fuente_texto
        for i, linea in enumerate(texto.split("\n")):
            self.mostrar_texto(linea, x, y + i * fuente.get_height(), fuente, color, centrado)

    def dibujar_caja_texto(self, x, y, w, h, color, radius=18):
        """Dibuja una caja de texto con esquinas redondeadas."""
        import ui.utils
        ui.utils.dibujar_caja_texto(self.pantalla, x, y, w, h, color, radius=radius)

    def mostrar_mensaje_temporal(self, mensaje, tiempo=60):
        """Muestra un mensaje temporal en pantalla durante 'tiempo' frames."""
        self.mensaje = mensaje
        self.tiempo_mensaje = tiempo

    def actualizar_botones_presionados(self):
        pass  # Puedes implementar si lo necesitas

    def manejar_transicion(self):
        pass  # Puedes implementar si lo necesitas

    def iniciar_transicion(self, color=(255,255,255), velocidad=18):
        self["transicion_en_progreso"] = True
        self["transicion_alpha"] = 0
        self["transicion_color"] = color
        self["transicion_velocidad"] = velocidad
        return self

    def manejar_transicion(self):
        if self["transicion_en_progreso"]:
            overlay = pygame.Surface((self["ANCHO"], self["ALTO"]), pygame.SRCALPHA)
            overlay.fill((*self["transicion_color"], int(self["transicion_alpha"])))
            self["pantalla"].blit(overlay, (0, 0))
            self["transicion_alpha"] += self["transicion_velocidad"]
            if self["transicion_alpha"] >= 255:
                self["transicion_en_progreso"] = False
                self["transicion_alpha"] = 0
        return self

    def avanzar_nivel(juego):
        niveles = ["Básico", "Medio", "Avanzado"]
        idx = niveles.index(juego["nivel_actual"])
        juego["nivel_actual"] = niveles[(idx + 1) % len(niveles)]
        if "sonido_acierto" in juego and juego["sonido_acierto"] and not juego.get("silencio", False):
            juego["sonido_acierto"].play()
        if "inicializar_nivel" in juego:
            juego["inicializar_nivel"]()

    def update(self):
        """Actualiza la lógica del juego (para usar con el screen manager)."""
        # Actualiza el temporizador del mensaje temporal
        if self.tiempo_mensaje > 0:
            self.tiempo_mensaje -= 1
            if self.tiempo_mensaje == 0:
                self.mensaje = ""

    def draw(self, surface=None):
        """Dibuja el juego en pantalla (para usar con el screen manager)."""
        pantalla = surface if surface else self.pantalla
        self.dibujar_fondo()
        # Dibuja el logo si existe
        if self.logo_img:
            pantalla.blit(self.logo_img, (20, 20))
        # Dibuja el mensaje temporal si existe
        if self.mensaje:
            self.mostrar_texto(self.mensaje, self.ANCHO // 2, 60, self.fuente_texto, (200, 50, 50), centrado=True)

    def handle_event(self, event):
        """Maneja eventos de pygame (teclado, mouse, etc)."""
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                exit()

    def resize(self, width, height):
        """Actualiza dimensiones y recursos dependientes del tamaño."""
        self.ANCHO = width
        self.ALTO = height

    def get_image(self, key, default=None):
        return self.images.get(key, default) if self.images else default

    def get_sound(self, key, default=None):
        return self.sounds.get(key, default) if self.sounds else default
