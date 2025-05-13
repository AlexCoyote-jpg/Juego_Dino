from chatbot.Conexion import obtener_respuesta
from chatbot.Configs import LLAMA
import logging
from typing import Callable, List, Tuple, Optional

class ChatBot:
    def __init__(self):
        self.historial: List[Tuple[str, str]] = []
        self.en_espera: bool = False
        self.callback_pendiente: Optional[Callable[[], None]] = None

    def procesar_input(self, texto_usuario: str, callback: Callable[[], None]) -> bool:
        """
        Envía el texto del usuario al modelo IA y guarda la respuesta cuando llega.
        """
        texto_usuario = texto_usuario.strip()
        if not texto_usuario:
            logging.warning("Se intentó enviar un mensaje vacío a la API. Operación cancelada.")
            if callback:
                callback()
            return False

        self.historial.append(("usuario", texto_usuario))
        self.en_espera = True
        self.callback_pendiente = callback

        respuesta = obtener_respuesta(
            user_input=texto_usuario,
            modelo=LLAMA.model,
            servicio_key=LLAMA.api_key,
        )
        self._recibir_respuesta(respuesta)
        return True

    def _recibir_respuesta(self, respuesta: str) -> None:
        self.historial.append(("bot", respuesta))
        self.en_espera = False
        logging.info("Respuesta recibida del modelo IA: %s", respuesta)
        if self.callback_pendiente:
            self.callback_pendiente()
            self.callback_pendiente = None

    def obtener_historial(self) -> List[Tuple[str, str]]:
        return self.historial
