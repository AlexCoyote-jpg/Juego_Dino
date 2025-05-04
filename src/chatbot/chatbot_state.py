class ChatbotStateManager:
    def __init__(self, max_messages=20):
        self.messages = []
        self.max_messages = max_messages
        self.needs_redraw = True  # Indica si hay que redibujar

    def add_message(self, text):
        self.messages.append(text)
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
        self.needs_redraw = True

    def clear(self):
        self.messages.clear()
        self.needs_redraw = True

    def get_messages(self):
        return list(self.messages)

    def mark_drawn(self):
        self.needs_redraw = False

    def should_redraw(self):
        return self.needs_redraw
    

    '''
    # Ejemplo de integración en tu main loop
from core.chatbot_state import ChatbotStateManager

state = ChatbotStateManager(max_messages=20)

# ... inicialización pygame ...

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Aquí agregas mensajes según la interacción
        # state.add_message("Nuevo mensaje")

    if state.should_redraw():
        pantalla.fill((255,255,255))
        y = 50
        for msg in state.get_messages():
            mostrar_alternativo_adaptativo(
                pantalla, msg, 50, y, 700, 40, color=(0,0,0), centrado=False
            )
            y += 45
        pygame.display.flip()
        state.mark_drawn()
    '''