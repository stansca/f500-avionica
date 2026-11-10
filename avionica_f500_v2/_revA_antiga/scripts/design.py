# Aviônica F-500 v2 — definição única (netlist + posições) usada pelo esquemático e pela PCB
# Cada componente: ref, lib_id, value, footprint, {pino: net}, (x,y) no esquemático, (x,y,rot,lado) na PCB
# Nets começando com "NC" => pino não conectado (no_connect)

ESP = "JS_Microcontroladores:ESP32-DevKitC-32E"
R_FP = "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal"
C_FP = "Capacitor_THT:C_Disc_D3.0mm_W2.0mm_P2.50mm"
XH2 = "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical"
XH4 = "Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical"
AK = "JS_Conectores:Borne_AK500-2"
TO220 = "Package_TO_SOT_THT:TO-220-3_Vertical"
TO92 = "Package_TO_SOT_THT:TO-92_Inline"

def R(ref, val, a, b, sch, pcb):
    return dict(ref=ref, lib="Device:R", value=val, fp=R_FP, pins={"1": a, "2": b}, sch=sch, pcb=pcb)
def C(ref, val, a, b, sch, pcb, fp=C_FP, lib="Device:C"):
    return dict(ref=ref, lib=lib, value=val, fp=fp, pins={"1": a, "2": b}, sch=sch, pcb=pcb)

