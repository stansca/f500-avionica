/*
 * teste_placa_f500v2.ino — Teste de bancada da Aviônica F-500 v2 (ESP32-DevKitC)
 *
 * Menu pela Serial (115200 baud). Cada teste diz OK / FALHOU e o que conferir.
 * Funciona também com o DevKit sozinho: os testes de periféricos ausentes só acusam falha.
 *
 * Bibliotecas: Adafruit BMP280 (+ Adafruit Unified Sensor, BusIO). SD, SPI e Wire vêm com o core.
 * O rádio é testado com registradores do SX1276 direto (não precisa de RadioLib).
 * Placa na IDE: "ESP32 Dev Module".
 *
 * SEGURANÇA: os pinos PYRO ficam em LOW desde a 1ª linha do setup(). O teste de disparo
 * (opção 'p') só roda se você digitar SIM, e deve ser feito com a CHAVE DE ARME ABERTA
 * ou com um LED/lâmpada no lugar do ignitor. NUNCA com ignitor ligado a uma carga.
 */
#include <Arduino.h>
#include <SPI.h>
#include <Wire.h>
#include <SD.h>
#include <Adafruit_BMP280.h>

// ---------------- Pinos da F-500 v2 (iguais a pinos_f500_v2.h) ----------------
#define PIN_SCK       18
#define PIN_MISO      19
#define PIN_MOSI      23
#define PIN_NSS        5
#define PIN_DIO0      26
#define PIN_DIO1      39
#define PIN_RST       14
#define PIN_SD_CS     15
#define PIN_GPS_RX    16
#define PIN_GPS_TX    17
#define PIN_SDA       21
#define PIN_SCL       22
#define PIN_PYRO1     32
#define PIN_PYRO2     33
#define PIN_PYRO1_SENSE 35
#define PIN_PYRO2_SENSE 36
#define PIN_VBAT      34
#define VBAT_DIV      (122.0f / 22.0f)
#define PIN_LED_VERDE  2
#define PIN_LED_VERM  12
#define PIN_BUZZER    27

// ---------------- Rádio (mesmos parâmetros do tracker_rx) ----------------
#define LORA_FREQ_HZ  917000000UL
#define LORA_PWR_DBM  14

Adafruit_BMP280 bmp(&Wire);
bool bmpOk = false;
SPISettings loraSpi(1000000, MSBFIRST, SPI_MODE0);

// ======================= utilidades =======================
void linha() { Serial.println(F("------------------------------------------------")); }
void resultado(const char *nome, bool ok, const char *dica = "") {
  Serial.printf("[%s] %s", ok ? " OK " : "FALHOU", nome);
  if (!ok && dica[0]) Serial.printf("  -> %s", dica);
  Serial.println();
}
void beep(int ms) { digitalWrite(PIN_BUZZER, HIGH); delay(ms); digitalWrite(PIN_BUZZER, LOW); }
String lerLinha(uint32_t timeoutMs) {
  String s; uint32_t t0 = millis();
  while (millis() - t0 < timeoutMs) {
    while (Serial.available()) {
      char c = Serial.read();
      if (c == '\n' || c == '\r') { if (s.length()) return s; }
      else s += c;
    }
    delay(5);
  }
  return s;
}

// ======================= SX1276 direto =======================
uint8_t loraRead(uint8_t reg) {
  SPI.beginTransaction(loraSpi); digitalWrite(PIN_NSS, LOW);
  SPI.transfer(reg & 0x7F); uint8_t v = SPI.transfer(0);
  digitalWrite(PIN_NSS, HIGH); SPI.endTransaction(); return v;
}
void loraWrite(uint8_t reg, uint8_t v) {
  SPI.beginTransaction(loraSpi); digitalWrite(PIN_NSS, LOW);
  SPI.transfer(reg | 0x80); SPI.transfer(v);
  digitalWrite(PIN_NSS, HIGH); SPI.endTransaction();
}
void loraWriteBuf(uint8_t reg, const uint8_t *buf, size_t n) {
  SPI.beginTransaction(loraSpi); digitalWrite(PIN_NSS, LOW);
  SPI.transfer(reg | 0x80); for (size_t i = 0; i < n; i++) SPI.transfer(buf[i]);
  digitalWrite(PIN_NSS, HIGH); SPI.endTransaction();
}
void loraReset() { digitalWrite(PIN_RST, LOW); delay(2); digitalWrite(PIN_RST, HIGH); delay(10); }

