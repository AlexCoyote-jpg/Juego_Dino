import pygame
import random
import time
from ui.components.utils import (
    mostrar_texto_adaptativo, Boton, obtener_fuente, get_gradient
)
from core.decoration.paleta import PALETA, PALETA_LISTA  # Asegúrate de importar la paleta correctamente

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
@staticmethod
def color_complementario(rgb):
    return tuple(255 - c for c in rgb)

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

def dibujar_debug_info(self):
        """Muestra información de depuración en pantalla."""
        debug_info = [
            f"FPS: {self.fps_actual}",
            f"Resolución: {self.ANCHO}x{self.ALTO}",
            f"Escala: {self.scaler._scale_x:.2f}x, {self.scaler._scale_y:.2f}y",
            f"Tiempo: {self.tiempo_juego:.1f}s",
            f"Estado: {self.estado}",
            f"Partículas: {len(self.particulas)}",
            f"Estrellas: {len(self.estrellas)}",
            f"Burbujas: {len(self.fondo_animado.burbujas)}"
        ]
        
        # Fondo semitransparente
        debug_panel = pygame.Surface((self.sx(200), self.sy(20) * len(debug_info)), pygame.SRCALPHA)
        debug_panel.fill((0, 0, 0, 150))
        self.pantalla.blit(debug_panel, (0, 0))
        
        # Mostrar información
        for i, info in enumerate(debug_info):
            mostrar_texto_adaptativo(
                self.pantalla,
                info,
                self.sx(5), self.sy(5) + i * self.sy(20),
                self.sx(190), self.sy(20),
                fuente_base=self.fuente_pequeña,
                color=(255, 255, 255),
                centrado=False
            )        

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

    
    