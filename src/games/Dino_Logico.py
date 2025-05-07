import pygame
import random
from pygame.locals import *
from ui.utils import Boton  # Usa la clase Boton para los botones de opciones

def generar_opciones(respuesta, min_diff=1, max_diff=3, cantidad=4):
    """
    Genera una lista de opciones (incluyendo la respuesta correcta) para preguntas de opción múltiple.
    Evita duplicados y asegura que todas las opciones sean positivas y distintas.
    """
    opciones = set([respuesta])
    intentos = 0
    while len(opciones) < cantidad and intentos < 30:
        delta = random.randint(min_diff, max_diff)
        signo = random.choice([-1, 1])
        opcion = respuesta + signo * delta
        # Evita opciones negativas, duplicadas o cero
        if opcion > 0 and opcion != respuesta:
            opciones.add(opcion)
        intentos += 1
    # Si no se lograron suficientes opciones, rellena con valores positivos únicos
    while len(opciones) < cantidad:
        opciones.add(respuesta + random.randint(1, 10))
    return list(opciones)

class JuegoLogico:
    def __init__(self, pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu):
        # --- Integración con el menú principal ---
        self.pantalla = pantalla
        self.config = config
        self.dificultad = dificultad
        self.fondo = fondo
        self.navbar = navbar
        self.images = images
        self.sounds = sounds
        self.return_to_menu = return_to_menu

        # --- Dimensiones y fuentes ---
        self.ANCHO = pantalla.get_width()
        self.ALTO = pantalla.get_height()
        self.fuente_titulo = pygame.font.SysFont("Segoe UI", max(36, int(0.04 * pantalla.get_height())), bold=True)
        self.fuente = pygame.font.SysFont("Segoe UI", max(20, int(0.025 * pantalla.get_height())))
        self.reloj = pygame.time.Clock()

        # --- Estado del juego ---
        self.problema_actual = ""
        self.opciones = []
        self.respuesta_correcta = None
        self.opciones_rects = []
        self.boton_opciones = []  # Lista de botones de opciones
        self.explicacion = ""
        self.puntuacion = 0
        self.jugadas_totales = 0
        self.racha = 0
        self.mensaje = ""
        self.tiempo_mensaje = 0
        self.animacion_opcion = None
        self.animacion_tiempo = 0

        # --- Cargar imágenes ---
        self.cargar_imagenes()

        # --- Determinar nivel actual ---
        self.nivel_actual = self._mapear_dificultad(dificultad)

        # --- Generar primer problema ---
        self.generar_problema()

    def _mapear_dificultad(self, dificultad):
        if dificultad == "Fácil":
            return "Básico"
        elif dificultad == "Normal":
            return "Medio"
        elif dificultad == "Difícil":
            return "Avanzado"
        return "Básico"

    def cargar_imagenes(self):
        # Usa imágenes del diccionario si existen, si no, usa cargar_imagen_segura
        # Ajusta tamaño para que no sobresalgan
        dino_size = (max(60, self.ANCHO // 16), max(60, self.ALTO // 12))
        mapa_size = (max(80, self.ANCHO // 12), max(60, self.ALTO // 14))
        self.dino_img = self.images.get("dino4") if self.images else None
        self.mapa_img = self.images.get("mapa") if self.images else None
        if not self.dino_img:
            self.dino_img = self.cargar_imagen_segura('dino4.png', dino_size, (0, 150, 0))
        else:
            self.dino_img = pygame.transform.smoothscale(self.dino_img, dino_size)
        if not self.mapa_img:
            self.mapa_img = self.cargar_imagen_segura('mapa.png', mapa_size, (255, 223, 186))
        else:
            self.mapa_img = pygame.transform.smoothscale(self.mapa_img, mapa_size)

    def cargar_imagen_segura(self, archivo, tam, color_fondo):
        try:
            img = pygame.image.load(archivo).convert_alpha()
            img = pygame.transform.smoothscale(img, tam)
            return img
        except Exception:
            surf = pygame.Surface(tam)
            surf.fill(color_fondo)
            return surf

    def generar_problema(self):
        if self.nivel_actual == "Básico":
            problema, respuesta, explicacion = self.generar_problema_logico_basico()
        elif self.nivel_actual == "Medio":
            problema, respuesta, explicacion = self.generar_problema_logico_medio()
        else:
            problema, respuesta, explicacion = self.generar_problema_logico_avanzado()
        self.problema_actual = problema
        self.respuesta_correcta = respuesta
        self.explicacion = explicacion
        self.opciones = generar_opciones(respuesta, min_diff=1, max_diff=3)
        random.shuffle(self.opciones)

    def generar_problema_logico_basico(self):
        nombres = ["Rexy", "Trici", "Spike", "Dina", "Terry"]
        objetos = ["pasteles", "galletas", "helados", "caramelos"]
        nombre = random.choice(nombres)
        obj = random.choice(objetos)
        n = random.randint(5, 15)
        x = random.randint(3, 8)
        y = random.randint(3, 7)
        f = random.randint(20, 40)
        c = random.randint(2, 5)
        problemas = [
            (f"{nombre} tiene {n} amigos. En la primera fiesta, les dio 1 {obj} a cada uno. En la segunda fiesta, les dio 2 {obj} a cada uno. ¿Cuántos {obj} ha dado en total?", n*3, f"Suma los {obj} de ambas fiestas: {n} + 2×{n} = 3×{n}."),
            (f"{nombre} plantó {x} árboles mágicos cada día durante {y} días. ¿Cuántos árboles plantó en total?", x*y, f"Multiplica árboles por día por el número de días: {x} × {y}."),
            (f"{nombre} tiene {f} frutas jurásicas y quiere repartirlas en {c} canastas iguales. ¿Cuántas frutas pondrá en cada canasta?", f//c, f"Divide el total de frutas entre las canastas: {f} ÷ {c}.")
        ]
        return random.choice(problemas)

    def generar_problema_logico_medio(self):
        nombres = ["Rexy", "Trici", "Spike", "Dina", "Terry"]
        nombre = random.choice(nombres)
        a = random.randint(2, 5)
        f = random.randint(5, 15)
        m = random.randint(10, 30)
        d = random.randint(2, 5)
        am = random.randint(3, 8)
        total = random.randint(6, 14)
        pos = random.randint(2, 4)
        problemas = [
            (f"{nombre} y sus {a} amigos fueron a recoger frutas. Cada uno recogió {f} frutas, pero luego decidieron repartirlas equitativamente. ¿Cuántas frutas recibió cada uno?", f, f"Multiplica {f} × {a+1} y divide entre {a+1}."),
            (f"{nombre} tiene {m} monedas. Si da {d} monedas a cada amigo y tiene {am} amigos, ¿cuántas monedas le quedarán?", m - (d * am), f"Multiplica {d} × {am} y réstalo de {m}."),
            (f"{nombre} y sus amigos están formados en un círculo. Si hay {total} dinosaurios en total y {nombre} es el número {pos}, ¿qué número es el dinosaurio que está exactamente al frente de {nombre}?", (pos + total // 2) % total if total % 2 == 0 else 1, f"Suma la mitad de {total} a {pos} y aplica módulo {total}.")
        ]
        return random.choice(problemas)

    def generar_problema_logico_avanzado(self):
        import math
        nombres = ["Rexy", "Trici", "Spike", "Dina", "Terry"]
        nombre = random.choice(nombres)
        a = random.randint(3, 6)
        p = random.randint(2, 3)
        l = random.randint(5, 10)
        total = random.randint(5, 10)
        salto = random.randint(2, 3)
        m = random.randint(20, 40)
        s = random.randint(4, 8)
        problemas = [
            (f"{nombre} organiza una carrera con {a} amigos. Si cada uno corre a una velocidad diferente y {nombre} llega en la posición {p}, ¿cuántos dinosaurios llegaron después de él?", a - p + 1, f"Resta la posición de {nombre} a los participantes: {a} - {p} + 1."),
            (f"{nombre} tiene un jardín cuadrado con {l} metros por lado. Quiere plantar flores en el borde, poniendo una flor cada metro. ¿Cuántas flores necesitará?", l * 4, f"El perímetro es 4 × {l}."),
            (f"{nombre} y sus amigos están jugando a pasarse una pelota. Son {total} dinosaurios en total, formados en círculo. Si cada uno pasa la pelota al dinosaurio que está {salto} posiciones a su derecha, ¿cuántos pases se necesitan para que la pelota vuelva al dinosaurio que la lanzó primero?", total // math.gcd(total, salto), f"El mínimo número de pases es {total} dividido por el MCD de {total} y {salto}."),
            (f"{nombre} tiene {m} monedas y quiere repartirlas en sobres de {s} monedas cada uno. ¿Cuántos sobres puede llenar completamente?", m // s, f"Divide {m} entre {s}.")
        ]
        return random.choice(problemas)

    def mostrar_mensaje_temporal(self, mensaje, correcto=None, opcion_idx=None):
        frases_correcto = [
            "¡Correcto! 🦖", "¡Genial! 🎉", "¡Eres un crack! 🥚", "¡Dino-aplausos! 👏",
            "¡Súper bien!", "¡Lo lograste!", "¡Respuesta jurásica!", "¡Dino-poder!"
        ]
        frases_incorrecto = [
            "¡Uy! Intenta de nuevo 🦕", "No te rindas 🦴", "¡Casi! 😅", "¡Ánimo! 🌟",
            "¡Sigue intentando!", "¡No te desanimes!", "¡Puedes lograrlo!", "¡Dino-ánimo!"
        ]
        if correcto is not None:
            if correcto:
                mensaje = random.choice(frases_correcto)
            else:
                mensaje = random.choice(frases_incorrecto) + f" La respuesta era {self.respuesta_correcta}."
        self.mensaje = mensaje
        self.tiempo_mensaje = 120
        if opcion_idx is not None:
            self.animacion_opcion = opcion_idx
            self.animacion_tiempo = 15

    def manejar_eventos_juego(self, evento):
        if evento.type == MOUSEBUTTONDOWN:
            for i, rect in enumerate(self.opciones_rects):
                if rect.collidepoint(evento.pos):
                    self.jugadas_totales += 1
                    if self.opciones[i] == self.respuesta_correcta:
                        self.puntuacion += 1
                        self.racha += 1
                        self.mostrar_mensaje_temporal("", correcto=True, opcion_idx=i)
                        if self.racha > 0 and self.racha % 3 == 0:
                            self.mensaje += f" ¡Racha de {self.racha}! 🏆"
                    else:
                        self.racha = 0
                        self.mostrar_mensaje_temporal("", correcto=False, opcion_idx=i)
                    self.tiempo_mensaje = 120
                    self.generar_problema()
                    return True
        return False

    def dibujar_boton(self, texto, x, y, w, h, color_normal, color_hover):
        mouse_pos = pygame.mouse.get_pos()
        rect = pygame.Rect(x, y, w, h)
        color = color_hover if rect.collidepoint(mouse_pos) else color_normal
        pygame.draw.rect(self.pantalla, color, rect, border_radius=12)
        pygame.draw.rect(self.pantalla, (80, 80, 80), rect, 2, border_radius=12)
        fuente = self.fuente
        txt = fuente.render(texto, True, (30, 30, 30))
        txt_rect = txt.get_rect(center=rect.center)
        self.pantalla.blit(txt, txt_rect)
        return rect

    def mostrar_texto(self, texto, x, y, fuente=None, centrado=False):
        fuente = fuente or self.fuente
        txt = fuente.render(texto, True, (30, 30, 30))
        rect = txt.get_rect()
        if centrado:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        self.pantalla.blit(txt, rect)

    def mostrar_texto_multilinea(self, texto, x, y, fuente=None, centrado=False):
        fuente = fuente or self.fuente
        lineas = texto.split("\n")
        for i, linea in enumerate(lineas):
            self.mostrar_texto(linea, x, y + i * 36, fuente, centrado)

    def dibujar_fondo(self):
        if self.fondo:
            self.fondo.draw(self.pantalla)
        else:
            self.pantalla.fill((255, 255, 255))

    def dibujar(self, pantalla):
        # Método requerido por el screen manager
        self.dibujar_fondo()
        # Dibuja imágenes si existen, ajustadas y sin sobresalir
        margen = 20
        if self.dino_img:
            self.pantalla.blit(self.dino_img, (margen, self.ALTO - self.dino_img.get_height() - margen))
        if self.mapa_img:
            self.pantalla.blit(self.mapa_img, (self.ANCHO - self.mapa_img.get_width() - margen, self.ALTO - self.mapa_img.get_height() - margen))
        # Problema
        self.mostrar_texto_multilinea(self.problema_actual, self.ANCHO // 2, 80, centrado=True)
        # Opciones con Boton de ui.utils
        self.opciones_rects = []
        self.boton_opciones = []
        colores = [(144, 238, 144), (173, 216, 230), (255, 255, 153), (255, 182, 193)]
        color_hover_default = (200, 200, 200)
        # Calcula posiciones y tamaños de botones de forma responsiva
        n = len(self.opciones)
        boton_w = max(70, min(120, self.ANCHO // (n * 2)))
        boton_h = max(40, min(70, self.ALTO // 16))
        espacio = max(20, min(50, self.ANCHO // (n * 6)))
        total_w = n * boton_w + (n - 1) * espacio
        x_ini = (self.ANCHO - total_w) // 2
        y_opciones = int(self.ALTO * 0.32)
        for i, opcion in enumerate(self.opciones):
            x = x_ini + i * (boton_w + espacio)
            boton = Boton(
                str(opcion), x, y_opciones, boton_w, boton_h,
                color_normal=colores[i % len(colores)],
                color_hover=color_hover_default,
                texto_adaptativo=True
            )
            boton.draw(self.pantalla)
            self.opciones_rects.append(boton.rect)
            self.boton_opciones.append(boton)
        # Mensaje y explicación
        if self.tiempo_mensaje > 0:
            self.mostrar_texto(self.mensaje, self.ANCHO // 2, 320, centrado=True)
            self.tiempo_mensaje -= 1
            if "Correcto" in self.mensaje or "¡Genial!" in self.mensaje or "¡Eres un crack!" in self.mensaje or "¡Dino-aplausos!" in self.mensaje:
                self.mostrar_texto_multilinea(self.explicacion, self.ANCHO // 2, 370, centrado=True)
        # Puntuación y racha
        self.mostrar_texto(f"Puntuación: {self.puntuacion}/{self.jugadas_totales}", 30, self.ALTO - 35)
        self.mostrar_texto(f"Racha: {self.racha}", self.ANCHO - 190, self.ALTO - 35)
        # Barra de navegación
        if self.navbar:
            self.navbar.draw(self.pantalla, self.images.get("dino_logo") if self.images else None)

    def handle_event(self, evento):
        # Compatible con ScreenManager: recibe un solo evento
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            if self.return_to_menu:
                self.return_to_menu()
        if self.navbar and hasattr(self.navbar, "handle_event"):
            nav_result = self.navbar.handle_event(evento, self.images.get("dino_logo") if self.images else None)
            if nav_result is not None and self.return_to_menu:
                self.return_to_menu()
        self.manejar_eventos_juego(evento)

    def update(self, dt=None):
        # Compatible con ScreenManager: dt puede ser None
        pass

    def draw(self, surface):
        # Compatible con ScreenManager: surface es la pantalla
        self.dibujar(surface)
