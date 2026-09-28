# -*- coding: utf-8 -*-
"""
Genera las dos piezas del envio de la IV Jornada de Arte y Ciencia:

  1. tarjeta-whatsapp.jpg   1080 x 1350 (4:5)  la que se manda por WhatsApp
  2. og-jornada-iv.jpg      1200 x 630         la vista previa del enlace

Las dos salen de los materiales que ya estan en docs/obras/jornada-iv/, con
los colores y las tipografias de la identidad de la web.
"""

import os
import re
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

BASE   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OBRAS  = os.path.join(BASE, "docs", "obras", "jornada-iv")

# ── Colores de la web y de la identidad ASN ───────────────────
CREAM      = (244, 237, 224)
CREAM_ALT  = (237, 230, 216)
CREAM_HONDO= (231, 222, 205)   # el crema de la franja de los retratos
TEXT       = ( 28,  27,  24)
TEXT_MID   = ( 74,  73,  64)
TEXT_LIGHT = (122, 120, 112)
BORDER     = (212, 204, 192)
GREEN      = ( 74, 103,  65)
GREEN_OSC  = ( 52,  76,  45)
GREEN_CLARO= (166, 204, 148)
SOMBRA     = ( 16,  22,  18)
RED        = (214,  69,  65)
BLUE       = (  0, 162, 210)
WHITE      = (255, 255, 255)

FUENTES = r"C:\Windows\Fonts"
def serif(px, negrita=False):
    return ImageFont.truetype(os.path.join(FUENTES, "georgiab.ttf" if negrita else "georgia.ttf"), px)
def sans(px, peso="normal"):
    fichero = {"normal": "segoeui.ttf", "bold": "segoeuib.ttf", "light": "segoeuil.ttf"}[peso]
    return ImageFont.truetype(os.path.join(FUENTES, fichero), px)


# ── Utilidades ────────────────────────────────────────────────
def ancho(draw, texto, fuente):
    return draw.textbbox((0, 0), texto, font=fuente)[2]

def fondo_cabecera(img, w, alto, intensidad=0.58, desvanece=70):
    """Funde el quirofano del CCMIJU bajo el bloque de cabecera.

    Se quiere que el material quirurgico se reconozca: los dos brazos del
    robot Versius, la cupula sobre la mesa y la lampara. Por eso el fundido
    es alto y el desenfoque minimo; la lectura del texto no se fia del
    fondo, sino del halo crema con que va perfilado. Por abajo se desvanece
    para entrar en el crema sin corte.
    """
    foto = recortar(Image.open(os.path.join(OBRAS, "ccmiju-quirofano.jpg")), w, alto, 0.5, 0.48)
    foto = foto.filter(ImageFilter.GaussianBlur(0.8))
    # apenas se le rebaja el contraste y se le sube un punto la luz: lo justo
    # para que ningun negro compita con el texto, sin aplanar la escena
    foto = ImageEnhance.Contrast(foto).enhance(0.88)
    foto = ImageEnhance.Brightness(foto).enhance(1.06)
    fundido = Image.blend(Image.new("RGB", (w, alto), CREAM), foto, intensidad)

    mascara = Image.new("L", (w, alto), 255)
    md = ImageDraw.Draw(mascara)
    for i in range(desvanece):
        md.line([(0, alto - desvanece + i), (w, alto - desvanece + i)],
                fill=round(255 * (1 - i / desvanece)))
    img.paste(fundido, (0, 0), mascara)


def fondo_cabecera_oscuro(img, w, alto, velo=0.46):
    """La otra manera de sobreimprimir: la foto entera, sin rebajar, y encima
    un velo oscuro que asienta el texto, que pasa a ir en blanco.

    Aqui el quirofano no es una marca de agua sino la imagen de la tarjeta;
    el velo solo baja la luz lo justo para que el blanco cante sobre ella.
    """
    foto = recortar(Image.open(os.path.join(OBRAS, "ccmiju-quirofano.jpg")), w, alto, 0.5, 0.48)
    foto = ImageEnhance.Color(foto).enhance(0.92)
    img.paste(Image.blend(foto, Image.new("RGB", (w, alto), (10, 14, 12)), velo), (0, 0))


