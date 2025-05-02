import pygame
from setup.Carga_Configs import configuracion

BLANCO = (255, 255, 255)
_imagenes_originales = {}
def cargar_imagen(ruta, tamaño, color_sustituto, texto_sustituto=""):
    try:
        img = pygame.image.load(ruta)
        return pygame.transform.scale(img, tamaño)
    except pygame.error:
        sustituto = pygame.Surface(tamaño)
        sustituto.fill(color_sustituto)
        if texto_sustituto:
            font = pygame.font.SysFont('Arial', 24)
            text = font.render(texto_sustituto, True, BLANCO)
            text_rect = text.get_rect(center=(tamaño[0]//2, tamaño[1]//2))
            sustituto.blit(text, text_rect)
        return sustituto

def cargar_imagen_original(nombre, ruta):
    try:
        return pygame.image.load(ruta).convert_alpha()
    except pygame.error:
        # Imagen de sustituto si falla la carga
        superficie = pygame.Surface((100, 100))
        superficie.fill((200, 200, 200))
        font = pygame.font.SysFont('Arial', 24)
        text = font.render(nombre, True, BLANCO)
        text_rect = text.get_rect(center=(50, 50))
        superficie.blit(text, text_rect)
        return superficie

def cargar_todas_las_imagenes():
    rutas = configuracion.imagenes
    for nombre, ruta in rutas.items():
        _imagenes_originales[nombre] = cargar_imagen_original(nombre, ruta)

def obtener_imagen(nombre, tamaño=None):
    """
    Devuelve la imagen original o escalada al tamaño solicitado.
    """
    img = _imagenes_originales.get(nombre)
    if img and tamaño:
        return pygame.transform.scale(img, tamaño)
    return img

def cargar_todos_los_sonidos():
    sonidos = {}
    rutas = configuracion.sonidos
    for nombre, ruta in rutas.items():
        try:
            sonidos[nombre] = pygame.mixer.Sound(ruta)
        except pygame.error:
            print(f"No se pudo cargar el sonido '{nombre}' ({ruta})")
            sonidos[nombre] = None
    return sonidos

# Carga global de imágenes y sonidos al importar el módulo
cargar_todas_las_imagenes()
sonidos_cargados = cargar_todos_los_sonidos()

if __name__ == "__main__":
    pygame.init()
    pantalla = pygame.display.set_mode((300, 300))
    pygame.display.set_caption("Prueba de carga de imágenes y sonidos")
    dino1 = obtener_imagen("dino1", (150, 150))
    if dino1 is None:
        print("No se pudo cargar la imagen 'dino1'")
    else:
        pantalla.blit(dino1, (75, 75))
        pygame.display.flip()
        print("Imagen 'dino1' cargada y mostrada correctamente.")
        sonido_fondo = sonidos_cargados.get("acierto")
        if sonido_fondo:
            sonido_fondo.play()
        esperando = True
        while esperando:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    esperando = False
    pygame.quit()