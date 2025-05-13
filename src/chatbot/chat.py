
class ChatBot:
    def __init__(self):
        self.historial = []

    def procesar_input(self, texto_usuario):
        # Simula una respuesta (aquí puedes integrar tu modelo o motor)
        respuesta = self.generar_respuesta_simulada(texto_usuario)
        self.historial.append(("usuario", texto_usuario))
        self.historial.append(("bot", respuesta))
        return respuesta

    def generar_respuesta_simulada(self, texto):
        if "suma" in texto.lower():
            return "Para sumar, solo tienes que juntar los números. Ej: 2 + 3 = 5"
        elif "multiplicar" in texto.lower():
            return "Multiplicar es sumar muchas veces. Ej: 3 x 2 = 6"
        else:
            return "¡Buena pregunta! Pero aún no sé responder eso... 😅"

    def obtener_historial(self):
        return self.historial
