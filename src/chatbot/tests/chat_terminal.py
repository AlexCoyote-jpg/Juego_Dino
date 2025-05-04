from chatbot.Configs import LLAMA
from chatbot.Conexion import obtener_respuesta
def run_chatbot():
    print("Escribe 'salir' para terminar.")
    

    while True:
        user_input = input("Tú: ").strip()
        if user_input.lower() == "salir":
            print("¡Hasta luego!")
            break
        if not user_input:
            print("Por favor, escribe algo.")
            continue
        response_text = obtener_respuesta(user_input, LLAMA.model, LLAMA.api_key)
        print("Chatbot:", response_text)

if __name__ == "__main__":
    run_chatbot()
#     run: python -m src.chatbot.tests.chat_terminal