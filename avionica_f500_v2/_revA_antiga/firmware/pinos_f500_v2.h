// Pinagem da Aviônica F-500 v2 (ESP32-DevKitC-32E / ESP32-WROOM clássico)
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

// ---- Câmera / VTX digital ----
#define PIN_CAM_EN    4   // HIGH = liga VBAT da câmera (P-MOSFET Q3)
#define PIN_CAM_TX   25   // UART1 TX -> RX da câmera (MSP/OSD)
#define PIN_CAM_RX   13   // UART1 RX <- TX da câmera

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
//   Serial1.begin(115200, SERIAL_8N1, PIN_CAM_RX, PIN_CAM_TX);
// Segurança: no setup(), coloque PYRO1/PYRO2 em LOW antes de qualquer outra coisa.
