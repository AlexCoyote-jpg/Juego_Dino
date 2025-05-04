"""
Módulo centralizado para utilidades de navegación, recursos y fondo.
Importa y expone funciones y clases clave para usarlas desde main.py, menu.py, etc.
"""

import pygame
import math
import time

PALETA_COLORES = {
    'BLANCO': (255, 255, 255),
    'NEGRO': (0, 0, 0),
    'BEIGE': (255, 248, 220),  # FONDO renombrado a BEIGE
    'AZUL_CIELO': (135, 206, 235),  # BOTON_NORMAL renombrado a AZUL_CIELO
    'AZUL_MEDIO': (100, 149, 237),  # BOTON_HOVER renombrado a AZUL_MEDIO
    'AZUL_OSCURO': (70, 130, 180),  # BOTON_ACTIVO y titulo renombrado a AZUL_OSCURO
    'VERDE_CLARO': (152, 251, 152),  # VERDE_OPCIONES renombrado a VERDE_CLARO
    'VERDE_OSCURO': (60, 179, 113),  # VERDE_OPCIONES_HOVER renombrado a VERDE_OSCURO
    'GRIS_OSCURO': (47, 79, 79),  # TEXTO_OSCURO renombrado a GRIS_OSCURO
    'BLANCO_AHUMADO': (240, 248, 255),  # TEXTO_CLARO renombrado a BLANCO_AHUMADO
    'AMARILLO_PALIDO': (255, 250, 205),  # AMARILLO_CLARO renombrado a AMARILLO_PALIDO
    'AZUL_CLARO': (173, 216, 230),
    'GRIS': (200, 200, 200),
    'LAVANDA': (230, 230, 250),  # fondo_juego renombrado a LAVANDA
    'NEGRO_CARTA': (0, 0, 0),  # carta renombrado a NEGRO_CARTA para diferenciar
    'VERDE_ACIERTO': (50, 205, 50),  # acierto renombrado a VERDE_ACIERTO
    'ROJO_ERROR': (255, 99, 71),  # error renombrado a ROJO_ERROR
    'AZUL_BORDE': (65, 105, 225),  # borde_carta renombrado a AZUL_BORDE
    'BEIGE_PANEL': (255, 248, 220),  # panel renombrado a BEIGE_PANEL para diferenciar
}

# --- Recursos ---
from setup.Carga_Recursos import Recursos

# --- Fondo ---
from setup.Fondo import (
    estrellas_animadas,
    crear_fondo,
    crear_estrellas,
    FondoAnimadoThread,
    estrellas_animadas_threadsafe,
)

# --- Navegación ---
from setup.navegacion import (
    JuegoBase,
    BarraNavegacion,
)

from setup.Carga_Configs import (
    conexiones,
    servicios, 
    prompt_inicial,
    configuracion,
)

# --- Variables de configuración globales ---
ANCHO = configuracion.pantalla.get("ancho")  # Ancho por defecto
ALTO = configuracion.pantalla.get("alto")  # Alto por defecto
NVIDIA = conexiones.get("nvidia")
DEEPSEEK = conexiones.get("deepseek")
LLAMA = conexiones.get("llama")

# --- Utilidades de navegación (alias directos) ---
mostrar_texto_adaptativo = JuegoBase.mostrar_texto_adaptativo
dibujar_caja_texto = JuegoBase.dibujar_caja_texto
dibujar_boton = JuegoBase.dibujar_boton
dibujar_carta_generica = JuegoBase.dibujar_carta_generica
mostrar_victoria = JuegoBase.mostrar_victoria
avanzar_nivel = JuegoBase.avanzar_nivel
dibujar_fondo_animado = JuegoBase.dibujar_fondo_animado

# --- Función para crear el hilo de fondo animado ---
def crear_fondo_thread(estrellas, ancho, alto):
    thread = FondoAnimadoThread(estrellas, ancho, alto)
    thread.start()
    return thread

# --- Elementos que pueden estar mejor aquí (core.py) ---
# Los siguientes elementos de navegacion.py pueden estar mejor aquí para centralizar la UI:
# - Colores globales (BLANCO, NEGRO, etc.) → ya están en PALETA_COLORES.
# - JuegoBase y BarraNavegacion → ya están importados y expuestos.
# - Alias de utilidades de UI (mostrar_texto_adaptativo, dibujar_boton, etc.) → ya están aquí.
# - Si tienes más utilidades estáticas de UI, puedes moverlas aquí para evitar dependencias cruzadas.

# --- Exporta todo lo necesario ---
__all__ = [
    "PALETA_COLORES",
    "Recursos",
    "JuegoBase",
    "BarraNavegacion",
    "mostrar_texto_adaptativo",
    "dibujar_caja_texto",
    "dibujar_boton",
    "dibujar_carta_generica",
    "mostrar_victoria",
    "avanzar_nivel",
    "dibujar_fondo_animado",
    "estrellas_animadas",
    "crear_fondo",
    "crear_estrellas",
    "FondoAnimadoThread",
    "estrellas_animadas_threadsafe",
    "crear_fondo_thread",
    "NVIDIA",
    "DEEPSEEK",
    "LLAMA",
    "ALTO",
    "ANCHO",
]
