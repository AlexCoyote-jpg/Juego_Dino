from chatbot.Conexion import obtener_respuesta
from chatbot.Configs import LLAMA
import logging
from typing import List, Tuple, Optional

class ChatBot:
    def __init__(self):
        self.historial: List[Tuple[str, str]] = []

    def procesar_input(self, texto_usuario: str) -> bool:
        texto_usuario = texto_usuario.strip()
        if not texto_usuario:
            logging.warning("Se intentó enviar un mensaje vacío a la API. Operación cancelada.")
            mensaje_bot = "Por favor, escribe algo antes de enviar tu mensaje."
            self.historial.append(("bot", mensaje_bot))
            return False

        self.historial.append(("usuario", texto_usuario))

        respuesta = obtener_respuesta(
            user_input=texto_usuario,
            modelo=LLAMA.model,
            servicio_key=LLAMA.api_key,
        )
        self.historial.append(("bot", respuesta))
        logging.info("Respuesta recibida del modelo IA: %s", respuesta)
        return True

    def obtener_historial(self) -> List[Tuple[str, str]]:
        return self.historial
