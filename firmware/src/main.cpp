#include <Arduino.h>
#include <EEPROM.h>
#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

#include "config.h"

// Variables
char buffer[LEN_BUFFER], redSSID[LEN_SSID], redPASS[LEN_PASSWORD];
int16_t buff_index;
State state = DO_CONNECT, prevState;
Marks mark;
UDP_Packet udp_packet;
PWM_Control fade = {0, 1};
uint16_t PC_port;
IPAddress PC_ip;

// Objetos
WiFiUDP udp;

/**
 * SETUP
 */
void setup() {
    // Hardware
    pinMode(D1, INPUT_PULLUP);
    pinMode(D5, INPUT_PULLUP);
    pinMode(D6, INPUT_PULLUP);
    pinMode(D7, INPUT_PULLUP);
    pinMode(2, OUTPUT);
    digitalWrite(2, HIGH);

    // Obtengo las credenciales de la EEPROM
    EEPROM.begin(LEN_SSID + LEN_PASSWORD);
    EEPROM.get(0, redSSID);
    EEPROM.get(LEN_SSID, redPASS);
    EEPROM.end();

    delay(1000);

    // Inicializacion y primeras impresiones
    Serial.begin(115200);
    Serial.print(F("\n\n\n--- SISTEMA INICIADO ---\nVersión firmware: "));
    Serial.print(VERSION);
    Serial.print(F("   CHIP ID: "));
    Serial.print(ESP.getChipId());
    Serial.print(F("\nEEPROM > SSID: ["));
    Serial.print(redSSID);
    Serial.print(F("] > PASS: ["));
    Serial.print(redPASS);
    Serial.println(F("]\n------------------------\n"));
}

/**
 * LOOP
 */
