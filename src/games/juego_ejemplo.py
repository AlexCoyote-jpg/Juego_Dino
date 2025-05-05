import pygame
import random

def juego_sumas(pantalla, config):
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Segoe UI", 48)
    font_small = pygame.font.SysFont("Segoe UI", 32)
    running = True
    puntos = 0
    input_text = ""
    feedback = ""
    color_feedback = (0, 0, 0)

    # Genera una nueva suma
    def nueva_suma():
        a = random.randint(1, 99)
        b = random.randint(1, 99)
        return a, b, a + b

    a, b, resultado = nueva_suma()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.key == pygame.K_RETURN:
                    # Verifica la respuesta
                    try:
                        if int(input_text) == resultado:
                            puntos += 1
                            feedback = "¡Correcto!"
                            color_feedback = (0, 180, 0)
                            a, b, resultado = nueva_suma()
                        else:
                            feedback = "Incorrecto"
                            color_feedback = (200, 0, 0)
                    except ValueError:
                        feedback = "Ingresa un número"
                        color_feedback = (200, 0, 0)
                    input_text = ""
                elif event.unicode.isdigit():
                    input_text += event.unicode

        pantalla.fill((240, 240, 255))
        # Muestra la suma
        suma_text = font.render(f"{a} + {b} =", True, (30, 30, 30))
        pantalla.blit(suma_text, (100, 120))

        # Muestra la entrada del usuario
        input_box = pygame.Rect(350, 120, 140, 60)
        pygame.draw.rect(pantalla, (255, 255, 255), input_box)
        pygame.draw.rect(pantalla, (100, 100, 200), input_box, 2)
        input_render = font.render(input_text, True, (30, 30, 30))
        pantalla.blit(input_render, (input_box.x + 10, input_box.y + 5))

        # Muestra el puntaje
        puntos_text = font_small.render(f"Puntos: {puntos}", True, (30, 30, 30))
        pantalla.blit(puntos_text, (100, 40))

        # Muestra feedback
        if feedback:
            feedback_text = font_small.render(feedback, True, color_feedback)
            pantalla.blit(feedback_text, (100, 200))

        # Instrucciones
        instrucciones = font_small.render("Escribe el resultado y presiona Enter. ESC para salir.", True, (60, 60, 60))
        pantalla.blit(instrucciones, (100, 320))

        pygame.display.flip()
        clock.tick(30)