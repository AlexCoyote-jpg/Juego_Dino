import pygame
import os
from collections import OrderedDict

# LRU Cache optimizada con límite de tamaño estricto
class LRUCache:
    def __init__(self, capacity=64):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key):
        if key not in self.cache:
            return None
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

# Caché global para fuentes y emojis
_CACHE_FUENTES = {}
_CACHE_EMOJIS = LRUCache(64)
_CACHE_MEDIDAS = LRUCache(128)
_CACHE_LINEAS = LRUCache(32)

def obtener_fuente(tamano, negrita=False):
    """Obtiene una fuente del tamaño especificado, usando caché."""
    key = (tamano, negrita)
    if key not in _CACHE_FUENTES:
        _CACHE_FUENTES[key] = pygame.font.SysFont("Arial", tamano, bold=negrita)
    return _CACHE_FUENTES[key]

# Conjunto de emojis comunes para detección rápida (evita importar la biblioteca emoji)
_EMOJI_RANGES = [
    (0x1F600, 0x1F64F),  # Emoticones
    (0x1F300, 0x1F5FF),  # Símbolos y pictogramas
    (0x1F680, 0x1F6FF),  # Transporte y símbolos de mapa
    (0x2600, 0x26FF),    # Símbolos misceláneos
    (0x2700, 0x27BF),    # Símbolos Dingbat
    (0x1F900, 0x1F9FF),  # Símbolos suplementarios
    (0x1F1E6, 0x1F1FF)   # Banderas regionales
]

def es_emoji(char):
    """Comprueba si un carácter es un emoji usando rangos predefinidos."""
    code = ord(char)
    return any(start <= code <= end for start, end in _EMOJI_RANGES)

def cargar_emoji(emoji_seq, size, emoji_path="assets/fuentes/twemoji_png"):
    """Carga un emoji desde el sistema de archivos."""
    key = f"{'-'.join(f'{ord(c):x}' for c in emoji_seq)}_{size}"
    surf = _CACHE_EMOJIS.get(key)
    if surf is not None:
        return surf
    
    # Intenta con codepoints completos
    full = "-".join(f"{ord(c):x}" for c in emoji_seq)
    path_full = os.path.join(emoji_path, f"{full}.png")
    
    try:
        if os.path.isfile(path_full):
            surf = pygame.image.load(path_full).convert_alpha()
            surf = pygame.transform.smoothscale(surf, (size, size))
            _CACHE_EMOJIS.put(key, surf)
            return surf
        
        # Fallback: elimina FE0F (variante de presentación)
        stripped = "".join(c for c in emoji_seq if ord(c) != 0xfe0f)
        if stripped != emoji_seq:
            short = "-".join(f"{ord(c):x}" for c in stripped)
            path_short = os.path.join(emoji_path, f"{short}.png")
            if os.path.isfile(path_short):
                surf = pygame.image.load(path_short).convert_alpha()
                surf = pygame.transform.smoothscale(surf, (size, size))
                _CACHE_EMOJIS.put(key, surf)
                return surf
    except:
        pass
    
    return None

def medir_texto(texto, tamano_fuente, emoji_size):
    """Mide el ancho de un texto con emojis de manera optimizada."""
    key = f"{texto}_{tamano_fuente}"
    cached = _CACHE_MEDIDAS.get(key)
    if cached is not None:
        return cached
    
    fuente = obtener_fuente(tamano_fuente)
    ancho = 0
    i = 0
    longitud = len(texto)
    
    while i < longitud:
        char = texto[i]
        
        # Comprueba si es un emoji
        if es_emoji(char):
            # Busca secuencia de emojis
            j = i + 1
            while j < longitud and es_emoji(texto[j]):
                j += 1
            
            # Añade el ancho del emoji
            ancho += emoji_size
            i = j
        else:
            # Carácter normal
            try:
                ancho += fuente.size(char)[0]
            except:
                ancho += tamano_fuente // 2  # Estimación para caracteres no soportados
            i += 1
    
    _CACHE_MEDIDAS.put(key, ancho)
    return ancho

def dividir_en_lineas(texto, ancho_max, tamano_fuente, emoji_size):
    """Divide el texto en líneas que se ajustan al ancho máximo."""
    key = f"{texto}_{ancho_max}_{tamano_fuente}"
    cached = _CACHE_LINEAS.get(key)
    if cached is not None:
        return cached
    
    lineas = []
    parrafos = texto.split('\n')
    
    for parrafo in parrafos:
        if not parrafo:
            lineas.append("")
            continue
            
        palabras = parrafo.split(' ')
        linea_actual = ""
        
        for palabra in palabras:
            linea_prueba = f"{linea_actual} {palabra}".strip() if linea_actual else palabra
            if medir_texto(linea_prueba, tamano_fuente, emoji_size) <= ancho_max:
                linea_actual = linea_prueba
            else:
                if linea_actual:
                    lineas.append(linea_actual)
                linea_actual = palabra
        
        if linea_actual:
            lineas.append(linea_actual)
    
    _CACHE_LINEAS.put(key, lineas)
    return lineas