bool loraConfigurar() {
  loraReset();
  if (loraRead(0x42) != 0x12) return false;            // RegVersion do SX1276
  loraWrite(0x01, 0x80);                                 // LoRa + sleep
  delay(5);
  loraWrite(0x01, 0x81);                                 // LoRa + standby
  uint64_t frf = ((uint64_t)LORA_FREQ_HZ << 19) / 32000000ULL;
  loraWrite(0x06, (frf >> 16) & 0xFF); loraWrite(0x07, (frf >> 8) & 0xFF); loraWrite(0x08, frf & 0xFF);
  loraWrite(0x09, 0x80 | (LORA_PWR_DBM - 2));            // PA_BOOST, 14 dBm
  loraWrite(0x0B, 0x2B);                                 // OCP 100 mA
  loraWrite(0x1D, (0x8 << 4) | (0x1 << 1));              // BW 250 kHz, CR 4/5, header explícito
  loraWrite(0x1E, (7 << 4) | 0x04);                      // SF7, CRC ligado
  loraWrite(0x26, 0x04);                                 // AGC automático
  loraWrite(0x20, 0x00); loraWrite(0x21, 0x08);          // preâmbulo 8
  loraWrite(0x39, 0x12);                                 // sync word padrão (igual RadioLib/tracker)
  loraWrite(0x0E, 0x00);                                 // FIFO TX base
  loraWrite(0x40, 0x00);                                 // DIO0 = TxDone
  return true;
}

// Pacote idêntico ao do foguete_tx / tracker_rx (26 bytes, magic 0xA5)
struct __attribute__((packed)) Packet {
  uint8_t magic, flags; uint16_t seq;
  int32_t lat, lon, altMsl;
  int16_t baroRel, vN, vE, vD;
  uint8_t sats, vbat;
};
static_assert(sizeof(Packet) == 26, "pacote deve ter 26 bytes");

bool loraEnviar(const uint8_t *buf, uint8_t n, bool &dio0Ok) {
  loraWrite(0x01, 0x81);
  loraWrite(0x0D, 0x00);                                 // ponteiro da FIFO
  loraWriteBuf(0x00, buf, n);
  loraWrite(0x22, n);                                    // tamanho
  loraWrite(0x12, 0xFF);                                 // limpa IRQs
  loraWrite(0x01, 0x83);                                 // TX
  uint32_t t0 = millis(); dio0Ok = false;
  while (millis() - t0 < 300) {
    if (digitalRead(PIN_DIO0)) dio0Ok = true;
    if (loraRead(0x12) & 0x08) { loraWrite(0x12, 0xFF); return true; }   // TxDone
    delay(1);
  }
  return false;
}

// ======================= testes =======================
void testeChip() {
  linha(); Serial.println(F("1) ESP32"));
  Serial.printf("Modelo: %s rev %d, %d nucleo(s), %d MHz\n", ESP.getChipModel(), ESP.getChipRevision(), ESP.getChipCores(), ESP.getCpuFreqMHz());
  Serial.printf("Flash: %u MB | RAM livre: %u kB | MAC: %012llX\n", ESP.getFlashChipSize() / 1048576, ESP.getFreeHeap() / 1024, ESP.getEfuseMac());
  resultado("ESP32 respondendo", true);
}

