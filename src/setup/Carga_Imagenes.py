import pygame

from setup.Carga_Configs import configuracion

def cargar_imagen_segura(self, ruta, tamaño, color_sustituto, texto_sustituto=""):
        try:
            img = pygame.image.load(ruta)
            return pygame.transform.scale(img, tamaño)
        except pygame.error:
            # Crear sustituto para la imagen
            sustituto = pygame.Surface(tamaño)
            sustituto.fill(color_sustituto)
            if texto_sustituto:
                font = pygame.font.SysFont('Arial', 24)
                text = font.render(texto_sustituto, True, BLANCO)
                text_rect = text.get_rect(center=(tamaño[0]//2, tamaño[1]//2))
                sustituto.blit(text, text_rect)
            return sustituto