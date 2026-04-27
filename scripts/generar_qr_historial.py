"""
Genera los QR del Historial de Actividades con el mismo estilo visual
que el QR de la Fundación Carmen Pascual:
  - Esquinas tricolor (rojo, azul, verde)
  - Logo ASN en el centro
  - Línea tricolor inferior
  - Título del evento
"""

import qrcode
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

# ── Colores identidad ASN ─────────────────────────────────────
RED   = (214,  69,  65)
BLUE  = (  0, 162, 210)
GREEN = ( 74, 103,  65)
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
CREAM = (244, 237, 224)

# ── Eventos ───────────────────────────────────────────────────
EVENTS = [
    {
        'file':     'qr-ciclo-xviii',
        'ext':      'png',
        'url':      'https://drive.google.com/drive/folders/1vD0fo9xC5_ghka8Kj-oI0_Ibv65ijAfN?usp=drive_link',
        'title':    'XVIII Ciclo ASN',
        'subtitle': 'Arte · Salud · Naturaleza',
    },
    {
        'file':     'qr-ciclo-xix',
        'ext':      'png',
        'url':      'https://drive.google.com/drive/folders/1D1STUhvaeZSALfZfqc7o7_1a11jXfpJW?usp=drive_link',
        'title':    'XIX Ciclo ASN',
        'subtitle': 'Arte · Salud · Naturaleza',
    },
    {
        'file':     'qr-ciclo-xx',
        'ext':      'png',
        'url':      'https://drive.google.com/drive/folders/1yCQ6KUGHu8qOIOjSncy303agS8cIM3Di?lfhs=2',
        'title':    'XX Ciclo ASN',
        'subtitle': 'Arte · Salud · Naturaleza',
    },
    {
        'file':     'qr-ciclo-xxi-jornada-iii',
        'ext':      'png',
        'url':      'https://drive.google.com/drive/folders/1W-N5Qop6chXRE1jr2lW0UNlXqJ2JZkCy?lfhs=2',
        'title':    'XXI Ciclo ASN',
        'subtitle': 'III Jornada Arte y Ciencia',
    },
    {
        'file':     'qr-cp-jrj',
        'ext':      'png',
        'url':      'https://drive.google.com/drive/folders/149LINCCryWzHLcAiLLWaPVy9zLWYZI7e?lfhs=2',
        'title':    'Carmen Pascual entre poetas',
        'subtitle': 'con Juan Ramón Jiménez',
    },
    {
        'file':     'qr-cp-gyg',
        'ext':      'png',
        'url':      'https://drive.google.com/drive/folders/1W-N5Qop6chXRE1jr2lW0UNlXqJ2JZkCy?lfhs=2',
        'title':    'Carmen Pascual entre poetas',
        'subtitle': 'con Gabriel y Galán',
    },
]

OUT_DIR = '/workspaces/FundacionCarmenPascual2/docs/historial'
BOX     = 12   # px por módulo
BORDER  = 4    # módulos de margen silencioso


def recolor_eye(arr, ox, oy, box, color):
    """Recolorea un ojo de esquina del QR en coordenadas de píxel."""
    s = 7 * box
    r, g, b = color
    # Primero blanquear toda la zona del ojo
    arr[oy:oy+s, ox:ox+s] = [255, 255, 255, 255]
    # Marco exterior (1 módulo de ancho)
    arr[oy        :oy+box,     ox:ox+s      ] = [r, g, b, 255]
    arr[oy+s-box  :oy+s,       ox:ox+s      ] = [r, g, b, 255]
    arr[oy        :oy+s,       ox:ox+box    ] = [r, g, b, 255]
    arr[oy        :oy+s,       ox+s-box:ox+s] = [r, g, b, 255]
    # Punto interior (3x3 módulos, offset 2)
    dx, dy = ox + 2*box, oy + 2*box
    arr[dy:dy+3*box, dx:dx+3*box] = [r, g, b, 255]


LOGO_ASN_PATH = '/workspaces/FundacionCarmenPascual2/docs/obras/LOGO  ARTE SALUD NATURALEZA.jpg'

