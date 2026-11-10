# Aviônica F-500 v2 — rev. C-V (com interface para o vídeo ao vivo 2,4 GHz do PDF "Transmissão de vídeo")
# Fonte única: componentes, nets, blocos do esquemático e posições na PCB.
# Net "NC" => pino não conectado.

ESP = "JS_Microcontroladores:ESP32-DevKitC-32E"
R0805 = "Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder"
C0805 = "Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder"
C1206 = "Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder"
LED0805 = "LED_SMD:LED_0805_2012Metric_Pad1.15x1.40mm_HandSolder"
SOT23 = "Package_TO_SOT_SMD:SOT-23"
XH2 = "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical"
XH4 = "Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical"
BORNE = "TerminalBlock_Phoenix:TerminalBlock_Phoenix_PT-1,5-2-3.5-H_1x02_P3.50mm_Horizontal"

DS = {
    "ESP32": "https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html",
    "BMP280": "https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp280-ds001.pdf",
    "MP1584": "https://www.monolithicpower.com/en/mp1584.html",
    "SD": "https://www.molex.com/en-us/products/part-detail/1040310811",
}

def R(ref, val, a, b, blk, sch):
    return dict(ref=ref, lib="Device:R", value=val, fp=R0805, pins={"1": a, "2": b}, blk=blk, sch=sch)
def C(ref, val, a, b, blk, sch, fp=C0805, lib="Device:C"):
    return dict(ref=ref, lib=lib, value=val, fp=fp, pins={"1": a, "2": b}, blk=blk, sch=sch)
def FET(ref, lib, val, g, s, d, blk, sch):
    return dict(ref=ref, lib=lib, value=val, fp=SOT23, pins={"1": g, "2": s, "3": d}, blk=blk, sch=sch)

# Blocos do esquemático (A3): chave -> (título, (x1, y1, x2, y2))
BLOCKS = {
    "ALIM": ("1. ALIMENTAÇÃO E MEDIÇÃO DA BATERIA", (10.16, 10.16, 167.64, 91.44)),
    "LORA": ("2. TELEMETRIA LoRa 917 MHz", (167.64, 10.16, 287.02, 91.44)),
    "CAM":  ("3. VÍDEO 2,4 GHz (Pi Zero 2W + SDR)", (287.02, 10.16, 412.75, 91.44)),
    "MCU":  ("4. MICROCONTROLADOR", (10.16, 91.44, 129.54, 190.5)),
    "SENS": ("5. SENSORES, GPS E LOG", (129.54, 91.44, 287.02, 190.5)),
    "PYRO": ("6. RECUPERAÇÃO (2 CANAIS PIROTÉCNICOS)", (287.02, 91.44, 412.75, 190.5)),
    "SIG":  ("7. SINALIZAÇÃO", (10.16, 190.5, 167.64, 248.92)),
}

