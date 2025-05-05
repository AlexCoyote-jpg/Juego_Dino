class ChatbotStateManager:
    def __init__(self, max_visible=10):
        self.all_messages = []          # Lista con todos los mensajes (ilimitada)
        self.max_visible = max_visible  # Cantidad máxima de mensajes a mostrar
        self.visible_start = 0          # Índice del primer mensaje visible
        self.needs_redraw = True        # Indica si hay que redibujar

    def add_message(self, text):
        """Agrega un mensaje a la lista total y ajusta la ventana de mensajes visibles."""
        self.all_messages.append(text)
        # Si estamos al final, mueve la ventana para mostrar el nuevo mensaje
        if self.visible_start + self.max_visible >= len(self.all_messages) - 1:
            self.visible_start = max(0, len(self.all_messages) - self.max_visible)
        self.needs_redraw = True

    def clear(self):
        """Limpia todos los mensajes."""
        self.all_messages.clear()
        self.visible_start = 0
        self.needs_redraw = True

    def get_messages(self):
        """Devuelve solo los mensajes actualmente visibles."""
        end = self.visible_start + self.max_visible
        return self.all_messages[self.visible_start:end]

    def scroll_up(self):
        """Desplaza la ventana de mensajes hacia arriba."""
        if self.visible_start > 0:
            self.visible_start -= 1
            self.needs_redraw = True

    def scroll_down(self):
        """Desplaza la ventana de mensajes hacia abajo."""
        if self.visible_start + self.max_visible < len(self.all_messages):
            self.visible_start += 1
            self.needs_redraw = True

    def mark_drawn(self):
        self.needs_redraw = False

    def should_redraw(self):
        return self.needs_redraw