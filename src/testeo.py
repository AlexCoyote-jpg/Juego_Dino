import pygame
import random
from core.game_base import JuegoBase

def generar_problema():
    a = random.randint(1, 20)
    b = random.randint(1, 20)
    op = random.choice(["+", "-"])
    if op == "+":
        resultado = a + b
    else:
        resultado = a - b
    texto = f"{a} {op} {b} = ?"
    return texto, resultado

class DinoMathGame(JuegoBase):
    def __init__(self, pantalla, config=None, dificultad=1, fondo=None, navbar=None, images=None, sounds=None, return_to_menu=None):
        nombre = "DinoMath"
        config = config or {}
        images = images or {}
        sounds = sounds or {}
        if return_to_menu is None:
            return_to_menu = lambda: None
        super().__init__(nombre, pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu)
        self.problemas = [generar_problema() for _ in range(10)]
        self.indice = 0
        self.puntaje = 0
        self.siguiente_problema()

    def siguiente_problema(self):
        if self.indice < len(self.problemas):
            texto, resultado = self.problemas[self.indice]
            self.operacion_actual = texto
            self.respuesta_correcta = resultado
            self.opciones = self.generar_opciones(resultado, 3)
        else:
            self.operacion_actual = "¡Juego terminado!"
            self.opciones = []

    def run(self):
        clock = pygame.time.Clock()
        corriendo = True
        while corriendo:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    corriendo = False
                elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    corriendo = False
                elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    for i, boton in enumerate(getattr(self, "opcion_botones", [])):
                        if boton.rect.collidepoint(mouse_pos):
                            try:
                                valor = int(boton.texto)
                            except ValueError:
                                valor = None
                            if valor == getattr(self, "respuesta_correcta", None):
                                self.puntaje += 1
                                self.mostrar_feedback(True)
                            else:
                                self.mostrar_feedback(False, respuesta_correcta=getattr(self, "respuesta_correcta", None))
                            self.indice += 1
                            self.siguiente_problema()
                            break
                else:
                    self.handle_event(evento)

            self.puntuacion = self.puntaje
            self.total_preguntas = len(self.problemas)
            self.update()
            self.draw()
            pygame.display.flip()
            clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    pygame.init()
    pantalla = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
    juego = DinoMathGame(pantalla)
    juego.run()