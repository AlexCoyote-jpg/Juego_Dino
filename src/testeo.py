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

# Mensajes de feedback mejorados con más variedad y emojis amigables para niños
mensajes_correcto = [
    "¡Excelente! 🦕✨",
    "¡Muy bien! ¡Dino está feliz! 🥚🎉",
    "¡Correcto! ¡Sigue así! 🌟",
    "¡Genial! ¡Eres un crack! 🦖",
    "¡Perfecto! ¡Continúa así! 🔥",
    "¡Increíble respuesta! 🌈",
    "¡Eso es! ¡Dino está impresionado! 🦖👏",
    "¡Fantástico trabajo! ⭐⭐⭐",
    "¡Súper! ¡Lo lograste! 🎯",
    "¡Maravilloso! ¡Sigue así! 🎊"
]

mensajes_incorrecto = [
    "¡Ups! Intenta de nuevo, tú puedes 🦕",
    "¡No te rindas! La respuesta era {respuesta} 🥚",
    "¡Casi! Sigue practicando 💪",
    "¡Ánimo! Dino confía en ti 🦖",
    "¡Inténtalo otra vez! Estás cerca 🔍",
    "¡No pasa nada! Aprendemos de los errores 📚",
    "¡Vamos! La próxima lo conseguirás 🎯",
    "¡Sigue intentando! Dino te apoya 🦕❤️",
    "¡Oops! Prueba de nuevo 🌟",
    "¡Casi lo tienes! Sigue intentando 🌈"
]

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

# Lista de colores para usar en ciclos
PALETA_LISTA = list(PALETA.values())

# --- Sistema de Escalado Responsivo Mejorado ---
class ResponsiveScaler:
    """
    Sistema de escalado responsivo que mantiene proporciones consistentes
    en diferentes resoluciones de pantalla, con optimizaciones de rendimiento.
    """
    def __init__(self, base_width=1280, base_height=720):
        """
        Inicializa el escalador con dimensiones base de referencia.
        
        Args:
            base_width: Ancho base de diseño (por defecto 1280)
            base_height: Alto base de diseño (por defecto 720)
        """
        self.base_width = base_width
        self.base_height = base_height
        self.current_width = base_width
        self.current_height = base_height
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.aspect_ratio = base_width / base_height
        self.cached_values = {}
        self.last_update_time = 0
        self.update_interval = 0.2  # Limitar actualizaciones a 5 por segundo
        
    def update(self, width, height):
        """
        Actualiza los factores de escala basados en las nuevas dimensiones.
        Incluye limitación de frecuencia para evitar cálculos excesivos.
        
        Args:
            width: Ancho actual de la pantalla
            height: Alto actual de la pantalla
        """
        current_time = time.time()
        # Solo actualizar si han pasado al menos update_interval segundos
        if current_time - self.last_update_time < self.update_interval:
            if width == self.current_width and height == self.current_height:
                return False  # No hay cambios, no actualizar
        
        # Si las dimensiones no han cambiado, no hacer nada
        if width == self.current_width and height == self.current_height:
            return False
            
        self.current_width = width
        self.current_height = height
        self.scale_x = width / self.base_width
        self.scale_y = height / self.base_height
        self.aspect_ratio = width / height
        # Limpiar caché cuando cambian las dimensiones
        self.cached_values = {}
        self.last_update_time = current_time
        return True
        
    @lru_cache(maxsize=1024)
    def scale_x_value(self, value):
        """Escala un valor horizontal con caché."""
        return int(value * self.scale_x)
        
    @lru_cache(maxsize=1024)
    def scale_y_value(self, value):
        """Escala un valor vertical con caché."""
        return int(value * self.scale_y)
    
    @lru_cache(maxsize=256)
    def scale_font_size(self, size):
        """Escala un tamaño de fuente de manera balanceada con caché."""
        # Usar un promedio ponderado para que la fuente no sea demasiado grande o pequeña
        scale_factor = (self.scale_x * 0.6 + self.scale_y * 0.4)
        return max(12, int(size * scale_factor))
    
    def scale_rect(self, x, y, width, height):
        """Escala un rectángulo completo."""
        return (
            self.scale_x_value(x),
            self.scale_y_value(y),
            self.scale_x_value(width),
            self.scale_y_value(height)
        )
    
    def get_centered_rect(self, width, height, vertical_offset=0, horizontal_offset=0):
        """
        Obtiene un rectángulo centrado en la pantalla con dimensiones escaladas.
        
        Args:
            width: Ancho base del rectángulo
            height: Alto base del rectángulo
            vertical_offset: Desplazamiento vertical desde el centro (positivo = hacia abajo)
            horizontal_offset: Desplazamiento horizontal desde el centro (positivo = hacia derecha)
        
        Returns:
            Tupla (x, y, width, height) con valores escalados
        """
        scaled_width = self.scale_x_value(width)
        scaled_height = self.scale_y_value(height)
        x = (self.current_width - scaled_width) // 2 + self.scale_x_value(horizontal_offset)
        y = (self.current_height - scaled_height) // 2 + self.scale_y_value(vertical_offset)
        return (x, y, scaled_width, scaled_height)
    
    def maintain_aspect_ratio(self, width, height):
        """
        Ajusta dimensiones para mantener la relación de aspecto.
        Útil para imágenes y elementos visuales que no deben distorsionarse.
        """
        target_ratio = width / height
        if target_ratio > self.aspect_ratio:
            # Limitar por ancho
            new_width = self.scale_x_value(width)
            new_height = int(new_width / target_ratio)
        else:
            # Limitar por alto
            new_height = self.scale_y_value(height)
            new_width = int(new_height * target_ratio)
        return new_width, new_height

