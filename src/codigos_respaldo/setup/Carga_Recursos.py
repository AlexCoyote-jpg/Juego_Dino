import os
import pygame
from functools import lru_cache
import logging
pygame.init()

IMAGES = {}
SOUNDS = {}

EXTENSIONES_IMAGEN = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
EXTENSIONES_SONIDO = {'.wav', '.ogg', '.mp3'}

class Recursos:
    @staticmethod
    @lru_cache(maxsize=1)
    def base_dir():
        return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    @staticmethod
    def cargar_imagenes():
        images_dir = os.path.join(Recursos.base_dir(), "assets", "imagenes")
        if not os.path.exists(images_dir):
            logging.warning(f"Image directory {images_dir} not found!")
            return
        for root, _, files in os.walk(images_dir):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in EXTENSIONES_IMAGEN:
                    file_path = os.path.join(root, file)
                    name = os.path.splitext(file)[0]
                    relative = os.path.relpath(root, images_dir)
                    if relative != '.':
                        prefix = relative.replace(os.path.sep, '_')
                        name = f"{prefix}_{name}"
                    try:
                        img = pygame.image.load(file_path).convert_alpha()
                        IMAGES[name] = img
                        globals()[name.upper()] = img
                    except Exception as e:
                        logging.error(f"Error loading image {file}: {e}")

    @staticmethod
    def cargar_sonidos():
        sounds_dir = os.path.join(Recursos.base_dir(), "assets", "sonidos")
        if not os.path.exists(sounds_dir):
            logging.warning(f"Sound directory {sounds_dir} not found!")
            return
        for root, _, files in os.walk(sounds_dir):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in EXTENSIONES_SONIDO:
                    file_path = os.path.join(root, file)
                    name = os.path.splitext(file)[0]
                    relative = os.path.relpath(root, sounds_dir)
                    if relative != '.':
                        prefix = relative.replace(os.path.sep, '_')
                        name = f"{prefix}_{name}"
                    try:
                        snd = pygame.mixer.Sound(file_path)
                        SOUNDS[name] = snd
                        globals()[name.upper()] = snd
                    except Exception as e:
                        logging.error(f"Error loading sound {file}: {e}")

    @staticmethod
    def get_imagen(nombre):
        img = IMAGES.get(nombre)
        if img is None:
            logging.warning(f"Image '{nombre}' not found!")
        return img

    @staticmethod
    def get_sonido(nombre):
        snd = SOUNDS.get(nombre)
        if snd is None:
            logging.warning(f"Sound '{nombre}' not found!")
        return snd

def cargar_recursos_completos():
    logging.info("Cargando imágenes...")
    Recursos.cargar_imagenes()
    logging.info(f"Total imágenes cargadas: {len(IMAGES)}")
    logging.info("Cargando sonidos...")
    Recursos.cargar_sonidos()
    logging.info(f"Total sonidos cargados: {len(SOUNDS)}")

def get_image(name):
    return Recursos.get_imagen(name)

def get_sound(name):
    return Recursos.get_sonido(name)
