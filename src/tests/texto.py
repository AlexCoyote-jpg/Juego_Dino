import pytest
import pygame
from src.ui.utils import mostrar_alternativo_adaptativo, get_fuente_base

@pytest.fixture
def pantalla():
    pygame.init()
    surface = pygame.display.set_mode((800, 600))
    yield surface
    pygame.quit()

def test_mostrar_alternativo_adaptativo_emojis(pantalla):
    # No crash when showing emojis
    mostrar_alternativo_adaptativo(
        pantalla,
        texto="¡Hola! 🌍✨🦖",
        x=10,
        y=10,
        w=300,
        h=100,
        fuente_base=get_fuente_base(),
        color=(255, 255, 255),
        centrado=True
    )

def test_mostrar_alternativo_adaptativo_math_symbols(pantalla):
    # No crash when showing math symbols
    mostrar_alternativo_adaptativo(
        pantalla,
        texto="E = mc² ∑(n=1 to ∞)",
        x=10,
        y=120,
        w=300,
        h=100,
        fuente_base=get_fuente_base(),
        color=(255, 255, 255),
        centrado=False
    )