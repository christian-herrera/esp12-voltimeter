import socket
import time
import struct
import sys
from datetime import datetime
import argparse

# ───── Argumentos ─────
parser = argparse.ArgumentParser(description="Voltímetro UDP desde ESP12")
parser.add_argument(
    "--vref",
    type=float,
    default=3.3,
    help="Voltaje de referencia (ej: 3.3 o 1.0)"
)
parser.add_argument(
    "--bits_adc",
    type=int,
    default=10,
    help="Cantidad de bits del ADC (ej: 10)"
)
parser.add_argument(
    "--factor_div",
    type=float,
    default=1.0,
    help="Factor del divisor de tensión (R2/(R1+R2))"
)
args = parser.parse_args()
VREF = args.vref
BITS_ADC = args.bits_adc
FACTOR_DIV = 1/args.factor_div

# ───── Constantes ─────
TIMEOUT = 0.4           # Segundos
NUM_MUESTRAS_ADC = 5    # Numero de muestras para promediar el ADC




def drawMenu():
    """Dibujar menú de opciones"""
    sys.stdout.write(f"\033[8;{24};{71}t")
    print("\033[2J\033[H\033[?25l", end="")  # Limpiar, home, ocultar cursor
    menu = """
 ╔════════════════════════════════════════════════════════════════════╗
 ║                                                                    ║
 ║               ███████╗███████╗██████╗  ██╗██████╗                  ║
 ║               ██╔════╝██╔════╝██╔══██╗███║╚════██╗                 ║
 ║               █████╗  ███████╗██████╔╝╚██║ █████╔╝                 ║
 ║               ██╔══╝  ╚════██║██╔═══╝  ██║██╔═══╝                  ║
 ║               ███████╗███████║██║      ██║███████╗                 ║
 ║               ╚══════╝╚══════╝╚═╝      ╚═╝╚══════╝                 ║
 ║   ██  ██  ▄▄▄  ▄▄   ▄▄▄▄▄▄ ▄▄ ▄▄   ▄▄ ▄▄▄▄▄ ▄▄▄▄▄▄ ▄▄▄▄▄ ▄▄▄▄      ║
 ║   ██▄▄██ ██▀██ ██     ██   ██ ██▀▄▀██ ██▄▄    ██   ██▄▄  ██▄█▄     ║
 ║    ▀██▀  ▀███▀ ██▄▄▄  ██   ██ ██   ██ ██▄▄▄   ██   ██▄▄▄ ██ ██     ║
 ║                                                                    ║
 ║               ░▒▓▆▅▃▂▁By Christian Herrera▁▂▃▅▆▓▒░                 ║
 ║                                                                    ║
 ║  Opciones:                                                         ║
 ║   1. Iniciar recepción UDP                                         ║
 ║   2. Salir                                                         ║
 ╚════════════════════════════════════════════════════════════════════╝
"""
    print(menu, end="", flush=True)


def drawGUI():
    """Dibujar interfaz gráfica completa"""
    sys.stdout.write(f"\033[8;{29};{56}t")
    print("\033[2J\033[H\033[?25l", end="")  # Limpiar, home, ocultar cursor
    
    gui = """
 ╔═════════════════════════════════════════════════════╗
 ║                  VOLTÍMETRO ESP8266                 ║
 ╠═════════════════════════════════════════════════════╣
 ║                                                     ║
 ║         🕒 00:00:00          📅 00/00/0000          ║
 ║                                                     ║
 ║       ╭───────────── VOLTAJE ─────────────╮         ║
 ║       │                                   │         ║
 ║       │              0.000 V              │         ║
 ║       │                                   │         ║
 ║       │                                   │         ║
 ║       ╰───────────────────────────────────╯         ║
 ║                                                     ║
 ║                                                     ║
 ║     ╭─────────── PINES DIGITALES ───────────╮       ║
 ║     │  D1 ┌─┐  D5 ┌─┐  D6 ┌─┐  D7 ┌─┐       │       ║
 ║     │     │ │     │ │     │ │     │ │       │       ║
 ║     │     └─┘     └─┘     └─┘     └─┘       │       ║
 ║     │     OFF     OFF     OFF     OFF       │       ║
 ║     ╰───────────────────────────────────────╯       ║
 ║                                                     ║
 ║  ╭───────────────── ESTADÍSTICAS ─────────────────╮ ║
 ║  │  📦 Paquete: #             🔄 FPS:             │ ║
 ║  │  ❌ Perdidos:              🕐 Retardo:         │ ║
 ║  ╰────────────────────────────────────────────────╯ ║
 ╚═════════════════════════════════════════════════════╝
 - Presione Ctrl+C para detener la recepción de datos -
"""
    print(gui, end="", flush=True)



