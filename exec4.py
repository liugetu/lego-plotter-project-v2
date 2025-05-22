import ev3dev.ev3 as ev3
import time

UMBRAL_MOVIMIENTO = 2

# =================== MOTORES & SENSORES ===================
# Motores
motor_x = ev3.LargeMotor('outA')  # Motor para el eje X (horizontal)
motor_y = ev3.LargeMotor('outD')  # Motor para el eje Y (vertical)
motor_lapiz = ev3.MediumMotor('outB')  # Motor para subir/bajar lápiz

# Sensores
sensor_tactil = ev3.TouchSensor('in2')  # Sensor táctil en puerto 2
sensor_color = ev3.ColorSensor('in1')  # Sensor de color en puerto 1

estado_lapiz = 'abajo'

# ====================== FUNCIONES ======================

def esperar_motor(motor):
    """Espera hasta que el motor termine o se supere el timeout (en segundos)."""
    start = time.time()
    while 'running' in motor.state:
        time.sleep(0.01)

def esperar_posicion(motor, target_pos, tol=5, timeout=5):
    """
    Espera hasta que:
      - motor.position esté dentro de tol grados de target_pos, o
      - el motor deje de estar 'running' (terminó por hold/stall), o
      - pase el timeout
    Luego fuerza motor.stop() si fuera necesario.
    """
    start = time.time()
    while True:
        pos = motor.position
        st  = motor.state

        # 1) Alcanzamos la posición dentro de la tolerancia
        if abs(pos - target_pos) <= tol:
            return

        # 2) El motor dejó de correr
        if 'running' not in st:
            return

        # 3) Timeout
        if time.time() - start > timeout:
            print("⚠️ Timeout: el motor tardó demasiado en completar el movimiento.")
            try:
                motor.stop()
            except:
                pass
            return

        time.sleep(0.01)


def move_x(grados, velocidad=400):
    #Mueve el eje X (motor_x) los grados indicados
    print("Moviendo eje X {} grados...".format(grados))
    motor_x.position_sp = motor_x.position + grados
    motor_x.run_to_abs_pos(speed_sp=velocidad, stop_action='hold')
    esperar_motor(motor_x)
    print("Movimiento eje X completo.")

def move_y(grados, velocidad=400):
    #Mueve el eje Y (motor_y) los grados indicados
    print("Moviendo eje Y {} grados...".format(grados))
    motor_y.position_sp = motor_y.position + grados
    motor_y.run_to_abs_pos(speed_sp=velocidad, stop_action='hold')
    esperar_motor(motor_y)
    print("Movimiento eje Y completo.")

def move_xy(dx, dy, velocidad=400):
    """Mueve ambos ejes simultáneamente en diagonal de forma segura."""
    target_x = motor_x.position + dx
    target_y = motor_y.position + dy

    dist = max(abs(dx), abs(dy))
    if dist == 0:
        return

    # velocidades proporcionales
    vel_x = int(velocidad * abs(dx) / dist)
    vel_y = int(velocidad * abs(dy) / dist)

    print("Diagonal → X:",target_x,", Y:",target_y," | velX=",vel_x,", velY=",vel_y)

    # Lanza sólo si velocidad > 0, para evitar estado colgado
    if vel_x > 0:
        motor_x.run_to_abs_pos(position_sp=target_x,
                               speed_sp=vel_x, stop_action='hold')
    if vel_y > 0:
        motor_y.run_to_abs_pos(position_sp=target_y,
                               speed_sp=vel_y, stop_action='hold')

    # Esperamos a que ambos motores dejen de “running”
    esperar_posicion(motor_x, target_x)
    esperar_posicion(motor_y, target_y)

    print("Diagonal completada en", motor_x.position, motor_y.position)

def ok(x, y, x_min=-1600, x_max=0, y_min=0, y_max=2000):
    x_limitado = max(x_min, min(x, x_max))
    y_limitado = max(y_min, min(y, y_max))
    return x_limitado, y_limitado

def subir_lapiz():
    global estado_lapiz
    if estado_lapiz != 'arriba':
        #Sube el lápiz girando el motor hasta que detecte que se ha trabado (llega al tope).
        motor_lapiz.run_forever(speed_sp=200)
        time.sleep(0.2)  # pequeña espera para que empiece a girar

        while abs(motor_lapiz.speed) > 5:
            time.sleep(0.05)

        motor_lapiz.stop()
        estado_lapiz = 'arriba'
    print("¡Lápiz arriba!")