void testeSinalizacao() {
  linha(); Serial.println(F("2) LEDs e buzzer (olhe e escute)"));
  for (int i = 0; i < 3; i++) {
    digitalWrite(PIN_LED_VERDE, HIGH); delay(200); digitalWrite(PIN_LED_VERDE, LOW);
    digitalWrite(PIN_LED_VERM, HIGH); delay(200); digitalWrite(PIN_LED_VERM, LOW);
  }
  beep(150); delay(100); beep(150);
  Serial.println(F("Verde e vermelho piscaram 3x e o buzzer deu 2 bipes? (confira visualmente)"));
}

void testeI2C() {
  linha(); Serial.println(F("3) Varredura I2C (SDA 21, SCL 22)"));
  int n = 0; bool achouBmp = false, achouImu = false;
  for (uint8_t a = 1; a < 127; a++) {
    Wire.beginTransmission(a);
    if (Wire.endTransmission() == 0) {
      const char *nome = (a == 0x76 || a == 0x77) ? "BMP280" : (a == 0x68 || a == 0x69) ? "IMU (MPU/ICM/BMI)" : "?";
      Serial.printf("  0x%02X  %s\n", a, nome); n++;
      if (a == 0x76 || a == 0x77) achouBmp = true;
      if (a == 0x68 || a == 0x69) achouImu = true;
    }
  }
  resultado("algum dispositivo no I2C", n > 0, "confira solda do BMP280 e o conector J5");
  resultado("BMP280 em 0x76/0x77", achouBmp, "módulo BMP280 (U4) ausente ou mal soldado");
  Serial.printf("IMU no J5: %s\n", achouImu ? "encontrada" : "não encontrada (opcional, mas recomendada para voo)");
}

void testeBMP() {
  linha(); Serial.println(F("4) BMP280"));
  bmpOk = bmp.begin(0x76) || bmp.begin(0x77);
  resultado("BMP280 iniciou", bmpOk, "ver teste 3");
  if (!bmpOk) return;
  float p = bmp.readPressure(), t = bmp.readTemperature();
  Serial.printf("Pressão %.1f hPa | Temperatura %.2f °C | Altitude ~%.1f m\n", p / 100.0, t, bmp.readAltitude(1013.25));
  resultado("leitura plausível (800–1100 hPa, -10–60 °C)", p > 80000 && p < 110000 && t > -10 && t < 60, "sensor com defeito?");
}

void testeGPS() {
  linha(); Serial.println(F("5) GPS no J6 (UART2: RX 16, TX 17) — antena perto da janela"));
  const uint32_t bauds[] = {9600, 38400};
  bool ok = false;
  for (uint32_t b : bauds) {
    Serial2.begin(b, SERIAL_8N1, PIN_GPS_RX, PIN_GPS_TX);
    uint32_t t0 = millis(); int bytes = 0, nmea = 0, ubx = 0; char ant = 0; String frase;
    while (millis() - t0 < 2500) {
      while (Serial2.available()) {
        char c = Serial2.read(); bytes++;
        if (ant == '$' && c == 'G') nmea++;
        if ((uint8_t)ant == 0xB5 && (uint8_t)c == 0x62) ubx++;
        if (nmea && frase.length() < 80 && c != '\r') { if (c == '\n') { if (frase.startsWith("$G")) break; frase = ""; } else frase += c; }
        ant = c;
      }
    }
    Serial.printf("  %6lu baud: %d bytes, %d frases NMEA, %d pacotes UBX\n", (unsigned long)b, bytes, nmea, ubx);
    if (frase.length()) Serial.printf("  exemplo: %s\n", frase.c_str());
    Serial2.end();
    if (nmea > 0 || ubx > 0) { ok = true; break; }
  }
  resultado("GPS falando na serial", ok, "confira J6 (5V, GND, TX do GPS no pino 3, RX no pino 4) e se não está invertido");
  Serial.println(F("  (fix demora 30 s a alguns minutos com céu aberto; aqui só testamos a comunicação)"));
}

