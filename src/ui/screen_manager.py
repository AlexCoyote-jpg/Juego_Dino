"""
Gestor funcional de pantallas: maneja el cambio y la gestión de diferentes pantallas o vistas del juego.
"""

def create_screen_manager():
    return {"current_screen": None}

def set_screen(screen_manager, screen):
    screen_manager["current_screen"] = screen
    return screen_manager

# Obtener la pantalla activa
def get_screen(screen_manager):
    return screen_manager.get("current_screen")

# Delegar evento al screen activo
def handle_event_screen(screen_manager, eventos):
    screen = screen_manager["current_screen"]
    for event in eventos:
        if hasattr(screen, "handle_event"):
            screen.handle_event(event)

# Actualizar lógica del screen activo (puede incluir dt)
def update_screen(screen_manager, dt=None):
    screen = screen_manager.get("current_screen")
    if screen and hasattr(screen, "update"):
        try:
            if dt is not None:
                screen.update(dt)
            else:
                screen.update()
        except TypeError:
            screen.update()

# Dibujar la pantalla activa
def draw_screen(screen_manager, surface):
    screen = screen_manager.get("current_screen")
    if screen and hasattr(screen, "draw"):
        screen.draw(surface)

# Clases de pantallas base que delegan en MenuPrincipal
class HomeScreen:
    def __init__(self, menu):
        self.menu = menu
    
    def handle_event(self, eventos):
        # Home no necesita eventos propios
        pass

    def update(self, dt=None):
        pass

    def draw(self, surface):
        self.menu.mostrar_home()

class JuegosScreen:
    def __init__(self, menu, dificultad):
        self.menu = menu
        self.dificultad = dificultad

    def handle_event(self, eventos):
        # Delegar clics de juegos
        if hasattr(self.menu, "handle_juegos_eventos"):
            self.menu.handle_juegos_eventos(eventos)

    def update(self, dt=None):
        pass

    def draw(self, surface):
        self.menu.mostrar_juegos(self.dificultad)

class ChatBotScreen:
    def __init__(self, menu):
        self.menu = menu

    def handle_event(self, eventos):
        # ChatBot puede procesar teclas o clics
        if hasattr(self.menu, "handle_chatbot_eventos"):
            self.menu.handle_chatbot_eventos(eventos)

    def update(self, dt=None):
        pass

    def draw(self, surface):
        self.menu.mostrar_chatbot()