def silueta(foto, x0=340, x1=700, umbral=95, suave=6):
    """Perfil de la figura del pianista, fila a fila: (x_ini, x_fin) o None.

    El escenario es azul oscuro y el pianista va de claro, asi que basta un
    umbral de luminosidad. Se mira solo la franja central para no confundirlo
    con el piano, que tambien es claro, y se dilata unas filas arriba y abajo
    para que el contorno no salga en dientes de sierra.
    """
    px = foto.convert("L").load()
    crudo = []
    for y in range(foto.height):
        xs = [x for x in range(x0, x1) if px[x, y] > umbral]
        crudo.append((xs[0], xs[-1]) if len(xs) > 12 else None)
    perfil = []
    for y in range(foto.height):
        v = [c for c in crudo[max(0, y - suave):y + suave + 1] if c]
        perfil.append((min(a for a, _ in v), max(b for _, b in v)) if v else None)
    return perfil


def hueco_en(perfil, y0, y1, desde, margen=10):
    """Lo que ocupa la figura entre dos alturas de la tarjeta, o None."""
    v = [perfil[y] for y in range(y0 - desde, y1 - desde)
         if 0 <= y < len(perfil) and perfil[y]]
    return (min(a for a, _ in v) - margen, max(b for _, b in v) + margen) if v else None


def escribir_esquivando(d, x, y, trozos, fuente, hueco, sombra):
    """Escribe la linea saltandose la figura: se para antes de tocarla y
    continua al otro lado, de modo que el texto la siluetea.

    trozos es una lista de (texto, color), porque INCLUSION va en otro color.
    """
    saltado = False
    for texto, color in trozos:
        # cada pieza se lleva sus espacios, los de delante y los de detras,
        # para que al empalmar dos trozos de distinto color no se pierda el
        # blanco que los separa
        for pieza in re.findall(r"\s*\S+\s*", texto):
            palabra = pieza.strip()
            avance, ancho_pal = (d.textlength(pieza, font=fuente),
                                 d.textlength(palabra, font=fuente))
            if hueco and not saltado:
                ini, fin = hueco
                x_tinta = x + d.textlength(pieza[:len(pieza) - len(pieza.lstrip())],
                                           font=fuente)
                if x_tinta < fin and x_tinta + ancho_pal > ini:
                    # al reanudar se quita el blanco de delante, pero se
                    # conserva el de detras: si no, se pegaria a la siguiente
                    pieza = pieza.lstrip()
                    x, avance = fin, d.textlength(pieza, font=fuente)
                    saltado = True
            d.text((x, y), pieza, font=fuente, fill=color, **sombra)
            x += avance


def fondo_pie(img, w, y0, alto, velo=0.55):
    """La misma idea que en la cabecera, pero abajo y con el concierto: el
    piano de cola y Jose Maria Villegas en el escenario del Gran Teatro.

    La foto ya viene oscura -fondo de teatro-, asi que el velo puede ser
    suave y el programa se lee en blanco sobre ella. Va a sangre por los
    lados y hasta la banda de logotipos, con la barra tricolor rematando
    por arriba, al reves que la cabecera.
    """
    # El recorte se reparte: lo justo por arriba para que quede aire sobre la
    # cabeza, y el resto por abajo, donde solo se pierde suelo de escenario.
    # Las manos y el teclado, que es lo que no se puede cortar, quedan dentro.
    foto = recortar(Image.open(os.path.join(OBRAS, "villegas-concierto.jpg")),
                    w, alto, 0.5, 0.70)
    foto = ImageEnhance.Color(foto).enhance(0.92)
    img.paste(Image.blend(foto, Image.new("RGB", (w, alto), (10, 12, 18)), velo), (0, y0))
    return silueta(foto)


def cuerpo_que_cabe(d, textos, w, maximo=52):
    """El mayor cuerpo con el que el mas largo de los textos cabe en w."""
    for px in range(maximo, 12, -1):
        f = serif(px)
        if max(ancho(d, t, f) for t in textos) <= w:
            return px
    return 12

def texto_justificado(d, x, y, w, texto, fuente, color, halo=0, halo_col=CREAM):
    """Escribe el texto ocupando el ancho w justo, repartiendo lo que sobra
    entre las letras. Asi dos lineas de distinto largo llenan las dos la caja."""
    sobra = w - ancho(d, texto, fuente)
    extra = sobra / (len(texto) - 1) if len(texto) > 1 else 0
    cx = x
    for letra in texto:
        d.text((cx, y), letra, font=fuente, fill=color,
               stroke_width=halo, stroke_fill=halo_col)
        cx += d.textlength(letra, font=fuente) + extra

def recortar(img, w, h, ancla_x=0.5, ancla_y=0.5):
    """Recorta para llenar exactamente w x h, sin deformar.

    ancla_x / ancla_y dicen por donde se corta: 0,5 es el centro; 0,35 en
    vertical deja mas aire por abajo y salva la cabeza en un retrato.
    """
    escala = max(w / img.width, h / img.height)
    img = img.resize((round(img.width * escala), round(img.height * escala)), Image.LANCZOS)
    izq = round((img.width - w) * ancla_x)
    arr = round((img.height - h) * ancla_y)
    return img.crop((izq, arr, izq + w, arr + h))


