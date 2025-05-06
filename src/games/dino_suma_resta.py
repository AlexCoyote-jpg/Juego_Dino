import pygame
import random
import sys
from ui.utils import Boton, dibujar_caja_texto, mostrar_texto_adaptativo
from ui.navigation_bar import NavigationBar
from core.game_state import JuegoBase

# Colores para botones de opciones
VERDE_OPCIONES = (180, 240, 180)
VERDE_OPCIONES_HOVER = (120, 200, 120)

def generar_problema_suma_resta(nivel):
    if nivel == "Básico":
        a, b = random.randint(1, 10), random.randint(1, 10)
        if random.choice([True, False]):
            return f"{a} + {b}", a + b
        else:
            a, b = max(a, b), min(a, b)
            return f"{a} - {b}", a - b
    elif nivel == "Medio":
        a, b = random.randint(10, 50), random.randint(1, 30)
        if random.choice([True, False]):
            return f"{a} + {b}", a + b
        else:
            a, b = max(a, b), min(a, b)
            return f"{a} - {b}", a - b
    else:  # Avanzado
        a, b, c = random.randint(10, 50), random.randint(1, 30), random.randint(1, 10)
        if random.choice([True, False]):
            return f"{a} + {b} - {c}", a + b - c
        else:
            return f"{a} - {b} + {c}", a - b + c

def generar_opciones(respuesta):
    opciones = [respuesta]
    while len(opciones) < 3:
        op = respuesta + random.choice([-3, -2, -1, 1, 2, 3, 4, -4])
        if op not in opciones:
            opciones.append(op)
    random.shuffle(opciones)
    return opciones

class JuegoSumaResta(JuegoBase):
    def __init__(self, pantalla, config, dificultad, fondo, navbar, images, sounds):
        super().__init__('Dino Suma y Resta', pantalla, config, dificultad, fondo, navbar, images, sounds)
        self.nivel_actual = self._nivel_from_dificultad(dificultad)
        self.puntuacion = 0
        self.jugadas_totales = 0
        self.tiempo_mensaje = 0
        self.mensaje = ""
        self.logo_img = images.get("dino1") if images else None
        self.dino_img = images.get("dino1") if images else None
        self.cueva_img = images.get("cueva") if images else None
        self.opciones_rects = []
        self.generar_problema()

    def _nivel_from_dificultad(self, dificultad):
        if dificultad == "Fácil":
            return "Básico"
        elif dificultad == "Normal":
            return "Medio"
        else:
            return "Avanzado"

    def generar_problema(self):
        self.problema_actual, self.respuesta_correcta = generar_problema_suma_resta(self.nivel_actual)
        self.opciones = generar_opciones(self.respuesta_correcta)

    def dibujar_pantalla_home(self):
        # Título
        dibujar_caja_texto(self.pantalla, self.ANCHO//2 - 320, 110, 640, 60, (70, 130, 180))
        mostrar_texto_adaptativo(
            self.pantalla, "Bienvenido a Dino Suma y Resta", self.ANCHO//2 - 320, 110, 640, 60,
            self.fuente_titulo, (255,255,255), centrado=True
        )
        # Instrucciones
        dibujar_caja_texto(self.pantalla, self.ANCHO//2 - 300, 180, 600, 300, (255, 255, 255, 200))
        instrucciones = (
            "¡Ayuda a Dino a resolver problemas de matemáticas!\n\n"
            "Nivel Básico: Sumas y restas simples\n"
            "Nivel Medio: Números más grandes\n"
            "Nivel Avanzado: Problemas con múltiples operaciones\n\n"
            "Haz clic en los botones de arriba para comenzar."
        )
        mostrar_texto_adaptativo(
            self.pantalla, instrucciones, self.ANCHO//2 - 300, 180, 600, 300,
            self.fuente_texto, (30,30,30), centrado=True
        )

    def dibujar_pantalla_juego(self):
        # Imágenes decorativas
        if self.dino_img:
            self.pantalla.blit(self.dino_img, (100, 240))
        if self.cueva_img:
            self.pantalla.blit(self.cueva_img, (self.ANCHO - 250, 240))
        # Título
        mostrar_texto_adaptativo(
            self.pantalla, f"Dino Suma y Resta - Nivel {self.nivel_actual}",
            self.ANCHO//2 - 320, 100, 640, 60, self.fuente_titulo, (70, 130, 180), centrado=True
        )
        # Problema
        mostrar_texto_adaptativo(
            self.pantalla, self.problema_actual, self.ANCHO//2 - 200, 170, 400, 60,
            self.fuente_texto, (30,30,30), centrado=True
        )
        # Opciones
        self.opciones_rects = []
        total_w = 3 * 100 + 2 * 60
        x_ini = (self.ANCHO - total_w) // 2
        for i, opcion in enumerate(self.opciones):
            x = x_ini + i * (100 + 60)
            rect = Boton(
                str(opcion), x, 390, 100, 70,
                color_normal=VERDE_OPCIONES,
                color_hover=VERDE_OPCIONES_HOVER,
                color_texto=(30, 30, 30),
                fuente=self.fuente_texto,
                border_radius=18,
                estilo="apple"
            )
            rect.draw(self.pantalla)
            self.opciones_rects.append(rect.rect)
        # Mensaje de retroalimentación
        if self.tiempo_mensaje > 0:
            color_msg = (152, 251, 152) if "Correcto" in self.mensaje else (255, 182, 193)
            dibujar_caja_texto(self.pantalla, self.ANCHO//2 - 250, 480, 500, 50, color_msg)
            mostrar_texto_adaptativo(
                self.pantalla, self.mensaje, self.ANCHO//2 - 250, 480, 500, 50,
                self.fuente_texto, (30,30,30), centrado=True
            )
            self.tiempo_mensaje -= 1
        # Puntuación
        dibujar_caja_texto(self.pantalla, 20, self.ALTO - 50, 180, 40, (70, 130, 180))
        mostrar_texto_adaptativo(
            self.pantalla, f"Puntuación: {self.puntuacion}/{self.jugadas_totales}",
            20, self.ALTO - 50, 180, 40, self.fuente_texto, (255,255,255), centrado=True
        )

    def manejar_eventos_juego(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            for i, rect in enumerate(self.opciones_rects):
                if rect.collidepoint(evento.pos):
                    self.jugadas_totales += 1
                    if self.opciones[i] == self.respuesta_correcta:
                        self.mostrar_mensaje_temporal("¡Correcto! ¡Muy bien!")
                        self.puntuacion += 1
                    else:
                        self.mostrar_mensaje_temporal(f"Incorrecto. La respuesta correcta era {self.respuesta_correcta}.")
                    self.generar_problema()
                    return True
        return False

    def mostrar_mensaje_temporal(self, mensaje, tiempo=60):
        self.mensaje = mensaje
        self.tiempo_mensaje = tiempo

    # El método ejecutar y el resto de la integración ya la tienes en tu sistema base

# Para integrarlo en tu menú principal:
# from games.dino_suma_resta import JuegoSumaResta
# Y en JUEGOS_DISPONIBLES: {"nombre": "Dino Sumas/Resta", "func": JuegoSumaResta, ...}