COMPS = [
    # ---------------- ALIMENTAÇÃO ----------------
    dict(ref="J1", lib=AK, value="BATERIA 2S (7,4 V)", fp=AK, pins={"1": "VBAT_IN", "2": "GND"},
         sch=(30.48, 45.72), pcb=(8, 143, 0, "F")),
    dict(ref="J2", lib="Connector_Generic:Conn_01x02", value="CHAVE_PRINCIPAL", fp=XH2,
         pins={"1": "VBAT_IN", "2": "VBAT_SW"}, sch=(30.48, 66.04), pcb=(22, 145, 0, "F")),
    dict(ref="D1", lib="Diode:1N5822", value="1N5822", fp="Diode_THT:D_DO-201AD_P15.24mm_Horizontal",
         pins={"2": "VBAT_SW", "1": "VBAT"}, sch=(60.96, 45.72), pcb=(31, 145, 0, "F")),
    C("C1", "470uF 16V", "VBAT", "GND", (78.74, 48.26), (54, 143, 0, "F"),
      fp="Capacitor_THT:CP_Radial_D8.0mm_P3.50mm", lib="Device:C_Polarized"),
    dict(ref="U2", lib="JS_Energia:Buck_Conversor", value="Buck LM2596 -> 5V", fp="JS_Energia:Buck_Conversor",
         pins={"3": "VBAT", "4": "GND", "2": "+5V", "1": "GND"}, sch=(99.06, 48.26), pcb=(14.5, 104, 0, "F")),
    C("C2", "100uF 10V", "+5V", "GND", (124.46, 48.26), (6, 128, 0, "F"),
      fp="Capacitor_THT:CP_Radial_D6.3mm_P2.50mm", lib="Device:C_Polarized"),
    C("C3", "100nF", "+5V", "GND", (134.62, 48.26), (14, 128, 0, "F")),
    C("C4", "100uF 10V", "+3V3", "GND", (144.78, 48.26), (52, 46, 0, "F"),
      fp="Capacitor_THT:CP_Radial_D6.3mm_P2.50mm", lib="Device:C_Polarized"),
    C("C5", "100nF", "+3V3", "GND", (154.94, 48.26), (40, 26, 0, "F")),
    R("R1", "100k", "VBAT", "VBAT_SENSE", (30.48, 88.9), (27, 54, 90, "F")),
    R("R2", "22k", "VBAT_SENSE", "GND", (40.64, 88.9), (31, 54, 90, "F")),
    C("C6", "100nF", "VBAT_SENSE", "GND", (50.8, 88.9), (35, 56, 90, "F")),

    # ---------------- MICROCONTROLADOR ----------------
    dict(ref="U1", lib=ESP, value="ESP32-DevKitC-32E", fp=ESP, sch=(119.38, 129.54), pcb=(30, 64, 0, "F"),
         pins={
             "J2_1": "+3V3", "J2_2": "NC", "J2_3": "PYRO2_SENSE", "J2_4": "LORA_DIO1", "J2_5": "VBAT_SENSE",
             "J2_6": "PYRO1_SENSE", "J2_7": "PYRO1_FIRE", "J2_8": "PYRO2_FIRE", "J2_9": "CAM_TX",
             "J2_10": "LORA_DIO0", "J2_11": "BUZZER", "J2_12": "LORA_RST", "J2_13": "LED_VERMELHO",
             "J2_14": "GND", "J2_15": "CAM_RX", "J2_16": "NC", "J2_17": "NC", "J2_18": "NC", "J2_19": "+5V",
             "J3_1": "GND", "J3_2": "SPI_MOSI", "J3_3": "I2C_SCL", "J3_4": "NC", "J3_5": "NC",
             "J3_6": "I2C_SDA", "J3_7": "GND", "J3_8": "SPI_MISO", "J3_9": "SPI_SCK", "J3_10": "LORA_NSS",
             "J3_11": "GPS_RX", "J3_12": "GPS_TX", "J3_13": "CAM_EN", "J3_14": "NC", "J3_15": "LED_VERDE",
             "J3_16": "SD_CS", "J3_17": "NC", "J3_18": "NC", "J3_19": "NC"}),

    # ---------------- TELEMETRIA LoRa (compatível com tracker_rx) ----------------
    dict(ref="U3", lib="RF_Module:RFM95W-915S2", value="RFM95W 915 MHz", fp="RF_Module:HOPERF_RFM9XW_SMD",
         pins={"1": "GND", "2": "SPI_MISO", "3": "SPI_MOSI", "4": "SPI_SCK", "5": "LORA_NSS", "6": "LORA_RST",
               "7": "NC", "8": "GND", "9": "LORA_ANT", "10": "GND", "11": "NC", "12": "NC", "13": "+3V3",
               "14": "LORA_DIO0", "15": "LORA_DIO1", "16": "NC"},
         sch=(210.82, 129.54), pcb=(47, 13, 0, "F")),
    dict(ref="J3", lib="Connector:Conn_Coaxial", value="SMA antena 915 MHz",
         fp="Connector_Coaxial:SMA_Amphenol_132289_EdgeMount", pins={"1": "LORA_ANT", "2": "GND"},
         sch=(246.38, 124.46), pcb=(47, 0, 270, "F")),

    # ---------------- SENSORES / GPS / LOG ----------------
    dict(ref="U4", lib="JS_Sensores:BMP280_Modulo", value="BMP280 (0x76)", fp="JS_Sensores:BMP280_Modulo",
         pins={"VCC": "+3V3", "GND": "GND", "SCL": "I2C_SCL", "SDA": "I2C_SDA", "CSB": "+3V3", "SDO": "GND"},
         sch=(210.82, 180.34), pcb=(43, 118, 0, "F")),
    dict(ref="J4", lib="Connector_Generic:Conn_01x04", value="I2C / IMU extra", fp=XH4,
         pins={"1": "+3V3", "2": "GND", "3": "I2C_SDA", "4": "I2C_SCL"}, sch=(246.38, 180.34), pcb=(49, 103, 0, "F")),
    dict(ref="J5", lib="Connector_Generic:Conn_01x04", value="GPS NEO-M8N (cabo)", fp=XH4,
         pins={"1": "+5V", "2": "GND", "3": "GPS_TX", "4": "GPS_RX"}, sch=(246.38, 152.4), pcb=(5, 4, 0, "F")),
    dict(ref="U5", lib="JS_Modulos:SD_Card_Adapter", value="Cartão microSD", fp="JS_Modulos:SD_Card_Adapter",
         pins={"1": "GND", "2": "+5V", "3": "SPI_MISO", "4": "SPI_MOSI", "5": "SPI_SCK", "6": "SD_CS"},
         sch=(162.56, 180.34), pcb=(57, 131, 180, "F")),

    # ---------------- RECUPERAÇÃO (2 canais pirotécnicos) ----------------
    dict(ref="J8", lib="Connector_Generic:Conn_01x02", value="CHAVE_ARME", fp=XH2,
         pins={"1": "VBAT_SW", "2": "VBAT_ARM"}, sch=(30.48, 157.48), pcb=(5, 47, 270, "F")),
    dict(ref="Q1", lib="Transistor_FET:IRLZ44N", value="IRLZ44N", fp=TO220,
         pins={"1": "PYRO1_G", "2": "PYRO1_D", "3": "GND"}, sch=(66.04, 157.48), pcb=(5, 66, 90, "F")),
    R("R3", "100", "PYRO1_FIRE", "PYRO1_G", (50.8, 154.94), (23, 48, 90, "F")),
    R("R4", "10k", "PYRO1_G", "GND", (55.88, 167.64), (19, 48, 90, "F")),
    dict(ref="J6", lib=AK, value="PYRO 1 (apogeu)", fp=AK, pins={"1": "VBAT_ARM", "2": "PYRO1_D"},
         sch=(83.82, 147.32), pcb=(-1, 60, 90, "F")),
    R("R5", "100k", "PYRO1_D", "PYRO1_SENSE", (76.2, 170.18), (23, 60, 90, "F")),
    R("R6", "22k", "PYRO1_SENSE", "GND", (86.36, 170.18), (19, 60, 90, "F")),
    dict(ref="Q2", lib="Transistor_FET:IRLZ44N", value="IRLZ44N", fp=TO220,
         pins={"1": "PYRO2_G", "2": "PYRO2_D", "3": "GND"}, sch=(66.04, 195.58), pcb=(5, 84, 90, "F")),
    R("R7", "100", "PYRO2_FIRE", "PYRO2_G", (50.8, 193.04), (23, 72, 90, "F")),
    R("R8", "10k", "PYRO2_G", "GND", (55.88, 205.74), (19, 72, 90, "F")),
    dict(ref="J7", lib=AK, value="PYRO 2 (backup)", fp=AK, pins={"1": "VBAT_ARM", "2": "PYRO2_D"},
         sch=(83.82, 185.42), pcb=(-1, 78, 90, "F")),
    R("R9", "100k", "PYRO2_D", "PYRO2_SENSE", (76.2, 208.28), (23, 84, 90, "F")),
    R("R10", "22k", "PYRO2_SENSE", "GND", (86.36, 208.28), (19, 84, 90, "F")),

    # ---------------- CÂMERA / VTX DIGITAL ----------------
    dict(ref="Q3", lib="Transistor_FET:IRF9540N", value="IRF9540N", fp=TO220,
         pins={"1": "CAM_G", "2": "VBAT_CAM", "3": "VBAT"}, sch=(279.4, 48.26), pcb=(25, 7, 0, "F")),
    R("R11", "10k", "VBAT", "CAM_G", (264.16, 40.64), (18, 18, 0, "F")),
    dict(ref="Q4", lib="Transistor_FET:2N7000", value="2N7000", fp=TO92,
         pins={"1": "GND", "2": "CAM_EN", "3": "CAM_G"}, sch=(264.16, 63.5), pcb=(30, 20, 0, "F")),
    R("R12", "10k", "CAM_EN", "GND", (251.46, 68.58), (18, 24, 0, "F")),
    dict(ref="J9", lib="Connector_Generic:Conn_01x04", value="CAMERA / VTX (DJI O4 / Walksnail)", fp=XH4,
         pins={"1": "VBAT_CAM", "2": "GND", "3": "CAM_TX", "4": "CAM_RX"}, sch=(304.8, 50.8), pcb=(5, 14, 0, "F")),

    # ---------------- SINALIZAÇÃO ----------------
    dict(ref="D2", lib="Device:LED", value="LED verde", fp="LED_THT:LED_D3.0mm",
         pins={"1": "GND", "2": "LED_G_A"}, sch=(304.8, 129.54), pcb=(13, 136, 0, "F")),
    R("R13", "330", "LED_VERDE", "LED_G_A", (292.1, 121.92), (28, 132, 0, "F")),
    dict(ref="D3", lib="Device:LED", value="LED vermelho", fp="LED_THT:LED_D3.0mm",
         pins={"1": "GND", "2": "LED_R_A"}, sch=(304.8, 152.4), pcb=(18.5, 136, 0, "F")),
    R("R14", "330", "LED_VERMELHO", "LED_R_A", (292.1, 144.78), (28, 136, 0, "F")),
    dict(ref="BZ1", lib="Device:Buzzer", value="Buzzer ativo 5V", fp="Buzzer_Beeper:Buzzer_12x9.5RM7.6",
         pins={"1": "+5V", "2": "BUZ_N"}, sch=(304.8, 182.88), pcb=(36, 92, 0, "F")),
    dict(ref="Q5", lib="Transistor_FET:2N7000", value="2N7000", fp=TO92,
         pins={"1": "GND", "2": "BUZZER", "3": "BUZ_N"}, sch=(292.1, 195.58), pcb=(28, 84, 0, "F")),
    R("R15", "10k", "BUZZER", "GND", (279.4, 203.2), (31, 79, 0, "F")),

    # ---------------- MECÂNICA ----------------
    *[dict(ref=f"H{i+1}", lib="Mechanical:MountingHole", value="M3", fp="MountingHole:MountingHole_3.2mm_M3",
           pins={}, sch=(345.44 + 10.16 * i, 213.36), pcb=p) for i, p in
      enumerate([(4, 28, 0, "F"), (56, 28, 0, "F"), (4, 122, 0, "F"), (56, 112, 0, "F")])],
]

