from setup.Carga_Configs import servicios, conexiones, configuracion, prompt_inicial

def main():
    # Ejemplo de acceso a los servicios
    deepseek = servicios["deepseek"]
    print("API Key Deepseek:", deepseek.api_key)
    print("Modelo Deepseek:", deepseek.model)

    # Ejemplo de acceso a una conexión
    conexion_nvidia = conexiones["nvidia"]
    print("URL Nvidia:", conexion_nvidia["url"])

    # Ejemplo de acceso a la configuración general
    print("Colores disponibles:", configuracion.colores)
    print("Imagen logo:", configuracion.imagenes.get("logo"))
    print("Sonido click:", configuracion.sonidos.get("click"))
    print("Ancho de pantalla:", configuracion.pantalla.get("ancho"))

    # Prompt inicial
    print("Prompt inicial:", prompt_inicial)

if __name__ == "__main__":
    main()