class JuegoBase:
    def __init__(self, nombre, pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu):
        """
        Clase base para juegos. Proporciona utilidades y estructura común.
        """
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
        self.scaler = ResponsiveScaler(1280, 720)  # Dimensiones base de diseño
        self.scaler.update(self.ANCHO, self.ALTO)
        
        # Funciones de escalado para facilitar el uso
        self.sx = self.scaler.scale_x_value
        self.sy = self.scaler.scale_y_value
        self.sf = self.scaler.scale_font_size
        
        # Fuentes escaladas - Tamaños más grandes para niños
        self.fuente_titulo = obtener_fuente(self.sf(40), negrita=True)
        self.fuente = obtener_fuente(self.sf(24))
        self.fuente_pequeña = obtener_fuente(self.sf(18))
        
        self.reloj = pygame.time.Clock()
        self.fps = 60  # Valor por defecto
        self.tiempo_ultimo_frame = time.time()
        self.delta_time = 0  # Tiempo entre frames para animaciones suaves
        
        self.navbar_height = 0
        self._update_navbar_height()

        # --- Tooltip manager ---
        self.tooltip_manager = TooltipManager(delay=0.6)  # Reducido para mejor UX con niños

        # --- Scroll manager ---
        self.scroll_manager = ScrollManager()

        # --- Actualiza el título de la ventana ---
        pygame.display.set_caption(f"{self.nombre} - {self.dificultad}")

        # --- Inicializa lista de botones de opciones ---
        self.opcion_botones = []

        # --- Mensaje temporal ---
        self.mensaje = ""
        self.tiempo_mensaje = 0
        self.mensaje_color = (255, 255, 255, 220)
        self.mensaje_animacion = 0  # Para efectos de animación
        
        # --- Elementos UI responsivos ---
        self.ui_elements = {}
        self.init_responsive_ui()

        # --- Racha ---
        self.racha_correctas = 0
        self.mejor_racha = 0
        self.racha_anterior = 0  # Para animaciones

        # --- Operación actual (para mostrar junto al problema) ---
        self.operacion_actual = ""

        # --- Animación de estrellas ---
        self.estrellas = []
        self.estrella_img = None
        self.tiempo_animacion = 0
        self.animacion_activa = False
        
        # --- Partículas ---
        self.particulas = []
        
        # --- Estado del juego ---
        self.estado = "jugando"  # jugando, victoria, derrota
        self.tiempo_inicio = time.time()
        self.tiempo_juego = 0
        
        # --- Sonidos ---
        self.sonido_activado = True
        
        # --- Debug ---
        self.debug_mode = False
        self.fps_counter = 0
        self.fps_timer = 0
        self.fps_actual = 0
        
        # --- Colores de tema ---
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
        
        # --- Animaciones adicionales ---
        self.nubes = self.generar_nubes(5)
        self.burbujas = []
        self.tiempo_burbuja = 0

    def generar_nubes(self, cantidad):
        """Genera nubes decorativas para el fondo"""
        nubes = []
        for _ in range(cantidad):
            x = random.randint(0, self.ANCHO)
            y = random.randint(self.navbar_height, self.ALTO // 3)
            velocidad = random.uniform(0.2, 0.8)
            tamaño = random.uniform(0.7, 1.3)
            nubes.append({
                'x': x, 'y': y, 
                'velocidad': velocidad, 
                'tamaño': tamaño,
                'color': (255, 255, 255, random.randint(150, 200))
            })
        return nubes
    
    def actualizar_nubes(self):
        """Actualiza la posición de las nubes decorativas"""
        for nube in self.nubes:
            nube['x'] += nube['velocidad']
            if nube['x'] > self.ANCHO + self.sx(100):
                nube['x'] = -self.sx(100)
                nube['y'] = random.randint(self.navbar_height, self.ALTO // 3)
    
    def dibujar_nubes(self):
        """Dibuja nubes decorativas en el fondo"""
        for nube in self.nubes:
            radio_base = self.sx(40) * nube['tamaño']
            # Dibujar varias formas circulares para crear una nube
            centros = [
                (nube['x'], nube['y']),
                (nube['x'] + radio_base * 0.7, nube['y'] - radio_base * 0.2),
                (nube['x'] + radio_base * 1.4, nube['y']),
                (nube['x'] + radio_base * 0.4, nube['y'] + radio_base * 0.3),
                (nube['x'] + radio_base, nube['y'] + radio_base * 0.4)
            ]
            
            # Crear superficie para la nube con transparencia
            ancho_nube = radio_base * 2.5
            alto_nube = radio_base * 1.5
            nube_surf = pygame.Surface((ancho_nube, alto_nube), pygame.SRCALPHA)
            
            # Dibujar círculos para formar la nube
            for cx, cy in centros:
                rel_x = cx - (nube['x'] - radio_base * 0.5)
                rel_y = cy - (nube['y'] - radio_base * 0.5)
                pygame.draw.circle(nube_surf, nube['color'], (rel_x, rel_y), radio_base * 0.6)
            
            # Suavizar bordes (efecto de desenfoque simple)
            for i in range(10):
                pygame.draw.circle(nube_surf, (*nube['color'][:3], 30), 
                                  (ancho_nube//2, alto_nube//2), 
                                  radio_base * (0.8 + i*0.05))
            
            # Dibujar la nube en pantalla
            self.pantalla.blit(nube_surf, (nube['x'] - radio_base * 0.5, nube['y'] - radio_base * 0.5))
    
    def crear_burbuja(self, x=None, y=None):
        """Crea una burbuja decorativa"""
        if x is None:
            x = random.randint(self.sx(50), self.ANCHO - self.sx(50))
        if y is None:
            y = self.ALTO + self.sy(20)
            
        color = random.choice([
            PALETA["azul_cielo"], 
            PALETA["rosa_pastel"],
            PALETA["verde_lima"],
            PALETA["lavanda"],
            PALETA["turquesa"]
        ])
        
        self.burbujas.append({
            'x': x, 'y': y,
            'radio': random.randint(self.sy(10), self.sy(30)),
            'velocidad': random.uniform(0.5, 2.0),
            'color': (*color[:3], 100),  # Semi-transparente
            'oscilacion': random.uniform(0.5, 1.5),
            'fase': random.uniform(0, 2 * math.pi)
        })
    
    def actualizar_burbujas(self):
        """Actualiza las burbujas decorativas"""
        # Crear nuevas burbujas ocasionalmente
        self.tiempo_burbuja -= 1
        if self.tiempo_burbuja <= 0:
            self.crear_burbuja()
            self.tiempo_burbuja = random.randint(30, 120)  # Intervalo aleatorio
            
        # Actualizar burbujas existentes
        for burbuja in self.burbujas[:]:
            burbuja['y'] -= burbuja['velocidad']
            # Movimiento oscilatorio horizontal
            burbuja['x'] += math.sin(time.time() * 2 + burbuja['fase']) * burbuja['oscilacion']
            
            # Eliminar si sale de la pantalla
            if burbuja['y'] < -burbuja['radio']:
                self.burbujas.remove(burbuja)
    
    def dibujar_burbujas(self):
        """Dibuja las burbujas decorativas"""
        for burbuja in self.burbujas:
            # Dibujar burbuja principal
            pygame.draw.circle(
                self.pantalla, 
                burbuja['color'], 
                (int(burbuja['x']), int(burbuja['y'])), 
                burbuja['radio']
            )
            
            # Dibujar brillo (círculo más pequeño y claro)
            brillo_radio = burbuja['radio'] // 3
            brillo_offset = burbuja['radio'] // 4
            pygame.draw.circle(
                self.pantalla,
                (255, 255, 255, 150),
                (int(burbuja['x'] - brillo_offset), int(burbuja['y'] - brillo_offset)),
                brillo_radio
            )

    def crear_estrella_img(self, tamaño=None, color=(255, 215, 0)):
        """Crea una imagen de estrella para efectos de celebración"""
        tamaño = tamaño or self.sy(20)  # Estrellas más grandes para niños
        img = pygame.Surface((tamaño, tamaño), pygame.SRCALPHA)
        puntos = []
        for i in range(5):
            ang = math.pi/2 + i * 2*math.pi/5
            puntos.append((
                tamaño//2 + int(tamaño//2 * math.cos(ang)),
                tamaño//2 - int(tamaño//2 * math.sin(ang))
            ))
            ang += math.pi/5
            puntos.append((
                tamaño//2 + int(tamaño//5 * math.cos(ang)),
                tamaño//2 - int(tamaño//5 * math.sin(ang))
            ))
        pygame.draw.polygon(img, color, puntos)
        return img

    def crear_efecto_estrellas(self, posicion, cantidad=12, colores=None):
        """
        Crea estrellas para celebrar una respuesta correcta con más variedad
        y mejores efectos visuales. Versión mejorada para niños.
        """
        x, y = posicion
        if not self.estrella_img:
            self.estrella_img = self.crear_estrella_img()
            
        # Usar colores variados y brillantes para niños
        if colores is None:
            colores = [
                PALETA["amarillo_sol"],    # Amarillo brillante
                PALETA["rosa_chicle"],     # Rosa
                PALETA["verde_lima"],      # Verde lima
                PALETA["azul_cielo"],      # Azul claro
                PALETA["naranja_zanahoria"] # Naranja
            ]
            
        for _ in range(cantidad):
            angulo = random.uniform(0, 2 * math.pi)
            distancia = random.uniform(self.sy(30), self.sy(150))
            estrella_x = x + math.cos(angulo) * distancia
            estrella_y = y + math.sin(angulo) * distancia
            escala = random.uniform(0.8, 1.8)  # Estrellas más grandes
            rotacion = random.uniform(0, 360)
            vida = random.randint(60, 100)  # Duran más tiempo
            velocidad_x = math.cos(angulo) * random.uniform(0.8, 2.5)
            velocidad_y = math.sin(angulo) * random.uniform(0.8, 2.5) - random.uniform(0.8, 2.0)  # Más elevación
            color = random.choice(colores)
            
            self.estrellas.append({
                'x': estrella_x, 'y': estrella_y,
                'escala': escala, 'rotacion': rotacion,
                'vida': vida, 'max_vida': vida,
                'vel_x': velocidad_x, 'vel_y': velocidad_y,
                'color': color
            })
        self.animacion_activa = True
        self.tiempo_animacion = 120  # Duración más larga para niños
        
        # Reproducir sonido si está disponible
        if self.sonido_activado and 'estrella' in self.sounds:
            self.sounds['estrella'].play()

    def crear_particula(self, x, y, color=None, velocidad=None, tamaño=None, vida=None, forma="circulo"):
        """
        Crea una partícula para efectos visuales.
        
        Args:
            x, y: Posición inicial
            color: Color de la partícula (o None para aleatorio)
            velocidad: Tupla (vel_x, vel_y) o None para aleatorio
            tamaño: Tamaño inicial (o None para aleatorio)
            vida: Duración en frames (o None para aleatorio)
            forma: "circulo", "cuadrado", "triangulo", "estrella", "corazon"
        """
        if color is None:
            color = random.choice(list(PALETA.values()))
        if velocidad is None:
            angulo = random.uniform(0, 2 * math.pi)
            magnitud = random.uniform(0.8, 3.0)  # Más rápido para niños
            velocidad = (math.cos(angulo) * magnitud, math.sin(angulo) * magnitud)
        if tamaño is None:
            tamaño = random.uniform(self.sy(5), self.sy(12))  # Más grandes para niños
        if vida is None:
            vida = random.randint(30, 70)
            
        self.particulas.append({
            'x': x, 'y': y,
            'vel_x': velocidad[0], 'vel_y': velocidad[1],
            'tamaño': tamaño, 'tamaño_original': tamaño,
            'color': color, 'vida': vida, 'max_vida': vida,
            'forma': forma
        })

    def crear_explosion_particulas(self, x, y, cantidad=30, colores=None, radio=None):
        """
        Crea una explosión de partículas en la posición dada.
        Versión mejorada para niños con más partículas y formas divertidas.
        
        Args:
            x, y: Centro de la explosión
            cantidad: Número de partículas
            colores: Lista de colores o None para usar la paleta
            radio: Radio máximo de dispersión o None para valor por defecto
        """
        if colores is None:
            colores = random.sample(list(PALETA.values()), min(6, len(PALETA)))
        if radio is None:
            radio = self.sy(120)
            
        formas = ["circulo", "cuadrado", "triangulo", "estrella", "corazon"]
            
        for _ in range(cantidad):
            angulo = random.uniform(0, 2 * math.pi)
            magnitud = random.uniform(1.5, 4.0)  # Más rápido y enérgico
            vel_x = math.cos(angulo) * magnitud
            vel_y = math.sin(angulo) * magnitud
            tamaño = random.uniform(self.sy(6), self.sy(15))  # Más grandes
            color = random.choice(colores)
            vida = random.randint(40, 80)
            forma = random.choice(formas)
            
            self.particulas.append({
                'x': x, 'y': y,
                'vel_x': vel_x, 'vel_y': vel_y,
                'tamaño': tamaño, 'tamaño_original': tamaño,
                'color': color, 'vida': vida, 'max_vida': vida,
                'forma': forma
            })
            
        # Reproducir sonido si está disponible
        if self.sonido_activado and 'explosion' in self.sounds:
            self.sounds['explosion'].play()

    def update_animacion_estrellas(self):
        """Actualiza la animación de estrellas con física mejorada."""
        for s in self.estrellas[:]:
            s['rotacion'] += 3  # Rotación más rápida para niños
            s['vida'] -= 1
            
            # Física mejorada
            s['vel_y'] += 0.05  # Gravedad suave
            s['x'] += s['vel_x']
            s['y'] += s['vel_y']
            
            # Reducción gradual de escala al final de la vida
            if s['vida'] < s['max_vida'] * 0.3:
                s['escala'] *= 0.97
                
            if s['vida'] <= 0:
                self.estrellas.remove(s)
                
        if self.animacion_activa:
            self.tiempo_animacion -= 1
            if self.tiempo_animacion <= 0:
                self.animacion_activa = False

    def update_particulas(self):
        """Actualiza las partículas con física y efectos visuales."""
        for p in self.particulas[:]:
            p['vida'] -= 1
            p['x'] += p['vel_x']
            p['y'] += p['vel_y']
            
            # Física: gravedad y fricción
            p['vel_y'] += 0.1  # Gravedad
            p['vel_x'] *= 0.98  # Fricción horizontal
            
            # Reducción de tamaño gradual
            factor_vida = p['vida'] / p['max_vida']
            p['tamaño'] = p['tamaño_original'] * max(0.2, factor_vida)
            
            if p['vida'] <= 0:
                self.particulas.remove(p)

    def draw_animacion_estrellas(self):
        """Dibuja las estrellas con efectos mejorados."""
        if not self.estrella_img:
            self.estrella_img = self.crear_estrella_img()
            
        for s in self.estrellas:
            # Calcular opacidad basada en vida
            opacidad = int(255 * (s['vida'] / s['max_vida']))
            
            # Crear estrella con el color específico
            estrella_coloreada = self.crear_estrella_img(
                tamaño=int(self.sy(20) * s['escala']), 
                color=s['color']
            )
            
            # Rotar y escalar
            img_rotada = pygame.transform.rotozoom(
                estrella_coloreada,
                s['rotacion'],
                1.0  # Ya aplicamos escala al crear la imagen
            )
            
            # Aplicar opacidad
            img_rotada.set_alpha(opacidad)
            
            # Dibujar con efecto de brillo
            if opacidad > 150:  # Solo para estrellas brillantes
                # Efecto de brillo: dibujar una versión más grande y transparente detrás
                glow = pygame.transform.rotozoom(img_rotada, 0, 1.5)
                glow.set_alpha(opacidad // 3)
                glow_rect = glow.get_rect(center=(s['x'], s['y']))
                self.pantalla.blit(glow, glow_rect)
                
            rect = img_rotada.get_rect(center=(s['x'], s['y']))
            self.pantalla.blit(img_rotada, rect)

    def draw_particulas(self):
        """Dibuja las partículas con diferentes formas y efectos."""
        for p in self.particulas:
            # Calcular opacidad basada en vida
            opacidad = int(255 * (p['vida'] / p['max_vida']))
            color = (*p['color'][:3], opacidad)
            
            # Crear superficie para la partícula
            tamaño = int(p['tamaño'])
            if tamaño <= 0:
                continue
                
            surf = pygame.Surface((tamaño*2, tamaño*2), pygame.SRCALPHA)
            
            # Dibujar según la forma
            if p['forma'] == "circulo":
                pygame.draw.circle(surf, color, (tamaño, tamaño), tamaño)
            elif p['forma'] == "cuadrado":
                pygame.draw.rect(surf, color, (0, 0, tamaño*2, tamaño*2), border_radius=tamaño//3)
            elif p['forma'] == "triangulo":
                pygame.draw.polygon(surf, color, [
                    (tamaño, 0),
                    (0, tamaño*2),
                    (tamaño*2, tamaño*2)
                ])
            elif p['forma'] == "estrella":
                # Dibujar una estrella simple
                puntos = []
                for i in range(5):
                    ang = math.pi/2 + i * 2*math.pi/5
                    puntos.append((
                        tamaño + int(tamaño * 0.8 * math.cos(ang)),
                        tamaño - int(tamaño * 0.8 * math.sin(ang))
                    ))
                    ang += math.pi/5
                    puntos.append((
                        tamaño + int(tamaño * 0.3 * math.cos(ang)),
                        tamaño - int(tamaño * 0.3 * math.sin(ang))
                    ))
                pygame.draw.polygon(surf, color, puntos)
            elif p['forma'] == "corazon":
                # Dibujar un corazón simple
                radio = tamaño * 0.8
                # Dos círculos para la parte superior
                pygame.draw.circle(surf, color, (tamaño - radio//2, tamaño - radio//2), radio//2)
                pygame.draw.circle(surf, color, (tamaño + radio//2, tamaño - radio//2), radio//2)
                # Triángulo para la parte inferior
                pygame.draw.polygon(surf, color, [
                    (tamaño - radio, tamaño - radio//3),
                    (tamaño + radio, tamaño - radio//3),
                    (tamaño, tamaño + radio)
                ])
            
            # Dibujar en pantalla
            self.pantalla.blit(surf, (p['x'] - tamaño, p['y'] - tamaño))

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

    def init_responsive_ui(self):
        """
        Inicializa elementos de UI responsivos.
        Este método debe ser sobrescrito por cada juego para definir sus elementos específicos.
        """
        # Elementos base comunes a todos los juegos
        self.ui_elements = {
            "titulo_rect": (0, self.navbar_height + self.sy(30), self.ANCHO, self.sy(70)),
            "feedback_rect": self.scaler.get_centered_rect(500, 60, vertical_offset=self.ALTO//2 - 50),
            "puntaje_rect": (self.sx(18), self.ALTO - self.sy(80), 
                            self.sx(200), self.sy(60)),
            "tiempo_rect": (self.ANCHO - self.sx(180) - self.sx(18), 
                           self.navbar_height + self.sy(18), 
                           self.sx(180), self.sy(50))
        }

    def _nivel_from_dificultad(self, dificultad):
        """
        Traduce la dificultad a un nivel textual amigable para niños.
        """
        if dificultad == "Fácil":
            return "Principiante 🌱"
        elif dificultad == "Normal":
            return "Aventurero 🌟"
        else:
            return "Experto 🏆"

    def _update_navbar_height(self):
        """
        Actualiza la altura de la barra de navegación si existe.
        """
        if self.navbar and hasattr(self.navbar, "get_height"):
            self.navbar_height = self.navbar.get_height()
        elif self.navbar and hasattr(self.navbar, "height"):
            self.navbar_height = self.navbar.height
        else:
            self.navbar_height = self.sy(60)  # Valor por defecto escalado

    def cargar_imagenes(self):
        """Para ser sobrescrito por cada juego si necesita cargar imágenes."""
        pass

    def dibujar_fondo(self):
        """
        Dibuja el fondo con gradiente o imagen, respetando la barra de navegación.
        Versión mejorada con estilo Apple para niños.
        """
        if self.fondo:
            # Si hay una imagen de fondo, usarla
            if isinstance(self.fondo, pygame.Surface):
                # Escalar la imagen para que cubra toda la pantalla
                fondo_escalado = pygame.transform.scale(self.fondo, (self.ANCHO, self.ALTO))
                self.pantalla.blit(fondo_escalado, (0, 0))
            elif isinstance(self.fondo, tuple) and len(self.fondo) >= 3:
                # Si es un color, llenar con ese color
                self.pantalla.fill(self.fondo)
            elif isinstance(self.fondo, tuple) and len(self.fondo) == 2:
                # Si son dos colores, crear un gradiente
                gradiente = get_gradient(self.ANCHO, self.ALTO, self.fondo[0], self.fondo[1])
                self.pantalla.blit(gradiente, (0, 0))
        else:
            # Fondo por defecto: gradiente suave estilo Apple para niños
            gradiente = get_gradient(
                self.ANCHO, self.ALTO, 
                (240, 248, 255),  # Azul muy claro arriba
                (230, 240, 250)   # Azul claro abajo
            )
            self.pantalla.blit(gradiente, (0, 0))
            
            # Dibujar nubes decorativas
            self.dibujar_nubes()
            
            # Dibujar burbujas
            self.dibujar_burbujas()

    def mostrar_texto(self, texto, x, y, w, h, fuente=None, color=(30,30,30), centrado=False):
        """Muestra texto adaptativo en pantalla con coordenadas escaladas."""
        fuente = fuente or self.fuente
        mostrar_texto_adaptativo(
            pantalla=self.pantalla,
            texto=texto,
            x=x,
            y=y,
            w=w,
            h=h,
            fuente_base=fuente,
            color=color,
            centrado=centrado
        )

    def mostrar_titulo(self):
        """
        Muestra el título del juego centrado debajo de la navbar con estilo Apple para niños.
        """
        titulo_rect = self.ui_elements.get("titulo_rect", 
                                          (0, self.navbar_height + self.sy(30), 
                                           self.ANCHO, self.sy(70)))
        
        x, y, w, h = titulo_rect
        
        # Crear superficie para sombra y fondo
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        
        # Dibujar fondo con borde redondeado
        pygame.draw.rect(
            surf,
            (255, 255, 255, 180),
            (0, 0, w, h),
            border_radius=self.sy(25)
        )
        
        # Aplicar gradiente como overlay
        gradiente = get_gradient(w, h, (220, 240, 255), (200, 220, 245))
        gradiente.set_alpha(120)
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(
            mask,
            (255, 255, 255, 255),
            (0, 0, w, h),
            border_radius=self.sy(25)
        )
        gradiente_masked = gradiente.copy()
        gradiente_masked.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(gradiente_masked, (0, 0))
        
        # Aplicar a la pantalla
        self.pantalla.blit(surf, (x, y))
        
        # Texto con sombra para profundidad
        nivel = self._nivel_from_dificultad(self.dificultad)
        texto = f"{self.nombre} - {nivel}"
        
        sombra_offset = self.sy(2)
        mostrar_texto_adaptativo(
            pantalla=self.pantalla,
            texto=texto,
            x=titulo_rect[0] + sombra_offset,
            y=titulo_rect[1] + sombra_offset,
            w=titulo_rect[2],
            h=titulo_rect[3],
            fuente_base=self.fuente_titulo,
            color=(40, 80, 120, 150),  # Color de sombra semitransparente
            centrado=True
        )
        
        # Texto principal con color vibrante
        mostrar_texto_adaptativo(
            pantalla=self.pantalla,
            texto=texto,
            x=titulo_rect[0],
            y=titulo_rect[1],
            w=titulo_rect[2],
            h=titulo_rect[3],
            fuente_base=self.fuente_titulo,
            color=PALETA["azul_oceano"],  # Color vibrante
            centrado=True
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

    def mostrar_tiempo(self, formato="mm:ss"):
        """
        Muestra el tiempo transcurrido en el juego con estilo Apple para niños.
        
        Args:
            formato: Formato de tiempo ("mm:ss" o "hh:mm:ss")
        """
        tiempo_rect = self.ui_elements.get("tiempo_rect")
        if not tiempo_rect:
            return
            
        x, y, w, h = tiempo_rect
        
        # Calcular tiempo transcurrido
        self.tiempo_juego = time.time() - self.tiempo_inicio
        
        # Formatear según el formato solicitado
        if formato == "mm:ss":
            minutos = int(self.tiempo_juego // 60)
            segundos = int(self.tiempo_juego % 60)
            texto_tiempo = f"⏱️ {minutos:02d}:{segundos:02d}"
        else:  # hh:mm:ss
            horas = int(self.tiempo_juego // 3600)
            minutos = int((self.tiempo_juego % 3600) // 60)
            segundos = int(self.tiempo_juego % 60)
            texto_tiempo = f"⏱️ {horas:02d}:{minutos:02d}:{segundos:02d}"
            
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
        
        # Mostrar texto
        mostrar_texto_adaptativo(
            pantalla=self.pantalla,
            texto=texto_tiempo,
            x=x,
            y=y,
            w=w,
            h=h,
            fuente_base=self.fuente,
            color=(50, 50, 100),
            centrado=True
        )

    def generar_opciones(self, respuesta: int, cantidad: int = 3, dificultad: str = None) -> list[int]:
        """
        Genera opciones aleatorias alrededor de la respuesta correcta, sin duplicados ni negativos.
        Mejorada para evitar bucles infinitos, asegurar variedad y ajustar según dificultad.
        
        Args:
            respuesta: La respuesta correcta
            cantidad: Número de opciones a generar (incluyendo la correcta)
            dificultad: Nivel de dificultad ("Fácil", "Normal", "Difícil") o None para usar el del juego
        
        Returns:
            Lista de opciones con la respuesta correcta incluida en posición aleatoria
        """
        if dificultad is None:
            dificultad = self.dificultad
            
        opciones = {respuesta}
        
        # Ajustar rango según dificultad
        if dificultad == "Fácil":
            rango_min = max(0, respuesta - 5)
            rango_max = respuesta + 6
            distractor_max = 10
        elif dificultad == "Normal":
            rango_min = max(0, respuesta - 10)
            rango_max = respuesta + 11
            distractor_max = 20
        else:  # Difícil
            rango_min = max(0, respuesta - 15)
            rango_max = respuesta + 16
            distractor_max = 30
            
        # Generar opciones cercanas primero
        posibles = set(range(rango_min, rango_max)) - {respuesta}
        while len(opciones) < cantidad and posibles:
            op = random.choice(list(posibles))
            opciones.add(op)
            posibles.remove(op)
            
        # Si necesitamos más opciones, generar distractores más lejanos
        if len(opciones) < cantidad:
            # Asegurar que al menos un distractor sea cercano a la respuesta
            if respuesta > 0:
                opciones.add(max(0, respuesta - 1))
            opciones.add(respuesta + 1)
            
            # Añadir distractores más lejanos si aún necesitamos más
            while len(opciones) < cantidad:
                # Alternar entre valores mayores y menores
                if random.random() < 0.5:
                    op = respuesta + random.randint(2, distractor_max)
                else:
                    op = max(0, respuesta - random.randint(2, distractor_max))
                opciones.add(op)
                
        # Convertir a lista y mezclar
        resultado = list(opciones)
        random.shuffle(resultado)
        
        # Asegurar que tenemos exactamente la cantidad solicitada
        return resultado[:cantidad]

    def dibujar_opciones(
        self,
        opciones=None,
        tooltips=None,
        estilo="apple",  # Cambiado a apple por defecto
        border_radius=None,
        x0=None,
        y0=None,
        espacio=None,
        colores=None,
        ancho=None,
        alto=None
    ):
        """
        Dibuja botones de opciones de forma responsiva, colorida y reutilizable.
        Estilo Apple para niños.
        
        Args:
            opciones: Lista de opciones a mostrar (o None para usar self.opciones)
            tooltips: Lista de tooltips para cada opción
            estilo: Estilo de botón ("flat", "apple", "round")
            border_radius: Radio de borde o None para valor por defecto
            x0, y0: Posición inicial o None para centrar
            espacio: Espacio entre botones o None para valor por defecto
            colores: Lista de colores para los botones o None para usar paleta
            ancho, alto: Dimensiones de los botones o None para calcular automáticamente
        """
        opciones = opciones if opciones is not None else getattr(self, "opciones", [])
        if not opciones:
            return  # No dibujar si no hay opciones
            
        # Valores escalados - Más grandes para niños
        border_radius = border_radius or self.sy(20)
        espacio = espacio or self.sx(25)
        
        cnt = len(opciones)
        
        # Calcular dimensiones si no se especifican - Más grandes para niños
        if ancho is None:
            w = max(self.sx(120), min(self.sx(200), self.ANCHO // (cnt * 2)))
        else:
            w = self.sx(ancho)
            
        if alto is None:
            h = max(self.sy(60), min(self.sy(90), self.ALTO // 10))
        else:
            h = self.sy(alto)
        
        # Calcular posición inicial si no se especifica
        if x0 is None:
            x0 = (self.ANCHO - (w * cnt + espacio * (cnt - 1))) // 2
        else:
            x0 = self.sx(x0)
            
        if y0 is None:
            y0 = self.ALTO // 2 - h // 2
        else:
            y0 = self.sy(y0)
            
        # Usar colores especificados o la paleta por defecto
        if colores is None:
            # Usar colores más vibrantes para niños
            paleta = [
                PALETA["rojo_manzana"],
                PALETA["verde_manzana"],
                PALETA["azul_cielo"],
                PALETA["amarillo_sol"],
                PALETA["rosa_chicle"],
                PALETA["morado_uva"]
            ]
            
            # Asegurar que tenemos suficientes colores
            if cnt > len(paleta):
                paleta = paleta * (cnt // len(paleta) + 1)
                
            paleta = paleta[:cnt]
        else:
            paleta = colores

        self.opcion_botones.clear()
        for i, val in enumerate(opciones):
            color_bg = paleta[i % len(paleta)]
            
            # Calcular color de hover basado en luminosidad
            lum = 0.299 * color_bg[0] + 0.587 * color_bg[1] + 0.114 * color_bg[2]
            if lum > 128:
                # Color oscuro para fondos claros
                color_hover = tuple(max(0, c - 30) for c in color_bg)
            else:
                # Color claro para fondos oscuros
                color_hover = tuple(min(255, c + 30) for c in color_bg)
                # Color claro para fondos oscuros
                color_hover = tuple(min(255, c + 30) for c in color_bg)
                
            # Calcular color de texto basado en luminosidad
            color_texto = (0, 0, 0) if lum > 180 else (255, 255, 255)
            
            x = x0 + i * (w + espacio)
            
            # Crear botón con estilo Apple para niños
            btn = Boton(
                texto=str(val),
                x=x, y=y0, ancho=w, alto=h,
                fuente=self.fuente,
                color_normal=color_bg,
                color_hover=color_hover,
                color_texto=color_texto,
                border_radius=border_radius,
                estilo=estilo,
                tooltip=tooltips[i] if tooltips and i < len(tooltips) else None,
                border_color=(255, 255, 255, 150),
                border_width=3
            )
            btn.draw(self.pantalla, tooltip_manager=self.tooltip_manager)
            self.opcion_botones.append(btn)

    @staticmethod
    def color_complementario(rgb):
        """Devuelve el color complementario."""
        return tuple(255 - c for c in rgb)

    def mostrar_victoria(
        self, carta_rects, color_panel=(255, 255, 224), color_borde=(255, 215, 0)
    ):
        """Muestra pantalla de victoria con escalado responsivo y efectos visuales mejorados."""
        ancho_panel = self.sx(550)
        alto_panel = self.sy(350)  # Más alto para más contenido
        x_panel = (self.ANCHO - ancho_panel) // 2
        y_panel = (self.ALTO - alto_panel) // 2
        
        # Efecto de oscurecimiento de fondo
        overlay = pygame.Surface((self.ANCHO, self.ALTO), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Semi-transparente
        self.pantalla.blit(overlay, (0, 0))
        
        # Crear superficie para sombra y fondo
        surf = pygame.Surface((ancho_panel, alto_panel), pygame.SRCALPHA)
        
        # Dibujar sombra
        sombra = pygame.Surface((ancho_panel, alto_panel), pygame.SRCALPHA)
        pygame.draw.rect(
            sombra,
            (0, 0, 0, 50),
            (8, 8, ancho_panel, alto_panel),
            border_radius=self.sy(30)
        )
        self.pantalla.blit(sombra, (x_panel, y_panel))
        
        # Dibujar fondo con borde redondeado
        pygame.draw.rect(
            surf,
            (255, 255, 255, 250),
            (0, 0, ancho_panel, alto_panel),
            border_radius=self.sy(30)
        )
        
        # Aplicar gradiente como overlay
        gradiente = get_gradient(ancho_panel, alto_panel, (255, 250, 230), (255, 240, 200))
        gradiente.set_alpha(180)
        mask = pygame.Surface((ancho_panel, alto_panel), pygame.SRCALPHA)
        pygame.draw.rect(
            mask,
            (255, 255, 255, 255),
            (0, 0, ancho_panel, alto_panel),
            border_radius=self.sy(30)
        )
        gradiente_masked = gradiente.copy()
        gradiente_masked.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(gradiente_masked, (0, 0))
        
        # Dibujar borde con estilo Apple
        pygame.draw.rect(
            surf,
            (255, 215, 0, 200),
            (0, 0, ancho_panel, alto_panel),
            width=4,
            border_radius=self.sy(30)
        )
        
        # Aplicar a la pantalla
        self.pantalla.blit(surf, (x_panel, y_panel))
        
        # Título con efecto de sombra
        sombra_offset = self.sy(3)
        mostrar_alternativo_adaptativo(
            self.pantalla, "¡FELICIDADES! 🎉",
            x_panel + sombra_offset, y_panel + self.sy(30) + sombra_offset, 
            ancho_panel, self.sy(70),
            self.fuente_titulo, (50, 80, 120, 150), centrado=True
        )
        
        mostrar_alternativo_adaptativo(
            self.pantalla, "¡FELICIDADES! 🎉",
            x_panel, y_panel + self.sy(30), ancho_panel, self.sy(70),
            self.fuente_titulo, PALETA["azul_oceano"], centrado=True
        )
        
        # Subtítulo
        mostrar_texto_adaptativo(
            self.pantalla, "¡Has completado el juego!",
            x_panel, y_panel + self.sy(110), ancho_panel, self.sy(50),
            fuente_base=self.fuente, 
            color=(30, 30, 30), 
            centrado=True
        )
        
        # Estadísticas
        tiempo_str = f"{int(self.tiempo_juego // 60):02d}:{int(self.tiempo_juego % 60):02d}"
        stats_text = f"Tiempo: {tiempo_str}\nRacha máxima: {self.mejor_racha}"
        
        mostrar_texto_adaptativo(
            self.pantalla, stats_text,
            x_panel, y_panel + self.sy(160), ancho_panel, self.sy(80),
            fuente_base=self.fuente, 
            color=(50, 50, 80), 
            centrado=True
        )
        
        # Botones con estilo Apple para niños
        boton_reiniciar = Boton(
            "¡Jugar otra vez! 🔄",
            x_panel + self.sx(60),
            y_panel + self.sy(250),
            self.sx(200), self.sy(70),
            color_normal=PALETA["verde_manzana"],
            color_hover=(50, 180, 80),
            fuente=self.fuente,
            texto_adaptativo=True,
            estilo="apple",
            border_radius=self.sy(25),
            border_color=(255, 255, 255, 150),
            border_width=3
        )
        
        boton_menu = Boton(
            "Menú Principal 🏠",
            x_panel + ancho_panel - self.sx(260),
            y_panel + self.sy(250),
            self.sx(200), self.sy(70),
            color_normal=PALETA["azul_cielo"],
            color_hover=(30, 150, 220),
            fuente=self.fuente,
            texto_adaptativo=True,
            estilo="apple",
            border_radius=self.sy(25),
            border_color=(255, 255, 255, 150),
            border_width=3
        )
        
        boton_reiniciar.draw(self.pantalla)
        boton_menu.draw(self.pantalla)
        
        carta_rects.append((boton_reiniciar.rect, {'id': 'reiniciar'}))
        carta_rects.append((boton_menu.rect, {'id': 'menu'}))
        
        # Efectos de partículas
        if random.random() < 0.05:  # Ocasionalmente añadir más partículas
            self.crear_explosion_particulas(
                random.randint(x_panel, x_panel + ancho_panel),
                random.randint(y_panel, y_panel + self.sy(60)),
                cantidad=15,
                colores=[PALETA["amarillo_sol"], PALETA["rosa_pastel"], PALETA["verde_lima"]]
            )

    def handle_event(self, evento):
        """
        Maneja eventos comunes a todos los juegos.
        
        Returns:
            True si el evento fue manejado, False en caso contrario
        """
        # Actualizar tooltip manager
        if hasattr(self, 'tooltip_manager'):
            self.tooltip_manager.update(pygame.mouse.get_pos())
        
        # Lógica base: salir, resize, etc.
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                if self.return_to_menu:
                    self.return_to_menu()
                    pygame.display.set_caption("jugando con dino")
                    return True
            elif evento.key == pygame.K_F3:
                # Alternar modo debug
                self.debug_mode = not self.debug_mode
                return True
                
        if evento.type == pygame.VIDEORESIZE:
            self.ANCHO, self.ALTO = evento.w, evento.h
            self.pantalla = pygame.display.set_mode((self.ANCHO, self.ALTO), pygame.RESIZABLE)
            self._update_navbar_height()
            
            # Actualizar el sistema de escalado
            self.scaler.update(self.ANCHO, self.ALTO)
            
            # Actualizar fuentes con nuevos tamaños escalados
            self.fuente_titulo = obtener_fuente(self.sf(40), negrita=True)
            self.fuente = obtener_fuente(self.sf(24))
            self.fuente_pequeña = obtener_fuente(self.sf(18))
            
            # Reinicializar elementos UI responsivos
            self.init_responsive_ui()
            
            # Llamar al método específico de cada juego
            self.on_resize(self.ANCHO, self.ALTO)
            return True
            
        # Manejar clicks en botones de opciones
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            # Botones de opciones
            for btn in self.opcion_botones:
                if btn.handle_event(evento):
                    return True
                    
        # Para ser sobrescrito por cada juego
        return False

    def on_resize(self, ancho, alto):
        """
        Método para que los juegos hijos ajusten elementos al redimensionar.
        Por defecto no hace nada, debe ser sobrescrito.
        """
        pass

    def update(self, dt=None):
        """
        Actualiza la lógica del juego.
        
        Args:
            dt: Delta time (tiempo transcurrido desde el último frame) o None para calcularlo
        """
        # Calcular delta time si no se proporciona
        current_time = time.time()
        if dt is None:
            dt = current_time - self.tiempo_ultimo_frame
        self.tiempo_ultimo_frame = current_time
        self.delta_time = dt
        
        # Actualizar FPS
        self.fps_counter += 1
        self.fps_timer += dt
        if self.fps_timer >= 1.0:
            self.fps_actual = self.fps_counter
            self.fps_counter = 0
            self.fps_timer = 0
        
        # Actualizar animaciones
        self.update_animacion_estrellas()
        self.update_particulas()
        self.actualizar_nubes()
        self.actualizar_burbujas()
        
        # Para ser sobrescrito por cada juego
        pass

    def draw(self, surface=None):
        """
        Dibuja el juego en la superficie especificada.
        
        Args:
            surface: Superficie donde dibujar o None para usar self.pantalla
        """
        surface = surface or self.pantalla
        
        # Dibujar fondo
        self.dibujar_fondo()
        
        # Dibujar elementos comunes
        # Dibujar título
        self.mostrar_titulo()
        
        # Dibujar tiempo
        self.mostrar_tiempo()
        
        # Dibujar animaciones
        self.draw_particulas()
        self.draw_animacion_estrellas()
        
        # Dibujar feedback si existe
        self.dibujar_feedback()
        
        # Dibujar tooltips
        if hasattr(self, 'tooltip_manager'):
            self.tooltip_manager.draw(self.pantalla)
            
        # Dibujar modo debug si está activado
        if self.debug_mode:
            self.dibujar_debug_info()
            
    def dibujar_debug_info(self):
        """Muestra información de depuración en pantalla."""
        debug_info = [
            f"FPS: {self.fps_actual}",
            f"Resolución: {self.ANCHO}x{self.ALTO}",
            f"Escala: {self.scaler.scale_x:.2f}x, {self.scaler.scale_y:.2f}y",
            f"Tiempo: {self.tiempo_juego:.1f}s",
            f"Estado: {self.estado}",
            f"Partículas: {len(self.particulas)}",
            f"Estrellas: {len(self.estrellas)}",
            f"Burbujas: {len(self.burbujas)}"
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

    def mostrar_feedback(self, es_correcto, respuesta_correcta=None):
        """
        Muestra feedback visual y auditivo sobre la respuesta del usuario.
        
        Args:
            es_correcto: True si la respuesta es correcta, False en caso contrario
            respuesta_correcta: La respuesta correcta para mostrar en caso de error
        """
        if es_correcto:
            mensaje = random.choice(mensajes_correcto)
            self.racha_correctas += 1
            self.mejor_racha = max(self.mejor_racha, self.racha_correctas)
            self.tiempo_cambio_racha = time.time()  # Para animación
            self.mensaje_color = (152, 251, 152, 220)  # Verde claro
            
            # Efectos visuales
            self.crear_efecto_estrellas((self.ANCHO // 2, self.ALTO // 2))
            
            # Reproducir sonido si está disponible
            if self.sonido_activado and 'correcto' in self.sounds:
                self.sounds['correcto'].play()
        else:
            mensaje = random.choice(mensajes_incorrecto)
            if respuesta_correcta is not None:
                mensaje = mensaje.format(respuesta=respuesta_correcta)
            self.racha_correctas = 0
            self.mensaje_color = (255, 182, 193, 220)  # Rosa claro
            
            # Reproducir sonido si está disponible
            if self.sonido_activado and 'incorrecto' in self.sounds:
                self.sounds['incorrecto'].play()
                
        self.mostrar_mensaje_temporal(mensaje)

    def mostrar_mensaje_temporal(self, mensaje, tiempo=60, color=None):
        """
        Activa un mensaje temporal de feedback para mostrar en pantalla.
        
        Args:
            mensaje: Texto a mostrar
            tiempo: Duración en frames
            color: Color del mensaje o None para usar el último color establecido
        """
        self.mensaje = mensaje
        self.tiempo_mensaje = tiempo
        if color:
            self.mensaje_color = color
        self.mensaje_animacion = 1.0  # Para animación de entrada

    def dibujar_feedback(self):
        """Dibuja el mensaje de feedback si está activo con animaciones mejoradas."""
        if self.tiempo_mensaje > 0 and self.mensaje:
            # Calcular posición del feedback
            ancho = self.sx(550)  # Más ancho para niños
            alto = self.sy(80)    # Más alto para niños
            x = (self.ANCHO - ancho) // 2
            y = self.ALTO - self.sy(180)  # Posición fija desde abajo
            
            # Asegurar que el feedback esté siempre visible
            if y < self.navbar_height:
                y = self.navbar_height + self.sy(10)
            
            # Animación de entrada/salida
            if self.tiempo_mensaje < 10:  # Animación de salida
                factor = self.tiempo_mensaje / 10
                alto = int(alto * factor)
                self.mensaje_animacion = factor
            elif self.mensaje_animacion < 1.0:  # Animación de entrada
                self.mensaje_animacion = min(1.0, self.mensaje_animacion + 0.1)
                alto = int(alto * self.mensaje_animacion)
            
            # Crear superficie para sombra y fondo
            surf = pygame.Surface((ancho, alto), pygame.SRCALPHA)
            
            # Dibujar sombra
            sombra = pygame.Surface((ancho, alto), pygame.SRCALPHA)
            pygame.draw.rect(
                sombra,
                (0, 0, 0, 40),
                (4, 4, ancho, alto),
                border_radius=self.sy(25)
            )
            surf.blit(sombra, (0, 0))
            
            # Dibujar fondo con borde redondeado
            pygame.draw.rect(
                surf,
                (255, 255, 255, 240),
                (0, 0, ancho, alto),
                border_radius=self.sy(25)
            )
            
            # Aplicar gradiente como overlay
            gradiente = get_gradient(ancho, alto, 
                                    self.mensaje_color[:3], 
                                    tuple(max(0, c-30) for c in self.mensaje_color[:3]))
            gradiente.set_alpha(self.mensaje_color[3] if len(self.mensaje_color) > 3 else 180)
            mask = pygame.Surface((ancho, alto), pygame.SRCALPHA)
            pygame.draw.rect(
                mask,
                (255, 255, 255, 255),
                (0, 0, ancho, alto),
                border_radius=self.sy(25)
            )
            gradiente_masked = gradiente.copy()
            gradiente_masked.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            surf.blit(gradiente_masked, (0, 0))
            
            # Dibujar borde con estilo Apple
            pygame.draw.rect(
                surf,
                (255, 255, 255, 150),
                (0, 0, ancho, alto),
                width=3,
                border_radius=self.sy(25)
            )
            
            # Aplicar a la pantalla
            self.pantalla.blit(surf, (x, y))
            
            # Mostrar texto con sombra sutil
            sombra_offset = self.sy(2)
            mostrar_texto_adaptativo(
                self.pantalla,
                self.mensaje,
                x + sombra_offset, y + sombra_offset,
                ancho, alto,
                fuente_base=self.fuente,
                color=(10, 10, 10, 150),
                centrado=True
            )
            
            mostrar_texto_adaptativo(
                self.pantalla,
                self.mensaje,
                x, y,
                ancho, alto,
                fuente_base=self.fuente,
                color=(30, 30, 30),
                centrado=True
            )
            
            self.tiempo_mensaje -= 1

# Ejemplo de uso para un juego específico
class JuegoEjemplo(JuegoBase):
    def __init__(self, nombre, pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu):
        super().__init__(nombre, pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu)
        
        # Inicializar elementos específicos del juego
        self.puntuacion = 0
        self.total_preguntas = 10
        self.pregunta_actual = 1
        self.respuesta_correcta = 42
        self.opciones = self.generar_opciones(self.respuesta_correcta, 4)
        
        # Elementos UI específicos de este juego
        self.init_responsive_ui()
        
    def init_responsive_ui(self):
        """Inicializa elementos UI específicos de este juego."""
        super().init_responsive_ui()  # Llamar al método de la clase base primero
        
        # Añadir elementos específicos de este juego
        self.ui_elements.update({
            "pregunta_rect": (self.sx(100), self.navbar_height + self.sy(100), 
                             self.ANCHO - self.sx(200), self.sy(120)),
            "opciones_y": self.ALTO // 2 + self.sy(50),
            "instrucciones_rect": (self.sx(50), self.ALTO - self.sy(100), 
                                  self.ANCHO - self.sx(100), self.sy(50))
        })
        
    def on_resize(self, ancho, alto):
        """Maneja el redimensionamiento específico para este juego."""
        # Actualizar posiciones de elementos específicos
        self.init_responsive_ui()
        
    def draw(self, surface=None):
        """Dibuja la interfaz del juego."""
        # Llamar al método de la clase base primero
        super().draw(surface)
        
        surface = surface or self.pantalla
            
        # Dibujar pregunta con estilo mejorado
        pregunta_rect = self.ui_elements["pregunta_rect"]
        x, y, w, h = pregunta_rect
        
        # Crear superficie para sombra y fondo
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        
        # Dibujar sombra
        sombra = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(
            sombra,
            (0, 0, 0, 30),
            (4, 4, w, h),
            border_radius=self.sy(25)
        )
        surface.blit(sombra, (x, y))
        
        # Dibujar fondo con borde redondeado
        pygame.draw.rect(
            surf,
            (255, 255, 255, 240),
            (0, 0, w, h),
            border_radius=self.sy(25)
        )
        
        # Aplicar gradiente como overlay
        gradiente = get_gradient(w, h, (240, 245, 255), (220, 230, 250))
        gradiente.set_alpha(120)
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(
            mask,
            (255, 255, 255, 255),
            (0, 0, w, h),
            border_radius=self.sy(25)
        )
        gradiente_masked = gradiente.copy()
        gradiente_masked.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(gradiente_masked, (0, 0))
        
        # Dibujar borde con estilo Apple
        pygame.draw.rect(
            surf,
            (100, 150, 255, 150),
            (0, 0, w, h),
            width=3,
            border_radius=self.sy(25)
        )
        
        # Aplicar a la pantalla
        surface.blit(surf, (x, y))
        
        # Texto de la pregunta
        self.mostrar_texto(
            f"Pregunta {self.pregunta_actual}/{self.total_preguntas}: ¿Cuál es la respuesta a la vida, el universo y todo lo demás?",
            x + self.sx(20), y + self.sy(20), 
            w - self.sx(40), h - self.sy(40),
            self.fuente, (30, 30, 90), centrado=True
        )
        
        # Dibujar opciones con estilo mejorado
        self.dibujar_opciones(
            opciones=self.opciones,
            y0=self.ui_elements["opciones_y"],
            estilo="apple",
            border_radius=self.sy(25)
        )
        
        # Dibujar puntaje
        self.mostrar_puntaje(self.puntuacion, self.total_preguntas)
        
        # Dibujar racha
        self.mostrar_racha()
        
        # Dibujar operación actual
        self.mostrar_operacion()
        
        # Dibujar instrucciones
        instrucciones_rect = self.ui_elements["instrucciones_rect"]
        
        # Fondo de instrucciones
        x, y, w, h = instrucciones_rect
        
        # Crear superficie para sombra y fondo
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        
        # Dibujar fondo con borde redondeado
        pygame.draw.rect(
            surf,
            (255, 255, 255, 180),
            (0, 0, w, h),
            border_radius=self.sy(20)
        )
        
        # Aplicar a la pantalla
        surface.blit(surf, (x, y))
        
        self.mostrar_texto(
            "Haz clic en la opción correcta. Presiona ESC para volver al menú.",
            instrucciones_rect[0], instrucciones_rect[1], 
            instrucciones_rect[2], instrucciones_rect[3],
            fuente=self.fuente_pequeña, 
            color=(100, 100, 100), 
            centrado=True
        )
        
    def handle_event(self, evento):
        """Maneja eventos específicos del juego."""
        # Primero manejar eventos base
        if super().handle_event(evento):
            return True
            
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for i, btn in enumerate(self.opcion_botones):
                if btn.collidepoint(evento.pos):
                    self.verificar_respuesta(self.opciones[i])
                    return True
                    
        return False
    
    def verificar_respuesta(self, respuesta):
        """Verifica si la respuesta seleccionada es correcta."""
        es_correcta = respuesta == self.respuesta_correcta
        
        if es_correcta:
            self.puntuacion += 1
            # Crear partículas de celebración
            self.crear_explosion_particulas(
                self.ANCHO // 2,
                self.ALTO // 2,
                cantidad=20,
                colores=[PALETA["amarillo_sol"], PALETA["verde_lima"], PALETA["azul_cielo"]]
            )
            
        self.mostrar_feedback(es_correcta, self.respuesta_correcta)
        
        # Generar nueva pregunta
        if self.pregunta_actual < self.total_preguntas:
            self.pregunta_actual += 1
            self.respuesta_correcta = random.randint(1, 100)
            self.opciones = self.generar_opciones(self.respuesta_correcta, 4)
            # Actualizar operación actual (ejemplo)
            self.operacion_actual = f"{self.respuesta_correcta - random.randint(1, 10)} + ? = {self.respuesta_correcta}"
        else:
            # Juego terminado
            self.estado = "victoria"
            self.mostrar_mensaje_temporal(
                f"¡Juego terminado! Puntuación final: {self.puntuacion}/{self.total_preguntas}", 
                120,
                (200, 255, 200, 220)
            )

# Función para probar el sistema responsivo
def test_responsive_game():
    pygame.init()
    pantalla = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
    pygame.display.set_caption("Test Responsivo")
    
    # Crear instancia del juego de ejemplo
    juego = JuegoEjemplo(
        nombre="Juego de Prueba",
        pantalla=pantalla,
        config={},
        dificultad="Normal",
        fondo=None,  # Usar fondo por defecto con nubes y burbujas
        navbar=None,
        images={},
        sounds={},
        return_to_menu=lambda: print("Volviendo al menú")
    )
    
    # Establecer operación actual de ejemplo
    juego.operacion_actual = "32 + 10 = ?"
    
    ejecutando = True
    reloj = pygame.time.Clock()
    
    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
                
            juego.handle_event(evento)
            
        juego.update()
        juego.draw()
        
        pygame.display.flip()
        reloj.tick(60)
        
    pygame.quit()

if __name__ == "__main__":
    test_responsive_game()