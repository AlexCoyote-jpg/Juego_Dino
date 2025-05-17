from chatbot.Conexion import obtener_respuesta
from chatbot.Configs import LLAMA
import logging
from typing import List, Tuple, Optional

class ChatBot:
    def __init__(self):
        self.historial: List[Tuple[str, str]] = []

    def procesar_input(self, texto_usuario: str) -> str:
        texto_usuario = texto_usuario.strip()
        if not texto_usuario:
            logging.warning("Se intentó enviar un mensaje vacío a la API. Operación cancelada.")
            mensaje_bot = "Por favor, escribe algo antes de enviar tu mensaje."
            self.historial.append(("bot", mensaje_bot))
            return mensaje_bot

        # Agregar mensaje del usuario al historial
        self.historial.append(("usuario", texto_usuario))
        # Agregar mensaje vacío del bot para animación de "escribiendo" (opcional)
        self.historial.append(("bot", ""))

        respuesta = obtener_respuesta(
            user_input=texto_usuario,
            modelo=LLAMA.model,
            servicio_key=LLAMA.api_key,
        )
        # Reemplazar el último mensaje vacío del bot con la respuesta real
        for i in range(len(self.historial) - 1, -1, -1):
            autor, texto = self.historial[i]
            if autor == "bot" and texto == "":
                self.historial[i] = ("bot", respuesta)
                break
        return respuesta

    def obtener_historial(self) -> List[Tuple[str, str]]:
        return self.historial
