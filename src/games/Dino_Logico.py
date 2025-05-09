import pygame
import random
import math
from pygame.locals import *
from ui.utils import mostrar_texto_adaptativo, dibujar_caja_texto, Boton
from core.juego_base import JuegoBase

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

    def generar_opciones(self, respuesta: int) -> list[int]:
        """Crea opciones alrededor de la respuesta correcta."""
        opciones = {respuesta}
        while len(opciones) < 4:
            opciones.add(respuesta + random.choice([-1,1]) * random.randint(1,5))
        return list(opciones)

    def generar_problema_logico_basico(self):
        nombre = random.choice(self.NOMBRES)
        obj = random.choice(self.OBJETOS)
        n, x, y, f, c = [random.randint(lo, hi) for lo,hi in ((5,15),(3,8),(3,7),(20,40),(2,5))]
        lista = [
            (f"{nombre} dio 1 {obj} a cada uno de sus {n} amigos en la primera fiesta y 2 en la segunda. ¿Cuántos {obj} dio en total?",
             n*3, f"Suma 1×{n} + 2×{n} = 3×{n}."),
            (f"{nombre} plantó {x} árboles cada día durante {y} días. ¿Cuántos en total?",
             x*y, f"{x} × {y}."),
            (f"{nombre} tenía {f} frutas y las repartió en {c} canastas iguales. ¿Cuántas por canasta?",
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
            (f"{nombre} y sus {a} amigos fueron a recoger frutas. Cada uno recogió {f} frutas, pero luego decidieron repartirlas equitativamente. ¿Cuántas frutas recibió cada uno?", f, f"Multiplica {f} × {a+1} y divide entre {a+1}."),
            (f"{nombre} tiene {m} monedas. Si da {d} monedas a cada amigo y tiene {am} amigos, ¿cuántas monedas le quedarán?", m - (d * am), f"Multiplica {d} × {am} y réstalo de {m}."),
            (f"{nombre} y sus amigos están formados en un círculo. Si hay {total} dinosaurios en total y {nombre} es el número {pos}, ¿qué número es el dinosaurio que está exactamente al frente de {nombre}?", (pos + total // 2) % total if total % 2 == 0 else 1, f"Suma la mitad de {total} a {pos} y aplica módulo {total}.")
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
            (f"{nombre} organiza una carrera con {a} amigos. Si cada uno corre a una velocidad diferente y {nombre} llega en la posición {p}, ¿cuántos dinosaurios llegaron después de él?", a - p + 1, f"Resta la posición de {nombre} a los participantes: {a} - {p} + 1."),
            (f"{nombre} tiene un jardín cuadrado con {l} metros por lado. Quiere plantar flores en el borde, poniendo una flor cada metro. ¿Cuántas flores necesitará?", l * 4, f"El perímetro es 4 × {l}."),
            (f"{nombre} y sus amigos están jugando a pasarse una pelota. Son {total} dinosaurios en total, formados en círculo. Si cada uno pasa la pelota al dinosaurio que está {salto} posiciones a su derecha, ¿cuántos pases se necesitan para que la pelota vuelva al dinosaurio que la lanzó primero?", total // math.gcd(total, salto), f"El mínimo número de pases es {total} dividido por el MCD de {total} y {salto}."),
            (f"{nombre} tiene {m} monedas y quiere repartirlas en sobres de {s} monedas cada uno. ¿Cuántos sobres puede llenar completamente?", m // s, f"Divide {m} entre {s}.")
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
        # problema
        mostrar_texto_adaptativo(self.pantalla, self.problema_actual,
                                 x=20, y=self.navbar_height+20,
                                 w=self.ANCHO-40, h=int(self.ALTO*0.2),
                                 fuente_base=self.fuente)
        # opciones
        self.dibujar_opciones()

        # — Dino pequeño a la izquierda del primer botón —
        if self.opcion_botones and self.dino_img:
            # calculamos nuevo ancho = 15% del ancho de pantalla
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
            nuevo_map_w = int(self.ANCHO * 0.25)   # 25% del ancho de pantalla
            nuevo_map_h = int(map_h * nuevo_map_w / map_w)
            mapa_small = pygame.transform.smoothscale(self.mapa_img, (nuevo_map_w, nuevo_map_h))
            if self.opcion_botones:
                y_map = self.opcion_botones[-1].rect.bottom + 10
            else:
                y_map = self.navbar_height + 10
            x_map = self.ANCHO - nuevo_map_w - 20  # <-- margen derecho de 20px
            self.pantalla.blit(mapa_small, (x_map, y_map))

        # feedback
        if self.tiempo_mensaje > 0:
            mostrar_texto_adaptativo(self.pantalla,
                                     f"{self.mensaje}\n{self.explicacion}",
                                     x=20, y=int(self.ALTO*0.5),
                                     w=self.ANCHO-40, h=int(self.ALTO*0.25),
                                     fuente_base=self.fuente, centrado=True)
        # puntaje y navbar
        self.mostrar_puntaje(self.puntuacion, self.jugadas_totales, "Puntaje")
        if self.navbar:
            self.navbar.draw(self.pantalla, self.images.get("dino_logo"))

    def dibujar_opciones(self):
        """Construye y dibuja botones de colores vivos para cada opción con hover complementario."""
        paleta = [
            (244, 67, 54),    # rojo
            (233, 30, 99),    # rosa
            (156, 39, 176),   # púrpura
            (63, 81, 181),    # índigo
            (33, 150, 243),   # azul claro
            (0, 188, 212),    # cian
            (0, 150, 136),    # teal
            (76, 175, 80),    # verde
            (255, 235, 59),   # amarillo
            (255, 152, 0),    # naranja
        ]
        espacio = 20
        cnt = len(self.opciones)
        w = max(100, min(180, self.ANCHO // (cnt * 2)))
        h = max(50, min(80, self.ALTO // 12))
        x0 = (self.ANCHO - (w * cnt + espacio * (cnt - 1))) // 2
        y0 = self.ALTO // 2 - h // 2

        

        self.opcion_botones.clear()
        for i, val in enumerate(self.opciones):
            color_bg = paleta[i % len(paleta)]
            color_hover = self.color_complementario(color_bg)
            lum = 0.299 * color_bg[0] + 0.587 * color_bg[1] + 0.114 * color_bg[2]
            color_texto = (0, 0, 0) if lum > 180 else (255, 255, 255)

            x = x0 + i * (w + espacio)
            btn = Boton(
                texto=str(val),
                x=x, y=y0, ancho=w, alto=h,
                fuente=self.fuente,
                color_normal=color_bg,
                color_hover=color_hover,
                color_texto=color_texto,
                estilo="flat"
            )
            btn.draw(self.pantalla, tooltip_manager=self.tooltip_manager)
            self.opcion_botones.append(btn)

    def mostrar_mensaje_temporal(self, mensaje):
        self.mensaje = mensaje
        self.tiempo_mensaje = 90