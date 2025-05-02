import os
import pygame

pygame.init()

IMAGES = {}
SOUNDS = {}

class Recursos:
    @staticmethod
    def cargar_imagenes():
        """
        Carga todas las imágenes desde assets/imagenes y subcarpetas.
        Debe llamarse después de pygame.display.set_mode().
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        images_dir = os.path.join(base_dir, "assets", "imagenes")
        if not os.path.exists(images_dir):
            print(f"Warning: Image directory {images_dir} not found!")
            return
        for root, _, files in os.walk(images_dir):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    file_path = os.path.join(root, file)
                    name = os.path.splitext(file)[0]
                    relative_dir = os.path.relpath(root, images_dir)
                    if relative_dir != '.':
                        prefix = relative_dir.replace(os.path.sep, '_')
                        name = f"{prefix}_{name}"
                    try:
                        # Solo usa convert_alpha() después de display.set_mode()
                        img = pygame.image.load(file_path).convert_alpha()
                        IMAGES[name] = img
                        globals()[name.upper()] = img
                    except Exception as e:
                        print(f"Error loading image {file}: {e}")

    @staticmethod
    def cargar_sonidos():
        """
        Carga todos los sonidos desde assets/sonidos y subcarpetas.
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        sounds_dir = os.path.join(base_dir, "assets", "sonidos")
        if not os.path.exists(sounds_dir):
            print(f"Warning: Sound directory {sounds_dir} not found!")
            return
        for root, _, files in os.walk(sounds_dir):
            for file in files:
                if file.lower().endswith(('.wav', '.ogg', '.mp3')):
                    file_path = os.path.join(root, file)
                    name = os.path.splitext(file)[0]
                    relative_dir = os.path.relpath(root, sounds_dir)
                    if relative_dir != '.':
                        prefix = relative_dir.replace(os.path.sep, '_')
                        name = f"{prefix}_{name}"
                    try:
                        snd = pygame.mixer.Sound(file_path)
                        SOUNDS[name] = snd
                        globals()[name.upper()] = snd
                    except Exception as e:
                        print(f"Error loading sound {file}: {e}")

    @staticmethod
    def get_imagen(nombre):
        if nombre in IMAGES:
            return IMAGES[nombre]
        print(f"Warning: Image '{nombre}' not found!")
        return None

    @staticmethod
    def get_sonido(nombre):
        if nombre in SOUNDS:
            return SOUNDS[nombre]
        print(f"Warning: Sound '{nombre}' not found!")
        return None

def get_image(name):
    return Recursos.get_imagen(name)

# --- Ejemplo de uso desde cualquier otro módulo ---
# from setup.Carga_Recursos import Recursos, get_image
# Recursos.cargar_imagenes()  # Debe llamarse después de display.set_mode()
# imagen = Recursos.get_imagen("dino1")  # o get_image("dino1")
# sonido = Recursos.get_sonido("salto")
# Si cargaste imágenes con subcarpetas: Recursos.get_imagen("subcarpeta_nombre")
# También puedes acceder a la variable global: DINO1 (si existe)
# -----------------------------------------------