def mosaico_cuatro(img, d, x, y, w, alto):
    """Los cuatro elementos que articulan la Jornada:

    los dos retratos a la izquierda -Carmen Pascual por Jesus Uson, y Jesus
    Uson por Olegario- y, a la derecha, el arte y la ciencia: el quirofano
    del CCMIJU y el piano de José María Villegas.
    """
    hueco = 16
    # los retratos son verticales y las escenas muy apaisadas: se les da a cada
    # una el ancho que pide su proporcion, para que ninguna quede recortada de mas
    col_r = 270                             # cada retrato
    col_e = w - 2 * col_r - 2 * hueco       # columna de las dos escenas
    alto_e = (alto - hueco) // 2

    piezas = [
        ("retrato-carmen-pascual-uson.jpg", x, y, col_r, alto, 0.5, 0.42),
        ("busto-jesus-uson-olegario.jpg",   x + col_r + hueco, y, col_r, alto, 0.5, 0.26),
        ("ccmiju-quirofano.jpg",            x + 2 * (col_r + hueco), y, col_e, alto_e, 0.5, 0.5),
        ("villegas-concierto.jpg",          x + 2 * (col_r + hueco), y + alto_e + hueco, col_e, alto_e, 0.46, 0.5),
    ]
    for nombre, px, py, pw, ph, ax, ay in piezas:
        pieza = recortar(Image.open(os.path.join(OBRAS, nombre)), pw, ph, ax, ay)
        img.paste(pieza, (px, py))
        d.rectangle([px, py, px + pw - 1, py + ph - 1], outline=BORDER, width=1)


# ── Mosaico de participantes, al modo del cartel de De profundis ──
JORNADA = r"C:\Users\Fernando Serrano P\Documents\FundacionCarmenPascual\IV Jornada Arte y Ciencia"

# Los recortes se dan en fracciones del original, no en pixeles, para poder
# sacarlos de los A3 a 3508x4961 que estan en la carpeta de la Jornada.
# (fichero, caja fraccional o None, nombre, ancla vertical del recorte final)
PERFIL = os.path.join(JORNADA, "A3 Cartel De profundis.jpg")

# La rejilla va en dos filas de distinto porte: seis piezas arriba, mas
# estrechas y ligeras, y cinco abajo, mas anchas y algo mas altas, haciendo
# de base. El reparto no es caprichoso: cada retrato cae en la fila cuya
# celda se parece mas a su proporcion, de modo que se recorte lo menos
# posible. De ahi que Silvia Nunez, Carlos Montenegro, KINI, Carmen Pascual
# y Olegario -los recortes mas anchos, de 0,72 a 0,65- vayan abajo, y Jesus
# Uson, Clara del Carmen, Elena Alvarez y Jose Maria Villegas -de 0,62 a
# 0,51- arriba.
#
# PENDIENTE reserva el hueco de los dos ponentes cuya foto no ha llegado:
# el Dr. Joaquin Gomez Abellan y el Dr. Angel Perez Nunez. Cuando lleguen,
# se sustituye PENDIENTE por el fichero y su caja, y no hay que tocar nada mas.
PENDIENTE = None

FILA_ALTA = [           # seis, las de menor extension horizontal
    (PERFIL, (0.2363, 0.2086, 0.3763, 0.4030), "Jesús Usón",        0.18),
    (PENDIENTE, None,                          "J. Gómez Abellán",  0.50),
    (PERFIL, (0.8019, 0.2086, 0.9713, 0.4030), "Clara del Carmen",  0.16),
    (os.path.join(JORNADA, "WhatsApp Image 2026-09-10 at 20.15.31.jpeg"),
             (0.1438, 0.2167, 0.4750, 0.9833), "Elena Álvarez",     0.22),
    (PENDIENTE, None,                          "Á. Pérez Núñez",    0.50),
    (os.path.join(JORNADA, "Chema Villegas. Foto. Manuel Curiel.jpg"),
             (0.3500, 0.0000, 0.6000, 1.0000), "J. M. Villegas",    0.28),
]

FILA_BASE = [           # cinco, las de mayor extension horizontal
    (PERFIL, (0.0331, 0.2086, 0.2163, 0.4030), "Carmen Pascual",    0.20),
    (PERFIL, (0.3981, 0.2086, 0.5756, 0.4030), "Olegario",          0.16),
    (os.path.join(JORNADA, "Kini Carrrasco o la voluntad de poder.jpg"),
             (0.1063, 0.3802, 0.3625, 0.8930), "KINI Carrasco",     0.30),
    (PERFIL, (0.5913, 0.2086, 0.7881, 0.4030), "Carlos Montenegro", 0.16),
    (os.path.join(JORNADA, "A3 Cartel Silvia y Elena.jpg"),
             (0.0344, 0.2298, 0.2063, 0.3977), "Silvia Núñez",      0.20),
]

