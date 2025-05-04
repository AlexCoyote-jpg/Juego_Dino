import pygame
from utils import Boton

def main():
    pygame.init()
    pantalla = pygame.display.set_mode((600, 300))
    pygame.display.set_caption("Prueba de Botones")

    # Crear botones de diferentes estilos
    botones = [
        Boton("Apple", 50, 50, 150, 60, estilo="apple", color_hover=(200, 220, 255)),
        Boton("Flat", 250, 50, 150, 60, estilo="flat", color_hover=(200, 220, 255)),
        Boton("Round", 450, 50, 60, 60, estilo="round", color_hover=(255, 200, 200)),
    ]

    corriendo = True
    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                for boton in botones:
                    if boton.collidepoint(evento.pos):
                        print(f"Botón '{boton.texto}' presionado")

        pantalla.fill((240, 240, 240))
        for boton in botones:
            boton.draw(pantalla)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()