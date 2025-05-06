import pygame

def iniciar_juego_sumas(pantalla, config, dificultad, fondo, navbar):
    reloj = pygame.time.Clock()
    running = True

    while running:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                running = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return  # salir del juego

        fondo.update(1)
        fondo.draw(pantalla)

        # Dibujo de contenido del juego
        font = pygame.font.SysFont("Arial", 40)
        mensaje = f"Sumas - Nivel {dificultad}"
        texto = font.render(mensaje, True, (20, 20, 20))
        pantalla.blit(texto, (100, 100))

        navbar.draw(pantalla, config.get("logo", None))  # muestra navbar sobre el juego
        pygame.display.flip()
        reloj.tick(60)
