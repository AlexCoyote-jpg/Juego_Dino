# screen_manager.py
"""
Gestor funcional de pantallas: maneja el cambio y la gestión de diferentes pantallas o vistas del juego.
"""

def create_screen_manager():
    return {"current_screen": None}

def set_screen(screen_manager, screen):
    screen_manager["current_screen"] = screen
    return screen_manager

def update_screen(screen_manager):
    screen = screen_manager["current_screen"]
    if screen and hasattr(screen, "update"):
        screen.update()

def draw_screen(screen_manager, surface):
    screen = screen_manager["current_screen"]
    if screen and hasattr(screen, "draw"):
        screen.draw(surface)
