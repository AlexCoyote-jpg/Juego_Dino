import pygame
import sys
import random
import time
from pygame.locals import MOUSEBUTTONDOWN, KEYDOWN, K_r, K_f, QUIT
from setup.core import (
    Recursos,
    mostrar_texto_adaptativo,
    dibujar_caja_texto,
    dibujar_boton,
    dibujar_carta_generica,
    mostrar_victoria,
    avanzar_nivel,
    dibujar_fondo_animado,
    JuegoBase,
    PALETA_COLORES,
)

class MemoriaJurasicaJuego:
    """Juego de memoria matemática con dinosaurios.
    Versión optimizada para niños con efectos visuales y sonoros."""

    # Colores centralizados desde core.py
    COLORES = {
        'fondo': PALETA_COLORES['LAVANDA'],
        'carta': PALETA_COLORES['NEGRO_CARTA'],
        'texto': PALETA_COLORES['BLANCO'],
        'texto_oscuro': PALETA_COLORES['NEGRO'],
        'acierto': PALETA_COLORES['VERDE_ACIERTO'],
        'error': PALETA_COLORES['ROJO_ERROR'],
        'borde': PALETA_COLORES['AZUL_BORDE'],
        'panel': PALETA_COLORES['BEIGE_PANEL'],
        'titulo': PALETA_COLORES['AZUL_OSCURO']
    }

    # Configuración por nivel
    CONFIG_NIVELES = {
        "Básico": {"pares": 6, "tipo": "suma", "tiempo_memoria": 4},
        "Medio": {"pares": 8, "tipo": "multiplicacion", "tiempo_memoria": 5},
        "Avanzado": {"pares": 10, "tipo": "mixto", "tiempo_memoria": 6}
    }
    
    def __init__(self, pantalla, estrellas=None, fondo=None, estrellas_animadas=None, 
                crear_fondo=None, crear_estrellas=None, recursos=None, fondo_thread=None):
        """Inicialización optimizada del juego"""
        # Configuración de pantalla
        self.pantalla = pantalla
        self.ancho, self.alto = pantalla.get_width(), pantalla.get_height()
        
        # Recursos de fondo y animación
        self.estrellas = estrellas
        self.fondo = fondo
        self.estrellas_animadas = estrellas_animadas
        self.crear_fondo = crear_fondo
        self.crear_estrellas = crear_estrellas
        self.fondo_thread = fondo_thread
        
        # Navegación y sistema
        self.Recursos = recursos
        self.salir_al_menu = False
        self.juego_base = JuegoBase(pantalla, self.ancho, self.alto)
        self.nivel_actual = "Básico"
        
        # Dimensiones de referencia
        self.base_width = 900
        self.base_height = 700
        
        # Inicializar componentes
        self._init_fuentes()
        self._cargar_recursos()
        self._reset_estado_juego()
        
        # Botón de silencio
        self.silencio = False
        self.btn_silencio_rect = None
        
        # Iniciar el juego
        self.inicializar_nivel()
    
    def _init_fuentes(self):
        """Inicializa fuentes con tamaños optimizados para lectura infantil"""
        self.fuente_titulo = pygame.font.SysFont("Comic Sans MS", 54, bold=True)
        self.fuente_texto = pygame.font.SysFont("Comic Sans MS", 28)
        self.fuente_cartas = pygame.font.SysFont("Comic Sans MS", 36, bold=True)
        self.fuente_info = pygame.font.SysFont("Comic Sans MS", 24)
        self.reloj = pygame.time.Clock()
    
    def _cargar_recursos(self):
        """Carga recursos optimizados con manejo de errores mejorado"""
        # Valores por defecto
        self.sonido_acierto = self.sonido_error = None
        self.logo_img = pygame.Surface((80, 80))
        self.carta_reverso_img = pygame.Surface((80, 100))
        self.img_sonido_encendido = pygame.Surface((40, 40))
        self.img_sonido_apagado = pygame.Surface((40, 40))
        
        try:
            if self.Recursos:
                # Cargar sonidos
                self.Recursos.cargar_sonidos()
                self.sonido_acierto = self.Recursos.get_sonido('acierto')
                self.sonido_error = self.Recursos.get_sonido('error')
                
                # Ajustar volumen para niños (no tan alto)
                if self.sonido_acierto:
                    self.sonido_acierto.set_volume(0.7)
                if self.sonido_error:
                    self.sonido_error.set_volume(0.5)
                
                # Cargar imágenes
                self.Recursos.cargar_imagenes()
                self.logo_img = self.Recursos.get_imagen("dino_logo") or self.logo_img
                self.carta_reverso_img = self.Recursos.get_imagen('card_back') or self.carta_reverso_img
                self.img_sonido_encendido = self.Recursos.get_imagen("encendido") or self.img_sonido_encendido
                self.img_sonido_apagado = self.Recursos.get_imagen("apagado") or self.img_sonido_apagado
        except Exception as e:
            print(f"Error al cargar recursos: {e}")
    
    def _reset_estado_juego(self):
        """Reinicia variables de estado del juego"""
        self.cartas = []
        self.carta_primera = None
        self.carta_segunda = None
        self.cartas_emparejadas = set()
        self.tiempo_espera = 0
        self.pares_encontrados = 0
        self.total_pares = 0
        self.nivel_completado = False
        self.carta_rects = []
        self.ultimo_tiempo_clic = 0
        self.procesando_par = False
        self.ultimo_frame = 0
        self.inicio_tiempo = pygame.time.get_ticks()
        self.tiempo_mensaje = 0
        self.mostrar_cartas_inicio = False
        self.tiempo_inicio_mostrar = 0
        self.mensaje_feedback = None
        self.tiempo_feedback = 0

    def sx(self, x):
        """Escala coordenada x usando util estática de JuegoBase."""
        return JuegoBase.sx(self.pantalla, x, self.base_width)
    
    def sy(self, y):
        """Escala coordenada y usando util estática de JuegoBase."""
        return JuegoBase.sy(self.pantalla, y, self.base_height)

    def inicializar_nivel(self):
        """Configura nivel con animaciones divertidas de inicio"""
        self._reset_estado_juego()
        
        if self.nivel_actual == "Home":
            self.nivel_actual = "Básico"
        
        # Obtener configuración del nivel
        config = self.CONFIG_NIVELES[self.nivel_actual]
        self.total_pares = config["pares"]
        
        # Crear cartas con operaciones matemáticas
        ops = self._generar_operaciones(self.total_pares)
        
        for i, (operacion, resultado) in enumerate(ops):
            self.cartas.append({
                'id': i, 
                'tipo': 'operacion', 
                'valor': operacion,
                'pareja_id': i + self.total_pares, 
                'volteada': True, 
                'bordes': None,
                'animacion': 0.0
            })
            self.cartas.append({
                'id': i + self.total_pares, 
                'tipo': 'resultado', 
                'valor': str(resultado),
                'pareja_id': i, 
                'volteada': True, 
                'bordes': None,
                'animacion': 0.0
            })
        
        # Barajar y mostrar brevemente
        random.shuffle(self.cartas)
        self.mostrar_cartas_inicio = True
        self.tiempo_inicio_mostrar = self.inicio_tiempo = pygame.time.get_ticks()
        
        # Mostrar mensaje de inicio del nivel
        self.mostrar_mensaje(f"¡Nivel {self.nivel_actual}!", 2.0)

    def _generar_operaciones(self, num_pares):
        """Genera operaciones matemáticas divertidas según nivel"""
        operaciones = []
        resultados = set()
        
        while len(operaciones) < num_pares:
            if self.nivel_actual == "Básico":
                a, b = random.randint(1, 9), random.randint(1, 9)
                operacion = f"{a} + {b}"
                resultado = a + b
            elif self.nivel_actual == "Medio":
                a, b = random.randint(1, 9), random.randint(1, 9)
                operacion = f"{a} × {b}"
                resultado = a * b
            else:  # Avanzado
                tipo = random.choice(['suma', 'resta', 'multiplicacion'])
                if tipo == 'suma':
                    a, b = random.randint(5, 15), random.randint(1, 9)
                    operacion = f"{a} + {b}"
                    resultado = a + b
                elif tipo == 'resta':
                    b = random.randint(1, 8)
                    a = b + random.randint(1, 10)  # Asegura resultado positivo
                    operacion = f"{a} - {b}"
                    resultado = a - b
                else:
                    a, b = random.randint(2, 6), random.randint(2, 6)  # Más fácil para niños
                    operacion = f"{a} × {b}"
                    resultado = a * b
            
            if resultado not in resultados:
                resultados.add(resultado)
                operaciones.append((operacion, resultado))
        
        return operaciones

    def dibujar_carta(self, carta, x, y, ancho, alto):
        """Dibuja carta usando utilidad de core para cartas genericas."""
        return dibujar_carta_generica(
            self.pantalla,
            carta,
            x, y, ancho, alto,
            self.fuente_cartas,
            self.COLORES['texto'],
            self.COLORES['acierto'],
            self.COLORES['error'],
            self.COLORES['borde'],
            self.carta_reverso_img,
            self.COLORES['carta'],
        )

    def actualizar_juego(self):
        """Actualiza estado del juego con animaciones suaves"""
        tiempo_actual = pygame.time.get_ticks()
        delta_tiempo = (tiempo_actual - self.ultimo_frame) / 1000.0
        
        # Limitar FPS para consistencia
        if tiempo_actual - self.ultimo_frame < 16:  # ~60 FPS
            return
            
        self.ultimo_frame = tiempo_actual
        
        # Animar cartas (hover effect)
        mouse_pos = pygame.mouse.get_pos()
        for carta in self.cartas:
            destino = 0.0
            for rect, c in self.carta_rects:
                if c['id'] == carta['id'] and rect.collidepoint(mouse_pos):
                    destino = 1.0
                    break
            
            # Animación suave
            carta['animacion'] = carta['animacion'] * 0.9 + destino * 0.1
        
        # Fase de memorización inicial
        if self.mostrar_cartas_inicio:
            tiempo_memoria = self.CONFIG_NIVELES[self.nivel_actual]["tiempo_memoria"]
            if tiempo_actual - self.tiempo_inicio_mostrar >= tiempo_memoria * 1000:
                for carta in self.cartas:
                    carta['volteada'] = False
                self.mostrar_cartas_inicio = False
                self.mostrar_mensaje("¡Encuentra los pares!", 1.5)
        
        # Procesar par de cartas
        if self.tiempo_espera > 0:
            self.tiempo_espera -= 1
            if self.tiempo_espera == 0:
                self._resolver_par()
        
        # Actualizaciones de mensajes
        if self.tiempo_mensaje > 0:
            self.tiempo_mensaje -= delta_tiempo
            if self.tiempo_mensaje <= 0:
                self.mensaje_feedback = None
        
        # Animar mensaje de feedback
        if self.tiempo_feedback > 0:
            self.tiempo_feedback -= delta_tiempo

    def mostrar_mensaje(self, texto, duracion=1.0):
        """Muestra mensaje temporal con animación usando utilidad de JuegoBase."""
        self.mensaje_feedback = texto
        self.tiempo_mensaje = duracion
        self.tiempo_feedback = duracion

    def dibujar_pantalla_juego(self):
        """Dibuja interfaz de juego colorida y amigable para niños"""
        # Título del juego
        titulo_fondo = pygame.Rect(self.sx(150), self.sy(100), self.sx(600), self.sy(60))
        dibujar_caja_texto(self.pantalla, titulo_fondo.x, titulo_fondo.y, titulo_fondo.width, titulo_fondo.height, self.COLORES['titulo'], radius=15)
        
        mostrar_texto_adaptativo(
            self.pantalla, f"Memoria Jurásica - Nivel {self.nivel_actual}",
            self.sx(150), self.sy(100), self.sx(600), self.sy(60),
            self.fuente_titulo, (255, 255, 255), centrado=True
        )
        
        # Panel de información
        info_y = self.sy(170)
        info_rect = pygame.Rect((self.ancho - self.sx(300)) // 2, info_y, self.sx(300), self.sy(40))
        dibujar_caja_texto(self.pantalla, info_rect.x, info_rect.y, info_rect.width, info_rect.height, self.COLORES['borde'], radius=10)
        
        # Mostrar estadísticas con iconos emoji para niños
        tiempo = (pygame.time.get_ticks() - self.inicio_tiempo) // 1000
        info_text = f"🧩 {self.pares_encontrados}/{self.total_pares}   ⏱️ {tiempo}s"
        
        mostrar_texto_adaptativo(
            self.pantalla, info_text,
            info_rect.x, info_rect.y, info_rect.width, info_rect.height,
            self.fuente_info, (255, 255, 255), centrado=True
        )
        
        # Dibujar mensaje de feedback animado
        if self.mensaje_feedback and self.tiempo_mensaje > 0:
            factor = min(1.0, self.tiempo_feedback * 2) 
            escala = 1.0 + (1.0 - abs(factor - 0.5) * 2) * 0.2
            
            msg_ancho, msg_alto = self.sx(400), self.sy(80)
            msg_x = (self.ancho - msg_ancho) // 2
            msg_y = self.sy(220)
            
            msg_ancho_real = int(msg_ancho * escala)
            msg_alto_real = int(msg_alto * escala)
            msg_x -= (msg_ancho_real - msg_ancho) // 2
            msg_y -= (msg_alto_real - msg_alto) // 2
            
            msg_rect = pygame.Rect(msg_x, msg_y, msg_ancho_real, msg_alto_real)
            pygame.draw.rect(self.pantalla, (255, 255, 200), msg_rect, border_radius=12)
            pygame.draw.rect(self.pantalla, (255, 200, 0), msg_rect, 3, border_radius=12)
            
            mostrar_texto_adaptativo(
                self.pantalla, self.mensaje_feedback,
                msg_x, msg_y, msg_ancho_real, msg_alto_real,
                self.fuente_texto, (30, 30, 30), centrado=True
            )
        
        # Tablero de cartas y nivel completado
        self._dibujar_tablero_cartas()
        if self.nivel_completado:
            self._mostrar_victoria()
        
        # Botón de silencio
        self._dibujar_boton_silencio()

    def _dibujar_boton_silencio(self):
        """Dibuja botón de silencio claro y visible"""
        # Usar icono según estado
        icono = self.img_sonido_encendido if not self.silencio else self.img_sonido_apagado
        
        # Tamaño apropiado para niños (más grande)
        tamaño = self.sx(50)
        icono_scaled = pygame.transform.scale(icono, (tamaño, tamaño))
        
        # Posición visible
        pos_x = self.ancho - tamaño - self.sx(20)
        pos_y = self.alto - tamaño - self.sy(20)
        
        # Fondo circular para destacar el botón
        radio = tamaño // 2 + 5
        centro = (pos_x + tamaño // 2, pos_y + tamaño // 2)
        pygame.draw.circle(self.pantalla, (220, 220, 250), centro, radio)
        pygame.draw.circle(self.pantalla, (70, 130, 180), centro, radio, 3)
        
        # Dibujar icono
        icono_rect = icono_scaled.get_rect(topleft=(pos_x, pos_y))
        self.pantalla.blit(icono_scaled, icono_rect)
        self.btn_silencio_rect = icono_rect

    def _dibujar_tablero_cartas(self):
        """Dibuja tablero con distribución optimizada para niños"""
        num_cartas = len(self.cartas)
        
        # Configuración adaptativa para diferentes niveles
        if num_cartas <= 12:  # Básico: 3x4
            filas, columnas = 3, 4
        elif num_cartas <= 16:  # Medio: 4x4
            filas, columnas = 4, 4
        else:  # Avanzado: 4x5
            filas, columnas = 4, 5
        
        # Espaciado generoso para niños
        espacio_h = self.sx(25)
        espacio_v = self.sy(25)
        
        # Calcular tamaño de cartas basado en espacio disponible
        ancho_disponible = self.ancho - espacio_h * (columnas + 1)
        alto_disponible = self.alto - self.sy(250) - espacio_v * (filas + 1)
        
        carta_ancho = min(self.sx(100), ancho_disponible // columnas)
        carta_alto = min(self.sy(120), alto_disponible // filas)
        
        # Centro del tablero
        inicio_x = (self.ancho - (columnas * carta_ancho + (columnas - 1) * espacio_h)) // 2
        inicio_y = self.sy(230)
        
        # Dibujar cartas con animación
        self.carta_rects = []
        for i, carta in enumerate(self.cartas):
            fila, col = divmod(i, columnas)
            x = inicio_x + col * (carta_ancho + espacio_h)
            y = inicio_y + fila * (carta_alto + espacio_v)
            rect = self.dibujar_carta(carta, x, y, carta_ancho, carta_alto)
            self.carta_rects.append((rect, carta))

    def _mostrar_victoria(self):
        mostrar_victoria(
            self.pantalla,
            self.sx, self.sy,
            self.ancho, self.alto,
            self.fuente_titulo, self.fuente_texto,
            self.juego_base,
            self.carta_rects
        )

    def _resolver_par(self):
        """Resuelve la jugada con efectos de sonido y animaciones"""
        if not self.carta_primera or not self.carta_segunda:
            self.procesando_par = False
            return
        
        # Verificar si forman pareja
        if self.carta_primera['pareja_id'] == self.carta_segunda['id']:
            # Acierto
            self.carta_primera['bordes'] = 'acierto'
            self.carta_segunda['bordes'] = 'acierto'
            self.cartas_emparejadas.add(self.carta_primera['id'])
            self.cartas_emparejadas.add(self.carta_segunda['id'])
            self.pares_encontrados += 1
            
            # Sonido de acierto
            if self.sonido_acierto and not self.silencio:
                self.sonido_acierto.play()
            
            # Mensaje positivo aleatorio
            mensajes = ["¡Muy bien!", "¡Correcto!", "¡Excelente!", "¡Genial!"]
            self.mostrar_mensaje(random.choice(mensajes), 1.0)
            
            # Verificar victoria
            if self.pares_encontrados >= self.total_pares:
                self.nivel_completado = True
        else:
            # Error
            self.carta_primera['bordes'] = 'error'
            self.carta_segunda['bordes'] = 'error'
            
            # Sonido de error
            if self.sonido_error and not self.silencio:
                self.sonido_error.play()
            
            # Mensaje de ánimo
            mensajes = ["¡Sigue intentando!", "¡Casi!", "¡Inténtalo de nuevo!"]
            self.mostrar_mensaje(random.choice(mensajes), 1.0)
            
            # Ocultar cartas después de un momento
            self.carta_primera['volteada'] = False
            self.carta_segunda['volteada'] = False
        
        # Limpiar selección
        self.carta_primera = None
        self.carta_segunda = None
        self.procesando_par = False

    def manejar_eventos_juego(self, evento):
        """Maneja eventos del juego con respuestas inmediatas"""
        # No procesar durante la memorización inicial
        if self.mostrar_cartas_inicio:
            return False
        
        if evento.type == MOUSEBUTTONDOWN:
            # Prevenir clics durante procesamiento
            if self.procesando_par or self.tiempo_espera > 0:
                return False
            
            # Anti-spam de clics
            tiempo_actual = time.time()
            if tiempo_actual - self.ultimo_tiempo_clic < 0.2:
                return False
            self.ultimo_tiempo_clic = tiempo_actual
            
            # Manejar botón de silencio
            if self.btn_silencio_rect and self.btn_silencio_rect.collidepoint(evento.pos):
                self.silencio = not self.silencio
                # Reproducir sonido de configuración
                if self.sonido_acierto and not self.silencio:
                    self.sonido_acierto.play()
                return True
            
            # Manejar clics en tarjetas
            for rect, carta in self.carta_rects:
                if rect.collidepoint(evento.pos):
                    # Botón Siguiente Nivel
                    if isinstance(carta, dict) and carta.get('id') == 'siguiente':
                        self._avanzar_nivel()
                        return True
                    
                    # Ignorar cartas ya emparejadas/volteadas
                    if carta['id'] in self.cartas_emparejadas or carta['volteada']:
                        continue
                    
                    # Voltear carta con efecto de sonido
                    carta['volteada'] = True
                    carta['animacion'] = 1.0  # Activar animación
                    
                    # Asignar como primera o segunda carta
                    if self.carta_primera is None:
                        self.carta_primera = carta
                    else:
                        # No permitir seleccionar la misma carta
                        if self.carta_primera['id'] == carta['id']:
                            continue
                        self.carta_segunda = carta
                        self.procesando_par = True
                        self.tiempo_espera = 35  # Mayor tiempo para niños
                    return True
        
        # Teclas de acceso rápido
        elif evento.type == KEYDOWN:
            if evento.key == K_r:  # Reiniciar nivel
                self.inicializar_nivel()
                return True
        
        return False

    def _avanzar_nivel(self):
        avanzar_nivel(self)

    def dibujar_fondo(self):
        dibujar_fondo_animado(
            self.pantalla,
            self.ancho, self.alto,
            self.fondo_thread,
            self.estrellas_animadas,
            self.fondo,
            self.estrellas
        )

    def ejecutar(self):
        """Bucle principal optimizado para rendimiento"""
        ejecutando = True
        while ejecutando and not self.salir_al_menu:
            for evento in pygame.event.get():
                if evento.type == QUIT:
                    ejecutando = False
                elif evento.type == pygame.VIDEORESIZE:
                    self.ancho, self.alto = evento.w, evento.h
                    self.pantalla = pygame.display.set_mode((self.ancho, self.alto), pygame.RESIZABLE)
                    self.juego_base.pantalla = self.pantalla
                    self.juego_base.ANCHO = self.ancho
                    self.juego_base.ALTO = self.alto
                    if self.fondo_thread and hasattr(self.fondo_thread, "update_size"):
                        self.fondo_thread.update_size(self.ancho, self.alto)
                    elif self.crear_fondo:
                        self.fondo = self.crear_fondo(self.ancho, self.alto)
                    if self.crear_estrellas:
                        self.estrellas = self.crear_estrellas(self.ancho, self.alto)
                elif evento.type == KEYDOWN and evento.key == K_f:
                    self.salir_al_menu = True
                    break
                else:
                    self.manejar_eventos_juego(evento)
            if self.salir_al_menu:
                break
            self.dibujar_fondo()
            self.actualizar_juego()
            self.dibujar_pantalla_juego()
            mostrar_texto_adaptativo(
                self.pantalla,
                "Presiona F para volver al menú",
                self.ancho - self.sx(300), self.sy(20),
                self.sx(280), self.sy(30),
                self.fuente_info, (30, 30, 30),
                centrado=True
            )
            self.juego_base.actualizar_botones_presionados()
            self.juego_base.manejar_transicion()
            pygame.display.flip()
            self.reloj.tick(60)
        if not self.salir_al_menu:
            pygame.quit()
            sys.exit()
        return
