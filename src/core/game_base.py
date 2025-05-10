import pygame
import random
import math
import time
from functools import lru_cache
from typing import Optional, Tuple, List, Dict, Any, Union, Callable

from ui.components.utils import (
    mostrar_texto_adaptativo, Boton, obtener_fuente, render_text_cached,
    dibujar_caja_texto, TooltipManager, ScrollManager, get_gradient
)
from ui.components.emoji import mostrar_alternativo_adaptativo

from core.scale.responsive_scaler_animated import ResponsiveScalerAnimado
from core.decoration.background_game import FondoAnimado
from core.decoration.effects import EffectsMixin

# Paleta de colores infantil inspirada en Apple
PALETA = {
    "rojo_manzana": (255, 59, 48),
    "naranja_zanahoria": (255, 149, 0),
    "amarillo_sol": (255, 204, 0),
    "verde_manzana": (76, 217, 100),
    "verde_lima": (186, 255, 86),
    "azul_cielo": (90, 200, 250),
    "azul_oceano": (0, 122, 255),
    "morado_uva": (175, 82, 222),
    "rosa_chicle": (255, 45, 85),
    "rosa_pastel": (255, 156, 189),
    "turquesa": (52, 199, 186),
    "coral": (255, 127, 80),
    "lavanda": (186, 156, 255),
    "melocoton": (255, 190, 152),
    "menta": (152, 255, 179)
}

PALETA_LISTA = list(PALETA.values())

