import requests
import sys
import subprocess
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# ========= SELECCIÓN DE IMAGEN ==========
Tk().withdraw()  # Oculta la ventana principal
INPUT_IMAGE = askopenfilename(title="Selecciona una imagen desde tu galería")
if not INPUT_IMAGE:
    print("❌ No se seleccionó ninguna imagen.")
    sys.exit(1)
CARTOON_IMAGE = "cartoon.jpg"

# ========== API CONFIG ================
API_URL = "https://cartoon-yourself.p.rapidapi.com/facebody/api/portrait-animation/portrait-animation"
API_KEY = "ENTER HERE YOUR API KEY"

# 1. Enviar imagen a la API
with open(INPUT_IMAGE, 'rb') as image_file:
    files = {
        'image': image_file,
        "type": (None, "full")
    }
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "cartoon-yourself.p.rapidapi.com"
    }

    response = requests.post(API_URL, headers=headers, files=files)

    print(response.json())

if response.status_code != 200:
    print("Error al llamar a la API:", response.text)
    sys.exit(1)

# 2. Extraer URL del JSON y descargar imagen
result = response.json()
image_url = result.get("data", {}).get("image_url")

if not image_url:
    print("No se encontró el enlace de la imagen en la respuesta")
    sys.exit(1)

# Descargar la imagen
img_data = requests.get(image_url).content
with open(CARTOON_IMAGE, 'wb') as handler:
    handler.write(img_data)

print("✅ Imagen descargada:", CARTOON_IMAGE)

# 3. Llamar a convert.py
subprocess.run(["python3", "convert.py", CARTOON_IMAGE])
subprocess.run(["python3", "preview.py"])
