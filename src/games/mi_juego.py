import pygame
from core.juego_base import JuegoBase
from ui.utils import Boton

class MiJuego(JuegoBase):
    def __init__(self, pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu):
        super().__init__("prueba", pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu)
        self.circulo_color = (0, 120, 255)
        self.circulo_radio = 60
        self._salir_clicked = False
        self._init_botones()

    def _init_botones(self):
        self.boton_salir = Boton(
            "Salir 🚪",
            x=30, y=30, ancho=120, alto=48,
            color_normal=(220, 240, 255),
            color_hover=(180, 210, 240),
            fuente=self.fuente,
            tooltip="Volver al menú"
        )

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.boton_salir.collidepoint(event.pos):
                self._salir_clicked = True

    def update(self, dt=None):
        pass

    def draw(self, surface):
        self.pantalla = surface
        self.dibujar_fondo()
        centro = (self.ANCHO // 2, self.ALTO // 2)
        pygame.draw.circle(surface, self.circulo_color, centro, self.circulo_radio)
        self.mostrar_titulo()
        ''' Mostrar texto de ejemplo
        self.mostrar_texto(
            "Redimensiona la ventana",
            x=self.ANCHO // 2 - 200,
            y=self.navbar_height + 30,
            w=400,
            h=48,
            fuente=self.fuente_titulo,
        )
        '''
        
        self.boton_salir.draw(surface)
        self.mostrar_puntaje(3, 15 , "hola")
        if self._salir_clicked:
            self.return_to_menu()

    def on_resize(self, ancho, alto):
        self._init_botones()