def bajar_lapiz():
    global estado_lapiz
    if estado_lapiz != 'abajo':
        motor_lapiz.position_sp = motor_lapiz.position - 90
        motor_lapiz.run_to_abs_pos(speed_sp=200, stop_action='hold')
        esperar_motor(motor_lapiz)
        estado_lapiz = 'abajo'
    print("¡Lápiz abajo!")

def leer_coordenadas(path):
    cmds = []
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            try:
                cmd, coord = line.split()
                x_str, y_str = coord.split(',')
                cmds.append((cmd, int(x_str), int(y_str)))
            except Exception as e:
                print("⚠️ Error al leer línea '{}': {}".format(line, e))
    return cmds

# =================== INICIALIZACIÓN & CALIBRACIÓN ===================
# Verificación de motores
for m, name in [(motor_x, 'A'), (motor_y, 'D'), (motor_lapiz, 'B')]:
    if not m.connected:
        print("El motor {} no está conectado.".format(name))
    else:
        print("El motor {} está conectado.".format(name))

# Verificar si los sensores están conectados
if not sensor_tactil.connected:
    print("El sensor táctil no está conectado.")
else:
    print("El sensor táctil está conectado.")

if not sensor_color.connected:
    print("El sensor de color no está conectado.")
else:
    print("El sensor de color está conectado.")

subir_lapiz()

# Paso 1: Girar motor A (eje X) hasta que el sensor táctil sea presionado
print("🔄 Calibrando X: girando hasta pulsar sensor táctil...")
while not sensor_tactil.is_pressed:
    motor_x.run_forever(speed_sp=400)  # Gira el motor hacia adelante a velocidad 400

# Cuando el sensor táctil se presiona, detener el motor
motor_x.stop()
print("📍 Sensor táctil pulsado → origen X establecido")

# Paso 2.1: Mover el motor Y (eje Y) inicialmente hasta que se deje de detectar la hoja
print("🔄 Introduciendo hoja en Y…")
sensor_color.mode = 'COL-REFLECT'  # Activamos el modo de reflexión de color, que nos da un valor de 0 (negro) a 100 (blanco)
# Mueve hasta que detecte blanco→negro→blanco
while sensor_color.reflected_light_intensity < 30:  # Mover hasta que se detecte la hoja (valor alto)
    motor_y.run_forever(speed_sp=400)  # Mueve el motor hacia atrás (sumando) a velocidad 400

# Paso 2.2: Mover el motor Y (eje Y) inicialmente hasta que se deje de detectar la hoja
while sensor_color.reflected_light_intensity > 30:  # Mover hasta que se deje de detectar la hoja (valor bajo)
    motor_y.run_forever(speed_sp=400)  # Mueve el motor hacia atrás (sumando) a velocidad 400

# Detener motor Y cuando ya no se detecte la hoja (cuando se detecta blanco)
motor_y.stop()

print("Posicionando la hoja")
move_y(-1800)
print("📍 Hoja pasada completamente → origen Y establecido")

# Tras calibrar:
x_origin = motor_x.position
y_origin = motor_y.position

# =================== DIBUJAR FIGURA ===================

cmds = leer_coordenadas('coordenadas.txt')

last_x = 0  # relativo
last_y = 0
for cmd, x, y in cmds:
    x, y = ok(x, y)         # que no salga del rango
    print(" - posicion {}, {}".format(x, y))

    dx = x - last_x
    dy = y - last_y

    if cmd == 'M':
        subir_lapiz()
    elif cmd == 'L':
        bajar_lapiz()
    else:
        print("❗ Comando desconocido:", cmd)
        continue
    
    # Ejecutamos el desplazamiento relativo
    if abs(dx) >= UMBRAL_MOVIMIENTO or abs(dy) >= UMBRAL_MOVIMIENTO:
        move_xy(dx, dy)

    # 🔁 ACTUALIZAR posiciones reales desde los motores
    last_x = motor_x.position - x_origin
    last_y = motor_y.position - y_origin

# Al terminar, levantamos el lápiz
subir_lapiz()
move_y(-500 - last_y) # sacar hoja
print("Dibujo completado")