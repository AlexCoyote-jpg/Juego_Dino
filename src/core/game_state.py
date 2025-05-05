"""
Lógica y utilidades para el estado base del juego y transiciones.
"""
import pygame

def create_juego_base(pantalla, ancho, alto):
    return {
        "pantalla": pantalla,
        "ANCHO": ancho,
        "ALTO": alto,
        "botones_presionados": {},
        "animacion_nivel": 0,
        "nivel_actual": "Home",
        "fuente_botones": pygame.font.SysFont("Segoe UI", 32),
        "transicion_alpha": 0,
        "transicion_en_progreso": False,
        "transicion_color": (255, 255, 255),
        "transicion_velocidad": 18
    }

def actualizar_botones_presionados(juego_base):
    expirados = [k for k, v in juego_base["botones_presionados"].items() if v <= 1]
    for k in expirados:
        del juego_base["botones_presionados"][k]
    for k in juego_base["botones_presionados"]:
        juego_base["botones_presionados"][k] -= 1
    return juego_base

def iniciar_transicion(juego_base, color=(255,255,255), velocidad=18):
    juego_base["transicion_en_progreso"] = True
    juego_base["transicion_alpha"] = 0
    juego_base["transicion_color"] = color
    juego_base["transicion_velocidad"] = velocidad
    return juego_base

def manejar_transicion(juego_base):
    if juego_base["transicion_en_progreso"]:
        overlay = pygame.Surface((juego_base["ANCHO"], juego_base["ALTO"]), pygame.SRCALPHA)
        overlay.fill((*juego_base["transicion_color"], int(juego_base["transicion_alpha"])))
        juego_base["pantalla"].blit(overlay, (0, 0))
        juego_base["transicion_alpha"] += juego_base["transicion_velocidad"]
        if juego_base["transicion_alpha"] >= 255:
            juego_base["transicion_en_progreso"] = False
            juego_base["transicion_alpha"] = 0
    return juego_base

def avanzar_nivel(juego):
    niveles = ["Básico", "Medio", "Avanzado"]
    idx = niveles.index(juego["nivel_actual"])
    juego["nivel_actual"] = niveles[(idx + 1) % len(niveles)]
    if "sonido_acierto" in juego and juego["sonido_acierto"] and not juego.get("silencio", False):
        juego["sonido_acierto"].play()
    if "inicializar_nivel" in juego:
        juego["inicializar_nivel"]()
