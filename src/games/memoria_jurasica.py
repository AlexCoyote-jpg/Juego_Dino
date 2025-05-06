import pygame
import random
import os
from games.cards import dibujar_carta_generica
from games.victory import mostrar_victoria

IMG_PATH = os.path.join("assets", "imagenes")
SND_PATH = os.path.join("assets", "sonidos")

def cargar_imagen(nombre, size=None):
    ruta = os.path.join(IMG_PATH, nombre)
    img = pygame.image.load(ruta).convert_alpha()
    if size:
        img = pygame.transform.smoothscale(img, size)
    return img

def cargar_sonido(nombre):
    ruta = os.path.join(SND_PATH, nombre)
    return pygame.mixer.Sound(ruta)

def generar_operaciones(nivel, num_pares):
    operaciones = []
    resultados_usados = set()
    while len(operaciones) < num_pares:
        if nivel == "Básico":
            a, b = random.randint(1, 9), random.randint(1, 9)
            op = f"{a} + {b}"
            res = a + b
        elif nivel == "Medio":
            a, b = random.randint(2, 9), random.randint(2, 9)
            op = f"{a} × {b}"
            res = a * b
        else:
            tipo = random.choice(['suma', 'resta', 'mult', 'div'])
            if tipo == 'suma':
                a, b = random.randint(10, 30), random.randint(1, 10)
                op = f"{a} + {b}"
                res = a + b
            elif tipo == 'resta':
                a, b = random.randint(10, 30), random.randint(1, 10)
                op = f"{a} - {b}"
                res = a - b
            elif tipo == 'mult':
                a, b = random.randint(2, 12), random.randint(2, 12)
                op = f"{a} × {b}"
                res = a * b
            else:
                b = random.randint(2, 10)
                a = b * random.randint(2, 10)
                op = f"{a} ÷ {b}"
                res = a // b
        if res not in resultados_usados:
            resultados_usados.add(res)
            operaciones.append((op, res))
    return operaciones

