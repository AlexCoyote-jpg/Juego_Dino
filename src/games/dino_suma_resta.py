import pygame
import random
import sys
from ui.utils import Boton, dibujar_caja_texto, mostrar_texto_adaptativo
from ui.navigation_bar import NavigationBar
from core.juego_base import JuegoBase

# Colores para botones de opciones
VERDE_OPCIONES = (180, 240, 180)

def generar_problema_suma_resta(nivel):
    """Genera un problema de suma o resta con enunciado temático según el nivel"""
    if nivel == "Básico":
        a = random.randint(1, 10)
        b = random.randint(1, min(10, a))
        operacion = random.choice(['+', '-'])
        if operacion == '+':
            problema = f"Dino encontró {a} huevos en su cueva y luego encontró {b} más en el bosque.\n ¿Cuántos huevos tiene en total?"
            respuesta = a + b
        else:
            problema = f"Dino tenía {a} huevos y usó {b} para hacer una tortilla.\n ¿Cuántos huevos le quedan?"
            respuesta = a - b
    elif nivel == "Medio":
        a = random.randint(10, 20)
        b = random.randint(1, min(15, a))
        operacion = random.choice(['+', '-'])
        if operacion == '+':
            problema = f"Dino recolectó {a} frutas y luego encontró {b} más.\n ¿Cuántas frutas tiene ahora?"
            respuesta = a + b
        else:
            problema = f"Dino tenía {a} piedras y perdió {b} en el camino.\n ¿Cuántas piedras le quedan?"
            respuesta = a - b
    else:  # Avanzado
        a = random.randint(10, 30)
        b = random.randint(5, 15)
        c = random.randint(1, 10)
        operacion = random.choice(['++', '+-', '-+'])
        if operacion == '++':
            problema = f"Dino encontró {a} semillas, luego {b} más y después otras {c}.\n ¿Cuántas semillas tiene en total?"
            respuesta = a + b + c
        elif operacion == '+-':
            problema = f"Dino tenía {a} hojas, encontró {b} más pero el viento se llevó {c}.\n ¿Cuántas hojas tiene ahora?"
            respuesta = a + b - c
        else:
            problema = f"Dino tenía {a} nueces, dio {b} a sus amigos y luego encontró {c} más.\n ¿Cuántas nueces tiene ahora?"
            respuesta = a - b + c
    return problema, respuesta

def generar_opciones(respuesta):
    opciones = [respuesta]
    while len(opciones) < 3:
        op = respuesta + random.choice([-3, -2, -1, 1, 2, 3, 4, -4])
        if op not in opciones:
            opciones.append(op)
    random.shuffle(opciones)
    return opciones

