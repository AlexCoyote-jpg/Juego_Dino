import pygame
import os
import emoji
from collections import OrderedDict

# LRU Cache para optimizar el rendimiento
class LRUCache:
    def __init__(self, capacity=128):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def put(self, key, value):
        self.cache[key] = value
        self.cache.move_to_end(key)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

# Caché global para fuentes
_fuentes_cache = {}

def obtener_fuente(tamano, negrita=False):
    """Obtiene una fuente del tamaño especificado, usando caché."""
    key = (tamano, negrita)
    if key not in _fuentes_cache:
        _fuentes_cache[key] = pygame.font.SysFont("Arial", tamano, bold=negrita)
    return _fuentes_cache[key]

def get_default_font():
    """Obtiene la fuente predeterminada."""
    return obtener_fuente(24)

# Clase para renderizar texto con emojis
class EmojiTextRenderer:
    def __init__(
        self, 
        font_names=["Segoe UI Symbol", "Arial Unicode MS"],
        emoji_path="assets/fuentes/twemoji_png",
        emoji_scale_factor=1.2,
        cache_capacity=256
    ):
        pygame.font.init()
        self.font_names = font_names
        self.emoji_path = emoji_path
        self.emoji_scale_factor = emoji_scale_factor
        self.emoji_cache = LRUCache(capacity=cache_capacity)
        self.line_cache = LRUCache(capacity=cache_capacity)
        self.fonts = {}  # Se inicializarán según el tamaño necesario

    def get_font(self, size, bold=False):
        """Obtiene una fuente del tamaño especificado."""
        key = (size, bold)
        if key not in self.fonts:
            for name in self.font_names:
                try:
                    self.fonts[key] = pygame.font.SysFont(name, size, bold=bold)
                    break
                except:
                    continue
            if key not in self.fonts:
                self.fonts[key] = pygame.font.SysFont(None, size, bold=bold)
        return self.fonts[key]

    def is_emoji(self, seq: str) -> bool:
        """Determina si una secuencia es un emoji."""
        return seq in emoji.EMOJI_DATA

    def _load_emoji_surf(self, seq: str, size):
        """Carga la superficie de un emoji desde el archivo."""
        # Intenta con codepoints completos
        full = "-".join(f"{ord(c):x}" for c in seq)
        path_full = os.path.join(self.emoji_path, f"{full}.png")
        if os.path.isfile(path_full):
            surf = pygame.image.load(path_full).convert_alpha()
            return pygame.transform.smoothscale(surf, (size, size))
        
        # Fallback: elimina FE0F (variante de presentación)
        stripped = "".join(c for c in seq if ord(c) != 0xfe0f)
        short = "-".join(f"{ord(c):x}" for c in stripped)
        path_short = os.path.join(self.emoji_path, f"{short}.png")
        if os.path.isfile(path_short):
            surf = pygame.image.load(path_short).convert_alpha()
            return pygame.transform.smoothscale(surf, (size, size))
        
        return None

    def get_emoji_surf(self, seq: str, size):
        """Obtiene la superficie de un emoji, usando caché."""
        key = f"{'-'.join(f'{ord(c):x}' for c in seq if ord(c) != 0xfe0f)}_{size}"
        surf = self.emoji_cache.get(key)
        if surf is not None:
            return surf
        surf = self._load_emoji_surf(seq, size)
        self.emoji_cache.put(key, surf)
        return surf

    def measure_text_width(self, text: str, font_size: int) -> int:
        """Mide el ancho de un texto con emojis."""
        width = 0
        i = 0
        length = len(text)
        font = self.get_font(font_size)
        emoji_size = int(font_size * self.emoji_scale_factor)
        
        while i < length:
            # Verifica si es un emoji
            emoji_seq = None
            for size in range(4, 0, -1):
                if i+size <= length and self.is_emoji(text[i:i+size]):
                    emoji_seq = text[i:i+size]
                    break
            
            if emoji_seq:
                width += emoji_size
                i += len(emoji_seq)
            else:
                ch = text[i]
                w = font.size(ch)[0]
                width += w
                i += 1
        
        return width

    def get_lines(self, text: str, max_width: int, font_size: int) -> list:
        """Divide el texto en líneas que se ajustan al ancho máximo."""
        font = self.get_font(font_size)
        parrafos = text.split('\n')
        all_lines = []
        
        for parrafo in parrafos:
            words = parrafo.split()
            if not words:  # Párrafo vacío (solo un salto de línea)
                all_lines.append("")
                continue
                
            line = ""
            for word in words:
                test_line = f"{line} {word}".strip() if line else word
                if self.measure_text_width(test_line, font_size) <= max_width:
                    line = test_line
                else:
                    if line:
                        all_lines.append(line)
                    line = word
            
            if line:
                all_lines.append(line)
        
        return all_lines

    def render_line(self, surface, text: str, x: int, y: int, font_size: int, color=(0,0,0), centered=False, max_width=None):
        """Renderiza una línea de texto con emojis."""
        font = self.get_font(font_size)
        emoji_size = int(font_size * self.emoji_scale_factor)
        
        # Si está centrado, calcula la posición x
        if centered and max_width:
            text_width = self.measure_text_width(text, font_size)
            x = x + (max_width - text_width) // 2
        
        pos_x = x
        i = 0
        length = len(text)
        
        while i < length:
            emoji_seq = None
            for size in range(4, 0, -1):
                if i+size <= length and self.is_emoji(text[i:i+size]):
                    emoji_seq = text[i:i+size]
                    break
            
            if emoji_seq:
                em_surf = self.get_emoji_surf(emoji_seq, emoji_size)
                if em_surf:
                    y_offset = (font.get_height() - emoji_size) // 2
                    surface.blit(em_surf, (pos_x, y + y_offset))
                    pos_x += emoji_size
                else:
                    # Emoji no encontrado, dibuja un carácter de reemplazo
                    txt = font.render("□", True, color)
                    surface.blit(txt, (pos_x, y))
                    pos_x += txt.get_width()
                
                i += len(emoji_seq)
            else:
                ch = text[i]
                try:
                    txt = font.render(ch, True, color)
                    surface.blit(txt, (pos_x, y))
                    pos_x += txt.get_width()
                except:
                    # Carácter no soportado
                    txt = font.render("?", True, color)
                    surface.blit(txt, (pos_x, y))
                    pos_x += txt.get_width()
                
                i += 1
        
        return pos_x - x  # Retorna el ancho total renderizado

