import ev3dev.ev3 as ev3
import time

# =================== MOTORES & SENSORES ===================
# Motores
motor_x = ev3.LargeMotor('outA')  # Motor para el eje X (horizontal)
motor_y = ev3.LargeMotor('outD')  # Motor para el eje Y (vertical)
motor_lapiz = ev3.MediumMotor('outB')  # Motor para subir/bajar lápiz

# Sensores
sensor_tactil = ev3.TouchSensor('in2')  # Sensor táctil en puerto 2
sensor_color = ev3.ColorSensor('in1')  # Sensor de color en puerto 1

# ====================== FUNCIONES ======================
def esperar_motor(motor):
    #Espera hasta que el motor termine de moverse
    while 'running' in motor.state:
        time.sleep(0.01)

def move_x(grados, velocidad=400):
    #Mueve el eje X (motor_x) los grados indicados
    print("Moviendo eje X {} grados...").format(grados)
    motor_x.position_sp = motor_x.position + grados
    motor_x.run_to_abs_pos(speed_sp=velocidad, stop_action='hold')
    esperar_motor(motor_x)
    print("Movimiento eje X completo.")

def move_y(grados, velocidad=400):
    #Mueve el eje Y (motor_y) los grados indicados
    print("Moviendo eje Y {} grados...").format(grados)
    motor_y.position_sp = motor_y.position + grados
    motor_y.run_to_abs_pos(speed_sp=velocidad, stop_action='hold')
    esperar_motor(motor_y)
    print("Movimiento eje Y completo.")

def subir_lapiz():
    #Sube el lápiz girando el motor hasta que detecte que se ha trabado (llega al tope).
    motor_lapiz.run_forever(speed_sp=200)
    time.sleep(0.2)  # pequeña espera para que empiece a girar

    while abs(motor_lapiz.speed) > 5:
        time.sleep(0.05)

    motor_lapiz.stop()
    print("¡Lápiz arriba!")

def bajar_lapiz():
    motor_lapiz.position_sp = motor_lapiz.position - 90
    motor_lapiz.run_to_abs_pos(speed_sp=200, stop_action='hold')
    esperar_motor(motor_lapiz)
    print("¡Lápiz abajo!")

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

# Detener motor
motor_y.stop()
print("STOPPED")