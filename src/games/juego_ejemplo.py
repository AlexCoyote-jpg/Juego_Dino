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
    print("¡Juego de sumas iniciado!")

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


'''
# Ejemplo de uso
# import pygame
import time
from games.juego_ejemplo import juego_sumas  # Importa tu juego aquí
# ...otros imports necesarios...

class MenuPrincipal:
    # ...otros métodos y __init__...

    def mostrar_juegos(self, dificultad):
        # Dibuja el título de la sección de juegos
        x_t, y_t, w_t, h_t = self.sx(130), self.sy(110), self.sx(640), self.sy(60)
        dibujar_caja_texto(self.pantalla, x_t, y_t, w_t, h_t, (70, 130, 180))
        mostrar_texto_adaptativo(
            self.pantalla,
            f"Juegos de nivel {dificultad}",
            x_t, y_t, w_t, h_t,
            self.font_titulo,
            (255,255,255),
            centrado=True
        )
        # --- Botón para el juego de sumas ---
        # Puedes agregar más botones para otros juegos aquí
        self.boton_sumas = pygame.Rect(self.sx(250), self.sy(220), self.sx(300), self.sy(60))
        dibujar_caja_texto(self.pantalla, *self.boton_sumas, (180, 220, 255))
        mostrar_texto_adaptativo(
            self.pantalla, "Juego de Sumas", *self.boton_sumas, self.font_texto, (30,30,30), centrado=True
        )

    def run(self):
        running = True
        last_time = time.time()
        while running:
            now = time.time()
            dt = now - last_time
            last_time = now

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    # Redimensiona la pantalla si es necesario
                    pass
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    # --- Detecta clic en el botón del juego de sumas ---
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if hasattr(self, "boton_sumas") and self.boton_sumas.collidepoint(event.pos):
                            # Llama al juego de sumas y pausa el menú principal hasta que termine
                            juego_sumas(self.pantalla, self.config)
                            # Al volver, puedes refrescar la pantalla o el menú si es necesario

            # --- Renderiza el menú principal y los botones ---
            self.pantalla.fill((255, 255, 255))
            self.mostrar_juegos(self.dificultad_seleccionada)
            pygame.display.flip()
            self.clock.tick(60)

# Notas:
# - Puedes agregar más botones para otros juegos repitiendo el patrón de self.boton_sumas.
# - Si tienes varios juegos, usa una lista de botones y un diccionario para asociar cada botón a una función de juego.
# - Puedes modificar el texto, colores y posiciones de los botones según tu diseño.
# '''