def renderizar_linea(superficie, texto, x, y, tamano_fuente, color, emoji_path, centrado=False, ancho_max=None):
    """Renderiza una línea de texto con emojis de manera optimizada."""
    fuente = obtener_fuente(tamano_fuente)
    emoji_size = tamano_fuente  # Simplificado: mismo tamaño que la fuente
    
    # Si está centrado, calcula la posición x
    if centrado and ancho_max:
        ancho_texto = medir_texto(texto, tamano_fuente, emoji_size)
        x = x + (ancho_max - ancho_texto) // 2
    
    pos_x = x
    i = 0
    longitud = len(texto)
    
    while i < longitud:
        char = texto[i]
        
        # Comprueba si es un emoji
        if es_emoji(char):
            # Busca secuencia de emojis
            j = i + 1
            while j < longitud and es_emoji(texto[j]):
                j += 1
            
            emoji_seq = texto[i:j]
            em_surf = cargar_emoji(emoji_seq, emoji_size, emoji_path)
            
            if em_surf:
                superficie.blit(em_surf, (pos_x, y))
                pos_x += emoji_size
            else:
                # Emoji no encontrado, usa un carácter de reemplazo
                txt = fuente.render("□", True, color)
                superficie.blit(txt, (pos_x, y))
                pos_x += txt.get_width()
            
            i = j
        else:
            # Carácter normal
            try:
                txt = fuente.render(char, True, color)
                superficie.blit(txt, (pos_x, y))
                pos_x += txt.get_width()
            except:
                # Carácter no soportado
                txt = fuente.render("?", True, color)
                superficie.blit(txt, (pos_x, y))
                pos_x += txt.get_width()
            
            i += 1

def mostrar_alternativo_adaptativo(
    pantalla: pygame.Surface,
    texto: str,
    x: int,
    y: int,
    w: int,
    h: int,
    fuente_base=None,
    color=(30, 30, 30),
    centrado=False,
    emoji_path="assets/fuentes/twemoji_png"
):
    """
    Versión optimizada que dibuja texto con soporte para emojis y símbolos,
    adaptando el tamaño de fuente para que quepa en el área dada.
    Detecta automáticamente saltos de línea (\n).
    
    Args:
        pantalla: Superficie de pygame donde dibujar
        texto: Texto a mostrar (puede incluir emojis y símbolos)
        x, y: Coordenadas de la esquina superior izquierda
        w, h: Ancho y alto del área disponible
        fuente_base: Fuente base (opcional)
        color: Color del texto (RGB)
        centrado: Si el texto debe estar centrado horizontalmente
        emoji_path: Ruta a la carpeta de emojis
    """
    # Tamaños de fuente mínimo y máximo
    min_font_size = 12
    max_font_size = 48 if fuente_base is None else fuente_base.get_height()
    
    # Búsqueda binaria para el tamaño de fuente óptimo
    left, right = min_font_size, max_font_size
    best_size = min_font_size
    best_lines = []
    
    while left <= right:
        mid = (left + right) // 2
        emoji_size = mid  # Simplificado: mismo tamaño que la fuente
        
        lines = dividir_en_lineas(texto, w, mid, emoji_size)
        
        # Calcula la altura total necesaria
        font = obtener_fuente(mid)
        line_height = font.get_height()
        total_height = len(lines) * line_height
        
        if total_height <= h:
            best_size = mid
            best_lines = lines
            left = mid + 1
        else:
            right = mid - 1
    
    # Renderiza con el mejor tamaño encontrado
    font = obtener_fuente(best_size)
    line_height = font.get_height()
    total_height = len(best_lines) * line_height
    
    # Calcula la posición Y inicial (centrado vertical si hay espacio)
    start_y = y + (h - total_height) // 2 if centrado else y
    
    # Renderiza cada línea
    for i, line in enumerate(best_lines):
        line_y = start_y + i * line_height
        renderizar_linea(
            pantalla, 
            line, 
            x, 
            line_y, 
            best_size, 
            color,
            emoji_path,
            centrado, 
            w
        )


#Prueba de la función
# ...existing code...

if __name__ == "__main__":
    import pygame

    pygame.init()
    pantalla = pygame.display.set_mode((800, 600))
    pantalla.fill((255, 255, 255))

    mostrar_alternativo_adaptativo(
        pantalla,
        "Hola mundo! 😊\nEsto es un texto con emojis y símbolos: ∑ ∞ π ❤️",
        100, 100,  # x, y
        600, 200,  # ancho, alto
        color=(0, 0, 0),
        centrado=True
    )

    pygame.display.flip()
    # Espera hasta que se cierre la ventana
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    pygame.quit()