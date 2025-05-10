import pygame
import random
import time
from ui.components.utils import (
    mostrar_texto_adaptativo, Boton, obtener_fuente, get_gradient
)
from . import PALETA_LISTA  # Asegúrate de importar la paleta correctamente

def mostrar_titulo(pantalla, nombre, dificultad, fuente_titulo, navbar_height, sy, ANCHO, ui_elements):
    titulo_rect = ui_elements.get(
        "titulo_rect",
        (0, navbar_height + sy(30), ANCHO, sy(60))
    )
    mostrar_texto_adaptativo(
        pantalla=pantalla,
        texto=f"{nombre} - Nivel {dificultad}",
        x=titulo_rect[0],
        y=titulo_rect[1],
        w=titulo_rect[2],
        h=titulo_rect[3],
        fuente_base=fuente_titulo,
        color=(70, 130, 180),
        centrado=True
    )

def mostrar_instrucciones(pantalla, sx, sy, ALTO, ANCHO, fuente_pequeña, texto=None):
    instrucciones_rect = (
        sx(50),
        ALTO - sy(70),
        ANCHO - sx(100),
        sy(50)
    )
    mostrar_texto_adaptativo(
        pantalla=pantalla,
        texto=texto or "Selecciona la opción correcta. Presiona ESC para volver.",
        x=instrucciones_rect[0],
        y=instrucciones_rect[1],
        w=instrucciones_rect[2],
        h=instrucciones_rect[3],
        fuente_base=fuente_pequeña,
        color=(100, 100, 100),
        centrado=True
    )

def mostrar_pregunta(pantalla, pregunta, sx, sy, navbar_height, ANCHO, fuente):
    pregunta_rect = (
        sx(100),
        navbar_height + sy(100),
        ANCHO - sx(200),
        sy(80)
    )
    mostrar_texto_adaptativo(
        pantalla=pantalla,
        texto=pregunta,
        x=pregunta_rect[0],
        y=pregunta_rect[1],
        w=pregunta_rect[2],
        h=pregunta_rect[3],
        fuente_base=fuente,
        color=(30, 30, 90),
        centrado=True
    )

def color_complementario(rgb):
    return tuple(255 - c for c in rgb)

def dibujar_opciones(
    pantalla, opciones, opcion_botones, fuente, sy, sx, ANCHO, ALTO,
    tooltips=None, estilo="flat", border_radius=None, x0=None, y0=None, espacio=None, tooltip_manager=None
):
    if not opciones:
        return

    border_radius = border_radius or sy(12)
    espacio = espacio or int(sx(20) * 2.5)
    cnt = len(opciones)
    w = max(sx(100), min(sx(180), ANCHO // (cnt * 2)))
    h = max(sy(50), min(sy(80), ALTO // 12))
    size = min(w, h)
    w = h = size

    if x0 is None:
        x0 = (ANCHO - (w * cnt + espacio * (cnt - 1))) // 2
    if y0 is None:
        y0 = ALTO // 2 - h // 2

    paleta = PALETA_LISTA[:cnt] if cnt <= len(PALETA_LISTA) else PALETA_LISTA * (cnt // len(PALETA_LISTA)) + PALETA_LISTA[:cnt % len(PALETA_LISTA)]

    opcion_botones.clear()
    for i, val in enumerate(opciones):
        color_bg = paleta[i % len(paleta)]
        color_hover = color_complementario(color_bg)
        lum = 0.299 * color_bg[0] + 0.587 * color_bg[1] + 0.114 * color_bg[2]
        color_texto = (0, 0, 0) if lum > 180 else (255, 255, 255)
        x = x0 + i * (w + espacio)
        btn = Boton(
            texto=str(val),
            x=x, y=y0, ancho=w, alto=h,
            fuente=fuente,
            color_normal=color_bg,
            color_hover=color_hover,
            color_texto=color_texto,
            border_radius=border_radius,
            estilo=estilo,
            tooltip=tooltips[i] if tooltips and i < len(tooltips) else None
        )
        btn.draw(pantalla, tooltip_manager=tooltip_manager)
        opcion_botones.append(btn)