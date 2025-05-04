from Configs import servicios
from Conexion import obtener_respuesta
def run_chatbot():
    print("Escribe 'salir' para terminar.")
    ia = servicios["llama"]
    modelo = ia.model
    key = ia.api_key
    while True:
        user_input = input("Tú: ").strip()
        if user_input.lower() == "salir":
            print("¡Hasta luego!")
            break
        if not user_input:
            print("Por favor, escribe algo.")
            continue
        response_text = obtener_respuesta(user_input, modelo, key)
        print("Chatbot:", response_text)

if __name__ == "__main__":
    run_chatbot()