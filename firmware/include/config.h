#pragma once
#include <stdint.h>

// Datos
#define VERSION "0.1.0"

// Tamaño para los buffers
#define LEN_BUFFER 64
#define LEN_SSID 32
#define LEN_PASSWORD 64

// Timeouts del sistema
#define TIMEOUT 10000     // Tiempo de espera para conexión WiFi
#define TIMEOUT_CMD 1000  // Tiempo de espera para recepción de comando por Serial

// Comandos esperados
#define UDP_KEY "START_TX"  // Clave para iniciar transmisión UDP

// Intervalos
#define MS_INTERVAL_SEND 50  // Intervalo de envío de datos en ms

// [ VARIABLES ]═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
// Maquina de estados
typedef enum { DO_CONNECT, CONNECTING, WIFI_ERROR, WAITING_PACKET, SENDING, RECEIVE_CMD, PROCESS_CMD } State;

// Marcas de tiempo
typedef struct {
    unsigned long now, led, print, timeout, send;
} Marks;

// Paquete UDP
typedef struct {
    uint8_t payload[8];  // [uint16_t, uint8_t, uint8_t, uint8_t, uint8_t, uint8_t, uint16_t]
    uint16_t counter;
    uint16_t size;
} UDP_Packet;

// Control PWM
typedef struct {
    uint16_t pwm;
    uint8_t dir : 1;
} PWM_Control;