void loop() {
    // Update de variablescasa
    mark.now = millis();

    // Lectura de puerto serial
    if (state != RECEIVE_CMD && Serial.available()) {
        prevState = state;
        state = RECEIVE_CMD;
        buff_index = 0;
        memset(buffer, 0, sizeof(buffer));
        mark.timeout = mark.now;
    }

    // Recepción de paquetes UDP
    udp_packet.size = udp.parsePacket();
    if (udp_packet.size) {
        memset(buffer, 0, sizeof(buffer));
        udp.read(buffer, sizeof(buffer));

        // Impresion simple
        Serial.print(F("Paquete recibido: ["));
        Serial.print(buffer);
        Serial.print(F("] de "));
        Serial.print(udp.remoteIP());
        Serial.print(F(":"));
        Serial.println(udp.remotePort());

        if (strcmp(buffer, UDP_KEY) == 0) {
            PC_ip = udp.remoteIP();
            PC_port = udp.remotePort();
            state = SENDING;
            udp_packet.counter = 0;
            digitalWrite(2, LOW);
        }
    }

    // Maquina de estados
    switch (state) {
        case DO_CONNECT:
            WiFi.mode(WIFI_STA);
            WiFi.begin(redSSID, redPASS);
            Serial.print(F("Conectando a la red ["));
            Serial.print(redSSID);
            Serial.print(F("]..."));

            mark.timeout = mark.now;
            udp_packet.counter = 0;
            state = CONNECTING;
            break;

        case CONNECTING:
            if (WiFi.status() != WL_CONNECTED) {
                // Fade
                fade.pwm += (fade.dir) ? 1 : -1;
                if (fade.pwm <= 0) {
                    fade.pwm = 0;
                    fade.dir = 1;
                } else if (fade.pwm >= 255) {
                    fade.pwm = 255;
                    fade.dir = 0;
                }
                analogWrite(2, fade.pwm);
                delay(5);

                // Impresion mas lenta en Serial
                if (mark.now - mark.print > 500) {
                    mark.print = mark.now;
                    Serial.print(F("."));
                }
            } else {
                Serial.print(F("\nConectado a la red ["));
                Serial.print(redSSID);
                Serial.print(F("] Dirección IP: "));
                Serial.println(WiFi.localIP());

                udp.begin(5000);
                state = WAITING_PACKET;
            }

            if (mark.now - mark.timeout > TIMEOUT) {
                Serial.print(F("\nError de conexión WiFi"));
                state = WIFI_ERROR;
            }
            break;

        case WIFI_ERROR:
            delay(35);
            digitalWrite(2, !digitalRead(2));
            break;

        case WAITING_PACKET:
            if (mark.now - mark.led > 350) {
                mark.led = mark.now;
                digitalWrite(2, !digitalRead(2));
            }

            delay(1);
            break;

        case SENDING:
            static uint16_t adc;
            if (WiFi.status() != WL_CONNECTED) {
                Serial.println(F("\nSe perdió la conexión WiFi"));
                state = WIFI_ERROR;
                break;
            }

            if (mark.now - mark.send > MS_INTERVAL_SEND) {
                mark.send = mark.now;

                udp_packet.payload[0] = udp_packet.counter & 0xFF;         // LSB counter
                udp_packet.payload[1] = (udp_packet.counter >> 8) & 0xFF;  // MSB counter
                udp_packet.counter++;

                udp_packet.payload[2] = (GPI >> 5) & 1;   // D1
                udp_packet.payload[3] = (GPI >> 14) & 1;  // D5
                udp_packet.payload[4] = (GPI >> 12) & 1;  // D6
                udp_packet.payload[5] = (GPI >> 13) & 1;  // D7

                adc = analogRead(A0);
                udp_packet.payload[6] = adc & 0xFF;
                udp_packet.payload[7] = (adc >> 8) & 0xFF;

                // Serial.printf("Enviando dato ADC: %u al PC %s:%u\n", adc, PC_ip.toString().c_str(), PC_port);
                udp.beginPacket(PC_ip, PC_port);
                udp.write(udp_packet.payload, sizeof(udp_packet.payload));
                udp.endPacket();
                yield();
            }
            delay(1);
            break;

        case RECEIVE_CMD:
            static char c;

            // Timeout
            if (mark.now - mark.timeout > TIMEOUT_CMD) {
                buffer[buff_index] = '\0';
                state = PROCESS_CMD;
                break;
            }

            // Llega un byte
            if (Serial.available()) {
                mark.timeout = mark.now;
                c = Serial.read();

                if (c == '\n' || c == '\r' || buff_index >= LEN_BUFFER - 1) {
                    buffer[buff_index] = '\0';
                } else {
                    buffer[buff_index++] = c;
                }
                delay(5);
            }
            break;

        case PROCESS_CMD:
            // Trabajo el comando recibido
            Serial.printf("\nComando recibido: [%s]\n", buffer);
            state = prevState;
            if (strncmp(buffer, "SET_SSID:", 9) == 0) {
                strncpy(redSSID, buffer + 9, LEN_SSID);  // Me quedo con el SSID
                redSSID[LEN_SSID - 1] = '\0';

                EEPROM.begin(LEN_SSID + LEN_PASSWORD);
                EEPROM.put(0, redSSID);
                EEPROM.end();

                Serial.print(F("=> Nuevo SSID: ["));
                Serial.print(redSSID);
                Serial.println(F("]"));
            } else if (strncmp(buffer, "SET_PASS:", 9) == 0) {
                strncpy(redPASS, buffer + 9, LEN_PASSWORD);  // Me quedo con el SSID
                redPASS[LEN_PASSWORD - 1] = '\0';

                EEPROM.begin(LEN_SSID + LEN_PASSWORD);
                EEPROM.put(LEN_SSID, redPASS);
                EEPROM.end();

                Serial.print(F("=> Nueva PASS: ["));
                Serial.print(redPASS);
                Serial.println(F("]"));
            } else if (strncmp(buffer, "CONNECT", 7) == 0) {
                state = DO_CONNECT;
            }
            break;
    }
}
