# -*- coding: utf-8 -*-
"""
Genera las dos piezas del envio de la IV Jornada de Arte y Ciencia:

  1. tarjeta-whatsapp.jpg   1080 x 1350 (4:5)  la que se manda por WhatsApp
  2. og-jornada-iv.jpg      1200 x 630         la vista previa del enlace

Las dos salen de los materiales que ya estan en docs/obras/jornada-iv/, con
los colores y las tipografias de la identidad de la web.
"""

import os
from PIL import Image, ImageDraw, ImageFont

BASE   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OBRAS  = os.path.join(BASE, "docs", "obras", "jornada-iv")

# ── Colores de la web y de la identidad ASN ───────────────────
CREAM      = (244, 237, 224)
CREAM_ALT  = (237, 230, 216)
TEXT       = ( 28,  27,  24)
TEXT_MID   = ( 74,  73,  64)
TEXT_LIGHT = (122, 120, 112)
BORDER     = (212, 204, 192)
GREEN      = ( 74, 103,  65)
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
    col_r = (w - 2 * hueco - 312) // 2      # ancho de cada retrato
    col_e = w - 2 * col_r - 2 * hueco       # ancho de la columna de escenas
    alto_e = (alto - hueco) // 2

    piezas = [
        ("retrato-carmen-pascual-uson.jpg", x, y, col_r, alto, 0.5, 0.42),
        ("busto-jesus-uson-olegario.jpg",   x + col_r + hueco, y, col_r, alto, 0.5, 0.30),
        ("ccmiju-quirofano.jpg",            x + 2 * (col_r + hueco), y, col_e, alto_e, 0.5, 0.5),
        ("villegas-concierto.jpg",          x + 2 * (col_r + hueco), y + alto_e + hueco, col_e, alto_e, 0.46, 0.5),
    ]
    for nombre, px, py, pw, ph, ax, ay in piezas:
        pieza = recortar(Image.open(os.path.join(OBRAS, nombre)), pw, ph, ax, ay)
        img.paste(pieza, (px, py))
        d.rectangle([px, py, px + pw - 1, py + ph - 1], outline=BORDER, width=1)

def barra_tricolor(draw, x, y, w, alto):
    tercio = w / 3
    for i, color in enumerate((RED, BLUE, GREEN)):
        draw.rectangle([x + i * tercio, y, x + (i + 1) * tercio, y + alto], fill=color)

def titulo_incl(draw, cx, y, antes, palabra, fuente, color_texto, color_incl):
    """Dibuja 'antes INCLUSION' centrado, con la palabra destacada en color."""
    w1 = ancho(draw, antes, fuente)
    w2 = ancho(draw, palabra, fuente)
    x = cx - (w1 + w2) / 2
    draw.text((x, y), antes, font=fuente, fill=color_texto)
    draw.text((x + w1, y), palabra, font=fuente, fill=color_incl)


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

    barra_tricolor(d, 0, 0, W, 10)

    f_tit  = serif(52, negrita=True)
    f_tit2 = serif(46)
    d.text((W / 2, 46), "IV JORNADA de ARTE y CIENCIA", font=f_tit, fill=TEXT, anchor="ma")
    titulo_incl(d, W / 2, 114, "por la ", "INCLUSIÓN", f_tit2, TEXT, GREEN)

    d.line([(W / 2 - 110, 188), (W / 2 + 110, 188)], fill=GREEN, width=1)

    d.text((W / 2, 206), "Viernes 23 de octubre de 2026  ·  09:45 h",
           font=sans(31, "bold"), fill=TEXT, anchor="ma")
    d.text((W / 2, 250), "CCMIJU · Cáceres · Entrada libre hasta completar aforo",
           font=sans(23), fill=TEXT_MID, anchor="ma")

    # imagen o mosaico
    if variante == "cuatro":
        mosaico_cuatro(img, d, M, 298, CW, 408)
        credito = "Fotos: Juanmi, CCMIJU y Manuel Curiel."
        y_credito, y_label, y_prog, salto = 714, 752, 792, 34
    else:
        foto = recortar(Image.open(os.path.join(OBRAS, "ccmiju-quirofano.jpg")), CW, 360)
        img.paste(foto, (M, 300))
        d.rectangle([M, 300, M + CW - 1, 300 + 360 - 1], outline=BORDER, width=1)
        credito = "Foto: CCMIJU, 2025."
        y_credito, y_label, y_prog, salto = 666, 706, 748, 38

    d.text((M + CW, y_credito), credito, font=sans(16), fill=TEXT_LIGHT, anchor="ra")

    # programa
    d.text((M, y_label), "P R O G R A M A", font=sans(19, "bold"), fill=GREEN)
    f_hora = serif(26)
    f_acto = sans(21 if variante == "foto" else 20)
    y = y_prog
    for hora, acto in PROGRAMA:
        d.text((M, y - 4), hora, font=f_hora, fill=GREEN)
        if "INCLUSIÓN" in acto:
            antes, despues = acto.split("INCLUSIÓN")
            x = M + 92
            d.text((x, y), antes, font=f_acto, fill=TEXT_MID)
            x += ancho(d, antes, f_acto)
            d.text((x, y), "INCLUSIÓN", font=f_acto, fill=GREEN)
            x += ancho(d, "INCLUSIÓN", f_acto)
            d.text((x, y), despues, font=f_acto, fill=TEXT_MID)
        else:
            d.text((M + 92, y), acto, font=f_acto, fill=TEXT_MID)
        y += salto

    # llamada a la web
    d.line([(M, 1108), (M + CW, 1108)], fill=BORDER, width=1)
    d.text((W / 2, 1122), "Los cinco carteles, las obras y los vídeos, en",
           font=sans(21), fill=TEXT_MID, anchor="ma")
    d.text((W / 2, 1152), "fundacioncarmenpascual.org", font=sans(31, "bold"), fill=GREEN, anchor="ma")

    # banda blanca con los logotipos del cartel
    d.rectangle([0, 1206, W, H], fill=WHITE)
    d.line([(0, 1206), (W, 1206)], fill=BORDER, width=1)
    cartel = Image.open(os.path.join(OBRAS, "cartel-general.jpg"))
    # el pie blanco del cartel empieza en el 0,9496 de su altura: por ahi se corta
    banda = cartel.crop((60, int(cartel.height * 0.9505), cartel.width - 60, int(cartel.height * 0.9935)))
    banda = banda.resize((CW, round(banda.height * CW / banda.width)), Image.LANCZOS)
    img.paste(banda, (M, 1224))
    d.text((W / 2, 1310),
           "* Fundación Carmen Pascual. Arte Salud Naturaleza, pendiente de inscripción "
           "en el Registro de Fundaciones de competencia estatal.",
           font=sans(14), fill=TEXT_LIGHT, anchor="ma")

    barra_tricolor(d, 0, H - 8, W, 8)

    nombre = "tarjeta-whatsapp.jpg" if variante == "foto" else "tarjeta-whatsapp-cuatro.jpg"
    salida = os.path.join(OBRAS, nombre)
    img.save(salida, "JPEG", quality=88, progressive=True, optimize=True)
    print("%-28s %dx%d  %d KB" % (nombre, img.width, img.height, os.path.getsize(salida) // 1024))


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
    og()
