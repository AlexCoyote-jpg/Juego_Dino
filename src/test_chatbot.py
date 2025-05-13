import pygame
from chatbot.chatbot import ChatBotScreen  # Import absoluto

ANCHO, ALTO = 800, 600

def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Test ChatBotScreen en área reducida")
    clock = pygame.time.Clock()

    # Área donde se dibujará el chatbot (por ejemplo, centrado y más pequeño)
    area_chatbot = pygame.Rect(150, 100, 600, 400)
    chatbot_screen = ChatBotScreen(None, area_chatbot)

    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        pantalla.fill((30, 30, 30))  # Fondo general de la ventana
        chatbot_screen.handle_events(events)
        chatbot_screen.update(clock.get_time())
        chatbot_screen.draw(pantalla)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()