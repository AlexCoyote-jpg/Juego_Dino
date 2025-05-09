import pygame
import sys
import random
from pygame.locals import *
from core.juego_base import JuegoBase  # Asegúrate de que la ruta sea correcta
from ui.utils import obtener_fuente

def generar_problema_multiplicacion(nivel):
    """Genera un problema de multiplicación según el nivel"""
    if nivel == "Básico":
        a = random.randint(1, 5)
        b = random.randint(1, 5)
        problema = f"Un dinosaurio pone {a} huevos cada semana. ¿Cuántos huevos pondrá en {b} semanas?"
        respuesta = a * b
    elif nivel == "Medio":
        a = random.randint(2, 10)
        b = random.randint(2, 10)
        problema = f"Hay {a} nidos con {b} huevos cada uno. ¿Cuántos huevos hay en total?"
        respuesta = a * b
    else:  # Avanzado
        a = random.randint(5, 15)
        b = random.randint(5, 10)
        c = random.randint(1, 5)
        problema = f"Un dinosaurio come {a} hojas por día. Si hay {b} dinosaurios y comen durante {c} días, ¿cuántas hojas comerán en total?"
        respuesta = a * b * c
    
    return problema, respuesta


class JuegoCazadorNumeros(JuegoBase):
    def __init__(self, pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu):
        super().__init__('Dino Cazador de Números', pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu)
        self.problema_actual = ""
        self.respuesta_correcta = None
        self.opciones = []
        self.puntuacion = 0
        self.jugadas_totales = 0
        self.tiempo_mensaje = 0
        self.mensaje = ""
        self.opcion_botones = []
        self.cargar_imagenes()  # <-- Agrega esta línea
        self.generar_problema()

    def cargar_imagenes(self):
        self.dino_img = self.images.get("dino3")
        self.fruta_img = self.images.get("fruta")

    def generar_problema(self):
        # Ejemplo simple: multiplicación básica, puedes adaptar según dificultad
        a = random.randint(2, 9)
        b = random.randint(2, 9)
        self.problema_actual = f"¿Cuánto es {a} × {b}?"
        self.respuesta_correcta = a * b
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
                    self.mostrar_feedback(es_correcto, self.respuesta_correcta)
                    self.generar_problema()
                    return

    def update(self, dt=None):
        if self.tiempo_mensaje > 0:
            self.tiempo_mensaje -= 1

    def draw(self, surface):
        self.dibujar_fondo()
        self.mostrar_titulo()

        # Enunciado grande, centrado, debajo del título y arriba de los botones
        enunciado_y = self.navbar_height + 100
        enunciado_h = max(90, int(self.ALTO * 0.13))
        enunciado_fuente = obtener_fuente(max(44, int(self.ALTO * 0.055)), negrita=True)
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

        # Opciones de respuesta, debajo del enunciado
        opciones_y = enunciado_y + enunciado_h + 30
        self.dibujar_opciones(y0=opciones_y)

        # Imagen decorativa (opcional)
        if self.dino_img and self.opcion_botones:
            nuevo_w = int(self.ANCHO * 0.13)
            ow, oh = self.dino_img.get_size()
            nuevo_h = int(oh * nuevo_w / ow)
            dino_small = pygame.transform.smoothscale(self.dino_img, (nuevo_w, nuevo_h))
            first_btn = self.opcion_botones[0]
            x_dino = max(10, first_btn.rect.left - nuevo_w - 10)
            y_dino = first_btn.rect.centery - nuevo_h // 2
            self.pantalla.blit(dino_small, (x_dino, y_dino))

        # Feedback
        self.dibujar_feedback()

        # Puntaje
        self.mostrar_puntaje(self.puntuacion, self.jugadas_totales, "Puntaje")

# Para usar esta clase, crea una instancia pasando los argumentos requeridos por JuegoBase.