HUECO, ALTO_ALTA, ALTO_BASE = 15, 140, 160
Y_PIE, FIN_PIE = 684, 1038     # banda del concierto, en la tarjeta oscura
X_DCHA = 1040                  # hasta donde puede llegar el programa


def _fila(img, d, x, y, w, piezas, ch, f_nombre):
    """Dibuja una fila de celdas iguales, centrada en el ancho disponible."""
    n = len(piezas)
    cw = (w - (n - 1) * HUECO) // n
    margen = (w - (n * cw + (n - 1) * HUECO)) // 2      # reparte el sobrante

    for i, (fichero, caja, nombre, ancla) in enumerate(piezas):
        px = x + margen + i * (cw + HUECO)
        if fichero is None:                              # foto aun por llegar
            d.rectangle([px, y, px + cw - 1, y + ch - 1], fill=CREAM,
                        outline=BORDER, width=1)
        else:
            pieza = Image.open(fichero).convert("RGB")
            if caja:
                x0, y0, x1, y1 = caja
                pieza = pieza.crop((round(x0 * pieza.width), round(y0 * pieza.height),
                                    round(x1 * pieza.width), round(y1 * pieza.height)))
            pieza = recortar(pieza, cw, ch, 0.5, ancla)
            img.paste(pieza, (px, y))
            d.rectangle([px, y, px + cw - 1, y + ch - 1], outline=BORDER, width=1)
        d.text((px + cw / 2, y + ch + 4), nombre, font=f_nombre, fill=TEXT_MID, anchor="ma")

    return ch + 20


def mosaico_participantes(img, d, x, y, w):
    """Una imagen por participante, como la fila de retratos de De profundis."""
    f_nombre = sans(12)
    alto = _fila(img, d, x, y, w, FILA_ALTA, ALTO_ALTA, f_nombre)
    alto += HUECO
    alto += _fila(img, d, x, y + alto, w, FILA_BASE, ALTO_BASE, f_nombre)
    return alto

def banda_logotipos(ancho, union=20, umbral=225):
    """Los logotipos del cartel, recortados uno a uno y repartidos a lo largo
    de la franja con la misma separacion entre ellos y en los dos extremos.

    Se localizan por las columnas que llevan tinta: dentro de un logotipo los
    huecos son de unos pocos pixeles y entre un logotipo y otro pasan de
    veinte. Asi el reparto se rehace solo el dia que entre uno mas -la
    Diputacion, si confirma- sin tocar nada aqui.
    """
    cartel = Image.open(os.path.join(OBRAS, "cartel-general.jpg"))
    # el pie blanco del cartel empieza en el 0,9496 de su altura: por ahi se corta
    franja = cartel.crop((60, int(cartel.height * 0.9505),
                          cartel.width - 60, int(cartel.height * 0.9935)))
    franja = franja.resize((ancho, round(franja.height * ancho / franja.width)),
                           Image.LANCZOS)
    px = franja.convert("L").load()
    W, H = franja.size

    trozos, ini = [], None
    for x in range(W + 1):
        hay = x < W and any(px[x, y] < umbral for y in range(H))
        if hay and ini is None:
            ini = x
        elif not hay and ini is not None:
            trozos.append((ini, x))
            ini = None
    piezas = []
    for a, b in trozos:                      # lo que solo separan unos pixeles
        if piezas and a - piezas[-1][1] < union:   # es el mismo logotipo
            piezas[-1] = (piezas[-1][0], b)
        else:
            piezas.append((a, b))

    banda = Image.new("RGB", (W, H), WHITE)
    paso = (W - sum(b - a for a, b in piezas)) / (len(piezas) + 1)
    x = paso
    for a, b in piezas:
        banda.paste(franja.crop((a, 0, b, H)), (round(x), 0))
        x += (b - a) + paso
    return banda


def barra_tricolor(draw, x, y, w, alto):
    tercio = w / 3
    for i, color in enumerate((RED, BLUE, GREEN)):
        draw.rectangle([x + i * tercio, y, x + (i + 1) * tercio, y + alto], fill=color)