def make_asn_logo(size):
    """Carga el logo ASN auténtico, recorta la parte superior (letras A·S·N)
    y lo enmarca en un cuadrado con borde blanco."""
    src = Image.open(LOGO_ASN_PATH).convert('RGBA')

    # Usar solo la mitad superior del logo (donde están las letras A, S, N)
    crop_h = int(src.height * 0.58)
    src = src.crop((0, 0, src.width, crop_h))

    # Redimensionar manteniendo proporción para que quepa en 'size'
    src.thumbnail((size, size), Image.LANCZOS)

    # Centrar en un cuadrado blanco con padding
    pad    = size // 8
    total  = size + pad * 2
    canvas = Image.new('RGBA', (total, total), (255, 255, 255, 255))
    ox = (total - src.width)  // 2
    oy = (total - src.height) // 2
    canvas.paste(src, (ox, oy), src)
    return canvas


def generate_qr(event):
    url      = event['url']
    title    = event['title']
    subtitle = event['subtitle']
    fname    = f"{event['file']}.{event['ext']}"
    out_path = os.path.join(OUT_DIR, fname)

    # 1. Generar QR base
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=BOX,
        border=BORDER,
    )
    qr.add_data(url)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color='black', back_color='white').convert('RGBA')
    arr    = np.array(qr_img)

    # 2. Recolorear las tres esquinas
    n       = qr.modules_count   # número de módulos
    quiet   = BORDER * BOX       # píxeles del margen
    eye_tl  = (quiet,                       quiet)
    eye_tr  = (quiet + (n - 7) * BOX,       quiet)
    eye_bl  = (quiet,                       quiet + (n - 7) * BOX)

    recolor_eye(arr, eye_tl[0], eye_tl[1], BOX, RED)
    recolor_eye(arr, eye_tr[0], eye_tr[1], BOX, BLUE)
    recolor_eye(arr, eye_bl[0], eye_bl[1], BOX, GREEN)

    qr_img = Image.fromarray(arr)

    # 3. Logo ASN en el centro
    # ERROR_CORRECT_H permite ~30% ocluido; usamos ~16% para máxima visibilidad segura
    logo_size = int(qr_img.width * 0.22)
    logo      = make_asn_logo(logo_size)
    cx = (qr_img.width  - logo.width)  // 2
    cy = (qr_img.height - logo.height) // 2
    qr_img.paste(logo, (cx, cy), logo)

    # 4. Añadir texto superior e inferior con fondo crema
    try:
        font_title = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 28)
        font_sub   = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 22)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub   = font_title

    PAD    = 28
    LINE_H = 36
    top_h  = PAD + LINE_H + LINE_H + PAD
    bot_h  = PAD + 10 + PAD           # línea tricolor + espacio

    W = qr_img.width
    H = qr_img.height

    canvas = Image.new('RGBA', (W, top_h + H + bot_h), (*CREAM, 255))

    # Texto superior
    d = ImageDraw.Draw(canvas)
    d.text((W//2, PAD + LINE_H//2),       title,    font=font_title, fill=BLACK, anchor='mm')
    d.text((W//2, PAD + LINE_H + LINE_H//2), subtitle, font=font_sub,   fill=(80, 80, 80, 255), anchor='mm')

    # QR
    canvas.paste(qr_img, (0, top_h), qr_img)

    # Línea tricolor inferior
    stripe = 5
    y0 = top_h + H + PAD
    d.rectangle([0,       y0, W//3-1,   y0+stripe-1], fill=(*RED,   255))
    d.rectangle([W//3,    y0, 2*W//3-1, y0+stripe-1], fill=(*BLUE,  255))
    d.rectangle([2*W//3,  y0, W-1,      y0+stripe-1], fill=(*GREEN, 255))

    # Convertir y guardar
    final = canvas.convert('RGB')
    final.save(out_path, 'PNG', optimize=True)
    print(f'  Generado: {fname}  ({final.width}x{final.height}px)')


print('Generando QR del Historial de Actividades...')
for ev in EVENTS:
    generate_qr(ev)
print('Listo.')
