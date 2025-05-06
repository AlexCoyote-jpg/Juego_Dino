import pygame
import sys
import random
from pygame.locals import *
from funciones_apoyo import *

class JuegoCazadorNumeros(JuegoBase):
    def __init__(self):
        super().__init__('Dino Cazador de Números')
        
        # Variables específicas del juego
        self.problema_actual = None
        self.opciones = []
        self.respuesta_correcta = None
        self.opciones_rects = []
        
        # Generar el primer problema
        self.generar_problema()
        
        # Crear barra de navegación
        self.barra_navegacion = BarraNavegacion(self)
        
        # Inicializar contador de jugadas totales
        self.jugadas_totales = 0
    
    def cargar_imagenes(self):
        super().cargar_imagenes()
        # Cargar imágenes específicas del juego
        self.dino_img = self.cargar_imagen_segura('dino3.png', (150, 150), (150, 100, 200))
        self.fruta_img = self.cargar_imagen_segura('fruta.png', (50, 50), (128, 0, 128))
    
    def generar_problema(self):
        """Genera un nuevo problema de multiplicación según el nivel actual"""
        problema, respuesta = generar_problema_multiplicacion(self.nivel_actual)
        self.problema_actual = problema
        self.respuesta_correcta = respuesta
        self.opciones = generar_opciones(respuesta)
    
    def cambiar_nivel(self):
        """Se llama cuando cambia el nivel"""
        if self.nivel_actual != "Home":
            self.generar_problema()
    
    def dibujar_pantalla_home(self):
        """Dibuja la pantalla de inicio"""
        # Título
        titulo_rect = self.dibujar_caja_texto(self.ANCHO//2 - 320, 110, 640, 60, BOTON_NORMAL)
        self.mostrar_texto("Bienvenido a Dino Cazador de Números", self.ANCHO//2, 140, 
                          self.fuente_titulo, centrado=True)
        
        # Instrucciones
        instr_rect = self.dibujar_caja_texto(self.ANCHO//2 - 300, 180, 600, 300, (255, 255, 255, 200))
        
        instrucciones = [
            "¡Ayuda a Dino a resolver problemas de multiplicación!",
            "",
            "Nivel Básico: Multiplicaciones simples",
            "Nivel Medio: Multiplicaciones con números más grandes",
            "Nivel Avanzado: Problemas con múltiples operaciones",
            "",
            "Haz clic en los botones de arriba para comenzar."
        ]
        
        for i, linea in enumerate(instrucciones):
            self.mostrar_texto(linea, self.ANCHO//2, 200 + i*40, centrado=True)
    
    def dibujar_pantalla_juego(self):
        """Dibuja la pantalla del juego"""
        # Dibujar imágenes
        self.pantalla.blit(self.dino_img, (100, 240))
        
        # Dibujar frutas en el camino
        for i in range(5):
            self.pantalla.blit(self.fruta_img, (250 + i*70, 280))
        
        # Dibujar título
        self.mostrar_texto(f"Dino Cazador de Números - Nivel {self.nivel_actual}", 
                          self.ANCHO//2, 100, self.fuente_titulo, centrado=True)
        
        # Dibujar problema
        self.mostrar_texto_multilinea(self.problema_actual, self.ANCHO//2, 170, 
                                     centrado=True)
        
        # Dibujar opciones de respuesta
        self.opciones_rects = []
        for i, opcion in enumerate(self.opciones):
            # Posición centrada con más espacio entre opciones
            x = self.ANCHO//2 - 170 + i*170
            rect = self.dibujar_boton(str(opcion), x, 390, 70, 70, 
                                     VERDE_OPCIONES, VERDE_OPCIONES_HOVER)
            self.opciones_rects.append(rect)
        
        # Mostrar mensaje de retroalimentación
        if self.tiempo_mensaje > 0:
            # Crear caja decorativa para el mensaje
            if "Correcto" in self.mensaje:
                color_msg = (152, 251, 152)  # Verde claro
            else:
                color_msg = (255, 182, 193)  # Rosa claro
                
            msg_rect = self.dibujar_caja_texto(self.ANCHO//2 - 250, 480, 500, 50, color_msg)
            self.mostrar_texto(self.mensaje, self.ANCHO//2, 505, centrado=True)
            self.tiempo_mensaje -= 1
        
        # Mostrar puntuación con estilo actualizado (ganadas/total)
        score_rect = self.dibujar_caja_texto(20, self.ALTO - 50, 180, 40, BOTON_NORMAL)
        self.mostrar_texto(f"Puntuación: {self.puntuacion}/{self.jugadas_totales}", 30, self.ALTO - 35)
    
    def manejar_eventos_juego(self, evento):
        """Maneja los eventos específicos del juego"""
        if evento.type == MOUSEBUTTONDOWN:
            # Verificar clics en las opciones de respuesta
            for i, rect in enumerate(self.opciones_rects):
                if rect.collidepoint(evento.pos):
                    self.jugadas_totales += 1  # Incrementar contador de jugadas totales
                    if self.opciones[i] == self.respuesta_correcta:
                        self.mostrar_mensaje_temporal("¡Correcto! ¡Muy bien!")
                        self.puntuacion += 1
                    else:
                        self.mostrar_mensaje_temporal(f"Incorrecto. La respuesta correcta era {self.respuesta_correcta}.")
                    
                    self.generar_problema()
                    return True
        return False
    
    def ejecutar(self):
        """Método principal para ejecutar el juego"""
        ejecutando = True
        
        while ejecutando:
            for evento in pygame.event.get():
                if evento.type == QUIT:
                    ejecutando = False
                
                # Manejar eventos de navegación
                if self.barra_navegacion.manejar_eventos(evento):
                    continue
                
                # Manejar eventos específicos del juego
                if self.nivel_actual != "Home":
                    self.manejar_eventos_juego(evento)
            
            # Dibujar fondo
            self.dibujar_fondo()
            
            # Dibujar logo
            self.pantalla.blit(self.logo_img, (20, 20))
            
            # Dibujar barra de navegación
            self.barra_navegacion.dibujar()
            
            # Mostrar contenido según la página actual
            if self.nivel_actual == "Home":
                self.dibujar_pantalla_home()
            else:
                self.dibujar_pantalla_juego()
            
            # Actualizar botones presionados
            self.actualizar_botones_presionados()
            
            # Manejar transición entre niveles
            self.manejar_transicion()
            
            # Actualizar pantalla
            pygame.display.flip()
            self.reloj.tick(30)
        
        # Salir del juego
        pygame.quit()
        sys.exit()

# Ejecutar el juego si este archivo es el principal
if __name__ == "__main__":
    juego = JuegoCazadorNumeros()
    juego.ejecutar()
