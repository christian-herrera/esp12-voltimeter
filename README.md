<h1 align="center">ESP12 - Voltímetro<br/><br/>
<div align="center">
<img src="docs/python.svg" style="max-width: 100%" width=150><br/><br/>

![GitHub License](https://img.shields.io/badge/LICENSE-MIT-green?style=for-the-badge)
![Static Badge](https://img.shields.io/badge/version-v0.1.0-blue?style=for-the-badge)


</div></h1>



# Descripción

El presente proyecto permite utilizar un microcontrolador ESP12F (ESP8266) con el fin de poder transmitir por UDP los valores de 4 canales digitales y 1 canal analogico.

La idea es simple, disponer de una especie de voltimetro para las mediciones simples en el desarrollo continuo de proyectos. El firmware permite enviar cada $50\;ms$ los valores mencionados.


# Características

-   **Módulo como Estación**: El ESP12 se debe conectar a la misma red en la que se dispone el dispositivo donde se ejecutará la App de python.

-   **Comunicaón sin ACK**: La idea es obtner un valor aproximado de la tension en el pin del ADC, con lo cual se utiliza UDP para enviar lo mas rápido posible.

-   **Aplicación**: La aplicación es simplemente un script en Python que muestra en la misma consola una especie de interfaz con los valores.

-   **Comunicación Serial**: Dado que es necesario conectarlo por WiFi a una red conocida, se permite la configuración por medio de la comunicación serial.


<br><br>

# Funcionamiento
## Configuración de la Red
Para establecer las credenciales de red, se utiliza la comunicación serial usando la velocidad de $115200$. Luego se envian los siguientes datos:

```
SET_SSID:MiRedWiFI
SET_PASS:ClaveDeLaRed
CONNECT
```

<br>

## Ejecución de la App
Como se mencionó, la app corre con Python con lo cual se puede ejecutar simplemente con:

```bash
python app.py
```

Adicionalmente, se pueden agregar algunos argumentos. Estos son:

|  *Argumento*   | *Descripción*                                                                                                                                                                                                                                           |
| :------------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|    `--vref`    | El ESP8266 tiene su tension de referencia fija de $3.3\;V$. Ante futuros cambios en el microcontrolador se adiciona esta variable para flexibilizar la app.                                                                                             |
|    `--bits`    | El ESP8266 envía el valor en crudo del ADC, es decir, los valores de $0 \sim 1023$. Esto es así dado que el ADC del microcontrolador es de *10* bits, con lo cual éste es el valor que espera recibir como argumento la app. (Por defecto se usa `10`). |
| `--factor_div` | Este valor es del tipo `float` y corresponde al término $\Large \cfrac{R_2}{R_1+R_2}$ de la expresión del divisor resistivo.<br>Permite tener el valor de tensión directo en la entrada del divisor resistivo, sin necesidad de realizar cuentas para transladar la tension de la salida del divisor a la entrada. |


<br>

## Funcionamiento
La app muestra la siguiente estructura en la ejecución:

```bash
 ╔═════════════════════════════════════════════════════╗
 ║                  VOLTÍMETRO ESP8266                 ║
 ╠═════════════════════════════════════════════════════╣
 ║                                                     ║
 ║         🕒 19:42:10          📅 02/01/2026          ║
 ║                                                     ║
 ║       ╭───────────── VOLTAJE ─────────────╮         ║
 ║       │                                   │         ║
 ║       │               2.340 V             │         ║
 ║       │                                   │         ║
 ║       │ ███████████████████████░░░░░░░░░░ │         ║
 ║       ╰───────────────────────────────────╯         ║
 ║                                                     ║
 ║                                                     ║
 ║     ╭─────────── PINES DIGITALES ───────────╮       ║
 ║     │  D1 ┌─┐  D5 ┌─┐  D6 ┌─┐  D7 ┌─┐       │       ║
 ║     │     │█│     │█│     │█│     │█│       │       ║
 ║     │     └─┘     └─┘     └─┘     └─┘       │       ║
 ║     │     ON      ON      ON      ON        │       ║
 ║     ╰───────────────────────────────────────╯       ║
 ║                                                     ║
 ║  ╭───────────────── ESTADÍSTICAS ─────────────────╮ ║
 ║  │  📦 Paquete: #001217       🔄 FPS: 19.67 Hz    │ ║
 ║  │  ❌ Perdidos: 0            🕐 Retardo: 50 ms   │ ║
 ║  ╰────────────────────────────────────────────────╯ ║
 ╚═════════════════════════════════════════════════════╝
```
Algunas caracteristicas de la disposición planteada son:

- Permite visualizar el fondo de escala del ADC, tanto si se utiliza con o sin divisor resistivo.
- Tensión con un promedio movil de 5 muestras (configurable en el firmware).
- El ESP12 envía el número de paquete en su payload, con esto se detectan paquetes perdidos.
- Los FPS (y el retardo) se obtienen de tomar la marca de tiempo de cada paquete que llega.
- Ante un tiempo de $400\;ms$ sin paquetes, se visualiza una alerta en la disposicion.


<br>

## 🐛 Reportar Bugs | 💡 Sugerir Mejoras | ❓ Preguntar

¡Tu ayuda es **crucial** para mejorar este sistema! Usa algunas de las opciones siguientes:

[![](https://img.shields.io/badge/%F0%9F%90%9B_Reportar_Bug-E4405F?style=for-the-badge)](https://github.com/christian-herrera/esp12-voltimeter/issues/new?template=reporte-de-bug.md)
[![](https://img.shields.io/badge/%F0%9F%92%A1_Sugerir_Feature-4285F4?style=for-the-badge)](https://github.com/christian-herrera/esp12-voltimeter/issues/new?template=sugerir-features.md)
[![](https://img.shields.io/badge/%E2%9D%94_Hacer_pregunta-FF5230?style=for-the-badge)](https://github.com/christian-herrera/esp12-voltimeter/discussions/new?category=q-a)