def titulo_incl(draw, cx, y, antes, palabra, fuente, color_texto, color_incl,
                halo=0, halo_col=CREAM):
    """Dibuja 'antes INCLUSION' centrado, con la palabra destacada en color."""
    w1 = ancho(draw, antes, fuente)
    w2 = ancho(draw, palabra, fuente)
    x = cx - (w1 + w2) / 2
    draw.text((x, y), antes, font=fuente, fill=color_texto,
              stroke_width=halo, stroke_fill=halo_col)
    draw.text((x + w1, y), palabra, font=fuente, fill=color_incl,
              stroke_width=halo, stroke_fill=halo_col)


# Donde parte cada linea al rodear al pianista, en la tarjeta del concierto.
# No se deja al azar del ancho: se corta donde la frase lo pide -tras un
# punto, o antes del nombre completo de quien interviene- y lo de la derecha
# arranca siempre en mayuscula, porque empieza tramo. Con "" a la derecha,
# la linea se queda solo con lo de la izquierda.
PARTIDO = {
    # el tercer valor, cuando lo hay, son los espacios que la parte derecha
    # se separa de mas: aqui, para no pegarse a la cara del pianista
    "09:45": ("Inauguración. Prof. Jesús Usón  y", "Dr. Francisco Sánchez-Margallo", 2),
    "10:00": ("Bioimpresión 3D", "En medicina personalizada. Dr. Joaquín Gómez Abellán"),
    "10:20": ("Deporte e INCLUSIÓN:", "La mística de la superación. KINI Carrasco Ávila"),
    "10:40": ("Travesía por el dolor.", "Lectura poética. Clara del Carmen Martín"),
    "11:00": ("Infancia debilitada.", "Presentación. Carlos Montenegro"),
    # con las iniciales del apellido -"Carmen P., Jesus U., ..."- hacen falta
    # 443 px y solo hay 404: se quedan los nombres, que ademas van con foto y
    # apellido en la rejilla de arriba
    "11:20": ("Exposición De profundis", "Carmen, Jesús, Olegario, Carlos y Clara"),
    "12:10": ("Música y educación inclusiva.", "Dra. Silvia Núñez y Elena Álvarez"),
    # a esta altura el brazo apoyado en el piano deja solo 331 px libres y el
    # texto pide 418, asi que arranca antes y se monta sobre el brazo: es la
    # unica de las nueve que invade la figura, y se hace a proposito
    "12:40": ("Cirugía cerebral", "En pacientes despiertos. Dr. Ángel Pérez Núñez"),
    "13:00": ("Concierto de clausura.", "José María Villegas, piano"),
}


WEB = "https://www.fundacioncarmenpascual.org/"
CAJA_QR = CAJA_WEB = None      # las rellena la tarjeta al dibujar el pie


PROGRAMA = [
    ("09:45", "Inauguración. Prof. Jesús Usón y Dr. Francisco Sánchez-Margallo"),
    ("10:00", "Bioimpresión 3D en medicina personalizada. Dr. Joaquín Gómez Abellán"),
    ("10:20", "Deporte e INCLUSIÓN: la mística de la superación. KINI Carrasco Ávila"),
    ("10:40", "Travesía por el dolor. Lectura poética. Clara del Carmen Martín"),
    ("11:00", "Infancia debilitada. Presentación. Carlos Montenegro"),
    ("11:20", "Exposición De profundis, con acto de entrega de obra"),
    ("12:10", "Música y educación inclusiva. Dra. Silvia Núñez y Elena Álvarez"),
    ("12:40", "Cirugía cerebral en pacientes despiertos. Dr. Ángel Pérez Núñez"),
    ("13:00", "Concierto de clausura. José María Villegas, piano"),
]