class JuegoSumaResta(JuegoBase):
    def __init__(self, pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu=None):
        super().__init__('Dino Suma y Resta', pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu)
        self.nivel_actual = self._nivel_from_dificultad(dificultad)
        print(f"Nivel actual: {self.nivel_actual}")
        self.puntuacion = 0
        self.jugadas_totales = 0
        self.tiempo_mensaje = 0
        self.mensaje = ""
        # Ajusta imágenes y posiciones
        self.piedrita = images.get("piedrita") if images else None
        self.dino_img = images.get("dino1") if images else None
        self.cueva_img = images.get("cueva") if images else None
        self._ajustar_imagenes()
        self.opciones_botones = []
        self.generar_problema()

    def _ajustar_imagenes(self):
        # Ajusta el tamaño de las imágenes según el alto de la pantalla
        alto_img = int(self.ALTO * 0.25)
        if self.dino_img:
            self.dino_img = pygame.transform.smoothscale(self.dino_img, (alto_img, alto_img))
        if self.cueva_img:
            self.cueva_img = pygame.transform.smoothscale(self.cueva_img, (alto_img, alto_img))
        if self.piedrita:
            self.piedrita = pygame.transform.smoothscale(self.piedrita, (60, 60))


    def generar_problema(self):
        self.problema_actual, self.respuesta_correcta = generar_problema_suma_resta(self.nivel_actual)
        self.opciones = generar_opciones(self.respuesta_correcta)
        self._init_opciones_botones()

    def _init_opciones_botones(self):
        # Calcula posiciones responsivas
        total_w = 3 * 120 + 2 * 60
        x_ini = (self.ANCHO - total_w) // 2
        y_btn = int(self.ALTO * 0.65)
        self.opciones_botones = []
        for i, opcion in enumerate(self.opciones):
            x = x_ini + i * (120 + 60)
            boton = Boton(
                str(opcion), x, y_btn, 120, 70,
                color_normal=VERDE_OPCIONES,
                color_hover=self.color_complementario(VERDE_OPCIONES),
                color_texto=(30, 30, 30),
                fuente=self.fuente,
                border_radius=18,
                estilo="apple",
                tooltip=f"Selecciona {opcion}"
            )
            self.opciones_botones.append(boton)

    def dibujar_pantalla_juego(self):
        try:
            # Fondo
            self.dibujar_fondo()
            self.mostrar_titulo()
            '''
            # Título
            self.mostrar_texto(
                f"Dino Suma y Resta - Nivel {self.nivel_actual}",
                x=0,
                y=self.navbar_height + 28,
                w=self.ANCHO,
                h=60,
                fuente=self.fuente_titulo,
                color=(70, 130, 180),
                centrado=True
            )
            '''
            # Problema (usando método más seguro)
            texto_problem_y = self.navbar_height + 95
            altura_caja = 80
            dibujar_caja_texto(
                self.pantalla, 
                self.ANCHO//2 - 350,
                texto_problem_y, 
                700,
                altura_caja,
                (245, 245, 245, 200)
            )
            
            # Usar fuente y tamaño de texto fijo para asegurar compatibilidad
            self.mostrar_texto(
                self.problema_actual,
                x=self.ANCHO//2 - 320,
                y=texto_problem_y + 10,
                w=640,
                h=altura_caja - 20,
                fuente=self.fuente,
                color=(20, 20, 80),
                centrado=True
            )
            
            # Imágenes decorativas ajustadas
            alto_img = int(self.ALTO * 0.22)
            y_fila = texto_problem_y + altura_caja + 20
            
            # Dino a la izquierda
            if self.dino_img:
                self.pantalla.blit(self.dino_img, (60, y_fila))
                
            # Cueva a la derecha
            if self.cueva_img:
                self.pantalla.blit(self.cueva_img, (self.ANCHO - alto_img - 60, y_fila))
                
            # Exactamente 3 piedritas entre dino y cueva (simplificado)
            if self.piedrita:
                espacio_total = self.ANCHO - 120 - alto_img * 2
                for i in range(3):
                    x = 60 + alto_img + espacio_total * (i + 1) // 4
                    self.pantalla.blit(self.piedrita, (x, y_fila + alto_img // 3))
            
            # Opciones (manejo simplificado)
            for boton in self.opciones_botones:
                # Usar método draw simplificado si está disponible
                if hasattr(boton, 'draw_simple'):
                    boton.draw_simple(self.pantalla)
                else:
                    boton.draw(self.pantalla, self.tooltip_manager)
                
            # Mensaje de retroalimentación y puntaje
            if self.tiempo_mensaje > 0:
                color_msg = (152, 251, 152) if "Correcto" in self.mensaje else (255, 182, 193)
                dibujar_caja_texto(self.pantalla, self.ANCHO//2 - 250, self.ALTO - 180, 500, 50, color_msg)
                self.mostrar_texto(
                    self.mensaje,
                    x=self.ANCHO//2 - 250,
                    y=self.ALTO - 180,
                    w=500,
                    h=50,
                    fuente=self.fuente,
                    color=(30, 30, 30),
                    centrado=True
                )
                self.tiempo_mensaje -= 1
            self.mostrar_puntaje(self.puntuacion, self.jugadas_totales, frase="Puntuación")
        except Exception as e:
            # Registrar el error pero permitir que el juego continúe
            print(f"Error en dibujar_pantalla_juego: {e}")
            import traceback
            traceback.print_exc()

    def handle_event(self, evento):
        super().handle_event(evento)
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for i, boton in enumerate(self.opciones_botones):
                if boton.collidepoint(evento.pos):
                    self.jugadas_totales += 1
                    if self.opciones[i] == self.respuesta_correcta:
                        self.puntuacion += 1
                        self.mostrar_feedback(True)
                    else:
                        self.mostrar_feedback(False, self.respuesta_correcta)
                    self.generar_problema()
                    return True
        return False

    def mostrar_mensaje_temporal(self, mensaje, tiempo=60):
        self.mensaje = mensaje
        self.tiempo_mensaje = tiempo

    def update(self, dt=0):
        pass

    def draw(self, surface=None):
        pantalla = surface if surface else self.pantalla
        self.pantalla = pantalla
        self.dibujar_pantalla_juego()

    def on_resize(self, ancho, alto):
        self.ANCHO = ancho
        self.ALTO = alto
        self._ajustar_imagenes()
        self._init_opciones_botones()

    