void testeLoRa() {
  linha(); Serial.println(F("6) Rádio RFM95W (SX1276)"));
  digitalWrite(PIN_SD_CS, HIGH);
  uint8_t ver = (loraReset(), loraRead(0x42));
  Serial.printf("RegVersion = 0x%02X (esperado 0x12)\n", ver);
  bool ok = loraConfigurar();
  resultado("SX1276 respondendo no SPI", ok, "confira solda do RFM95W, NSS=5, RST=14, SCK/MISO/MOSI 18/19/23");
  if (!ok) return;
  Serial.println(F("Enviando 10 pacotes no formato do tracker (917 MHz, SF7, BW250). Ligue o tracker_rx para ver o seq subir."));
  int okTx = 0; bool dio0 = false;
  for (uint16_t i = 0; i < 10; i++) {
    Packet pk = {}; pk.magic = 0xA5; pk.flags = bmpOk ? 0x02 : 0; pk.seq = i; pk.sats = 0;
    if (bmpOk) pk.baroRel = 0;
    float vcell = analogReadMilliVolts(PIN_VBAT) * VBAT_DIV / 2.0f;     // por célula (2S)
    pk.vbat = (uint8_t)min(255.0f, vcell / 20.0f);
    bool d = false;
    if (loraEnviar((uint8_t *)&pk, sizeof(pk), d)) okTx++;
    dio0 |= d;
    delay(200);
  }
  Serial.printf("TxDone em %d/10 pacotes\n", okTx);
  resultado("transmissão (TxDone)", okTx == 10, "antena no SMA? alimentação 3V3 do módulo?");
  resultado("pino DIO0 (26) sinalizou TxDone", dio0, "trilha DIO0 aberta");
  loraWrite(0x01, 0x80);   // sleep
}

void testeSD() {
  linha(); Serial.println(F("7) microSD (CS 15, SPI compartilhado)"));
  digitalWrite(PIN_NSS, HIGH);
  bool ok = SD.begin(PIN_SD_CS, SPI, 4000000);
  resultado("cartão montado", ok, "cartão inserido? formatado em FAT32? soquete J7 soldado?");
  if (!ok) return;
  Serial.printf("Tipo %d | %llu MB\n", SD.cardType(), SD.cardSize() / (1024ULL * 1024ULL));
  File f = SD.open("/teste_f500.txt", FILE_WRITE);
  bool w = f && f.println("F-500 v2 teste de bancada");
  if (f) f.close();
  f = SD.open("/teste_f500.txt");
  String s = f ? f.readStringUntil('\n') : "";
  if (f) f.close();
  resultado("escrever e ler arquivo", w && s.startsWith("F-500"), "cartão protegido ou com defeito");
  SD.end();
}

void testeVBAT() {
  linha(); Serial.println(F("8) Tensão da bateria (IO34, divisor 100k/22k)"));
  float mv = 0; for (int i = 0; i < 16; i++) mv += analogReadMilliVolts(PIN_VBAT); mv /= 16;
  float v = mv * VBAT_DIV / 1000.0f;
  Serial.printf("ADC %.0f mV -> VBAT %.2f V (%.2f V por célula)\n", mv, v, v / 2);
  if (v < 1.0f) Serial.println(F("  (sem bateria: alimentado só pelo USB — normal na bancada)"));
  else resultado("VBAT na faixa 2S (6,4–8,4 V)", v > 6.4f && v < 8.6f, "bateria descarregada ou divisor errado");
}

