#!/usr/bin/env python3
import cv2
import sys

# ============ CONFIG ============

if len(sys.argv) < 2:
    print("Uso: python3 convert.py imagen.jpg", file=sys.stderr)
    sys.exit(1)

IMAGE_PATH  = sys.argv[1]
OUTPUT_PATH = 'coordenadas.txt'
RESIZE_W    = 300  # ancho para procesar

# Rango físico
X_MIN, X_MAX = -1400, -200
Y_MIN, Y_MAX =  200, 1800

# ============ CARGA & PREPROCESADO ============

img = cv2.imread(IMAGE_PATH, cv2.IMREAD_GRAYSCALE)
if img is None:
    print(f"ERROR: no puedo cargar '{IMAGE_PATH}'", file=sys.stderr)
    sys.exit(1)

h0, w0 = img.shape
scale_px = RESIZE_W / float(w0)
w = RESIZE_W
h = int(h0 * scale_px)
img = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)

# Suavizado para evitar ruido
blurred = cv2.GaussianBlur(img, (5, 5), 0)

# Detección de bordes más fina que threshold
edges = cv2.Canny(blurred, 50, 150)

# ============ CONTORNOS DETALLADOS ============

contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

# Filtrado: quitar contornos pequeños
contours = [c for c in contours if len(c) > 10]

# ============ ESCALA Y CENTRADO ============

span_x = X_MAX - X_MIN
span_y = Y_MAX - Y_MIN
scale = min(span_x / float(w), span_y / float(h))
margin_x = (span_x - w * scale) / 2.0
margin_y = (span_y - h * scale) / 2.0

def map_point(px, py):
    px = (w - 1) - px
    x = X_MIN + margin_x + px * scale
    y = Y_MIN + margin_y + (h - 1 - py) * scale
    x = max(X_MIN, min(X_MAX, x))
    y = max(Y_MIN, min(Y_MAX, y))
    return int(round(x)), int(round(y))

# ============ EXPORTACIÓN ============

with open(OUTPUT_PATH, 'w') as f:
    for cnt in contours:
        if len(cnt) < 2:
            continue
        first = True
        for pt in cnt:
            px, py = pt[0]
            x, y = map_point(px, py)
            if first:
                f.write(f"M {x},{y}\n")
                first = False
            else:
                f.write(f"L {x},{y}\n")
        f.write("\n")

print(f"→ Coordenadas generadas en '{OUTPUT_PATH}'")
