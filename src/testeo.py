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

def main():
    pygame.init()
    pantalla = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
    clock = pygame.time.Clock()

    nombre = "DinoMath"
    config = {}
    dificultad = 1
    fondo = None
    navbar = None
    images = {}
    sounds = {}
    def return_to_menu(): pass

    juego = JuegoBase(nombre, pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu)

    # Lista de problemas
    problemas = [generar_problema() for _ in range(10)]
    indice = 0
    puntaje = 0

    def siguiente_problema():
        nonlocal indice
        if indice < len(problemas):
            texto, resultado = problemas[indice]
            juego.operacion_actual = texto
            juego.respuesta_correcta = resultado
            juego.opciones = juego.generar_opciones(resultado, 3)
        else:
            juego.operacion_actual = "¡Juego terminado!"
            juego.opciones = []
    
    siguiente_problema()

    corriendo = True
    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                corriendo = False
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for i, boton in enumerate(getattr(juego, "opcion_botones", [])):
                    # Suponiendo que cada 'boton' es un objeto con .rect y .texto
                    if boton.rect.collidepoint(mouse_pos):
                        valor = int(boton.texto)
                        if valor == juego.respuesta_correcta:
                            puntaje += 1
                            juego.mostrar_feedback(True)
                        else:
                            juego.mostrar_feedback(False, respuesta_correcta=juego.respuesta_correcta)
                        indice += 1
                        siguiente_problema()
                        break
            else:
                juego.handle_event(evento)

        juego.puntuacion = puntaje
        juego.total_preguntas = len(problemas)
        juego.update()
        juego.draw()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()