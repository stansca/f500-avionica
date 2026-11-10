// Pinagem da Aviônica F-500 v2 rev.C-V (com vídeo 2,4 GHz) — ESP32-DevKitC-32E
// Substitui o bloco de pinos do foguete_tx.ino (que era para ESP32-C3 SuperMini).
// Rádio, modulação e pacote ficam IGUAIS -> o tracker_rx continua compatível sem mudar nada.
#pragma once

// ---- LoRa RFM95W (SX1276) — mesmos GPIOs do tracker_rx (VSPI) ----
#define PIN_SCK      18
#define PIN_MISO     19
#define PIN_MOSI     23
#define PIN_NSS       5
#define PIN_DIO0     26
#define PIN_DIO1     39   // só entrada (SENSOR_VN); opcional no RadioLib
#define PIN_RST      14
#define PIN_BUSY     RADIOLIB_NC

// ---- microSD (mesmo barramento SPI, CS próprio) ----
#define PIN_SD_CS    15

// ---- GPS u-blox por cabo (UART2) ----
#define PIN_GPS_RX   16   // recebe do TX do GPS
#define PIN_GPS_TX   17   // vai para o RX do GPS

// ---- I2C: BMP280 (0x76) + conector J4 para IMU ----
#define PIN_SDA      21
#define PIN_SCL      22

// ---- Vídeo ao vivo 2,4 GHz (Pi Zero 2W + ADRV1CRR-BOB/ADRV9361 + SKY85333-11) ----
// O vídeo tem bateria e regulador 5 V/5 A próprios. A aviônica só o controla:
#define PIN_VID_OFF   4   // HIGH = desliga o vídeo (Q4 puxa o EN do regulador p/ GND). LOW/boot = vídeo LIGADO
#define PIN_VID_TX   25   // UART1 TX -> RX da Pi Zero 2W (GPIO15), R20 1k em série
#define PIN_VID_RX   13   // UART1 RX <- TX da Pi Zero 2W (GPIO14), R21 1k em série

// ---- Recuperação ----
#define PIN_PYRO1    32   // HIGH = dispara canal 1 (apogeu)
#define PIN_PYRO2    33   // HIGH = dispara canal 2 (backup)
#define PIN_PYRO1_SENSE 35  // continuidade: ~1,5 V com ignitor + arme ligado; 0 V aberto
#define PIN_PYRO2_SENSE 36  // (SENSOR_VP)

// ---- Bateria 2S: divisor 100k/22k -> fator 5,545 ----
#define PIN_VBAT     34
#define VBAT_DIV     (122.0f / 22.0f)

// ---- Sinalização ----
#define PIN_LED_VERDE     2
#define PIN_LED_VERMELHO 12
#define PIN_BUZZER       27   // HIGH = buzzer ativo liga (via 2N7000)

// Pacote: o campo vbat tem passo de 20 mV (máx 5,1 V). Com 2S, envie a tensão POR CÉLULA
// para não mudar o protocolo do tracker:
//   uint32_t mv = analogReadMilliVolts(PIN_VBAT) * VBAT_DIV;
//   pkt.vbat = (uint8_t)min<uint32_t>(255, (mv / 2) / 20);
// Barramentos:
//   SPI.begin(PIN_SCK, PIN_MISO, PIN_MOSI, PIN_NSS);
//   Wire.begin(PIN_SDA, PIN_SCL);
//   Serial2.begin(baud, SERIAL_8N1, PIN_GPS_RX, PIN_GPS_TX);
//   Serial1.begin(115200, SERIAL_8N1, PIN_VID_RX, PIN_VID_TX);   // status/telemetria p/ overlay na Pi
// Antes de cortar o vídeo (VID_OFF = HIGH), mande "SHUTDOWN" pela UART e espere ~10 s: a Pi precisa desligar
// o Linux para não corromper o cartão SD.
// Segurança: no setup(), coloque PYRO1/PYRO2 em LOW antes de qualquer outra coisa.