COMPS = [
    # ---------------- 1. ALIMENTAÇÃO ----------------
    dict(ref="J1", lib="Connector_Generic:Conn_01x02", value="XT30 BATERIA 2S", blk="ALIM",
         fp="Connector_AMASS:AMASS_XT30PW-M_1x02_P2.50mm_Horizontal", pins={"1": "VBAT_IN", "2": "GND"}, sch=(25.4, 40.64, 180)),
    dict(ref="J2", lib="Connector_Generic:Conn_01x02", value="CHAVE PRINCIPAL", blk="ALIM", fp=XH2,
         pins={"1": "VBAT_IN", "2": "VBAT_SW"}, sch=(25.4, 60.96, 180)),
    dict(ref="D1", lib="Diode:SS34", value="SS34", blk="ALIM", fp="Diode_SMD:D_SMA_Handsoldering",
         pins={"1": "VBAT", "2": "VBAT_SW"}, sch=(50.8, 58.42, 180)),
    C("C1", "470uF 16V", "VBAT", "GND", "ALIM", (66.04, 66.04, 0), fp="Capacitor_THT:CP_Radial_D8.0mm_P3.50mm", lib="Device:C_Polarized"),
    C("C2", "10uF 25V", "VBAT", "GND", "ALIM", (81.28, 66.04, 0), fp=C1206),
    dict(ref="U2", lib="JS_Energia:Buck_Conversor", value="MP1584EN 5V 3A", blk="ALIM", fp="F500v2:MP1584_Modulo",
         pins={"3": "VBAT", "4": "GND", "2": "+5V", "1": "GND"}, sch=(99.06, 59.69, 0), ds=DS["MP1584"]),
    C("C3", "10uF", "+5V", "GND", "ALIM", (134.62, 66.04, 0), fp=C1206),
    C("C4", "100nF", "+5V", "GND", "ALIM", (147.32, 66.04, 0)),
    R("R1", "100k", "VBAT", "VBAT_SENSE", "ALIM", (66.04, 33.02, 0)),
    R("R2", "22k", "VBAT_SENSE", "GND", "ALIM", (66.04, 50.8, 0)),
    C("C5", "100nF", "VBAT_SENSE", "GND", "ALIM", (78.74, 50.8, 0)),

    # ---------------- 4. MICROCONTROLADOR ----------------
    dict(ref="U1", lib=ESP, value="ESP32-DevKitC-32E", fp=ESP, blk="MCU", sch=(71.12, 142.24, 0), ds=DS["ESP32"],
         pins={
             "J2_1": "+3V3", "J2_2": "NC", "J2_3": "PYRO2_SENSE", "J2_4": "LORA_DIO1", "J2_5": "VBAT_SENSE",
             "J2_6": "PYRO1_SENSE", "J2_7": "PYRO1_FIRE", "J2_8": "PYRO2_FIRE", "J2_9": "VID_TX",
             "J2_10": "LORA_DIO0", "J2_11": "BUZZER", "J2_12": "LORA_RST", "J2_13": "LED_VERMELHO",
             "J2_14": "GND", "J2_15": "VID_RX", "J2_16": "NC", "J2_17": "NC", "J2_18": "NC", "J2_19": "+5V",
             "J3_1": "GND", "J3_2": "SPI_MOSI", "J3_3": "I2C_SCL", "J3_4": "NC", "J3_5": "NC",
             "J3_6": "I2C_SDA", "J3_7": "GND", "J3_8": "SPI_MISO", "J3_9": "SPI_SCK", "J3_10": "LORA_NSS",
             "J3_11": "GPS_RX", "J3_12": "GPS_TX", "J3_13": "VID_CTRL", "J3_14": "NC", "J3_15": "LED_VERDE",
             "J3_16": "SD_CS", "J3_17": "NC", "J3_18": "NC", "J3_19": "NC"}),
    C("C6", "100nF", "+3V3", "GND", "MCU", (20.32, 116.84, 0)),
    C("C7", "100nF", "+5V", "GND", "MCU", (20.32, 170.18, 0)),

    # ---------------- 2. LoRa ----------------
    dict(ref="U3", lib="RF_Module:RFM95W-915S2", value="RFM95W 915 MHz", fp="RF_Module:HOPERF_RFM9XW_SMD", blk="LORA",
         pins={"1": "GND", "2": "SPI_MISO", "3": "SPI_MOSI", "4": "SPI_SCK", "5": "LORA_NSS", "6": "LORA_RST",
               "7": "NC", "8": "GND", "9": "LORA_ANT", "10": "GND", "11": "NC", "12": "NC", "13": "+3V3",
               "14": "LORA_DIO0", "15": "LORA_DIO1", "16": "NC"}, sch=(220.98, 55.88, 0)),
    dict(ref="J3", lib="Connector:Conn_Coaxial", value="SMA 50R", blk="LORA",
         fp="Connector_Coaxial:SMA_Amphenol_132289_EdgeMount", pins={"1": "LORA_ANT", "2": "GND"}, sch=(256.54, 48.26, 0)),
    C("C8", "10uF", "+3V3", "GND", "LORA", (246.38, 30.48, 0)),
    C("C9", "100nF", "+3V3", "GND", "LORA", (256.54, 30.48, 0)),

    # ---------------- 3. VÍDEO AO VIVO 2,4 GHz (interface) ----------------
    # O sistema de vídeo (câmera GS + Pi Zero 2W + ADRV1CRR-BOB/ADRV9361 + FEM SKY85333-11 + filtro + antena)
    # tem BATERIA E REGULADOR 5 V / 5 A PRÓPRIOS. Esta placa só controla e conversa com ele:
    #  - VID_OFF: dreno aberto (Q4) que puxa para GND o EN do regulador do vídeo -> desliga o vídeo.
    #    Com o ESP32 em reset/boot (R4 segura o gate em 0) o vídeo fica LIGADO: funciona mesmo se a aviônica falhar.
    #  - UART com a Pi Zero 2W (3,3 V nos dois lados), com 1k em série: protege a Pi quando ela está desligada.
    FET("Q4", "Transistor_FET:AO3400A", "AO3400A", "VID_CTRL", "GND", "VID_OFF", "CAM", (321.31, 60.96, 0)),
    R("R4", "10k", "VID_CTRL", "GND", "CAM", (306.07, 71.12, 0)),
    R("R20", "1k", "VID_TX", "PI_RXD", "CAM", (345.44, 40.64, 90)),
    R("R21", "1k", "PI_TXD", "VID_RX", "CAM", (345.44, 53.34, 90)),
    dict(ref="J4", lib="Connector_Generic:Conn_01x04", value="VIDEO: EN regulador / UART Pi Zero 2W", fp=XH4, blk="CAM",
         pins={"1": "VID_OFF", "2": "GND", "3": "PI_RXD", "4": "PI_TXD"}, sch=(398.78, 50.8, 0)),

    # ---------------- 5. SENSORES / GPS / LOG ----------------
    dict(ref="U4", lib="JS_Sensores:BMP280_Modulo", value="BMP280 (0x76)", fp="JS_Sensores:BMP280_Modulo", blk="SENS",
         pins={"VCC": "+3V3", "GND": "GND", "SCL": "I2C_SCL", "SDA": "I2C_SDA", "CSB": "+3V3", "SDO": "GND"},
         sch=(152.4, 128.27, 0), ds=DS["BMP280"]),
    C("C12", "100nF", "+3V3", "GND", "SENS", (144.78, 104.14, 0)),
    dict(ref="J5", lib="Connector_Generic:Conn_01x04", value="I2C / IMU extra", fp=XH4, blk="SENS",
         pins={"1": "+3V3", "2": "GND", "3": "I2C_SDA", "4": "I2C_SCL"}, sch=(196.85, 119.38, 0)),
    dict(ref="J6", lib="Connector_Generic:Conn_01x04", value="GPS NEO-M8N (cabo)", fp=XH4, blk="SENS",
         pins={"1": "+5V", "2": "GND", "3": "GPS_TX", "4": "GPS_RX"}, sch=(196.85, 167.64, 0)),
    C("C13", "10uF", "+5V", "GND", "SENS", (162.56, 167.64, 0)),
    C("C14", "100nF", "+5V", "GND", "SENS", (172.72, 167.64, 0)),
    dict(ref="J7", lib="Connector:Micro_SD_Card", value="microSD Molex 104031", fp="Connector_Card:microSD_HC_Molex_104031-0811",
         blk="SENS", pins={"1": "SD_DAT2", "2": "SD_CS", "3": "SPI_MOSI", "4": "+3V3", "5": "SPI_SCK", "6": "GND",
                           "7": "SPI_MISO", "8": "SD_DAT1", "SH": "GND"}, sch=(259.08, 149.86, 0), ds=DS["SD"]),
    R("R5", "10k", "+3V3", "SD_DAT2", "SENS", (215.9, 119.38, 0)),
    R("R6", "10k", "+3V3", "SD_CS", "SENS", (223.52, 119.38, 0)),
    R("R7", "10k", "+3V3", "SPI_MISO", "SENS", (231.14, 119.38, 0)),
    R("R8", "10k", "+3V3", "SD_DAT1", "SENS", (238.76, 119.38, 0)),
    C("C15", "10uF", "+3V3", "GND", "SENS", (218.44, 177.8, 0)),
    C("C16", "100nF", "+3V3", "GND", "SENS", (228.6, 177.8, 0)),

    # ---------------- 6. RECUPERAÇÃO ----------------
    dict(ref="J8", lib="Connector_Generic:Conn_01x02", value="CHAVE DE ARME", fp=XH2, blk="PYRO",
         pins={"1": "VBAT_SW", "2": "VBAT_ARM"}, sch=(302.26, 109.22, 180)),
    FET("Q1", "Transistor_FET:AO3400A", "AO3400A", "PYRO1_G", "GND", "PYRO1_D", "PYRO", (341.63, 134.62, 0)),
    R("R9", "100", "PYRO1_FIRE", "PYRO1_G", "PYRO", (325.12, 134.62, 90)),
    R("R10", "10k", "PYRO1_G", "GND", "PYRO", (331.47, 144.78, 0)),
    dict(ref="J9", lib="Connector_Generic:Conn_01x02", value="PYRO 1 (apogeu)", fp=BORNE, blk="PYRO",
         pins={"1": "VBAT_ARM", "2": "PYRO1_D"}, sch=(400.05, 121.92, 0)),
    R("R11", "100k", "PYRO1_D", "PYRO1_SENSE", "PYRO", (367.03, 134.62, 0)),
    R("R12", "22k", "PYRO1_SENSE", "GND", "PYRO", (367.03, 152.4, 0)),
    FET("Q2", "Transistor_FET:AO3400A", "AO3400A", "PYRO2_G", "GND", "PYRO2_D", "PYRO", (341.63, 167.64, 0)),
    R("R13", "100", "PYRO2_FIRE", "PYRO2_G", "PYRO", (325.12, 167.64, 90)),
    R("R14", "10k", "PYRO2_G", "GND", "PYRO", (331.47, 177.8, 0)),
    dict(ref="J10", lib="Connector_Generic:Conn_01x02", value="PYRO 2 (backup)", fp=BORNE, blk="PYRO",
         pins={"1": "VBAT_ARM", "2": "PYRO2_D"}, sch=(400.05, 157.48, 0)),
    R("R15", "100k", "PYRO2_D", "PYRO2_SENSE", "PYRO", (367.03, 167.64, 0)),
    R("R16", "22k", "PYRO2_SENSE", "GND", "PYRO", (367.03, 182.88, 0)),

    # ---------------- 7. SINALIZAÇÃO ----------------
    R("R17", "330", "LED_VERDE", "LED_G_A", "SIG", (33.02, 213.36, 90)),
    dict(ref="D2", lib="Device:LED", value="LED verde", fp=LED0805, blk="SIG", pins={"1": "GND", "2": "LED_G_A"}, sch=(50.8, 213.36, 180)),
    R("R18", "330", "LED_VERMELHO", "LED_R_A", "SIG", (33.02, 233.68, 90)),
    dict(ref="D3", lib="Device:LED", value="LED vermelho", fp=LED0805, blk="SIG", pins={"1": "GND", "2": "LED_R_A"}, sch=(50.8, 233.68, 180)),
    dict(ref="BZ1", lib="Device:Buzzer", value="Buzzer ativo 5V", fp="Buzzer_Beeper:Buzzer_12x9.5RM7.6", blk="SIG",
         pins={"1": "+5V", "2": "BUZ_N"}, sch=(124.46, 210.82, 0)),
    FET("Q5", "Transistor_FET:AO3400A", "AO3400A", "BUZZER", "GND", "BUZ_N", "SIG", (119.38, 228.6, 0)),
    R("R19", "10k", "BUZZER", "GND", "SIG", (101.6, 236.22, 0)),

    # ---------------- MECÂNICA ----------------
    *[dict(ref=f"H{i+1}", lib="Mechanical:MountingHole", value="M3", fp="MountingHole:MountingHole_3.2mm_M3",
           pins={}, blk=None, sch=(186.69 + 10.16 * i, 241.3, 0)) for i in range(4)],
]

