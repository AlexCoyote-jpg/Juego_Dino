from openai import OpenAI
import logging
from Configs import conexiones, prompt_inicial

logging.basicConfig(level=logging.INFO)


def obtener_respuesta(user_input: str, modelo: str, servicio_key: str) -> str:
    """
    Envía el mensaje del usuario a la API y retorna la respuesta generada.
    """
    prompt = prompt_inicial
    conexion = conexiones["nvidia"]
    logging.info(f"Enviando solicitud a la API con modelo: {modelo}")
    try:
        # Configuración de la API
        client = OpenAI(
            base_url=conexion["url"],
            api_key=servicio_key,
         )
        completion = client.chat.completions.create(
           
            model=modelo,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=conexion.get("temperature"),
            top_p=conexion.get("top_p"),
            max_tokens=conexion.get("max_tokens"),
            stream=conexion.get("stream")
        )
        response_chunks = []
        for chunk in completion:
            delta_content = getattr(chunk.choices[0].delta, "content", None)
            if delta_content:
                response_chunks.append(delta_content)
        logging.info("Solicitud enviada correctamente a la API.")
        return "".join(response_chunks)
    except Exception as e:
        logging.error(f"Error al procesar la respuesta de la API: {e}")
        return "Ocurrió un error al procesar la respuesta de la API."