# Inicializa el renderer global
_emoji_renderer = None

def get_emoji_renderer():
    """Obtiene el renderer de emojis global."""
    global _emoji_renderer
    if _emoji_renderer is None:
        _emoji_renderer = EmojiTextRenderer()
    return _emoji_renderer

def mostrar_alternativo_adaptativo(
    pantalla: pygame.Surface,
    texto: str,
    x: int,
    y: int,
    w: int,
    h: int,
    fuente_base: pygame.font.Font = None,
    color: tuple = (30, 30, 30),
    centrado: bool = False
):
    """
    Dibuja texto con soporte para emojis y símbolos, adaptando el tamaño de fuente 
    para que quepa en el área dada. Detecta automáticamente saltos de línea (\n).
    Usa búsqueda binaria para optimizar el ajuste.
    
    Args:
        pantalla: Superficie de pygame donde dibujar
        texto: Texto a mostrar (puede incluir emojis y símbolos)
        x, y: Coordenadas de la esquina superior izquierda
        w, h: Ancho y alto del área disponible
        fuente_base: Fuente base (opcional)
        color: Color del texto (RGB)
        centrado: Si el texto debe estar centrado horizontalmente
    """
    renderer = get_emoji_renderer()
    
    # Tamaños de fuente mínimo y máximo
    min_font_size = 12
    max_font_size = 48 if fuente_base is None else fuente_base.get_height()
    
    # Búsqueda binaria para el tamaño de fuente óptimo
    left, right = min_font_size, max_font_size
    best_size = min_font_size
    best_lines = []
    
    while left <= right:
        mid = (left + right) // 2
        lines = renderer.get_lines(texto, w, mid)
        
        # Calcula la altura total necesaria
        font = renderer.get_font(mid)
        line_height = font.get_height()
        total_height = len(lines) * line_height
        
        if total_height <= h:
            best_size = mid
            best_lines = lines
            left = mid + 1
        else:
            right = mid - 1
    
    # Renderiza con el mejor tamaño encontrado
    font = renderer.get_font(best_size)
    line_height = font.get_height()
    total_height = len(best_lines) * line_height
    
    # Calcula la posición Y inicial (centrado vertical si hay espacio)
    start_y = y + (h - total_height) // 2 if centrado else y
    
    # Renderiza cada línea
    for i, line in enumerate(best_lines):
        line_y = start_y + i * line_height
        renderer.render_line(
            pantalla, 
            line, 
            x, 
            line_y, 
            best_size, 
            color, 
            centrado, 
            w
        )