class JuegoBase(EffectsMixin):
    def __init__(self, nombre, pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu):
        self.nombre = nombre
        self.pantalla = pantalla
        self.config = config
        self.dificultad = dificultad
        self.fondo = fondo
        self.navbar = navbar
        self.images = images
        self.sounds = sounds
        self.return_to_menu = return_to_menu

        # --- Dimensiones y fuentes ---
        self.ANCHO = pantalla.get_width()
        self.ALTO = pantalla.get_height()

        # --- Sistema de escalado responsivo ---
        self.scaler = ResponsiveScaler(1280, 720)
        self.scaler.update(self.ANCHO, self.ALTO)
        self.sx = self.scaler.sx
        self.sy = self.scaler.sy
        self.sf = self.scaler.sf

        # Fuentes escaladas
        self.fuente_titulo = obtener_fuente(self.sf(40), negrita=True)
        self.fuente = obtener_fuente(self.sf(24))
        self.fuente_pequeña = obtener_fuente(self.sf(18))

        self.reloj = pygame.time.Clock()
        self.fps = 60
        self.tiempo_ultimo_frame = time.time()
        self.delta_time = 0

        self.navbar_height = 0
        self._update_navbar_height()

        self.tooltip_manager = TooltipManager(delay=0.6)
        self.scroll_manager = ScrollManager()
        pygame.display.set_caption(f"{self.nombre} - {self.dificultad}")

        self.opcion_botones = []
        self.mensaje = ""
        self.tiempo_mensaje = 0
        self.mensaje_color = (255, 255, 255, 220)
        self.mensaje_animacion = 0

        self.ui_elements = {}
        self.init_responsive_ui()

        self.racha_correctas = 0
        self.mejor_racha = 0
        self.racha_anterior = 0

        self.operacion_actual = ""

        # --- Fondo animado modular ---
        self.fondo_animado = FondoAnimado(self.pantalla, self.ANCHO, self.ALTO, self.navbar_height, self.sx, self.sy)

        # --- Estado del juego ---
        self.estado = "jugando"
        self.tiempo_inicio = time.time()
        self.tiempo_juego = 0

        self.sonido_activado = True
        self.debug_mode = False
        self.fps_counter = 0
        self.fps_timer = 0
        self.fps_actual = 0

        self.colores_tema = {
            "primario": PALETA["azul_cielo"],
            "secundario": PALETA["verde_manzana"],
            "acento": PALETA["rosa_chicle"],
            "fondo": (245, 245, 250),
            "texto": (50, 50, 60),
            "exito": PALETA["verde_manzana"],
            "error": PALETA["rosa_chicle"],
            "neutro": PALETA["azul_cielo"]
        }

    def init_responsive_ui(self):
        self.ui_elements = {
            "titulo_rect": (0, self.navbar_height + self.sy(30), self.ANCHO, self.sy(70)),
            "feedback_rect": self.scaler.get_centered_rect(500, 60, vertical_offset=self.ALTO//2 - 50),
            "puntaje_rect": (self.sx(18), self.ALTO - self.sy(80),
                            self.sx(200), self.sy(60)),
            "tiempo_rect": (self.ANCHO - self.sx(180) - self.sx(18),
                           self.navbar_height + self.sy(18),
                           self.sx(180), self.sy(50))
        }

    def _update_navbar_height(self):
        if self.navbar and hasattr(self.navbar, "get_height"):
            self.navbar_height = self.navbar.get_height()
        elif self.navbar and hasattr(self.navbar, "height"):
            self.navbar_height = self.navbar.height
        else:
            self.navbar_height = self.sy(60)

    def on_resize(self, ancho, alto):
        self.fondo_animado.resize(ancho, alto)
        self.init_responsive_ui()

    def dibujar_fondo(self):
        self.fondo_animado.dibujar_fondo(self.fondo)

    def update(self, dt=None):
        # Optimización: limitar el delta time para evitar saltos grandes
        current_time = time.time()
        if dt is None:
            dt = current_time - self.tiempo_ultimo_frame
        dt = min(dt, 1/30)  # Limita el salto máximo a ~33ms
        self.tiempo_ultimo_frame = current_time
        self.delta_time = dt

        # Actualizaciones de fondo y efectos
        self.fondo_animado.actualizar_nubes()
        self.fondo_animado.actualizar_burbujas()
        self.update_animacion_estrellas()
        self.update_particulas()

        # Animaciones suaves para racha
        if hasattr(self, "racha_correctas") and hasattr(self, "racha_anterior"):
            if self.racha_correctas != self.racha_anterior:
                self.tiempo_cambio_racha = time.time()
                self.racha_anterior = self.racha_correctas

    def draw(self, surface=None):
        surface = surface or self.pantalla
        self.dibujar_fondo()
        self.draw_particulas()
        self.draw_animacion_estrellas()
        self.dibujar_feedback()

        # Mostrar UI principal con textos y posiciones predeterminadas
        self.mostrar_titulo()
        self.mostrar_pregunta(getattr(self, "operacion_actual", "¿Cuál es la respuesta?"))
        self.mostrar_instrucciones("Selecciona la opción correcta. Presiona ESC para volver.")
        self.dibujar_opciones()
        # Puntaje y racha con valores actuales
        self.mostrar_puntaje(getattr(self, "puntuacion", 0), getattr(self, "total_preguntas", 10))
        self.mostrar_operacion()
        self.mostrar_racha()

    def handle_event(self, evento):
        # Procesamiento eficiente de eventos
        if hasattr(self, 'tooltip_manager'):
            self.tooltip_manager.update(pygame.mouse.get_pos())
        if evento.type == pygame.VIDEORESIZE:
            self.ANCHO, self.ALTO = evento.w, evento.h
            self.pantalla = pygame.display.set_mode((self.ANCHO, self.ALTO), pygame.RESIZABLE)
            self._update_navbar_height()
            self.scaler.update(self.ANCHO, self.ALTO)
            self.fuente_titulo = obtener_fuente(self.sf(40), negrita=True)
            self.fuente = obtener_fuente(self.sf(24))
            self.fuente_pequeña = obtener_fuente(self.sf(18))
            self.on_resize(self.ANCHO, self.ALTO)
            return True
        return False

    def mostrar_titulo(self):
        """Muestra el título del juego centrado debajo de la navbar."""
        titulo_rect = self.ui_elements.get(
            "titulo_rect",
            (0, self.navbar_height + self.sy(30), self.ANCHO, self.sy(60))
        )
        mostrar_texto_adaptativo(
            pantalla=self.pantalla,
            texto=f"{self.nombre} - Nivel {self.dificultad}",
            x=titulo_rect[0],
            y=titulo_rect[1],
            w=titulo_rect[2],
            h=titulo_rect[3],
            fuente_base=self.fuente_titulo,
            color=(70, 130, 180),
            centrado=True
        )

    def mostrar_instrucciones(self, texto=None):
        """Muestra instrucciones en la parte inferior de la pantalla."""
        instrucciones_rect = (
            self.sx(50),
            self.ALTO - self.sy(70),
            self.ANCHO - self.sx(100),
            self.sy(50)
        )
        mostrar_texto_adaptativo(
            pantalla=self.pantalla,
            texto=texto or "Selecciona la opción correcta. Presiona ESC para volver.",
            x=instrucciones_rect[0],
            y=instrucciones_rect[1],
            w=instrucciones_rect[2],
            h=instrucciones_rect[3],
            fuente_base=self.fuente_pequeña,
            color=(100, 100, 100),
            centrado=True
        )

    def mostrar_pregunta(self, pregunta):
        """Muestra la pregunta actual en pantalla."""
        pregunta_rect = (
            self.sx(100),
            self.navbar_height + self.sy(100),
            self.ANCHO - self.sx(200),
            self.sy(80)
        )
        mostrar_texto_adaptativo(
            pantalla=self.pantalla,
            texto=pregunta,
            x=pregunta_rect[0],
            y=pregunta_rect[1],
            w=pregunta_rect[2],
            h=pregunta_rect[3],
            fuente_base=self.fuente,
            color=(30, 30, 90),
            centrado=True
        )

    def generar_opciones(self, respuesta: int, cantidad: int = 3) -> list[int]:
        """
        Genera opciones aleatorias alrededor de la respuesta correcta, sin duplicados ni negativos.
        Mejorada para evitar bucles infinitos y asegurar variedad.
        """
        opciones = {respuesta}
        posibles = set(range(max(0, respuesta - 10), respuesta + 11)) - {respuesta}
        while len(opciones) < cantidad and posibles:
            op = random.choice(list(posibles))
            opciones.add(op)
            posibles.remove(op)
        while len(opciones) < cantidad:
            op = respuesta + random.randint(1, 20)
            opciones.add(op)
        resultado = list(opciones)
        random.shuffle(resultado)
        return resultado

    def dibujar_opciones(
        self,
        opciones=None,
        tooltips=None,
        estilo="flat",
        border_radius=None,
        x0=None,
        y0=None,
        espacio=None
    ):
        """
        Dibuja botones de opciones de forma responsiva, colorida y reutilizable.
        """
        opciones = opciones if opciones is not None else getattr(self, "opciones", [])
        if not opciones:
            return  # No dibujar si no hay opciones

        border_radius = border_radius or self.sy(12)
        # Aumenta el espacio entre botones (por ejemplo, 2.5 veces el valor base)
        espacio = espacio or int(self.sx(20) * 2.5)

        cnt = len(opciones)
        w = max(self.sx(100), min(self.sx(180), self.ANCHO // (cnt * 2)))
        h = max(self.sy(50), min(self.sy(80), self.ALTO // 12))
        # Hacer los botones cuadrados
        size = min(w, h)
        w = h = size

        if x0 is None:
            x0 = (self.ANCHO - (w * cnt + espacio * (cnt - 1))) // 2
        if y0 is None:
            y0 = self.ALTO // 2 - h // 2

        paleta = PALETA_LISTA[:cnt] if cnt <= len(PALETA_LISTA) else PALETA_LISTA * (cnt // len(PALETA_LISTA)) + PALETA_LISTA[:cnt % len(PALETA_LISTA)]

        self.opcion_botones.clear()
        for i, val in enumerate(opciones):
            color_bg = paleta[i % len(paleta)]
            color_hover = self.color_complementario(color_bg)
            lum = 0.299 * color_bg[0] + 0.587 * color_bg[1] + 0.114 * color_bg[2]
            color_texto = (0, 0, 0) if lum > 180 else (255, 255, 255)
            x = x0 + i * (w + espacio)
            btn = Boton(
                texto=str(val),
                x=x, y=y0, ancho=w, alto=h,
                fuente=self.fuente,
                color_normal=color_bg,
                color_hover=color_hover,
                color_texto=color_texto,
                border_radius=border_radius,
                estilo=estilo,
                tooltip=tooltips[i] if tooltips and i < len(tooltips) else None
            )
            btn.draw(self.pantalla, tooltip_manager=getattr(self, "tooltip_manager", None))
            self.opcion_botones.append(btn)

    @staticmethod
    def color_complementario(rgb):
        """Devuelve el color complementario."""
        return tuple(255 - c for c in rgb)
    
    def mostrar_puntaje(self, juegos_ganados, juegos_totales, frase="¡Puntaje!"):
        """
        Muestra el puntaje en la parte inferior izquierda en una caja bonita con emojis.
        Estilo Apple para niños.
        """
        puntaje_rect = self.ui_elements.get("puntaje_rect", 
                                           (self.sx(18), self.ALTO - self.sy(80), 
                                            self.sx(200), self.sy(60)))
        
        x, y, ancho_caja, alto_caja = puntaje_rect
        
        # Crear superficie para sombra y fondo
        surf = pygame.Surface((ancho_caja, alto_caja), pygame.SRCALPHA)
        
        # Dibujar sombra
        sombra = pygame.Surface((ancho_caja, alto_caja), pygame.SRCALPHA)
        pygame.draw.rect(
            sombra,
            (0, 0, 0, 30),
            (4, 4, ancho_caja, alto_caja),
            border_radius=self.sy(20)
        )
        surf.blit(sombra, (0, 0))
        
        # Dibujar fondo con borde redondeado
        pygame.draw.rect(
            surf,
            (255, 255, 255, 240),
            (0, 0, ancho_caja, alto_caja),
            border_radius=self.sy(20)
        )
        
        # Aplicar gradiente como overlay
        gradiente = get_gradient(ancho_caja, alto_caja, (220, 240, 255), (200, 220, 245))
        gradiente.set_alpha(120)
        mask = pygame.Surface((ancho_caja, alto_caja), pygame.SRCALPHA)
        pygame.draw.rect(
            mask,
            (255, 255, 255, 255),
            (0, 0, ancho_caja, alto_caja),
            border_radius=self.sy(20)
        )
        gradiente_masked = gradiente.copy()
        gradiente_masked.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(gradiente_masked, (0, 0))
        
        # Dibujar borde con estilo Apple
        pygame.draw.rect(
            surf,
            (100, 150, 255, 150),
            (0, 0, ancho_caja, alto_caja),
            width=2,
            border_radius=self.sy(20)
        )
        
        # Aplicar a la pantalla
        self.pantalla.blit(surf, (x, y))

        texto = f"🏆 {frase}: {juegos_ganados}/{juegos_totales} 🎮"

        # Mostrar texto con sombra sutil
        sombra_offset = self.sy(1)
        mostrar_texto_adaptativo(
            pantalla=self.pantalla,
            texto=texto,
            x=x + sombra_offset,
            y=y + sombra_offset,
            w=ancho_caja,
            h=alto_caja,
            fuente_base=self.fuente,
            color=(10, 30, 50, 150),
            centrado=True
        )
        
        mostrar_texto_adaptativo(
            pantalla=self.pantalla,
            texto=texto,
            x=x,
            y=y,
            w=ancho_caja,
            h=alto_caja,
            fuente_base=self.fuente,
            color=(30, 60, 90),
            centrado=True
        )

    
    def mostrar_racha(self, rect=None, animado=True):
        """
        Muestra la racha actual y la mejor racha en pantalla con animación.
        Estilo Apple para niños.
        """
        if rect is None:
            rect = (self.ANCHO - self.sx(220), self.ALTO - self.sy(80), self.sx(200), self.sy(60))
            
        # Animación cuando cambia la racha
        escala = 1.0
        color_texto = (50, 50, 60)
        
        if animado and self.racha_correctas > self.racha_anterior:
            # Calcular tiempo desde el cambio
            tiempo_desde_cambio = time.time() - getattr(self, 'tiempo_cambio_racha', 0)
            if tiempo_desde_cambio < 0.5:  # Duración de la animación
                escala = 1.0 + 0.4 * (1 - tiempo_desde_cambio / 0.5)
                color_texto = (50, 50, 60)
            self.racha_anterior = self.racha_correctas
            
        # Calcular rectángulo con escala
        x, y, w, h = rect
        if escala > 1.0:
            w_escalado = int(w * escala)
            h_escalado = int(h * escala)
            x_escalado = x - (w_escalado - w) // 2
            y_escalado = y - (h_escalado - h) // 2
            rect_escalado = (x_escalado, y_escalado, w_escalado, h_escalado)
        else:
            rect_escalado = rect
            
        # Dibujar caja con estilo Apple para niños
        x, y, w, h = rect_escalado
        
        # Fondo con gradiente suave
        gradiente = get_gradient(w, h, (255, 240, 200), (255, 220, 150))
        
        # Crear superficie para sombra y fondo
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        
        # Dibujar sombra
        sombra = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(
            sombra,
            (0, 0, 0, 40),
            (4, 4, w, h),
            border_radius=self.sy(20)
        )
        surf.blit(sombra, (0, 0))
        
        # Dibujar fondo con borde redondeado
        pygame.draw.rect(
            surf,
            (255, 255, 255, 240),
            (0, 0, w, h),
            border_radius=self.sy(20)
        )
        
        # Aplicar gradiente como overlay
        gradiente.set_alpha(100)
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(
            mask,
            (255, 255, 255, 255),
            (0, 0, w, h),
            border_radius=self.sy(20)
        )
        gradiente_masked = gradiente.copy()
        gradiente_masked.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(gradiente_masked, (0, 0))
        
        # Dibujar borde con estilo Apple
        pygame.draw.rect(
            surf,
            (255, 200, 100, 150),
            (0, 0, w, h),
            width=2,
            border_radius=self.sy(20)
        )
        
        # Aplicar a la pantalla
        self.pantalla.blit(surf, (x, y))
        
        # Mostrar texto
        mostrar_texto_adaptativo(
            self.pantalla,
            f"🔥 Racha: {self.racha_correctas} (Mejor: {self.mejor_racha})",
            x, y, w, h,
            fuente_base=obtener_fuente(self.sf(22)),
            color=color_texto,
            centrado=True
        )

    def mostrar_operacion(self, rect=None):
        """Muestra la operación matemática actual con estilo Apple para niños."""
        if not self.operacion_actual:
            return
            
        if rect is None:
            rect = (self.ANCHO - self.sx(220), self.navbar_height + self.sy(50), self.sx(200), self.sy(50))
            
        x, y, w, h = rect
        
        # Crear superficie para sombra y fondo
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        
        # Dibujar sombra
        sombra = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(
            sombra,
            (0, 0, 0, 30),
            (4, 4, w, h),
            border_radius=self.sy(20)
        )
        surf.blit(sombra, (0, 0))
        
        # Dibujar fondo con borde redondeado
        pygame.draw.rect(
            surf,
            (255, 255, 255, 240),
            (0, 0, w, h),
            border_radius=self.sy(20)
        )
        
        # Aplicar gradiente como overlay
        gradiente = get_gradient(w, h, (220, 240, 255), (200, 220, 245))
        gradiente.set_alpha(120)
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(
            mask,
            (255, 255, 255, 255),
            (0, 0, w, h),
            border_radius=self.sy(20)
        )
        gradiente_masked = gradiente.copy()
        gradiente_masked.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(gradiente_masked, (0, 0))
        
        # Dibujar borde con estilo Apple
        pygame.draw.rect(
            surf,
            (100, 150, 255, 150),
            (0, 0, w, h),
            width=2,
            border_radius=self.sy(20)
        )
        
        # Aplicar a la pantalla
        self.pantalla.blit(surf, (x, y))
        
        # Texto con sombra sutil
        sombra_offset = self.sy(1)
        mostrar_texto_adaptativo(
            self.pantalla,
            self.operacion_actual,
            x + sombra_offset, y + sombra_offset, w, h,
            fuente_base=obtener_fuente(self.sf(24), negrita=True),
            color=(20, 20, 50, 150),
            centrado=True
        )
        mostrar_texto_adaptativo(
            self.pantalla,
            self.operacion_actual,
            x, y, w, h,
            fuente_base=obtener_fuente(self.sf(24), negrita=True),
            color=(50, 50, 120),
            centrado=True
        )
