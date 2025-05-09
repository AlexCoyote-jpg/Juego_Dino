import pygame
import random
import math
from pygame.locals import *
from ui.components.utils import mostrar_texto_adaptativo, dibujar_caja_texto, Boton , obtener_fuente
from core.juego_base import JuegoBase , PALETA

class JuegoLogico(JuegoBase):
    # Constantes de clase para reutilizar
    NOMBRES = ["Rexy", "Trici", "Spike", "Dina", "Terry"]
    OBJETOS = ["pasteles", "galletas", "helados", "caramelos"]
    USEREVENT_SIGUIENTE = USEREVENT + 1

    def __init__(self, pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu):
        super().__init__("Dino Lógico", pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu)
        # --- Carga de imágenes específicas del juego ---
        self.cargar_imagenes()
        # Estado del juego
        self.nivel_actual = self._nivel_from_dificultad(dificultad)
        self.puntuacion = 0
        self.jugadas_totales = 0
        self.racha = 0
        self.tiempo_mensaje = 0
        self.mensaje = ""
        self.problema_actual = ""
        self.respuesta_correcta = None
        self.explicacion = ""
        self.opcion_botones: list[Boton] = []
        self.generar_problema()

    def cargar_imagenes(self):
        """Override: asigna imágenes usadas en draw()"""
        self.dino_img = self.images.get("dino4")
        self.mapa_img = self.images.get("mapa")

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
        self.opciones = self.generar_opciones(respuesta)
        random.shuffle(self.opciones)
        self.tiempo_mensaje = 0
        self.mensaje = ""


    def generar_problema_logico_basico(self):
        nombre = random.choice(self.NOMBRES)
        obj = random.choice(self.OBJETOS)
        n, x, y, f, c = [random.randint(lo, hi) for lo,hi in ((5,15),(3,8),(3,7),(20,40),(2,5))]
        lista = [
            (f"{nombre} dio 1 {obj} a cada uno de sus {n} amigos en la primera fiesta y 2 en la segunda.\n ¿Cuántos {obj} dio en total?",
             n*3, f"Suma 1×{n} + 2×{n} = 3×{n}."),
            (f"{nombre} plantó {x} árboles cada día durante {y} días.\n ¿Cuántos en total?",
             x*y, f"{x} × {y}."),
            (f"{nombre} tenía {f} frutas y las repartió en {c} canastas iguales.\n ¿Cuántas por canasta?",
             f//c, f"{f} ÷ {c}.")
        ]
        return random.choice(lista)

    def generar_problema_logico_medio(self):
        nombre = random.choice(self.NOMBRES)
        a = random.randint(2, 5)
        f = random.randint(5, 15)
        m = random.randint(10, 30)
        d = random.randint(2, 5)
        am = random.randint(3, 8)
        total = random.randint(6, 14)
        pos = random.randint(2, 4)
        problemas = [
            (f"{nombre} y sus {a} amigos fueron a recoger frutas. Cada uno recogió {f} frutas, pero luego decidieron repartirlas equitativamente.\n ¿Cuántas frutas recibió cada uno?", f, f"Multiplica {f} × {a+1} y divide entre {a+1}."),
            (f"{nombre} tiene {m} monedas. Si da {d} monedas a cada amigo y tiene {am} amigos,\n ¿cuántas monedas le quedarán?", m - (d * am), f"Multiplica {d} × {am} y réstalo de {m}."),
            (f"{nombre} y sus amigos están formados en un círculo. Si hay {total} dinosaurios en total y {nombre} es el número {pos},\n ¿qué número es el dinosaurio que está exactamente al frente de {nombre}?", (pos + total // 2) % total if total % 2 == 0 else 1, f"Suma la mitad de {total} a {pos} y aplica módulo {total}.")
        ]
        return random.choice(problemas)

    def generar_problema_logico_avanzado(self):
        nombre = random.choice(self.NOMBRES)
        a = random.randint(3, 6)
        p = random.randint(2, 3)
        l = random.randint(5, 10)
        total = random.randint(5, 10)
        salto = random.randint(2, 3)
        m = random.randint(20, 40)
        s = random.randint(4, 8)
        problemas = [
            (f"{nombre} organiza una carrera con {a} amigos. Si cada uno corre a una velocidad diferente y {nombre} llega en la posición {p},\n ¿cuántos dinosaurios llegaron después de él?", a - p + 1, f"Resta la posición de {nombre} a los participantes: {a} - {p} + 1."),
            (f"{nombre} tiene un jardín cuadrado con {l} metros por lado. Quiere plantar flores en el borde, poniendo una flor cada metro.\n ¿Cuántas flores necesitará?", l * 4, f"El perímetro es 4 × {l}."),
            (f"{nombre} y sus amigos están jugando a pasarse una pelota. Son {total} dinosaurios en total, formados en círculo. Si cada uno pasa la pelota al dinosaurio que está {salto} posiciones a su derecha,\n ¿cuántos pases se necesitan para que la pelota vuelva al dinosaurio que la lanzó primero?", total // math.gcd(total, salto), f"El mínimo número de pases es {total} dividido por el MCD de {total} y {salto}."),
            (f"{nombre} tiene {m} monedas y quiere repartirlas en sobres de {s} monedas cada uno.\n ¿Cuántos sobres puede llenar completamente?", m // s, f"Divide {m} entre {s}.")
        ]
        return random.choice(problemas)

    def handle_event(self, evento):
        super().handle_event(evento)
        if evento.type == MOUSEBUTTONDOWN and evento.button == 1:
            for btn in self.opcion_botones:
                if btn.rect.collidepoint(evento.pos):
                    self.jugadas_totales += 1
                    es_correcto = int(btn.texto) == self.respuesta_correcta
                    if es_correcto:
                        self.puntuacion += 1
                        self.racha += 1
                    else:
                        self.racha = 0
                    self.mostrar_feedback(es_correcto, self.respuesta_correcta)
                    self.tiempo_mensaje = 90
                    pygame.time.set_timer(self.USEREVENT_SIGUIENTE, 900, True)
                    return
        elif evento.type == self.USEREVENT_SIGUIENTE:
            self.generar_problema()

    def update(self, dt=None):
        if self.tiempo_mensaje > 0:
            self.tiempo_mensaje -= 1

    def draw(self, surface):
        self.dibujar_fondo()
        self.mostrar_titulo()

        # --- Mejoras para el enunciado del problema ---
        enunciado_y = self.navbar_height + 100  # Debajo del título
        enunciado_h = max(90, int(self.ALTO * 0.13))
        enunciado_fuente = obtener_fuente(max(38, int(self.ALTO * 0.045)), negrita=True)

        # Opcional: dibujar una caja suave de fondo para el enunciado
        dibujar_caja_texto(
            self.pantalla,
            40, enunciado_y,
            self.ANCHO - 80, enunciado_h,
            color=(255, 255, 240, 220),
            radius=18
        )

        self.mostrar_texto(
            self.problema_actual,
            x=40,
            y=enunciado_y,
            w=self.ANCHO - 80,
            h=enunciado_h,
            fuente=enunciado_fuente,
            color=(30, 30, 30),
            centrado=True
        )

        # opciones
        opciones_y = enunciado_y + enunciado_h + 30  # Espacio debajo del enunciado
        self.dibujar_opciones(y0=opciones_y)

        # — Dino pequeño a la izquierda del primer botón —
        if self.opcion_botones and self.dino_img:
            nuevo_w = int(self.ANCHO * 0.15)
            ow, oh = self.dino_img.get_size()
            nuevo_h = int(oh * nuevo_w / ow)
            dino_small = pygame.transform.smoothscale(self.dino_img, (nuevo_w, nuevo_h))
            first_btn = self.opcion_botones[0]
            x_dino = max(10, first_btn.rect.left - nuevo_w - 10)
            y_dino = first_btn.rect.centery - nuevo_h // 2
            self.pantalla.blit(dino_small, (x_dino, y_dino))

        # — Mapa pequeño debajo de los botones —
        if self.mapa_img:
            map_w, map_h = self.mapa_img.get_size()
            nuevo_map_w = int(self.ANCHO * 0.25)
            nuevo_map_h = int(map_h * nuevo_map_w / map_w)
            mapa_small = pygame.transform.smoothscale(self.mapa_img, (nuevo_map_w, nuevo_map_h))
            if self.opcion_botones:
                y_map = self.opcion_botones[-1].rect.bottom + 10
            else:
                y_map = self.navbar_height + 10
            x_map = self.ANCHO - nuevo_map_w - 20
            self.pantalla.blit(mapa_small, (x_map, y_map))

        # feedback
        self.dibujar_feedback()

        # puntaje y navbar
        self.mostrar_puntaje(self.puntuacion, self.jugadas_totales, "Puntaje")



