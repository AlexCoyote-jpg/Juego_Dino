import json
import os

def cargar_json(ruta):
    """
    Carga y devuelve el contenido de un archivo JSON.
    """
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")
    with open(ruta, 'r', encoding='utf-8') as f:
        return json.load(f)

class ServicioConexion:
    def __init__(self, nombre, datos):
        self.nombre = nombre
        self.api_key = datos.get("api_key")
        self.model = datos.get("model")


def cargar_servicios_conexion(ruta):
    """
    Devuelve un diccionario de instancias ServicioConexion por cada servicio.
    """
    datos = cargar_json(ruta)
    return {nombre: ServicioConexion(nombre, cfg) for nombre, cfg in datos.get("servicios", {}).items()}

def cargar_conexiones(ruta):
    """
    Devuelve el diccionario de configuraciones de conexión.
    """
    datos = cargar_json(ruta)
    return datos.get("conexion", {})

def cargar_prompt_inicial(ruta):
    """
    Devuelve el prompt inicial definido en la configuración.
    """
    datos = cargar_json(ruta)
    return datos.get("prompt_inicial", "")


class Configuracion:
    def __init__(self, datos):
        self.pantalla = datos.get("pantalla", {})
        self.colores = datos.get("colores", {})
        self.imagenes = datos.get("imagenes", {})
        self.sonidos = datos.get("sonidos", {})


def cargar_configuracion(ruta):
    """
    Carga y devuelve la configuración general.
    """
    datos = cargar_json(ruta)
    return Configuracion(datos)

# Instancias globales Conexion (ajusta las rutas si es necesario)
ruta_conex = os.path.join(os.path.dirname(__file__), "../Settings/Conexion_Settings.json")
servicios = cargar_servicios_conexion(ruta_conex)
conexiones = cargar_conexiones(ruta_conex)
prompt_inicial = cargar_prompt_inicial(ruta_conex)

# Instancias globales Configuracion (ajusta las rutas si es necesario)
ruta_config = os.path.join(os.path.dirname(__file__), "../Settings/Configuracion.json")
configuracion = cargar_configuracion(ruta_config)

# Ejemplo de acceso rápido:
# deepseek = servicios["deepseek"]
# print(deepseek.api_key)
# print(deepseek.api_key)

#conexion = conexiones["nvidia"]

#print(conexion["url"])
#print(conexion["temperature"])
#print(conexion["top_p"])
#print(conexion["max_tokens"])
#print(conexion["stream"])
#print(prompt_inicial)
# Acceso a la configuración
# print(configuracion.pantalla)
# print(configuracion.colores)
#print(configuracion.imagenes)
# print(configuracion.sonidos)
# Acceso a los colores
# print(configuracion.colores.get("fondo"))
# Acceso a los sonidos
# print(configuracion.sonidos.get("click"))
# Acceso a las imágenes
# print(configuracion.imagenes.get("logo"))
# Acceso a la pantalla
# print(configuracion.pantalla.get("ancho"))
