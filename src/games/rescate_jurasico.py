import pygame
import sys
import random
from pygame.locals import *
from funciones_apoyo import *

def generar_problema_division(nivel):
    """Genera un problema de división según el nivel"""
    if nivel == "Básico":
        b = random.randint(1, 5)
        a = b * random.randint(1, 5)
        problema = f"Dino tiene {a} bayas. Si las reparte en {b} grupos iguales, ¿cuántas bayas habrá en cada grupo?"
        respuesta = a // b
    elif nivel == "Medio":
        b = random.randint(2, 5)
        a = b * random.randint(3, 8)
        problema = f"Dino tiene {a} bayas y quiere repartirlas entre {b} amigos. ¿Cuántas bayas recibirá cada amigo?"
        respuesta = a // b
    else:  # Avanzado
        b = random.randint(3, 6)
        a = b * random.randint(5, 10)
        c = random.randint(1, 3)
        problema = f"Dino tiene {a} bayas. Si las reparte en {b} grupos iguales y luego come {c} de un grupo, ¿cuántas bayas le quedan en ese grupo?"
        respuesta = (a // b) - c
    
    return problema, respuesta

class JuegoRescate(JuegoBase):
    def __init__(self):
        super().__init__('Rescate Jurásico')
        
        # Variables específicas del juego
        self.problema_actual = None
        self.opciones = []
        self.respuesta_correcta = None
        self.opciones_rects = []
        self.nivel_completado = False
        self.posicion_dino = 0  # Posición del dinosaurio en el camino
        self.total_pasos = 3  # Número total de pasos para llegar al bebé
        
        # Generar el primer problema
        self.generar_problema()
        
        # Crear barra de navegación
        self.barra_navegacion = BarraNavegacion(self)
    
    def cargar_imagenes(self):
        super().cargar_imagenes()
        # Cargar imágenes específicas del juego
        self.dino_mama_img = self.cargar_imagen_segura('dino_mama.png', (100, 100), (0, 150, 100))
        self.dino_bebe_img = self.cargar_imagen_segura('dino_bebe.png', (80, 80), (0, 200, 150))
        self.roca_img = self.cargar_imagen_segura('roca.png', (80, 100), (150, 150, 150))
    
    def generar_problema(self):
        """Genera un nuevo problema de división según el nivel actual"""
        if self.nivel_actual == "Básico":
            # Problemas de división simple
            divisor = random.randint(2, 5)
            total = divisor * random.randint(2, 8)
            problema = f"Dino tiene {total} bayas. Si las reparte en {divisor} grupos iguales y luego come 1 de un grupo, ¿cuántas bayas le quedan en ese grupo?"
            respuesta = (total // divisor) - 1
        
        elif self.nivel_actual == "Medio":
            # Problemas de división con restos
            divisor = random.randint(3, 6)
            total = divisor * random.randint(4, 10) + random.randint(1, divisor-1)
            problema = f"Dino tiene {total} bayas. Si las reparte en {divisor} grupos iguales, ¿cuántas bayas habrá en cada grupo?"
            respuesta = total // divisor
        
        else:  # Avanzado
            # Problemas más complejos
            divisor = random.randint(3, 7)
            cantidad_por_grupo = random.randint(3, 8)
            total = divisor * cantidad_por_grupo
            consumo = random.randint(1, cantidad_por_grupo - 1)
            problema = f"Dino tiene {total} bayas. Si las reparte en {divisor} grupos iguales y luego come {consumo} de un grupo, ¿cuántas bayas le quedan en ese grupo?"
            respuesta = cantidad_por_grupo - consumo
        
        self.problema_actual = problema
        self.respuesta_correcta = respuesta
        self.opciones = generar_opciones(respuesta, min_diff=1, max_diff=3)
    
    def cambiar_nivel(self):
        """Se llama cuando cambia el nivel"""
        if self.nivel_actual != "Home":
            self.generar_problema()
            self.posicion_dino = 0
            self.nivel_completado = False
    
    def dibujar_pantalla_home(self):
        """Dibuja la pantalla de inicio"""
        # Título
        titulo_rect = self.dibujar_caja_texto(self.ANCHO//2 - 320, 110, 640, 60, BOTON_NORMAL)
        self.mostrar_texto("Bienvenido a Rescate Jurásico", self.ANCHO//2, 140, 
                          self.fuente_titulo, centrado=True)
        
        # Instrucciones
        instr_rect = self.dibujar_caja_texto(self.ANCHO//2 - 300, 180, 600, 300, (255, 255, 255, 200))
        
        instrucciones = [
            "¡Ayuda a mamá dinosaurio a rescatar a su bebé perdido!",
            "",
            "Nivel Básico: Divisiones simples",
            "Nivel Medio: Divisiones con restos",
            "Nivel Avanzado: Problemas más complejos",
            "",
            "Resuelve problemas matemáticos para avanzar en el camino.",
            "Haz clic en los botones de arriba para comenzar."
        ]
        
        for i, linea in enumerate(instrucciones):
            self.mostrar_texto(linea, self.ANCHO//2, 200 + i*40, centrado=True)
    
    def dibujar_pantalla_juego(self):
        """Dibuja la pantalla del juego"""
        # Dibujar título
        self.mostrar_texto(f"Rescate Jurásico - Nivel {self.nivel_actual}", 
                          self.ANCHO//2, 100, self.fuente_titulo, centrado=True)
        
        # Dibujar subtítulo
        self.mostrar_texto("Ayuda a mamá saurio a ir por su bebé perdido", 
                          self.ANCHO//2, 140, centrado=True)
        
        # Dibujar camino con rocas
        camino_x = 250
        camino_y = 250
        espacio_rocas = 120
        
        # Dibujar mamá dinosaurio
        mama_x = 100
        if self.posicion_dino > 0:
            mama_x = camino_x + (self.posicion_dino - 1) * espacio_rocas
        self.pantalla.blit(self.dino_mama_img, (mama_x, camino_y))
        
        # Dibujar rocas en el camino
        for i in range(self.total_pasos):
            self.pantalla.blit(self.roca_img, (camino_x + i * espacio_rocas, camino_y))
        
        # Dibujar bebé dinosaurio
        bebe_x = camino_x + self.total_pasos * espacio_rocas + 20
        self.pantalla.blit(self.dino_bebe_img, (bebe_x, camino_y + 10))
        
        # Dibujar problema
        problema_rect = self.dibujar_caja_texto(self.ANCHO//2 - 300, 370, 600, 80, (255, 255, 255, 200))
        self.mostrar_texto_multilinea(self.problema_actual, self.ANCHO//2, 380, 
                                     centrado=True)
        
        # Dibujar opciones de respuesta si no se ha completado el nivel
        if not self.nivel_completado:
            self.opciones_rects = []
            for i, opcion in enumerate(self.opciones):
                # Posición centrada con más espacio entre opciones
                x = self.ANCHO//2 - 170 + i*170
                rect = self.dibujar_boton(str(opcion), x, 470, 70, 70, 
                                         VERDE_OPCIONES, VERDE_OPCIONES_HOVER)
                self.opciones_rects.append(rect)
        else:
            # Mostrar mensaje de nivel completado
            self.mostrar_texto("¡Nivel completado! ¡Has rescatado al bebé dinosaurio!", 
                              self.ANCHO//2, 470, centrado=True)
            
            # Botón para siguiente nivel
            siguiente_rect = self.dibujar_boton("Siguiente Nivel", self.ANCHO//2 - 100, 520, 200, 50, 
                                               BOTON_NORMAL, BOTON_HOVER)
            self.opciones_rects = [siguiente_rect]
        
        # Mostrar mensaje de retroalimentación
        if self.tiempo_mensaje > 0:
            # Crear caja decorativa para el mensaje
            if "Correcto" in self.mensaje:
                color_msg = (152, 251, 152)  # Verde claro
            else:
                color_msg = (255, 182, 193)  # Rosa claro
                
            msg_rect = self.dibujar_caja_texto(self.ANCHO//2 - 250, 550, 500, 40, color_msg)
            self.mostrar_texto(self.mensaje, self.ANCHO//2, 570, centrado=True)
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
                    if self.nivel_completado:
                        # Pasar al siguiente nivel
                        niveles = ["Básico", "Medio", "Avanzado"]
                        nivel_actual_index = niveles.index(self.nivel_actual)
                        if nivel_actual_index < len(niveles) - 1:
                            self.nivel_actual = niveles[nivel_actual_index + 1]
                        else:
                            self.nivel_actual = "Básico"
                        
                        self.cambiar_nivel()
                        return True
                
                    self.jugadas_totales += 1  # Incrementar contador de jugadas totales
                    if self.opciones[i] == self.respuesta_correcta:
                        self.mostrar_mensaje_temporal("¡Correcto! ¡Avanzas un paso!")
                        self.puntuacion += 1
                        self.posicion_dino += 1
                        
                        # Verificar si se ha completado el nivel
                        if self.posicion_dino > self.total_pasos:
                            self.nivel_completado = True
                            self.mostrar_mensaje_temporal("¡Felicidades! ¡Has rescatado al bebé dinosaurio!")
                        else:
                            self.generar_problema()
                    else:
                        self.mostrar_mensaje_temporal(f"Incorrecto. La respuesta correcta era {self.respuesta_correcta}.")
                        # No avanzar en caso de error
                
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
    juego = JuegoRescate()
    juego.ejecutar()
