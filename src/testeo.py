import pygame
from core.scale.responsive_scaler_animated import ResponsiveScalerAnimado
from core.decoration.background_game import FondoAnimado
from core.decoration.ui_draw_helpers import (
    mostrar_titulo, mostrar_instrucciones, mostrar_pregunta,
    dibujar_opciones, mostrar_racha, mostrar_puntaje
)
from ui.components.utils import obtener_fuente
from core.decoration.effects import EffectsMixin
from core.decoration.paleta import PALETA, PALETA_LISTA

class JuegoBase(EffectsMixin):
    def __init__(self, pantalla, nombre_juego="Mi Juego", dificultad="1"):
        self.pantalla = pantalla
        self.ANCHO, self.ALTO = pantalla.get_size()
        self.nombre_juego = nombre_juego
        self.dificultad = dificultad
        self.racha_correctas = 0
        self.mejor_racha = 0
        self.racha_anterior = 0
        self.juegos_ganados = 0
        self.juegos_totales = 0
        self.tiempo_cambio_racha = 0
        self.sonido_activado = True
        self.sounds = {}
        self.navbar_height = 0

        # Escalado responsive
        self.scaler = ResponsiveScalerAnimado(self.ANCHO, self.ALTO)
        self.sx = self.scaler.sx
        self.sy = self.scaler.sy
        self.sf = self.scaler.sf

        # Fuentes
        self.fuente = obtener_fuente(self.sf(28))
        self.fuente_titulo = obtener_fuente(self.sf(36))
        self.fuente_pequeña = obtener_fuente(self.sf(20))

        # Fondo animado
        self.fondo = FondoAnimado(pantalla, self.ANCHO, self.ALTO, self.navbar_height, self.sx, self.sy)

        # Otros atributos visuales
        self.mensaje = ""
        self.tiempo_mensaje = 0
        self.mensaje_animacion = 1.0
        self.ui_elements = {}

    def manejar_eventos(self, eventos):
        for evento in eventos:
            if evento.type == pygame.QUIT:
                return False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return False
            if evento.type == pygame.VIDEORESIZE:
                self.ANCHO, self.ALTO = evento.size
                # Actualiza el escalador y los factores de escala
                self.scaler.update(self.ANCHO, self.ALTO)
                self.sx = self.scaler.sx
                self.sy = self.scaler.sy
                self.sf = self.scaler.sf
                # Actualiza las fuentes con el nuevo escalado
                self.fuente = obtener_fuente(self.sf(28))
                self.fuente_titulo = obtener_fuente(self.sf(36))
                self.fuente_pequeña = obtener_fuente(self.sf(20))
                # Rescala el fondo y sus elementos
                self.fondo.resize(self.ANCHO, self.ALTO)
        return True

    def actualizar(self):
        self.scaler.tick()
        self.fondo.actualizar_nubes()
        self.fondo.actualizar_burbujas()
        self.update_animacion_estrellas()
        self.update_particulas()

    def dibujar(self):
        # Recalcula las fuentes en cada frame para un escalado suave
        self.fuente = obtener_fuente(self.sf(28))
        self.fuente_titulo = obtener_fuente(self.sf(36))
        self.fuente_pequeña = obtener_fuente(self.sf(20))

        self.fondo.dibujar_fondo()
        mostrar_titulo(self.pantalla, self.nombre_juego, self.dificultad, self.fuente_titulo, self.navbar_height, self.sy, self.ANCHO, self.ui_elements)
        mostrar_pregunta(self.pantalla, self.operacion_actual, self.sx, self.sy, self.navbar_height, self.ANCHO, self.fuente)
        dibujar_opciones(
            self.pantalla,
            self.opciones,
            self.opcion_botones,
            self.fuente,
            self.sy,
            self.sx,
            self.ANCHO,
            self.ALTO
        )
        mostrar_racha(self)
        mostrar_puntaje(self, self.juegos_ganados, self.juegos_totales)
        mostrar_instrucciones(self.pantalla, self.sx, self.sy, self.ALTO, self.ANCHO, self.fuente_pequeña)
        self.dibujar_feedback()
        self.draw_animacion_estrellas()
        self.draw_particulas()

    def run(self):
        reloj = pygame.time.Clock()
        ejecutando = True
        while ejecutando:
            eventos = pygame.event.get()
            ejecutando = self.manejar_eventos(eventos)
            self.actualizar()
            self.dibujar()
            pygame.display.flip()
            reloj.tick(60)

class JuegoColores(JuegoBase):
    def __init__(self, pantalla):
        super().__init__(pantalla, "Colores Dinámicos", "1")
        self.preguntas = [
            {"pregunta": "¿Cuál es el color del cielo?", "opciones": ["Azul", "Rojo", "Verde", "Amarillo"], "respuesta": "Azul"},
            {"pregunta": "¿Cuál es el color de una manzana madura?", "opciones": ["Verde", "Rojo", "Azul", "Amarillo"], "respuesta": "Rojo"},
            {"pregunta": "¿Cuál es el color del sol?", "opciones": ["Amarillo", "Azul", "Verde", "Rosa"], "respuesta": "Amarillo"},
        ]
        self.indice_pregunta = 0
        self.cargar_pregunta_actual()

    def cargar_pregunta_actual(self):
        actual = self.preguntas[self.indice_pregunta]
        self.operacion_actual = actual["pregunta"]
        self.opciones = actual["opciones"]
        self.respuesta = actual["respuesta"]
        self.opcion_botones = []

    def manejar_eventos(self, eventos):
        for evento in eventos:
            if evento.type == pygame.QUIT:
                return False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return False
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                for i, btn in enumerate(self.opcion_botones):
                    if btn.rect.collidepoint(evento.pos):
                        seleccion = self.opciones[i]
                        self.juegos_totales += 1
                        if seleccion == self.respuesta:
                            self.racha_correctas += 1
                            self.juegos_ganados += 1
                            self.mejor_racha = max(self.mejor_racha, self.racha_correctas)
                            self.tiempo_cambio_racha = pygame.time.get_ticks() / 1000
                            self.mostrar_feedback(es_correcto=True)
                        else:
                            self.racha_correctas = 0
                            self.tiempo_cambio_racha = pygame.time.get_ticks() / 1000
                            self.mostrar_feedback(es_correcto=False)
                        # Siguiente pregunta
                        self.indice_pregunta = (self.indice_pregunta + 1) % len(self.preguntas)
                        self.cargar_pregunta_actual()
                        break
            if evento.type == pygame.VIDEORESIZE:
                self.ANCHO, self.ALTO = evento.size
                self.scaler.update(self.ANCHO, self.ALTO)
                self.sx = self.scaler.sx
                self.sy = self.scaler.sy
                self.sf = self.scaler.sf
                self.fuente = obtener_fuente(self.sf(28))
                self.fuente_titulo = obtener_fuente(self.sf(36))
                self.fuente_pequeña = obtener_fuente(self.sf(20))
                self.fondo.resize(self.ANCHO, self.ALTO)
        return True

if __name__ == "__main__":
    pygame.init()
    pantalla = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
    juego = JuegoColores(pantalla)
    juego.run()
    pygame.quit()
