import pygame
import sys
from chatbot.Configs import LLAMA
from chatbot.Conexion import obtener_respuesta

pygame.init()

# Constantes
ANCHO, ALTO = 800, 600
FUENTE = pygame.font.SysFont("arial", 20)
COLOR_FONDO = (30, 30, 30)
COLOR_TEXTO = (255, 255, 255)
COLOR_ENTRADA = (50, 50, 50)

# Inicializar ventana
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Chatbot en Pygame")

# Variables
entrada_usuario = ""
historial = []

def renderizar_historial():
    y_offset = 10
    for mensaje in historial[-20:]:  # Mostrar últimos 20 mensajes
        render = FUENTE.render(mensaje, True, COLOR_TEXTO)
        pantalla.blit(render, (10, y_offset))
        y_offset += 25

def main():
    global entrada_usuario
    clock = pygame.time.Clock()

    while True:
        pantalla.fill(COLOR_FONDO)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    if entrada_usuario.strip():
                        historial.append("Tú: " + entrada_usuario)
                        respuesta = obtener_respuesta(entrada_usuario, LLAMA.model, LLAMA.api_key)
                        historial.append("Bot: " + respuesta)
                        entrada_usuario = ""
                elif evento.key == pygame.K_BACKSPACE:
                    entrada_usuario = entrada_usuario[:-1]
                else:
                    entrada_usuario += evento.unicode

        # Mostrar historial
        renderizar_historial()

        # Mostrar caja de entrada
        pygame.draw.rect(pantalla, COLOR_ENTRADA, (10, ALTO - 40, ANCHO - 20, 30))
        texto_render = FUENTE.render(entrada_usuario, True, COLOR_TEXTO)
        pantalla.blit(texto_render, (15, ALTO - 35))

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()