def drawBar(value, max_value, width=33):
    line_value = 10
    line_simbol = 12

    if value < 0:
        value = 0
    if value > max_value:
        value = max_value

    filled = int((value / max_value) * width)
    level = "█" * filled + "░" * (width - filled)

    print(f"\033[{line_value};25H{value:6.3f} V", end="")
    print(f"\033[{line_simbol};12H{level}", end="")



def drawPins(D1, D5, D6, D7):
    """Dibujar estado de pines digitales D1, D5, D6, D7"""
    line_simbol = 18
    line_text = 20

    for i, state in enumerate([D1, D5, D6, D7], start=1):
        if(state == 1):
            print(f"\033[{line_simbol};{15+(i-1)*8}H█", end="")
            print(f"\033[{line_text};{14+(i-1)*8}HON ", end="")
        else:
            print(f"\033[{line_simbol};{15+(i-1)*8}H ", end="")
            print(f"\033[{line_text};{14+(i-1)*8}HOFF", end="")



def drawStats(packet_count, seconds_diff, perdidos, offline = False):
    """Dibujar estadísticas de paquetes"""
    line_paquet = 24
    line_perdidos = 25
    line_offline = 3

    retardo = int(seconds_diff * 1000)  # ms
    if(retardo > TIMEOUT * 1000):
        offline = True
    if(seconds_diff > 0):
        fps = 1 / seconds_diff

    if(offline):
        print(f"\033[{line_paquet};21H------    ", end="") # Paquete
        print(f"\033[{line_paquet};42H--.- Hz   ", end="")  # FPS
        print(f"\033[{line_perdidos};21HInf      ", end="")  # Perdidos
        print(f"\033[{line_perdidos};46H>{(TIMEOUT * 1000):.0f} ms ", end="")  # Retardo
        print(f"\033[{line_offline};5H🔴 🔴 🔴 🔴 🔴", end="")  # Offline
        print(f"\033[{line_offline};40H🔴 🔴 🔴 🔴 🔴", end="")  # Offline
    else:
        print(f"\033[{line_paquet};21H{packet_count:06d}    ", end="") # Paquete
        print(f"\033[{line_paquet};42H{fps:.2f} Hz   ", end="")  # FPS
        print(f"\033[{line_perdidos};21H{perdidos}      ", end="")  # Perdidos
        print(f"\033[{line_perdidos};46H{retardo} ms  ", end="")  # Retardo
        print(f"\033[3;2H║                  VOLTÍMETRO ESP8266                 ║", end="")


def drawTimeDate():
    """Dibujar hora y fecha actuales"""
    line = 6
    print(f"\033[{line};15H{datetime.now().strftime('%H:%M:%S')}", end="")
    print(f"\033[{line};36H{datetime.now().strftime('%d/%m/%Y')}", end="")




def loopReceiver():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(("0.0.0.0", 5000))
    sock.settimeout(TIMEOUT)  # Timeout de 200ms
    sock.sendto(b"START_TX", ("255.255.255.255", 5000))

    prevPaquet = -1
    prevMark = -1
    perdidos = 0
    adc_promedio = []
    while True:
        try:
            # Espero a recibir por UDP
            data, addr = sock.recvfrom(1024)

            # Counter
            newIndex = int.from_bytes(data[0:2], 'little')  # counter
            perdidos = (newIndex - prevPaquet - 1)
            newMark = time.time()
            
            # Pines digitales
            D1 = data[2]
            D5 = data[3]
            D6 = data[4]
            D7 = data[5]

            # ADC
            adc = int.from_bytes(data[6:8], 'little')
            adc_promedio.append(adc)
            if len(adc_promedio) > NUM_MUESTRAS_ADC:   # Tamaño fijo
                adc_promedio.pop(0)
            adc = sum(adc_promedio) / len(adc_promedio) # Promedio de la ventana
            volts = adc * VREF / (2**BITS_ADC) * FACTOR_DIV 
            
            # Impresiones
            drawTimeDate()
            drawBar(volts, VREF*FACTOR_DIV)
            drawPins(D1, D5, D6, D7)
            drawStats(newIndex, newMark - prevMark, perdidos)
            sys.stdout.flush()
            
            # Actualizar previos
            prevPaquet = newIndex
            prevMark = newMark
            time.sleep(0.001)

        except socket.timeout:
            drawTimeDate()
            drawStats(0, 0, 0, True)
            sys.stdout.flush()
            continue

        except KeyboardInterrupt:
            break




# ───── MAIN ─────
while True:
    try:
        drawMenu();
        resp = input("\nSeleccione una opción: ")
        if(resp == "1"):
            drawGUI()
            loopReceiver()
        elif(resp == "2"):
            print("\033[?25h")  # Mostrar cursor
            sys.exit(0)

    except KeyboardInterrupt:
        print("\033[?25h")  # Mostrar cursor
        sys.exit(0)
    

    