def iniciar_juego_memoria(pantalla, config, dificultad, fondo, navbar, images, sounds):
    pygame.font.init()
    reloj = pygame.time.Clock()
    font = pygame.font.SysFont("Segoe UI", 32, bold=True)
    font_small = pygame.font.SysFont("Segoe UI", 24)
    running = True

    # Recursos
    reverso = images.get("card_back") or cargar_imagen("card_back.png", (100, 120))
    sonido_acierto = sounds.get("acierto") if sounds else cargar_sonido("acierto.wav")
    sonido_error = sounds.get("error") if sounds else cargar_sonido("error.wav")
    img_sonido_encendido = images.get("encendido") or cargar_imagen("encendido.png", (40, 40))
    img_sonido_apagado = images.get("apagado") or cargar_imagen("apagado.png", (40, 40))
    silenciado = False
    btn_silencio_rect = None

    # Lógica de nivel
    nivel = "Básico" if dificultad == "Fácil" else "Medio" if dificultad == "Normal" else "Avanzado"
    num_pares = 6 if nivel == "Básico" else 8 if nivel == "Medio" else 10
    operaciones = generar_operaciones(nivel, num_pares)

    cartas = []
    for i, (op, res) in enumerate(operaciones):
        cartas.append({
            'id': i,
            'tipo': 'operacion',
            'valor': op,
            'pareja_id': i + num_pares,
            'volteada': True,
            'bordes': None
        })
        cartas.append({
            'id': i + num_pares,
            'tipo': 'resultado',
            'valor': str(res),
            'pareja_id': i,
            'volteada': True,
            'bordes': None
        })
    random.shuffle(cartas)
    cartas_emparejadas = set()
    carta_primera = None
    carta_segunda = None
    pares_encontrados = 0
    total_pares = num_pares
    nivel_completado = False
    carta_rects = []
    mostrar_cartas_inicio = True
    tiempo_inicio_mostrar = pygame.time.get_ticks()
    tiempo_espera = 0
    procesando_par = False
    mensaje = ""
    tiempo_mensaje = 0

    while running:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return
            elif evento.type == pygame.VIDEORESIZE:
                pantalla = pygame.display.set_mode((evento.w, evento.h), pygame.RESIZABLE)
                # Redibuja el fondo y ajusta elementos si es necesario
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                # Botón de silenciar
                if btn_silencio_rect and btn_silencio_rect.collidepoint(evento.pos):
                    silenciado = not silenciado
                    volumen = 0.0 if silenciado else 1.0
                    if sonido_acierto:
                        sonido_acierto.set_volume(volumen)
                    if sonido_error:
                        sonido_error.set_volume(volumen)
                    continue
                # Lógica de cartas
                if nivel_completado:
                    for rect, carta in carta_rects:
                        if rect.collidepoint(evento.pos) and isinstance(carta, dict) and carta.get('id') == 'siguiente':
                            return  # Sale y vuelve al menú principal
                if mostrar_cartas_inicio or procesando_par or nivel_completado:
                    continue
                for rect, carta in carta_rects:
                    if rect.collidepoint(evento.pos):
                        if carta['id'] in cartas_emparejadas or carta.get('volteada'):
                            continue
                        carta['volteada'] = True
                        if not carta_primera:
                            carta_primera = carta
                        elif not carta_segunda and carta_primera['id'] != carta['id']:
                            carta_segunda = carta
                            procesando_par = True
                            tiempo_espera = pygame.time.get_ticks()
                        break

        # Lógica de mostrar cartas al inicio
        if mostrar_cartas_inicio:
            if pygame.time.get_ticks() - tiempo_inicio_mostrar > 2000:
                for carta in cartas:
                    if carta['id'] not in cartas_emparejadas:
                        carta['volteada'] = False
                mostrar_cartas_inicio = False

        # Lógica de emparejamiento
        if procesando_par and carta_primera and carta_segunda:
            if pygame.time.get_ticks() - tiempo_espera > 700:
                if carta_primera['pareja_id'] == carta_segunda['id']:
                    cartas_emparejadas.add(carta_primera['id'])
                    cartas_emparejadas.add(carta_segunda['id'])
                    pares_encontrados += 1
                    carta_primera['bordes'] = 'acierto'
                    carta_segunda['bordes'] = 'acierto'
                    if sonido_acierto:
                        sonido_acierto.play()
                    mensaje = "¡Correcto!"
                else:
                    carta_primera['bordes'] = 'error'
                    carta_segunda['bordes'] = 'error'
                    if sonido_error:
                        sonido_error.play()
                    mensaje = "Intenta de nuevo"
                    carta_primera['volteada'] = False
                    carta_segunda['volteada'] = False
                carta_primera = None
                carta_segunda = None
                procesando_par = False
                tiempo_mensaje = pygame.time.get_ticks()
                if pares_encontrados >= total_pares:
                    nivel_completado = True

        # Dibujar fondo y navbar
        fondo.update(1)
        fondo.draw(pantalla)
        navbar.draw(pantalla, config.get("logo", None))

        # Título
        txt = font.render(f"Memoria Jurásica - {nivel}", True, (80, 0, 80))
        pantalla.blit(txt, (pantalla.get_width() // 2 - txt.get_width() // 2, 40))

        # Info
        txt_info = font_small.render(f"Pares: {pares_encontrados}/{total_pares}", True, (30, 30, 30))
        pantalla.blit(txt_info, (pantalla.get_width() // 2 - txt_info.get_width() // 2, 90))

        # Calcular cuadrícula
        num = len(cartas)
        if num <= 12:
            filas, columnas = 3, 4
        elif num <= 16:
            filas, columnas = 4, 4
        else:
            filas, columnas = 4, 5
        base_ancho, base_alto = 100, 120
        espacio_h, espacio_v = 24, 24
        total_ancho = columnas * base_ancho + (columnas - 1) * espacio_h
        total_alto = filas * base_alto + (filas - 1) * espacio_v
        inicio_x = (pantalla.get_width() - total_ancho) // 2
        inicio_y = 140

        # Dibujar cartas
        carta_rects = []
        for i, carta in enumerate(cartas):
            fila = i // columnas
            columna = i % columnas
            x = inicio_x + columna * (base_ancho + espacio_h)
            y = inicio_y + fila * (base_alto + espacio_v)
            rect = dibujar_carta_generica(
                pantalla, {**carta, "cartas_emparejadas": cartas_emparejadas},
                x, y, base_ancho, base_alto, font_small,
                (255, 255, 255), (0, 180, 0), (180, 0, 0), (0, 0, 120),
                reverso, (80, 80, 80)
            )
            carta_rects.append((rect, carta))

        # Mensaje temporal
        if mensaje and pygame.time.get_ticks() - tiempo_mensaje < 1200:
            txt_msg = font_small.render(mensaje, True, (0, 120, 0))
            pantalla.blit(txt_msg, (pantalla.get_width() // 2 - txt_msg.get_width() // 2, 120))
        elif mensaje:
            mensaje = ""

        # Victoria
        if nivel_completado:
            mostrar_victoria(
                pantalla,
                lambda v: v, lambda v: v, pantalla.get_width(), pantalla.get_height(),
                font, font_small,
                {"pantalla": pantalla}, carta_rects
            )

        # Dibujar botón de silenciar (esquina inferior derecha, SIEMPRE visible y encima de todo)
        icono = img_sonido_apagado if silenciado else img_sonido_encendido
        x_btn = pantalla.get_width() - 60
        y_btn = pantalla.get_height() - 60
        btn_silencio_rect = pygame.Rect(x_btn, y_btn, 40, 40)
        # Fondo circular para mejor visibilidad
        pygame.draw.circle(pantalla, (240, 240, 240, 220), (x_btn + 20, y_btn + 20), 24)
        pantalla.blit(icono, (x_btn, y_btn))

        pygame.display.flip()
        reloj.tick(60)