BOARD_W, BOARD_H = 60.0, 150.0

NETCLASSES = {
    "Potencia": dict(track=1.0, clearance=0.3, via_dia=1.2, via_drill=0.6,
                     nets=["VBAT_IN", "VBAT_SW", "VBAT", "VBAT_ARM", "VBAT_CAM", "PYRO1_D", "PYRO2_D", "GND", "+5V"]),
    "RF_50ohm": dict(track=2.8, clearance=0.3, via_dia=0.8, via_drill=0.4, nets=["LORA_ANT"]),
    "Alimentacao3V3": dict(track=0.6, clearance=0.25, via_dia=0.9, via_drill=0.45, nets=["+3V3"]),
}

TEXT_NOTES = [
    ((25.4, 228.6), "AVIÔNICA F-500 v2 — foguete apogeu ~500 m — UTFPR Rocket"),
    ((25.4, 234.95), "1) ALIMENTAÇÃO: LiPo 2S -> chave -> 1N5822 -> buck 5 V -> LDO 3V3 do DevKitC"),
    ((25.4, 241.3), "2) RECUPERAÇÃO: 2 canais IRLZ44N (porta lógica) + continuidade no ADC; arme físico separado (J8)"),
    ((25.4, 247.65), "3) TELEMETRIA: RFM95W (SX1276) 917 MHz — mesmos pinos SPI/DIO0/RST e pacote do tracker_rx"),
    ((25.4, 254.0), "4) CÂMERA/VTX: VBAT chaveado por P-MOSFET (CAM_EN) + UART (MSP) para OSD/gravação"),
    ((25.4, 260.35), "5) SENSORES/LOG: BMP280 I2C 0x76, GPS por cabo (UART2), microSD no SPI compartilhado"),
]

