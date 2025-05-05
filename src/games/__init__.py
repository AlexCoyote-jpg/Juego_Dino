# Permite que la carpeta sea reconocida como un módulo de Python
# En __init__:
# Permite que la carpeta sea reconocida como un módulo de Python

from .juego_ejemplo import juego_sumas
# from .otro_juego import otro_juego  # Descomenta y agrega más juegos aquí

# Lista centralizada de juegos (opcional, para usar en el menú principal)
JUEGOS_DISPONIBLES = [
    {"nombre": "Juego de Sumas", "func": juego_sumas , "imagen": "dino1"},
    {"nombre": "Juego de Sumas", "func": juego_sumas , "imagen": "dino2"},
    {"nombre": "Juego de Sumas", "func": juego_sumas , "imagen": "dino3"},
    {"nombre": "Juego de Sumas", "func": juego_sumas , "imagen": "dino4"},
    {"nombre": "Juego de Sumas", "func": juego_sumas , "imagen": "dino1"},
    
    
    # {"nombre": "Otro Juego", "func": otro_juego},
]

# Ejemplo de cómo podrías usarlo en el menú principal
#from games import JUEGOS_DISPONIBLES

# Luego en tu clase MenuPrincipal:
#self.juegos = JUEGOS_DISPONIBLES

# ejemplo de cómo podrías usarlo en el menú principal 2
'''
self.juegos = [
    {"nombre": "Juego de Sumas", "rect": pygame.Rect(...), "func": juego_sumas},
    # {"nombre": "Otro Juego", "rect": pygame.Rect(...), "func": otro_juego},
]
# En mostrar_juegos:
for juego in self.juegos:
    dibujar_caja_texto(self.pantalla, *juego["rect"], (180, 220, 255))
    mostrar_texto_adaptativo(self.pantalla, juego["nombre"], *juego["rect"], self.font_texto, (30,30,30), centrado=True)
# En run:
if event.type == pygame.MOUSEBUTTONDOWN:
    for juego in self.juegos:
        if juego["rect"].collidepoint(event.pos):
            juego["func"](self.pantalla, self.config)
'''