# ══ 1. Tarjeta de WhatsApp, 1080 x 1350 ═══════════════════════
def tarjeta(variante="foto"):
    """variante 'foto': solo el quirofano.  'cuatro': los cuatro elementos."""
    W, H, M = 1080, 1350, 70
    CW = W - 2 * M
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    sobre_foto   = variante in ("participantes", "quirofano")
    fondo_oscuro = variante == "quirofano"

    if fondo_oscuro:
        # la foto manda: entra a sangre por arriba y por los dos lados, sin
        # nada encima que le haga margen, y la barra tricolor baja al pie de
        # la banda, donde remata la imagen y la separa del crema
        fondo_cabecera_oscuro(img, W, 302)
        barra_tricolor(d, 0, 302, W, 8)
        # las dos franjas de papel -la de los retratos y la del enlace- en un
        # crema mas hondo: amortiguan el salto entre las bandas oscuras, le
        # quitan el blanco a las fotos y quedan del mismo tono entre si
        d.rectangle([0, 310, W, Y_PIE - 1], fill=CREAM_HONDO)
        d.rectangle([0, FIN_PIE, W, 1205], fill=CREAM_HONDO)
    else:
        if sobre_foto:
            fondo_cabecera(img, W, 310)
        barra_tricolor(d, 0, 0, W, 10)

    # El titulo cede tamano para que las dos instituciones que organizan -la
    # Fundacion, bajo el encabezamiento, y el Centro, bajo la fecha- crezcan
    # hasta llenar la caja de margen a margen. Van al mismo cuerpo: el mayor
    # con el que cabe la mas larga, y la otra se justifica separando las
    # letras, de modo que las dos lineas midan lo mismo.
    FUNDACION = "Fundación Carmen Pascual. Arte Salud Naturaleza"
    CENTRO    = "Centro de Cirugía de Mínima Invasión Jesús Usón · Cáceres"
    f_inst = serif(cuerpo_que_cabe(d, [FUNDACION, CENTRO], CW))

    # Tres maneras de resolver el texto de cabecera: sobre crema limpio, con
    # halo crema sobre la foto rebajada, o en blanco sobre la foto velada.
    if fondo_oscuro:            # blanco con sombra: la foto tiene blancos
        col_tit, col_inst, col_incl, halo, halo_col = WHITE, CREAM, GREEN_CLARO, 2, SOMBRA
    elif sobre_foto:            # negro perfilado en crema sobre la foto rebajada
        col_tit, col_inst, col_incl, halo, halo_col = TEXT, TEXT, GREEN_OSC, 3, CREAM
    else:
        col_tit, col_inst, col_incl, halo, halo_col = TEXT, TEXT_MID, GREEN, 0, CREAM

    f_tit  = serif(40, negrita=True)
    f_tit2 = serif(35, negrita=sobre_foto)
    d.text((W / 2, 44), "IV JORNADA de ARTE y CIENCIA", font=f_tit, fill=col_tit,
           anchor="ma", stroke_width=halo, stroke_fill=halo_col)
    titulo_incl(d, W / 2, 97, "por la ", "INCLUSIÓN", f_tit2, col_tit, col_incl, halo, halo_col)

    texto_justificado(d, M, 148, CW, FUNDACION, f_inst, col_inst, halo, halo_col)

    d.line([(W / 2 - 110, 202), (W / 2 + 110, 202)], fill=col_incl, width=2)

    d.text((W / 2, 214), "Viernes 23 de octubre de 2026  ·  09:45 h",
           font=sans(29, "bold"), fill=col_tit, anchor="ma",
           stroke_width=halo, stroke_fill=halo_col)
    texto_justificado(d, M, 256, CW, CENTRO, f_inst, col_inst, halo, halo_col)

    # imagen o mosaico
    if sobre_foto:
        mosaico_participantes(img, d, M, 316, CW)
        credito = None          # los creditos de las fotos van en la web
        if fondo_oscuro:
            perfil = fondo_pie(img, W, Y_PIE, FIN_PIE - Y_PIE)
            barra_tricolor(d, 0, Y_PIE, W, 8)
            # bajado 24 px: deja el mismo aire sobre "PROGRAMA" que bajo la
            # ultima linea, dentro de la banda del concierto
            y_credito, y_label, y_prog, salto = 0, 712, 744, 31
        else:
            y_credito, y_label, y_prog, salto = 0, 774, 808, 33
    elif variante == "cuatro":
        mosaico_cuatro(img, d, M, 298, CW, 408)
        credito = "Fotos: Juanmi, CCMIJU y Manuel Curiel."
        y_credito, y_label, y_prog, salto = 714, 752, 792, 34
    else:
        foto = recortar(Image.open(os.path.join(OBRAS, "ccmiju-quirofano.jpg")), CW, 360)
        img.paste(foto, (M, 300))
        d.rectangle([M, 300, M + CW - 1, 300 + 360 - 1], outline=BORDER, width=1)
        credito = "Foto: CCMIJU, 2025."
        y_credito, y_label, y_prog, salto = 666, 706, 748, 38

    if credito:
        d.text((M + CW, y_credito), credito, font=sans(16), fill=TEXT_LIGHT, anchor="ra")

    # programa
    col_acto = CREAM if fondo_oscuro else TEXT_MID
    col_hora = GREEN_CLARO if fondo_oscuro else GREEN
    sombra   = dict(stroke_width=1, stroke_fill=SOMBRA) if fondo_oscuro else {}

    # Sobre la foto del concierto el bloque se arrima al borde izquierdo: el
    # texto tiene que rodear al pianista y necesita todo el ancho que pueda.
    x_hora = 44 if fondo_oscuro else M
    x_acto = x_hora + (84 if fondo_oscuro else 92)

    d.text((x_hora, y_label), "P R O G R A M A", font=sans(19, "bold"), fill=col_hora, **sombra)
    # ahi el texto va en negrita: gana cuerpo y se despega del fondo mejor
    # que subiendo el tamano
    f_hora = serif(26, negrita=fondo_oscuro)
    f_acto = sans(21 if variante == "foto" else (19 if fondo_oscuro else 20),
                  "bold" if fondo_oscuro else "normal")
    def trozos_de(texto):
        if "INCLUSIÓN" in texto:
            antes, despues = texto.split("INCLUSIÓN")
            return [(antes, col_acto), ("INCLUSIÓN", col_hora), (despues, col_acto)]
        return [(texto, col_acto)]

    y = y_prog
    for hora, acto in PROGRAMA:
        d.text((x_hora, y - 4), hora, font=f_hora, fill=col_hora, **sombra)
        if fondo_oscuro:
            hueco = hueco_en(perfil, y, y + f_acto.size + 6, Y_PIE)
            reparto = PARTIDO.get(hora, (acto, None))
            izq, der = reparto[0], reparto[1]
            aparte = reparto[2] * d.textlength(" ", font=f_acto) if len(reparto) > 2 else 0
            escribir_esquivando(d, x_acto, y, trozos_de(izq), f_acto,
                                None if der is not None else hueco, sombra)
            if der:
                # normalmente arranca donde acaba la figura; si asi no cabe
                # hasta el margen, retrocede lo justo y se superpone a ella,
                # reforzando la sombra para que siga leyendose encima
                x_der, ancho_der = hueco[1] + aparte, ancho(d, der, f_acto)
                sombra_der = sombra
                if x_der + ancho_der > X_DCHA:
                    x_der = X_DCHA - ancho_der
                    sombra_der = dict(stroke_width=2, stroke_fill=SOMBRA)
                escribir_esquivando(d, x_der, y, trozos_de(der), f_acto, None, sombra_der)
        else:
            escribir_esquivando(d, x_acto, y, trozos_de(acto), f_acto, None, sombra)
        y += salto

    # llamada a la web
    if fondo_oscuro:
        # el enlace sale de la foto y se lee sobre el crema, entre la banda
        # del concierto y los logotipos
        # Centrado en la franja de crema que queda entre la banda del
        # concierto y la de los logotipos. Se centra la mancha real de las
        # letras, no la caja de la fuente: si no, el hueco del descendente
        # -la p de pascual- deja mas aire arriba que abajo.
        # El QR de la Fundacion -el mismo que ya esta difundido y que esta en
        # la web, docs/qr-fundacion.png- recortado sin su pie, que aqui sobra
        # porque el nombre y la direccion van al lado. Es lo unico que lleva a
        # la web desde la propia imagen: el texto de una foto no se pulsa.
        LADO = 148
        qr = Image.open(os.path.join(BASE, "docs", "qr-fundacion.png")).convert("RGB")
        qr = qr.crop((96, 96, 670, 670)).resize((LADO, LADO), Image.LANCZOS)

        f_pie, f_web = sans(20), sans(27, "bold")
        rotulo, web = "Programa, obras y vídeos en", "www.fundacioncarmenpascual.org"
        ancho_txt = max(ancho(d, rotulo, f_pie), ancho(d, web, f_web))
        x = (W - (LADO + 26 + ancho_txt)) // 2
        y = FIN_PIE + ((1206 - FIN_PIE) - LADO) // 2

        img.paste(qr, (x, y))
        d.text((x + LADO + 26, y + 42), rotulo, font=f_pie, fill=TEXT_MID)
        d.text((x + LADO + 26, y + 74), web, font=f_web, fill=GREEN)

        # se apuntan las dos zonas, para que el PDF ponga ahi los enlaces
        global CAJA_QR, CAJA_WEB
        CAJA_QR  = (x, y, x + LADO, y + LADO)
        CAJA_WEB = (x + LADO + 26, y + 70,
                    x + LADO + 26 + ancho(d, web, f_web), y + 110)
    else:
        d.line([(M, 1108), (M + CW, 1108)], fill=BORDER, width=1)
        d.text((W / 2, 1122), "Los cinco carteles, las obras y los vídeos, en",
               font=sans(21), fill=TEXT_MID, anchor="ma")
        d.text((W / 2, 1152), "fundacioncarmenpascual.org", font=sans(31, "bold"),
               fill=GREEN, anchor="ma")

    # banda blanca con los logotipos del cartel
    d.rectangle([0, 1206, W, H], fill=WHITE)
    d.line([(0, 1206), (W, 1206)], fill=BORDER, width=1)
    img.paste(banda_logotipos(CW), (M, 1224))
    d.text((W / 2, 1310),
           "* Fundación Carmen Pascual. Arte Salud Naturaleza, pendiente de inscripción "
           "en el Registro de Fundaciones de competencia estatal.",
           font=sans(14), fill=TEXT_LIGHT, anchor="ma")

    barra_tricolor(d, 0, H - 8, W, 8)

    nombre = {"foto":          "tarjeta-whatsapp.jpg",
              "cuatro":        "tarjeta-whatsapp-cuatro.jpg",
              "participantes": "tarjeta-whatsapp-participantes.jpg",
              "quirofano":     "tarjeta-whatsapp-quirofano.jpg"}[variante]
    salida = os.path.join(OBRAS, nombre)
    img.save(salida, "JPEG", quality=88, progressive=True, optimize=True)
    print("%-28s %dx%d  %d KB" % (nombre, img.width, img.height, os.path.getsize(salida) // 1024))


# ══ 1 bis. La misma tarjeta en PDF, con la direccion pulsable ══
def tarjeta_pdf(jpg="tarjeta-whatsapp-quirofano.jpg",
                nombre="IV Jornada de Arte y Ciencia por la INCLUSIÓN.pdf"):
    """Mete el JPG en un PDF y le pone encima una zona de enlace sobre la
    direccion escrita.

    En una imagen el texto no se puede pulsar; en un PDF si, porque el enlace
    es una anotacion aparte que el visor coloca sobre la pagina. Y al mandarlo
    como documento, lo que se anuncia es el nombre del fichero: de ahi que se
    llame como la Jornada.
    """
    from reportlab.pdfgen import canvas

    ANCHO, ALTO, ESCALA = 1080, 1350, 0.5        # 540 x 675 pt, a 144 ppp
    W, H = ANCHO * ESCALA, ALTO * ESCALA
    salida = os.path.join(OBRAS, nombre)
    c = canvas.Canvas(salida, pagesize=(W, H))
    c.drawImage(os.path.join(OBRAS, jpg), 0, 0, W, H)

    for caja in (CAJA_QR, CAJA_WEB):     # de pixeles a puntos, con el origen
        if caja:                         # abajo, que es como cuenta el PDF
            x0, y0, x1, y1 = caja
            c.linkURL(WEB, (x0 * ESCALA, (ALTO - y1) * ESCALA,
                            x1 * ESCALA, (ALTO - y0) * ESCALA), relative=0, thickness=0)

    c.setTitle("IV Jornada de Arte y Ciencia por la INCLUSIÓN")
    c.setAuthor("Fundación Carmen Pascual. Arte Salud Naturaleza")
    c.setSubject("Viernes 23 de octubre de 2026, 09:45 h. CCMIJU, Cáceres")
    c.save()
    print("%-28s %.0fx%.0f pt  %d KB" % (nombre[:28], W, H,
                                          os.path.getsize(salida) // 1024))


# ══ 2. Vista previa del enlace, 1200 x 630 ════════════════════
def og():
    W, H, M = 1200, 630, 56
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    foto = recortar(Image.open(os.path.join(OBRAS, "ccmiju-quirofano.jpg")), W, 340)
    img.paste(foto, (0, 0))
    barra_tricolor(d, 0, 340, W, 8)

    d.text((W / 2, 382), "IV JORNADA de ARTE y CIENCIA", font=serif(46, negrita=True),
           fill=TEXT, anchor="ma")
    titulo_incl(d, W / 2, 442, "por la ", "INCLUSIÓN", serif(40), TEXT, GREEN)
    d.text((W / 2, 512), "Viernes 23 de octubre de 2026  ·  09:45 h  ·  CCMIJU, Cáceres",
           font=sans(26, "bold"), fill=TEXT, anchor="ma")
    d.text((W / 2, 552), "Centro de Cirugía de Mínima Invasión Jesús Usón · Fundación Carmen Pascual",
           font=sans(20), fill=TEXT_MID, anchor="ma")
    d.text((W / 2, 584), "Entrada libre hasta completar aforo",
           font=sans(20), fill=TEXT_LIGHT, anchor="ma")

    salida = os.path.join(OBRAS, "og-jornada-iv.jpg")
    img.save(salida, "JPEG", quality=88, progressive=True, optimize=True)
    print("og        %dx%d  %d KB" % (img.width, img.height, os.path.getsize(salida) // 1024))


if __name__ == "__main__":
    tarjeta("foto")
    tarjeta("cuatro")
    tarjeta("participantes")
    tarjeta("quirofano")
    tarjeta_pdf()
    og()