# Posição na PCB: (x0, y0, rot) = canto superior esquerdo do bbox já rotacionado (mm). "pad1": posição do pad 1.
BOARD_H = 170.0
PCB_POS = {
    "J3": ("pad1", 57.46, 19.3, 0),
    "U3": (35, 4, 0), "C5": (36, 23, 0), "C4": (46, 23.5, 0),
    "J9": (1, 1, 0), "J5": (15, 1, 0), "Q3": (1, 9, 0), "R11": (13, 10, 0), "Q4": (25, 9, 0), "R12": (13, 15, 0),
    "U1": (15.5, 29, 0),
    "R1": (2, 30, 90), "R2": (2, 42, 90), "C6": (2, 54, 90),
    "R3": (6.5, 30, 90), "R4": (6.5, 42, 90), "R5": (6.5, 54, 90), "R6": (6.5, 66, 90),
    "R7": (11, 30, 90), "R8": (11, 42, 90), "R9": (11, 54, 90), "R10": (11, 66, 90),
    "J4": (53, 31, 90), "R13": (47, 45.7, 90), "R14": (50.5, 45.7, 90), "D2": (54, 46, 0), "D3": (54, 52, 0),
    "Q5": (47, 62, 0), "R15": (52.5, 58, 90),
    "U5": (1, 89, 90), "U4": (41, 89, 0), "BZ1": (24, 104, 0),
    "U2": (1, 119, 90), "C2": (46, 119, 0), "C3": (53, 119, 0),
    "Q1": (1, 145, 0), "Q2": (13, 145, 0), "J8": (26, 145, 0), "D1": (35.8, 144, 0),
    "J6": (0.5, 158, 0), "J7": (12, 158, 0), "J1": (24, 158, 0), "J2": (37, 160, 0), "C1": (50, 158, 0),
    "H1": (1, 79, 0), "H2": (53, 80, 0), "H3": (46, 108, 0), "H4": (53, 132, 0),
}
