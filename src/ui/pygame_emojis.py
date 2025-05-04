import pygame
import requests
from io import BytesIO
from time import *
from emoji import *

memory = {}

def save_data(key, value):
    memory[key] = value

def get_emoji_name(emoji):
    hex_code_points = [hex(ord(char))[2:].upper() for char in emoji]
    unicode_strings = [f"{code_point}" for code_point in hex_code_points]
    return ' '.join(unicode_strings)

def get_img(emoji):
    name_emoji = str(get_emoji_name(emoji))
    url = "https://emojiapi.dev/api/v1/"+str(name_emoji)+"/412.png"
    response = requests.get(str(url))
    save_data(str(emoji), response.content)
    return response.content

class emojis:
    def __init__(self, screen):
        self.screen = screen

    def load_emoji(self, emoji, xy):
        if str(emoji) in memory:
            img_data = memory[str(emoji)]
        else:
            img_data = get_img(emoji)
        if img_data:
            img = BytesIO(img_data)
            try:
                image = pygame.image.load(img).convert_alpha()
            except pygame.error as e:
                print(f"Error loading emoji image: {e}")
                image = None
            return image
        else:
            return None

    def render_text_and_emojis(self, text, color, xy, font_size):
        screen = self.screen
        x, y = xy
        v, b, w = color
        parts = text.split("/e")
        font = pygame.font.Font(None, font_size)
        current_x = x

        for i, part in enumerate(parts):
            if part:
                if i % 2 == 0:
                    text_surface = font.render(part, True, (v, b, w))
                    text_rect = text_surface.get_rect()
                    screen.blit(text_surface, (current_x, y))
                    current_x += text_surface.get_width()
                else:
                    emoji_image = self.load_emoji(part, (current_x, y))
                    scaled_emoji = pygame.transform.scale(emoji_image, (text_rect.height, text_rect.height))
                    screen.blit(scaled_emoji, (current_x, y))
                    current_x += scaled_emoji.get_width()

        if parts[-1]:
            text_surface = font.render(parts[-1], True, (v, b, w))
            screen.blit(text_surface, (current_x, y))