void testeContinuidade() {
  linha(); Serial.println(F("9) Continuidade dos ignitores (só leitura)"));
  float s1 = analogReadMilliVolts(PIN_PYRO1_SENSE) / 1000.0f, s2 = analogReadMilliVolts(PIN_PYRO2_SENSE) / 1000.0f;
  Serial.printf("PYRO1: %.2f V -> %s\n", s1, s1 > 0.5f ? "CONTINUIDADE" : "aberto");
  Serial.printf("PYRO2: %.2f V -> %s\n", s2, s2 > 0.5f ? "CONTINUIDADE" : "aberto");
  Serial.println(F("  (só lê algo com a chave de ARME fechada e ignitor/resistor no borne)"));
}

void testePyro() {
  linha(); Serial.println(F("p) TESTE DOS MOSFETs DE DISPARO"));
  Serial.println(F("  !! Só com a CHAVE DE ARME ABERTA ou com LED/lâmpada no borne. NUNCA com ignitor numa carga. !!"));
  Serial.println(F("  Digite SIM em 15 s para pulsar PYRO1 e PYRO2 por 50 ms cada:"));
  String r = lerLinha(15000); r.trim();
  if (r != "SIM") { Serial.println(F("  Cancelado.")); return; }
  for (int ch = 1; ch <= 2; ch++) {
    int pin = ch == 1 ? PIN_PYRO1 : PIN_PYRO2;
    Serial.printf("  PYRO%d em 3...", ch); delay(1000); Serial.print("2..."); delay(1000); Serial.println("1");
    beep(300);
    digitalWrite(pin, HIGH); delay(50); digitalWrite(pin, LOW);
    Serial.printf("  PYRO%d pulsou (LED/lâmpada deve ter piscado)\n", ch);
    delay(500);
  }
}

void menu() {
  linha();
  Serial.println(F("AVIÔNICA F-500 v2 — TESTE DE BANCADA"));
  Serial.println(F(" a = todos os testes seguros (1 a 9)"));
  Serial.println(F(" 1 ESP32   2 LEDs/buzzer   3 I2C   4 BMP280   5 GPS"));
  Serial.println(F(" 6 LoRa    7 microSD       8 VBAT  9 continuidade"));
  Serial.println(F(" p = pulso nos MOSFETs de disparo (pede confirmação)"));
  linha();
}

void setup() {
  // SEGURANÇA PRIMEIRO: disparos desligados antes de tudo
  pinMode(PIN_PYRO1, OUTPUT); digitalWrite(PIN_PYRO1, LOW);
  pinMode(PIN_PYRO2, OUTPUT); digitalWrite(PIN_PYRO2, LOW);

  pinMode(PIN_LED_VERDE, OUTPUT); pinMode(PIN_LED_VERM, OUTPUT); pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_NSS, OUTPUT); digitalWrite(PIN_NSS, HIGH);
  pinMode(PIN_SD_CS, OUTPUT); digitalWrite(PIN_SD_CS, HIGH);
  pinMode(PIN_RST, OUTPUT); digitalWrite(PIN_RST, HIGH);
  pinMode(PIN_DIO0, INPUT);
  analogReadResolution(12);

  Serial.begin(115200);
  delay(800);
  Wire.begin(PIN_SDA, PIN_SCL);
  SPI.begin(PIN_SCK, PIN_MISO, PIN_MOSI);
  menu();
}

void loop() {
  if (!Serial.available()) return;
  char c = Serial.read();
  switch (c) {
    case 'a': testeChip(); testeSinalizacao(); testeI2C(); testeBMP(); testeGPS(); testeLoRa(); testeSD(); testeVBAT(); testeContinuidade(); linha(); Serial.println(F("Fim dos testes.")); break;
    case '1': testeChip(); break;
    case '2': testeSinalizacao(); break;
    case '3': testeI2C(); break;
    case '4': testeBMP(); break;
    case '5': testeGPS(); break;
    case '6': testeLoRa(); break;
    case '7': testeSD(); break;
    case '8': testeVBAT(); break;
    case '9': testeContinuidade(); break;
    case 'p': testePyro(); break;
    case '\n': case '\r': return;
    default: menu();
  }
}
