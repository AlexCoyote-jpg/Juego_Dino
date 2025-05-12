import pygame
import random
from pygame.locals import *
from core.juego_base import JuegoBase
from ui.components.utils import obtener_fuente

def generar_problema_division(nivel):
    if nivel == "Básico":
        b = random.randint(1, 5)
        a = b * random.randint(1, 5)
        problema = f"Dino tiene {a} bayas. Si las reparte en {b} grupos iguales, ¿cuántas bayas habrá en cada grupo?"
        respuesta = a // b
    elif nivel == "Medio":
        b = random.randint(2, 5)
        a = b * random.randint(3, 8)
        problema = f"Dino tiene {a} bayas y quiere repartirlas entre {b} amigos. ¿Cuántas bayas recibirá cada amigo?"
        respuesta = a // b
    else:  # Avanzado
        b = random.randint(3, 6)
        a = b * random.randint(5, 10)
        c = random.randint(1, 3)
        problema = f"Dino tiene {a} bayas. Si las reparte en {b} grupos iguales y luego come {c} de un grupo, ¿cuántas bayas le quedan en ese grupo?"
        respuesta = (a // b) - c
    return problema, respuesta

class JuegoRescate(JuegoBase):
    def __init__(self, pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu):
        super().__init__('Rescate Jurásico', pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu)
        self.puntuacion = 0
        self.jugadas_totales = 0
        self.posicion_dino = 0
        self.total_pasos = 3
        self.feedback = ""
        self.feedback_color = (0, 120, 0)
        self.tiempo_feedback = 0
        self.cargar_imagenes()
        self.generar_problema()

    def cargar_imagenes(self):
        # Guardamos las imágenes según las claves preestablecidas.
        self.dino_mama_img = self.images.get("dino5")   # Se usará solo para dibujar a la izquierda
        self.dino_bebe_img = self.images.get("dino2")     # Se usará para dibujar a la derecha
        self.roca_img = self.images.get("roca")           # Imagen para las rocas centrales

    def generar_problema(self):
        nivel = self._nivel_from_dificultad(self.dificultad)
        problema, respuesta = generar_problema_division(nivel)
        self.problema_actual = problema
        self.respuesta_correcta = respuesta
        self.opciones = self.generar_opciones(self.respuesta_correcta, cantidad=3)
        random.shuffle(self.opciones)
        self.feedback = ""
        self.tiempo_feedback = 0

    def mostrar_feedback(self, correcto, respuesta_correcta=None):
        if correcto:
            self.feedback = "¡Correcto!"
            self.feedback_color = (0, 120, 0)
        else:
            self.feedback = f"Incorrecto. Respuesta: {respuesta_correcta}"
            self.feedback_color = (180, 40, 40)
        self.tiempo_feedback = 60  # Duración en frames

    def handle_event(self, evento):
        super().handle_event(evento)
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for btn in self.opcion_botones:
                if btn.rect.collidepoint(evento.pos):
                    self.jugadas_totales += 1
                    if int(btn.texto) == self.respuesta_correcta:
                        self.puntuacion += 1
                        self.posicion_dino += 1
                        self.mostrar_feedback(True)
                        # En lugar de finalizar, se reinicia el avance al pasarse el total
                        if self.posicion_dino > self.total_pasos:
                            self.posicion_dino = 0
                        self.generar_problema()
                    else:
                        self.mostrar_feedback(False, self.respuesta_correcta)
                    break

    def update(self, dt=None):
        super().update(dt)
        if self.tiempo_feedback:
            self.tiempo_feedback -= 1
            if self.tiempo_feedback <= 0:
                self.feedback = ""

    def draw(self, surface=None):
        destino = surface if surface is not None else self.pantalla
        self.dibujar_fondo()

        # Variables locales para mayor eficiencia
        sx = self.sx
        sy = self.sy
        sf = self.sf

        margen_x = sx(40)
        area_top = self.navbar_height + sy(20)
        ancho_area = self.ANCHO - 2 * margen_x

        # Título e instrucciones
        self.mostrar_titulo()
        instrucciones_h = sy(40)
        self.mostrar_texto(
            "¡Ayuda a mamá dinosaurio a rescatar a su bebé!",
            x=margen_x,
            y=area_top + sy(50),
            w=ancho_area,
            h=instrucciones_h,
            fuente=obtener_fuente(sf(22)),
            color=(80, 80, 80),
            centrado=True
        )

        # Área de imágenes centrada
        area_img_y = area_top + sy(100)
        area_img_h = sy(120)
        roca_espacio = sx(80)
        roca_w = sx(60)
        roca_h = sy(60)
        dino_w = sx(80)
        dino_h = sy(80)
        # Ancho total del bloque: dino_mama + espacio + (total_pasos * roca_espacio) + espacio + dino_bebe
        block_width = dino_w + sx(30) + self.total_pasos * roca_espacio + sx(30) + dino_w
        start_x = (self.ANCHO - block_width) // 2

        # Dibujar mamá dino (solo a la izquierda)
        if self.dino_mama_img:
            img_mama = pygame.transform.smoothscale(self.dino_mama_img, (int(dino_w), int(dino_h)))
            destino.blit(img_mama, (start_x, area_img_y + area_img_h//2 - dino_h//2))

        # Dibujar rocas (centradas)
        roca_start_x = start_x + dino_w + sx(30)
        if self.roca_img:
            img_roca = pygame.transform.smoothscale(self.roca_img, (int(roca_w), int(roca_h)))
            for i in range(self.total_pasos):
                x = roca_start_x + i * roca_espacio
                destino.blit(img_roca, (x, area_img_y + area_img_h//2 - roca_h//2))

        # Dibujar bebé dino (derecha)
        bebe_x = roca_start_x + self.total_pasos * roca_espacio + sx(30)
        if self.dino_bebe_img:
            img_bebe = pygame.transform.smoothscale(self.dino_bebe_img, (int(dino_w), int(dino_h)))
            destino.blit(img_bebe, (bebe_x, area_img_y + area_img_h//2 - dino_h//2 + sy(10)))

        # Mostrar problema
        enunciado_y = area_img_y + area_img_h + sy(10)
        enunciado_h = sy(60)
        self.mostrar_texto(
            self.problema_actual,
            x=margen_x,
            y=enunciado_y,
            w=ancho_area,
            h=enunciado_h,
            fuente=obtener_fuente(sf(22)),
            color=(30, 30, 30),
            centrado=True
        )

        # Dibujar opciones (botones)
        opciones_y = enunciado_y + enunciado_h + sy(10)
        self.dibujar_opciones(y0=opciones_y)

        # Mostrar feedback debajo de las opciones
        if self.feedback:
            self.mostrar_texto(
                self.feedback,
                x=margen_x,
                y=opciones_y + sy(60),
                w=ancho_area,
                h=sy(40),
                fuente=obtener_fuente(sf(20), negrita=True),
                color=self.feedback_color,
                centrado=True
            )

        # Mostrar puntaje y racha con helpers de la clase base
        self.mostrar_puntaje(self.puntuacion, self.jugadas_totales, "Puntuación")
        self.mostrar_racha()
