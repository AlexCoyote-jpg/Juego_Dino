import pygame
import sys
import random
from pygame.locals import *
from core.juego_base import JuegoBase  # Usa tu base común
from ui.components.utils import obtener_fuente
# Si tienes imágenes, importa/carga aquí

def generar_problema_division(nivel):
    """Genera un problema de división según el nivel"""
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
        self.problema_actual = ""
        self.respuesta_correcta = None
        self.opciones = []
        self.puntuacion = 0
        self.jugadas_totales = 0
        self.tiempo_mensaje = 0
        self.mensaje = ""
        self.opcion_botones = []
        self.posicion_dino = 0
        self.total_pasos = 3
        self.nivel_completado = False
        self.cargar_imagenes()
        self.generar_problema()

    def cargar_imagenes(self):
        self.dino_mama_img = self.images.get("dino_mama")
        self.dino_bebe_img = self.images.get("dino_bebe")
        self.roca_img = self.images.get("roca")

    def generar_problema(self):
        nivel = self._nivel_from_dificultad(self.dificultad)  # Usa el método de JuegoBase
        problema, respuesta = generar_problema_division(nivel)
        self.problema_actual = problema
        self.respuesta_correcta = respuesta
        self.opciones = self.generar_opciones(self.respuesta_correcta)
        random.shuffle(self.opciones)
        self.tiempo_mensaje = 0
        self.mensaje = ""

    def handle_event(self, evento):
        super().handle_event(evento)
        if evento.type == MOUSEBUTTONDOWN and evento.button == 1:
            for btn in self.opcion_botones:
                if btn.rect.collidepoint(evento.pos):
                    self.jugadas_totales += 1
                    es_correcto = int(btn.texto) == self.respuesta_correcta
                    if es_correcto:
                        self.puntuacion += 1
                        self.posicion_dino += 1
                        self.mostrar_feedback(True)
                        if self.posicion_dino > self.total_pasos:
                            self.nivel_completado = True
                            self.mostrar_mensaje_temporal("¡Felicidades! ¡Has rescatado al bebé dinosaurio!")
                        else:
                            self.generar_problema()
                    else:
                        self.mostrar_feedback(False, self.respuesta_correcta)
                    return

    def update(self, dt=None):
        if self.tiempo_mensaje > 0:
            self.tiempo_mensaje -= 1

    def draw(self, surface):
        self.dibujar_fondo()
        self.mostrar_titulo()

        # Mensaje debajo del título
        self.mostrar_texto(
            "¡Ayuda a mamá dinosaurio a rescatar a su bebé perdido!",
            x=40,
            y=140,  # Ajusta la posición Y según el diseño de tu título
            w=self.ANCHO - 80,
            h=40,
            fuente=obtener_fuente(30, negrita=False),
            color=(80, 80, 80),
            centrado=True
        )

        # Camino y personajes
        camino_x = 250
        camino_y = 250
        espacio_rocas = 120

        # Mamá dino
        mama_x = 100
        if self.posicion_dino > 0:
            mama_x = camino_x + (self.posicion_dino - 1) * espacio_rocas
        if self.dino_mama_img:
            self.pantalla.blit(self.dino_mama_img, (mama_x, camino_y))

        # Rocas
        if self.roca_img:
            for i in range(self.total_pasos):
                self.pantalla.blit(self.roca_img, (camino_x + i * espacio_rocas, camino_y))

        # Bebé dino
        if self.dino_bebe_img:
            bebe_x = camino_x + self.total_pasos * espacio_rocas + 20
            self.pantalla.blit(self.dino_bebe_img, (bebe_x, camino_y + 10))

        # Problema
        enunciado_y = camino_y + 120
        enunciado_h = 80
        enunciado_fuente = obtener_fuente(28, negrita=False)
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

        # Opciones
        if not self.nivel_completado:
            opciones_y = enunciado_y + enunciado_h + 30
            self.dibujar_opciones(y0=opciones_y)
        else:
            self.mostrar_texto(
                "¡Nivel completado! ¡Has rescatado al bebé dinosaurio!",
                x=40,
                y=enunciado_y + enunciado_h + 30,
                w=self.ANCHO - 80,
                h=60,
                fuente=obtener_fuente(30, negrita=True),
                color=(0, 120, 0),
                centrado=True
            )

        # Feedback
        self.dibujar_feedback()

        # Puntaje
        self.mostrar_puntaje(self.puntuacion, self.jugadas_totales, "Puntuación")

# Para usar esta clase, crea una instancia pasando los argumentos requeridos por JuegoBase.
