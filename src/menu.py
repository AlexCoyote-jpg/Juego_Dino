# Ejemplo para menu.py
import pygame
import time
import random
import math
from pygame.locals import MOUSEBUTTONDOWN
from setup.navegacion import JuegoBase, BarraNavegacion

class MenuPrincipal:
    def __init__(self, pantalla, estrellas, fondo, estrellas_animadas, crear_fondo, crear_estrellas):
        self.juegos = [
            {"nombre": "Dino Suma/Resta", "imagen": "assets/imagenes/dino1.png"},
            {"nombre": "DinoCazador", "imagen": "assets/imagenes/dino2.png"},
            {"nombre": "DinoLógico", "imagen": "assets/imagenes/dino3.png"},
            {"nombre": "Memoria Jurásica", "imagen": "assets/imagenes/dino4.png"},
            {"nombre": "Rescate Jurásico", "imagen": "assets/imagenes/dino5.png"}
        ]
        self.pantalla = pantalla
        self.estrellas = estrellas
        self.fondo = fondo
        self.estrellas_animadas = estrellas_animadas
        self.crear_fondo = crear_fondo
        self.crear_estrellas = crear_estrellas

        self.juego_base = JuegoBase(self.pantalla, self.pantalla.get_width(), self.pantalla.get_height())
        self.barra_nav = BarraNavegacion(self.juego_base, niveles=["Home", "Fácil", "Normal", "Difícil", "ChatBot"])

        self.base_width = 900
        self.base_height = 700
        self.scale = self.pantalla.get_width() / self.base_width
        self.imagenes_dinos = [pygame.image.load(j["imagen"]) for j in self.juegos]
        self.dinos_actuales = [0, 1, 2]
        self.ultimo_cambio_dinos = time.time()
        self.dificultad_seleccionada = "Fácil"
        self.juego_seleccionado = None
        self.botones_juegos = []

        # Pre-carga de fuentes y colores para evitar recalcular
        self.font_titulo = pygame.font.SysFont("Segoe UI", 54, bold=True)
        self.font_instrucciones = pygame.font.SysFont("Segoe UI", 28)
        self.color_azul = (70, 130, 180)
        self.color_blanco_trans = (255, 255, 255, 220)
        self.color_gris = (245,245,245)
        self.color_hover = (100, 149, 237)

    def sx(self, x):
        return int(x * self.pantalla.get_width() / self.base_width)
    def sy(self, y):
        return int(y * self.pantalla.get_height() / self.base_height)

    def mostrar_home(self):
        # Título centrado
        x_t, y_t, w_t, h_t = self.sx(130), self.sy(110), self.sx(640), self.sy(60)
        JuegoBase.dibujar_caja_texto(self, x_t, y_t, w_t, h_t, self.color_azul)
        JuegoBase.mostrar_texto_adaptativo(
            self.pantalla,
            "¡Bienvenido a Jugando con Dino!",
            x_t, y_t, w_t, h_t,
            self.font_titulo,
            (255,255,255),
            centrado=True
        )
        # Caja de instrucciones centrada
        caja_x, caja_y, caja_w, caja_h = self.sx(150), self.sy(180), self.sx(600), self.sy(320)
        JuegoBase.dibujar_caja_texto(self, caja_x, caja_y, caja_w, caja_h, self.color_blanco_trans)
        instrucciones = (
            "¡Aprende matemáticas jugando con Dino y sus amigos!\n\n"
            "Selecciona una opción en la barra superior:\n\n"
            "- Fácil: Juegos para principiantes\n"
            "- Normal: Juegos para quienes ya conocen los conceptos básicos\n"
            "- Difícil: Juegos para expertos en matemáticas\n"
            "- ChatBot: Habla directamente con Dino y pregúntale sobre matemáticas\n\n"
            "¡Diviértete y aprende mientras juegas!"
        )
        JuegoBase.mostrar_texto_adaptativo(
            self.pantalla,
            instrucciones,
            caja_x, caja_y, caja_w, caja_h,
            self.font_instrucciones,
            (30,30,30),
            centrado=True
        )
        # Animación de dinosaurios (solo cambia cada 3s, no recalcula imágenes)
        if time.time() - self.ultimo_cambio_dinos >= 3.0:
            self.dinos_actuales = random.sample(range(len(self.imagenes_dinos)), 3)
            self.ultimo_cambio_dinos = time.time()
        dino_positions = [(self.sx(200), self.sy(520)), (self.sx(400), self.sy(520)), (self.sx(600), self.sy(520))]
        self.juego_base.animar_dinos(
            self.pantalla,
            [self.imagenes_dinos[idx] for idx in self.dinos_actuales],
            dino_positions,
            self.scale,
            pygame.time.get_ticks()
        )

    def dibujar_pantalla_juegos(self):
        sx, sy = self.sx, self.sy
        x_t, y_t, w_t, h_t = sx(130), sy(110), sx(640), sy(60)
        JuegoBase.dibujar_caja_texto(self, x_t, y_t, w_t, h_t, self.color_azul)
        JuegoBase.mostrar_texto_adaptativo(
            self.pantalla,
            f"Juegos de nivel {self.dificultad_seleccionada}",
            x_t, y_t, w_t, h_t,
            self.font_titulo,
            (255,255,255),
            centrado=True
        )
        self.botones_juegos.clear()

        # Responsivo: ajusta juegos_por_fila según ancho de pantalla, mínimo 1, máximo 3
        min_card_width = sx(170)
        margen_lateral = sx(40)
        espacio_h = sx(30)
        ancho_disp = self.pantalla.get_width() - 2 * margen_lateral
        juegos_por_fila = max(1, min(3, ancho_disp // (min_card_width + espacio_h)))
        filas = math.ceil(len(self.juegos) / juegos_por_fila)

        margen_superior = sy(180)
        margen_inferior = sy(40)
        espacio_v = sy(30)

        ancho_disp = max(self.pantalla.get_width() - 2 * margen_lateral - (juegos_por_fila - 1) * espacio_h, 1)
        alto_disp = max(self.pantalla.get_height() - margen_superior - margen_inferior - (filas - 1) * espacio_v, 1)

        ancho_juego = max(min(int(ancho_disp / juegos_por_fila), sx(260)), sx(90))
        alto_juego = max(min(int(alto_disp / filas) - sy(60), sy(260)), sy(90))

        boton_alto = max(sy(36), int(alto_juego * 0.22))
        boton_espacio = sy(8)

        ancho_total = juegos_por_fila * ancho_juego + (juegos_por_fila - 1) * espacio_h
        inicio_x = max((self.pantalla.get_width() - ancho_total) // 2, margen_lateral)

        alto_grid = filas * (alto_juego + boton_alto + boton_espacio) + (filas - 1) * espacio_v
        inicio_y = max(margen_superior, (self.pantalla.get_height() - alto_grid) // 2)

        ocupados = [
            pygame.Rect(x_t, y_t, w_t, h_t),
            pygame.Rect(0, 0, self.pantalla.get_width(), sy(100))
        ]

        mouse_pos = pygame.mouse.get_pos()

        # Mejora: solo chequea colisiones con tarjetas ya dibujadas, no con la propia animada
        tarjetas_rects = []

        for i, (juego, imagen) in enumerate(zip(self.juegos, self.imagenes_dinos)):
            fila = i // juegos_por_fila
            col = i % juegos_por_fila
            x = inicio_x + (ancho_juego + espacio_h) * col
            y = inicio_y + (alto_juego + boton_alto + boton_espacio + espacio_v) * fila
            caja_rect = pygame.Rect(x, y, ancho_juego, alto_juego)

            # Animación sutil al pasar el mouse sobre la tarjeta
            hover = caja_rect.collidepoint(mouse_pos)
            anim_scale = 1.06 if hover else 1.0
            anim_offset = -sy(6) if hover else 0

            card_w = int(ancho_juego * anim_scale)
            card_h = int(alto_juego * anim_scale)
            card_x = x - (card_w - ancho_juego) // 2
            card_y = y + anim_offset - (card_h - alto_juego) // 2
            card_rect_anim = pygame.Rect(card_x, card_y, card_w, card_h)

            img_rect = imagen.get_rect()
            img_w, img_h = img_rect.width, img_rect.height
            max_w, max_h = card_w - 20, card_h - 20
            scale = min(max_w / img_w, max_h / img_h)
            new_w, new_h = int(img_w * scale), int(img_h * scale)
            img_x = card_x + (card_w - new_w) // 2
            img_y = card_y + (card_h - new_h) // 2
            img_rect_final = pygame.Rect(img_x, img_y, new_w, new_h)

            boton_y = card_y + card_h + boton_espacio
            boton_rect = pygame.Rect(card_x, boton_y, card_w, boton_alto)

            # Solo chequea colisiones con tarjetas ya dibujadas (no con la propia animada)
            if any(
                card_rect_anim.colliderect(r) or img_rect_final.colliderect(r) or boton_rect.colliderect(r)
                for r in ocupados + tarjetas_rects
            ):
                continue

            card_color = (220, 240, 255) if hover else self.color_gris
            JuegoBase.dibujar_caja_texto(self, card_x, card_y, card_w, card_h, card_color, radius=22)
            img = pygame.transform.smoothscale(imagen, (new_w, new_h))
            self.pantalla.blit(img, (img_x, img_y))
            tarjetas_rects.append(card_rect_anim)
            ocupados.extend([img_rect_final, boton_rect])

            boton_real_rect = self.juego_base.dibujar_boton(
                juego["nombre"], card_x, boton_y, card_w, boton_alto,
                self.color_azul, self.color_hover
            )
            self.botones_juegos.append((boton_real_rect, juego))

    def cargar_juego(self, juego):
        # Lógica para cargar el juego real desde otro módulo
        nombre = juego["nombre"]
        # Ejemplo: import dinámico según nombre
        try:
            if nombre == "Dino Suma/Resta":
                from juegos.dino_suma import DinoSumaJuego
                DinoSumaJuego(self.pantalla).ejecutar()
            elif nombre == "DinoCazador":
                from juegos.dino_cazador import DinoCazadorJuego
                DinoCazadorJuego(self.pantalla).ejecutar()
            elif nombre == "DinoLógico":
                from juegos.dino_logico import DinoLogicoJuego
                DinoLogicoJuego(self.pantalla).ejecutar()
            elif nombre == "Memoria Jurásica":
                from juegos.memoria_jurasica import MemoriaJurasicaJuego
                MemoriaJurasicaJuego(self.pantalla).ejecutar()
            elif nombre == "Rescate Jurásico":
                from juegos.rescate_jurasico import RescateJurasicoJuego
                RescateJurasicoJuego(self.pantalla).ejecutar()
            else:
                print(f"Juego no implementado: {nombre}")
        except Exception as e:
            print(f"Error al cargar el juego {nombre}: {e}")

    def mostrar_chatbot(self):
        # Lógica para mostrar el chatbot desde otro módulo
        try:
            from chatbot.chatbot_ui import mostrar_chatbot_ui
            mostrar_chatbot_ui(self.pantalla, self.sx, self.sy)
        except Exception as e:
            # Fallback simple si no existe el módulo
            sx, sy = self.sx, self.sy
            ancho, alto = self.pantalla.get_width(), self.pantalla.get_height()
            pygame.draw.rect(self.pantalla, (245, 245, 255), (sx(80), sy(120), ancho - sx(160), alto - sy(180)), border_radius=24)
            JuegoBase.mostrar_texto_adaptativo(
                self.pantalla,
                "ChatBot Dino",
                sx(100), sy(140), ancho - sx(200), sy(60),
                pygame.font.SysFont("Segoe UI", 48, bold=True),
                (70, 130, 180),
                centrado=True
            )
            JuegoBase.mostrar_texto_adaptativo(
                self.pantalla,
                "¡Hola! Soy Dino. Pregúntame cualquier cosa sobre matemáticas.",
                sx(120), sy(220), ancho - sx(240), sy(60),
                pygame.font.SysFont("Segoe UI", 28),
                (30, 30, 30),
                centrado=True
            )
            print(f"Error al mostrar el chatbot: {e}")

    def manejar_eventos_menu(self, evento):
        if evento.type == MOUSEBUTTONDOWN:
            for boton, juego in self.botones_juegos:
                if boton.collidepoint(evento.pos):
                    self.juego_seleccionado = juego
                    self.cargar_juego(juego)
                    return True
        return False

    def ejecutar(self):
        clock = pygame.time.Clock()
        running = True
        pantalla, estrellas, fondo = self.pantalla, self.estrellas, self.fondo
        sx, sy = self.sx, self.sy
        barra_nav = self.barra_nav
        juego_base = self.juego_base
        estrellas_animadas = self.estrellas_animadas
        crear_fondo = self.crear_fondo
        crear_estrellas = self.crear_estrellas

        FPS = 120  # Alto para máxima fluidez

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    ancho, alto = event.w, event.h
                    pantalla = pygame.display.set_mode((ancho, alto), pygame.RESIZABLE)
                    fondo = crear_fondo(ancho, alto)
                    estrellas = crear_estrellas(ancho, alto)
                    juego_base.pantalla = pantalla
                    juego_base.ANCHO = ancho
                    juego_base.ALTO = alto
                    self.pantalla = pantalla
                    self.fondo = fondo
                    self.estrellas = estrellas
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for nivel, rect in barra_nav.botones.items():
                        if rect.collidepoint(event.pos):
                            juego_base.nivel_actual = nivel
                            break
                    if juego_base.nivel_actual in ["Fácil", "Normal", "Difícil"]:
                        self.manejar_eventos_menu(event)
            estrellas_animadas(pantalla, estrellas, fondo, pantalla.get_width(), pantalla.get_height())
            barra_nav.dibujar(x_inicial=sx(80), y=sy(30), ancho=sx(120), alto=sy(50), espacio=sx(30))
            if juego_base.nivel_actual == "Home":
                self.mostrar_home()
            elif juego_base.nivel_actual in ["Fácil", "Normal", "Difícil"]:
                self.dificultad_seleccionada = juego_base.nivel_actual
                self.dibujar_pantalla_juegos()
            elif juego_base.nivel_actual == "ChatBot":
                self.mostrar_chatbot()
            pygame.display.flip()
            clock.tick(FPS)