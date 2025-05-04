import pygame
import pygame_emojis

# Initialize Pygame and create a window
pygame.init()
screen = pygame.display.set_mode((640, 480))

# Load and render emojis
emojis = pygame_emojis.emojis(screen)
emojis.render_text_and_emojis("Hello /e😀/e /e👍/e", (255, 255, 255), (0, 0), 60)

# Update the display
pygame.display.flip()

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

# Quit Pygam
pygame.quit()