BOARD_W, BOARD_H = 60.0, 100.0

# Larguras pela calculadora do KiCad (1 oz, camada externa, ΔT = 10 °C)
NETCLASSES = {
    "Bateria":  dict(track=1.2, clearance=0.25, via_dia=1.0, via_drill=0.5,
                     nets=["VBAT_IN", "VBAT_SW", "VBAT", "GND"]),
    "Pyro":     dict(track=1.0, clearance=0.25, via_dia=1.0, via_drill=0.5, nets=["VBAT_ARM", "PYRO1_D", "PYRO2_D"]),
    "Alim_5V":  dict(track=0.6, clearance=0.2, via_dia=0.8, via_drill=0.4, nets=["+5V"]),
    "Alim_3V3": dict(track=0.5, clearance=0.2, via_dia=0.8, via_drill=0.4, nets=["+3V3"]),
    "RF_50ohm": dict(track=2.8, clearance=0.3, via_dia=0.8, via_drill=0.4, nets=["LORA_ANT"]),
}
DEFAULT_TRACK = 0.25

TEXT_NOTES = [
    "AVIÔNICA F-500 v2 rev.C-V (com vídeo) — foguete com apogeu ~500 m — UTFPR Rocket — segue o Guia de PCB (Payload 2026)",
    "Corrente de pico (pior caso): ESP32 250 mA + RFM95W 120 mA + microSD 100 mA + GPS 45 mA + buzzer 30 mA + BMP/IMU 6 mA",
    "=> +5 V: ~550 mA (2,75 W); entrada do buck a 80 %: 3,4 W / 6,4 V (2S descarregada) = 0,54 A; pulso pyro ~3 A",
    "VÍDEO: bateria + regulador 5 V/5 A próprios (Pi 5 V/2,5 A + BOB/SDR + FEM ~0,5 A). Aqui só passam VID_OFF e UART (mA)",
]

# ---------------- PCB (60 x 100 mm) ----------------
PCB_POS = {}
