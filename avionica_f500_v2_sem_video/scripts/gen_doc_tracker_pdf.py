import os, math
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
                                Image, PageBreak, NextPageTemplate, CondPageBreak, KeepTogether)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon, Circle, Wedge, PolyLine

F = "/System/Library/Fonts/Supplemental/"
pdfmetrics.registerFont(TTFont("Body", F + "Arial Unicode.ttf"))
pdfmetrics.registerFont(TTFont("Bold", F + "Arial Bold.ttf"))
registerFontFamily("Body", normal="Body", bold="Bold", italic="Body", boldItalic="Bold")

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # pasta do projeto, relativa ao script
OUT = PROJ + "/docs/Avionica_F-500_v2_e_Antena_Tracker.pdf"
NAVY = colors.HexColor("#14213D"); ORANGE = colors.HexColor("#E76F24"); GREY = colors.HexColor("#5C6370")
LIGHT = colors.HexColor("#EEF1F6"); GREEN = colors.HexColor("#2A9D8F"); RED = colors.HexColor("#C0392B")
BLUE = colors.HexColor("#3A6EA5"); PURPLE = colors.HexColor("#6A4C93")

ss = {
    "body": ParagraphStyle("body", fontName="Body", fontSize=10, leading=14.2, alignment=TA_JUSTIFY, spaceAfter=6),
    "h1": ParagraphStyle("h1", fontName="Bold", fontSize=18, leading=22, textColor=NAVY, spaceBefore=4, spaceAfter=10),
    "h2": ParagraphStyle("h2", fontName="Bold", fontSize=13, leading=17, textColor=ORANGE, spaceBefore=10, spaceAfter=5),
    "cell": ParagraphStyle("cell", fontName="Body", fontSize=8.6, leading=11),
    "cellb": ParagraphStyle("cellb", fontName="Bold", fontSize=8.6, leading=11, textColor=colors.white),
    "cap": ParagraphStyle("cap", fontName="Body", fontSize=8.5, leading=11, textColor=GREY, alignment=TA_CENTER, spaceAfter=8),
    "box": ParagraphStyle("box", fontName="Body", fontSize=9.6, leading=13.5, alignment=TA_JUSTIFY),
    "code": ParagraphStyle("code", fontName="Courier", fontSize=8.2, leading=10.5, textColor=NAVY),
    "toc1": ParagraphStyle("toc1", fontName="Body", fontSize=11, leading=17),
    "toc2": ParagraphStyle("toc2", fontName="Body", fontSize=9.5, leading=13, leftIndent=14, textColor=GREY),
}
ss["bul"] = ParagraphStyle("bul", parent=ss["body"], leftIndent=12, bulletIndent=2, spaceAfter=3, alignment=TA_LEFT)
story = []
def P(t, s="body"): story.append(Paragraph(t, ss[s]))
def SP(h=4): story.append(Spacer(1, h * mm))
def H1(t):
    story.append(CondPageBreak(70 * mm)); p = Paragraph(t, ss["h1"]); p._toc = (0, t); story.append(p)
def H2(t):
    story.append(CondPageBreak(40 * mm)); p = Paragraph(t, ss["h2"]); p._toc = (1, t); story.append(p)
def B(items):
    for it in items: story.append(Paragraph(it, ss["bul"], bulletText="•"))
    story.append(Spacer(1, 3))
def table(rows, widths, head=True):
    data = [[Paragraph(str(c), ss["cellb"] if (head and i == 0) else ss["cell"]) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1 if head else 0)
    st = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C9CED6")),
          ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
          ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    if head: st.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
    for i in range(1 if head else 0, len(rows)):
        if i % 2 == 0: st.append(("BACKGROUND", (0, i), (-1, i), LIGHT))
    t.setStyle(TableStyle(st)); story.append(t); SP(3)
def callout(title, text, color=ORANGE):
    bg = {ORANGE: "#FFF6EF", GREEN: "#EAF6F4", RED: "#FBECEA"}.get(color, "#EEF1F6")
    inner = [Paragraph(f"<b>{title}</b>", ParagraphStyle("ct", parent=ss["box"], textColor=color, fontName="Bold")),
             Paragraph(text, ss["box"])]
    t = Table([[inner]], colWidths=[170 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(bg)), ("LINEBEFORE", (0, 0), (0, -1), 3, color),
                           ("LEFTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story.append(t); SP(3)
def code(lines):
    t = Table([[Paragraph("<br/>".join(l.replace(" ", "&nbsp;") for l in lines), ss["code"])]], colWidths=[170 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F4F6F9")), ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#C9CED6")),
                           ("LEFTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    story.append(t); SP(3)

def box(d, x, y, w, h, title, sub="", fill=LIGHT, stroke=NAVY, tc=NAVY, fs=8.2):
    d.add(Rect(x, y, w, h, rx=4, ry=4, fillColor=fill, strokeColor=stroke, strokeWidth=1))
    d.add(String(x + w / 2, y + h - 12, title, fontName="Bold", fontSize=fs, fillColor=tc, textAnchor="middle"))
    for i, s in enumerate(sub.split("\n") if sub else []):
        d.add(String(x + w / 2, y + h - 23 - 9 * i, s, fontName="Body", fontSize=6.8, fillColor=GREY, textAnchor="middle"))
def arrow(d, x1, y1, x2, y2, label="", color=GREY, lw=1, lx=0, ly=3, fs=6.5):
    d.add(Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=lw))
    a = math.atan2(y2 - y1, x2 - x1); L = 5
    d.add(Polygon([x2, y2, x2 - L * math.cos(a - 0.4), y2 - L * math.sin(a - 0.4), x2 - L * math.cos(a + 0.4), y2 - L * math.sin(a + 0.4)],
                  fillColor=color, strokeColor=color))
    if label: d.add(String((x1 + x2) / 2 + lx, (y1 + y2) / 2 + ly, label, fontName="Body", fontSize=fs, fillColor=color, textAnchor="middle"))

# ---------- diagramas ----------
def system_diagram():
    d = Drawing(170 * mm, 95 * mm)
    # foguete
    d.add(Rect(2, 18, 205, 245, rx=8, ry=8, fillColor=colors.HexColor("#F7F9FC"), strokeColor=NAVY, strokeDasharray=[4, 3]))
    d.add(String(105, 250, "NO FOGUETE — Aviônica F-500 v2", fontName="Bold", fontSize=8.5, fillColor=NAVY, textAnchor="middle"))
    box(d, 12, 185, 85, 50, "GPS NEO-M8N", "J6 · UART2 16/17\n5 Hz, AIRBORNE 4g")
    box(d, 112, 185, 85, 50, "BMP280", "I2C 21/22 · 0x76\naltitude relativa")
    box(d, 12, 120, 85, 50, "VBAT ÷5,545", "ADC IO34\n(enviar por célula)")
    box(d, 112, 105, 85, 75, "ESP32-DevKitC", "monta o pacote\n26 B · 0xA5\na cada 200 ms\n+ log no SD/flash", fill=colors.HexColor("#DDE6F5"))
    box(d, 60, 30, 100, 55, "RFM95W", "SX1276 · 917 MHz\nSF7 · BW250 · CR4/5\n14 dBm → SMA", fill=colors.HexColor("#FDE8D7"), stroke=ORANGE)
    arrow(d, 97, 200, 140, 180, "", NAVY); arrow(d, 155, 185, 155, 180, "", NAVY); arrow(d, 97, 145, 112, 145, "", NAVY)
    arrow(d, 150, 105, 125, 85, "SPI 18/19/23/5", NAVY, lx=24)
    # enlace
    d.add(Line(165, 58, 290, 58, strokeColor=ORANGE, strokeWidth=2, strokeDashArray=[6, 4]))
    for k in range(3):
        d.add(Wedge(165, 58, 10 + 7 * k, -30, 30, fillColor=None, strokeColor=ORANGE, strokeWidth=1))
    d.add(String(228, 66, "rádio LoRa 917 MHz", fontName="Bold", fontSize=8, fillColor=ORANGE, textAnchor="middle"))
    d.add(String(228, 46, "~31 ms no ar · 5 pacotes/s", fontName="Body", fontSize=6.8, fillColor=GREY, textAnchor="middle"))
    # tracker
    d.add(Rect(272, 18, 205, 245, rx=8, ry=8, fillColor=colors.HexColor("#F7FCFA"), strokeColor=GREEN, strokeDasharray=[4, 3]))
    d.add(String(375, 250, "NO SOLO — tracker_rx", fontName="Bold", fontSize=8.5, fillColor=GREEN, textAnchor="middle"))
    box(d, 285, 30, 100, 55, "RFM95W (RX)", "mesma configuração\nCRC + byte 0xA5\nRSSI / SNR", fill=colors.HexColor("#FDE8D7"), stroke=ORANGE)
    box(d, 285, 105, 100, 75, "ESP32 DevKit V1", "geo → ENU (base)\npredição 0,15–1,5 s\naz / el + flip\nservos a 50 Hz", fill=colors.HexColor("#E3F2EF"), stroke=GREEN)
    box(d, 395, 185, 75, 50, "SERVOS", "PAN IO32\nTILT IO33", fill=colors.white, stroke=GREEN)
    box(d, 395, 120, 75, 50, "OLED + BUZZER", "az, el, RSSI\nlink perdido", fill=colors.white, stroke=GREEN)
    box(d, 285, 185, 100, 50, "BOTÕES + NVS", "BASE (IO27)\nALINHAR (IO0)", fill=colors.white, stroke=GREEN)
    box(d, 395, 30, 75, 55, "NOTEBOOK", "CSV pela serial\n115200 baud", fill=colors.white, stroke=GREY)
    arrow(d, 335, 85, 335, 105, "", GREEN); arrow(d, 385, 160, 395, 205, "", GREEN); arrow(d, 385, 140, 395, 145, "", GREEN)
    arrow(d, 335, 185, 335, 180, "", GREEN); arrow(d, 385, 115, 420, 85, "", GREY)
    return d

def packet_diagram():
    d = Drawing(170 * mm, 44 * mm)
    fields = [("magic", 1, "0xA5"), ("flags", 1, "fix|baro"), ("seq", 2, "contador"), ("lat", 4, "°×1e7"), ("lon", 4, "°×1e7"),
              ("altMsl", 4, "cm"), ("baroRel", 2, "dm"), ("vN", 2, "cm/s"), ("vE", 2, "cm/s"), ("vD", 2, "cm/s"),
              ("sats", 1, ""), ("vbat", 1, "20 mV")]
    W = 470 / 26; x = 5; y = 60
    cols = [NAVY, GREY, GREY, BLUE, BLUE, BLUE, PURPLE, GREEN, GREEN, GREEN, GREY, ORANGE]
    off = 0
    for (n, sz, u), c in zip(fields, cols):
        w = sz * W
        d.add(Rect(x, y, w, 34, fillColor=c, strokeColor=colors.white, strokeWidth=1.5))
        d.add(String(x + w / 2, y + 20, n, fontName="Bold", fontSize=6.6 if sz < 2 else 7.5, fillColor=colors.white, textAnchor="middle"))
        if u: d.add(String(x + w / 2, y + 8, u, fontName="Body", fontSize=5.6, fillColor=colors.white, textAnchor="middle"))
        d.add(String(x + 1, y - 9, str(off), fontName="Body", fontSize=6, fillColor=GREY))
        x += w; off += sz
    d.add(String(x - 4, y - 9, "26", fontName="Body", fontSize=6, fillColor=GREY))
    d.add(String(5, 30, "Little-endian, struct packed (sem preenchimento). Azul: posição GPS · roxo: barômetro · verde: velocidade NED · laranja: bateria.",
                 fontName="Body", fontSize=7, fillColor=GREY))
    d.add(String(5, 18, "O receptor descarta o pacote se o CRC falhar, se o tamanho for diferente de 26 bytes ou se o 1º byte não for 0xA5.",
                 fontName="Body", fontSize=7, fillColor=GREY))
    return d

def geometry_diagram():
    d = Drawing(170 * mm, 78 * mm)
    gx, gy = 40, 40
    d.add(Line(10, gy, 470, gy, strokeColor=colors.HexColor("#8D6E63"), strokeWidth=1.5))
    d.add(String(440, gy - 12, "solo", fontName="Body", fontSize=7, fillColor=GREY))
    # tracker
    d.add(Rect(gx - 8, gy, 16, 14, fillColor=GREEN, strokeColor=GREEN)); d.add(String(gx, gy - 12, "BASE (tracker)", fontName="Bold", fontSize=7.5, fillColor=GREEN, textAnchor="middle"))
    # pad
    px = 300
    d.add(Line(px, gy, px, gy + 18, strokeColor=NAVY, strokeWidth=2)); d.add(String(px, gy - 12, "RAMPA", fontName="Bold", fontSize=7.5, fillColor=NAVY, textAnchor="middle"))
    d.add(Line(gx, gy + 7, px, gy + 7, strokeColor=GREY, strokeDashArray=[3, 3]))
    d.add(String((gx + px) / 2, gy - 24, "padDist (≥ 30 m; típico 300–500 m) · azimute = azFront", fontName="Body", fontSize=6.8, fillColor=GREY, textAnchor="middle"))
    # rocket at apogee
    ax, ay = 330, 190
    d.add(Polygon([ax - 4, ay - 12, ax + 4, ay - 12, ax, ay + 6], fillColor=ORANGE, strokeColor=ORANGE))
    d.add(String(ax + 10, ay, "foguete (n, e, u) em ENU", fontName="Bold", fontSize=7.5, fillColor=ORANGE))
    d.add(PolyLine([px, gy + 18, px + 5, 90, px + 15, 140, ax, ay - 12], strokeColor=ORANGE, strokeWidth=1.2, strokeDashArray=[2, 2]))
    d.add(Line(gx, gy + 7, ax, ay - 3, strokeColor=RED, strokeWidth=1.6))
    d.add(String(190, 125, "linha de visada (distância)", fontName="Body", fontSize=7, fillColor=RED, textAnchor="middle"))
    d.add(Line(ax, ay - 3, ax, gy + 7, strokeColor=PURPLE, strokeDashArray=[2, 2]))
    d.add(String(ax + 6, 110, "u = altura acima da base", fontName="Body", fontSize=7, fillColor=PURPLE))
    # elevation arc
    el = math.atan2(ay - 3 - gy - 7, ax - gx)
    d.add(Wedge(gx, gy + 7, 45, 0, math.degrees(el), fillColor=colors.HexColor("#FBECEA"), strokeColor=RED, strokeWidth=0.8))
    d.add(String(gx + 110, gy + 26, "el = atan2(u, h)", fontName="Bold", fontSize=7.5, fillColor=RED))
    d.add(String(gx + 110, gy + 15, "h = √(n² + e²)", fontName="Body", fontSize=7, fillColor=GREY))
    return d

def timeline_diagram():
    d = Drawing(170 * mm, 50 * mm)
    steps = [("1 LIGAR", "placa + tracker", NAVY), ("2 BASE", "placa EM CIMA\ndo tracker · 20 pac.", GREEN),
             ("3 LEVAR", "placa → rampa\n(sem desligar!)", GREY), ("4 ALINHAR", "pan 90° · tilt 0°\nmirar a rampa", GREEN),
             ("5 ARMAR", "chave de ARME\nT−60 s câmera", RED), ("6 VOO", "tracker segue\naz/el a 50 Hz", ORANGE),
             ("7 POUSO", "último GPS\nno OLED/CSV", BLUE)]
    w, g = 58, 9
    for i, (a, b, c) in enumerate(steps):
        x = 4 + i * (w + g)
        d.add(Rect(x, 60, w, 62, rx=5, ry=5, fillColor=colors.white, strokeColor=c, strokeWidth=1.3))
        d.add(String(x + w / 2, 105, a, fontName="Bold", fontSize=7.4, fillColor=c, textAnchor="middle"))
        for k, ln in enumerate(b.split("\n")):
            d.add(String(x + w / 2, 88 - 10 * k, ln, fontName="Body", fontSize=5.9, fillColor=GREY, textAnchor="middle"))
        if i < len(steps) - 1: arrow(d, x + w, 91, x + w + g, 91, "", GREY)
    d.add(String(4, 35, "A placa do foguete é o GPS da base: o tracker não tem GPS próprio. Por isso a placa precisa ficar em cima do tracker",
                 fontName="Body", fontSize=7, fillColor=GREY))
    d.add(String(4, 24, "no passo 2, e não pode reiniciar entre o passo 4 e o voo (a referência do barômetro é a do boot).",
                 fontName="Body", fontSize=7, fillColor=GREY))
    return d

def flip_diagram():
    d = Drawing(170 * mm, 66 * mm)
    for i, (title, rel, flip) in enumerate([("NORMAL: |rel| < 85°", 40, False), ("FLIP: |rel| > 95°", 120, True)]):
        cx, cy = 120 + i * 240, 80
        d.add(String(cx, cy + 92, title, fontName="Bold", fontSize=8.5, fillColor=NAVY if not flip else ORANGE, textAnchor="middle"))
        d.add(Wedge(cx, cy, 70, 0, 180, fillColor=colors.HexColor("#EEF1F6"), strokeColor=GREY))
        d.add(String(cx - 72, cy - 12, "faixa do pan (0–180°)", fontName="Body", fontSize=6.5, fillColor=GREY, textAnchor="start"))
        d.add(Line(cx, cy, cx, cy + 75, strokeColor=GREEN, strokeDashArray=[3, 2]))
        d.add(String(cx + 3, cy + 78, "azFront (pan 90°)", fontName="Body", fontSize=6.3, fillColor=GREEN))
        tgt = math.radians(90 - rel)
        L = 85 if not flip else 62
        d.add(Line(cx, cy, cx + L * math.cos(tgt), cy + L * math.sin(tgt), strokeColor=RED, strokeWidth=1.4))
        d.add(String(cx + (L + 4) * math.cos(tgt) + (8 if flip else 0), cy + (L + 4) * math.sin(tgt) - 3, "alvo (atrás)" if flip else "alvo", fontName="Bold", fontSize=7, fillColor=RED, textAnchor="middle"))
        if not flip:
            d.add(String(cx, cy - 52, "pan = 90 + rel · tilt = el", fontName="Bold", fontSize=7.5, fillColor=NAVY, textAnchor="middle"))
        else:
            ant = math.radians(90 - (rel - 180))
            d.add(Line(cx, cy, cx + 60 * math.cos(ant), cy + 60 * math.sin(ant), strokeColor=ORANGE, strokeWidth=1.6))
            d.add(String(cx, cy - 52, "pan = 90 + (rel ± 180) · tilt = 180 − el", fontName="Bold", fontSize=7.5, fillColor=ORANGE, textAnchor="middle"))
            d.add(String(cx, cy - 62, "o pan gira para o lado oposto e o tilt passa do zênite", fontName="Body", fontSize=6.5, fillColor=GREY, textAnchor="middle"))
    return d

# ================= CONTEÚDO =================
story.append(Spacer(1, 16 * mm))
story.append(Paragraph("AVIÔNICA F-500 v2<br/>+ ANTENA TRACKER", ParagraphStyle("t", fontName="Bold", fontSize=28, leading=33, textColor=NAVY)))
story.append(Paragraph("Como a placa do foguete e a estação de solo conversam, se calibram e se mantêm apontadas durante o voo",
                       ParagraphStyle("st", fontName="Body", fontSize=13.5, leading=18, textColor=ORANGE, spaceAfter=8)))
story.append(Paragraph("Documentação de integração · UTFPR Rocket · 08/11/2026 · firmwares <font face='Courier'>foguete_tx.ino</font> e <font face='Courier'>tracker_rx.ino</font>",
                       ParagraphStyle("st2", fontName="Body", fontSize=10, textColor=GREY, spaceAfter=10)))
story.append(system_diagram())
P("Figura 1 — Visão geral: a placa mede, empacota e transmite; o tracker recebe, calcula para onde o foguete está e move a antena.", "cap")
callout("Resumo em quatro frases",
        "1) A placa F-500 v2 manda <b>um pacote de 26 bytes a cada 200 ms</b> por LoRa a 917 MHz, com posição GPS, altitude barométrica, velocidade e bateria. "
        "2) O tracker recebe, converte a posição para metros em relação à base e calcula o <b>azimute</b> e a <b>elevação</b>. Ele compensa o atraso com a velocidade do GPS e move dois servos. "
        "3) O tracker <b>não tem GPS próprio</b>: a posição da base e a direção da rampa são aprendidas com a <b>própria placa do foguete</b>, nos botões BASE e ALINHAR. "
        "4) Se o GPS cair (na queima, por exemplo), o tracker usa o <b>barômetro</b> e a última posição. Se o rádio cair, ele segura a predição e apita.")
story.append(PageBreak())
story.append(Paragraph("Sumário", ss["h1"]))
toc = TableOfContents(); toc.levelStyles = [ss["toc1"], ss["toc2"]]; story.append(toc)
story.append(PageBreak())

# 1
H1("1. Quem faz o quê")
table([["", "Placa F-500 v2 (no foguete)", "tracker_rx (no solo)"],
       ["Microcontrolador", "ESP32-DevKitC-32E", "ESP32 DevKit V1 (WROOM-32)"],
       ["Rádio", "RFM95W (SX1276), <b>transmite</b> a 14 dBm", "RFM95W (SX1276), <b>recebe</b> (CRC + filtro 0xA5)"],
       ["Pinos do rádio", "SCK 18 · MISO 19 · MOSI 23 · NSS 5 · DIO0 26 · RST 14", "<b>os mesmos</b>: SCK 18 · MISO 19 · MOSI 23 · NSS 5 · DIO0 26 · RST 14"],
       ["Sensores", "GPS u-blox (J6), BMP280, divisor de VBAT", "nenhum (usa os dados do foguete)"],
       ["Saídas", "pacote LoRa + log no microSD e na flash", "servos pan/tilt, OLED, buzzer, CSV na serial"],
       ["Firmware", "foguete_tx.ino, portado para o ESP32 clássico com <font face='Courier'>pinos_f500_v2.h</font>", "tracker_rx.ino (sem alterações)"],
       ["Antena", "915 MHz no SMA de borda (J3), ao longo do corpo", "direcional (Yagi/patch 8–10 dBi) no pan/tilt"]],
      [30, 70, 70])
callout("Por que os pinos iguais importam",
        "O código de rádio (RadioLib) é literalmente o mesmo dos dois lados. Um módulo RFM95W testado num lado funciona no outro, e a bancada de testes fica simples. "
        "<b>Atenção:</b> no tracker, IO32/IO33 são os <b>servos</b>. Na placa do foguete, IO32/IO33 são os <b>disparos pirotécnicos</b>. "
        "<b>Nunca grave o firmware do tracker na placa do foguete.</b> O PWM dos servos acionaria os MOSFETs dos ignitores.", RED)

# 2 enlace
H1("2. O enlace de rádio")
H2("2.1 Parâmetros que precisam ser idênticos")
table([["Parâmetro", "Valor", "Se for diferente…"],
       ["Frequência", "917,0 MHz (faixa 915–928 MHz)", "nenhum pacote chega"],
       ["Largura de banda (BW)", "250 kHz", "nenhum pacote chega"],
       ["Spreading factor (SF)", "7", "nenhum pacote chega"],
       ["Coding rate (CR)", "4/5", "pacotes corrompidos"],
       ["Sync word", "padrão SX127x (0x12)", "o receptor ignora tudo"],
       ["Preâmbulo", "8 símbolos", "perda de pacotes"],
       ["CRC", "ligado", "pacotes ruins passam"],
       ["Estrutura do pacote", "26 bytes, 0xA5 (seção 3)", "descartados pelo filtro de tamanho/magic"]],
      [42, 62, 66])
H2("2.2 Tempo no ar e taxa")
P("Em SF7/BW250 cada símbolo dura 2<super>7</super>/250 kHz = 0,512 ms. Um pacote de 26 bytes com CRC dá "
  "12,25 símbolos de preâmbulo + 48 símbolos de dados ≈ <b>31 ms no ar</b>. A 5 Hz o canal fica ocupado ~15 % do tempo. "
  "Isso deixa folga para um segundo pacote de status, ou para subir a 10 Hz se for preciso (o GPS também precisaria ir a 10 Hz).")
H2("2.3 Orçamento de enlace")
table([["Distância", "Perda no espaço livre", "Potência recebida*", "Margem sobre −120 dBm"],
       ["0,5 km", "85,7 dB", "−62 dBm", "58 dB"], ["1 km", "91,7 dB", "−68 dBm", "52 dB"],
       ["2 km", "97,7 dB", "−74 dBm", "46 dB"], ["3 km", "101,2 dB", "−77 dBm", "43 dB"], ["5 km", "105,7 dB", "−82 dBm", "38 dB"]],
      [30, 45, 45, 50])
P("* 14 dBm de transmissão, 2 dBi na antena do foguete e 8 dBi na antena direcional do tracker. A sensibilidade do SX1276 em SF7/BW250 é de ~−120 dBm. "
  "Num voo de 500 m com a rampa a até 500 m da base, a distância máxima fica em ~1–2 km. Mesmo descontando ~20 dB de desvanecimento "
  "(foguete girando, polarização cruzada, antena de lado na descida), sobram mais de 25 dB.", "cap")
callout("Coexistência com a câmera",
        "O VTX da câmera transmite em 5,8 GHz e o GPS recebe em 1,575 GHz, ambos longe de 917 MHz. Ainda assim: "
        "antenas separadas (LoRa embaixo, VTX em cima ou vice-versa), cabos curtos e o VTX ligado só em T−60 s, para evitar aquecimento e harmônicos durante a calibração.", GREEN)

# 3 pacote
H1("3. O pacote de telemetria, byte a byte")
story.append(packet_diagram())
P("Figura 2 — Mapa dos 26 bytes.", "cap")
table([["Offset", "Campo", "Tipo", "Origem na placa F-500 v2", "Uso no tracker"],
       ["0", "magic = 0xA5", "uint8", "constante", "filtro: descarta o que não for 0xA5"],
       ["1", "flags", "uint8", "bit0 = fix 3D do GPS; bit1 = BMP280 OK", "decide entre o modo GPS e o modo barômetro"],
       ["2", "seq", "uint16", "contador incrementado a cada pacote", "CSV: mostra pacotes perdidos"],
       ["4 / 8", "lat / lon", "int32", "GPS (J6), graus × 10<super>7</super>", "posição → ENU (norte/leste em metros)"],
       ["12", "altMsl", "int32", "GPS, cm acima do nível do mar", "altura u = altMsl − homeAlt"],
       ["16", "baroRel", "int16", "BMP280, dm em relação ao <b>boot</b>", "altura no modo barômetro (GPS sem fix)"],
       ["18–22", "vN, vE, vD", "int16", "GPS, velocidade NED em cm/s (vD+ = descendo)", "predição: posição + v·dt"],
       ["24", "sats", "uint8", "satélites usados", "OLED / CSV"],
       ["25", "vbat", "uint8", "VBAT ÷ 5,545 no IO34, passo de 20 mV", "OLED: \"Bat x,xx V\""]],
      [13, 22, 14, 63, 58])
callout("Ajuste obrigatório para a bateria 2S",
        "O campo <font face='Courier'>vbat</font> vai até 255 × 20 mV = 5,1 V, então uma 2S (8,4 V) satura. Para <b>não mudar o tracker</b>, a placa deve mandar a "
        "tensão <b>por célula</b>: <font face='Courier'>pkt.vbat = (mv / 2) / 20</font>. O OLED passa a mostrar, por exemplo, \"Bat 3,95 V\", que é a tensão por célula.")
callout("Não reinicie a referência do barômetro",
        "O tracker grava <font face='Courier'>baroAtPad</font> no ALINHAR e depois usa <font face='Courier'>baroRel − baroAtPad</font> como altura. "
        "Se a placa reiniciar, ou se o firmware de voo <b>zerar</b> o barômetro no arme, essa referência fica errada e o modo barômetro aponta para a altura errada. "
        "Regra: o campo <font face='Courier'>baroRel</font> do pacote é <b>sempre relativo ao boot</b>. A máquina de estados pode ter a sua própria referência interna, mas não muda esse campo.", RED)

# 4 geometria
H1("4. Como o tracker calcula para onde apontar")
story.append(geometry_diagram())
P("Figura 3 — Geometria: a base é a origem, e o foguete é localizado em metros para o norte (n), leste (e) e para cima (u).", "cap")
H2("4.1 Passo a passo do cálculo (a cada pacote e a 50 Hz)")
B(["<b>De latitude/longitude para metros (ENU):</b> com terra plana (ótima para menos de 10 km): "
   "n = Δlat·(π/180)·R<sub>T</sub> e e = Δlon·(π/180)·R<sub>T</sub>·cos(lat<sub>base</sub>), com R<sub>T</sub> = 6 371 km.",
   "<b>Altura:</b> u = altMsl − homeAlt (GPS). No modo barômetro: u = (baroRel − baroAtPad) + (padAlt − homeAlt).",
   "<b>Predição:</b> o pacote chega com atraso (GPS + rádio + servo). O tracker soma v·dt, com dt = idade do pacote + 0,15 s (LEAD_S), "
   "limitado a 1,5 s (MAX_PREDICT_S). No modo barômetro dt = 0, porque a velocidade não é confiável.",
   "<b>Ângulos:</b> az = atan2(e, n), de 0 a 360°, e el = atan2(u, √(n²+e²)), limitado a 0–90°.",
   "<b>Zona morta:</b> se o alvo estiver a menos de 3 m da base, na horizontal e na vertical, o tracker não se mexe. Isso evita ruído quando a placa está em cima dele.",
   "<b>Velocidade dos servos:</b> limitada a 200°/s (SLEW_DEG_S), para não dar trancos nem puxar corrente demais."])
H2("4.2 O truque do flip (cobrir 360° com servos de 180°)")
story.append(flip_diagram())
P("Figura 4 — Se o alvo sai mais de 95° do centro, o pan gira 180° para o outro lado e o tilt passa do zênite (180 − el). Ele volta ao normal abaixo de 85°: essa histerese de 10° evita ficar alternando.", "cap")
H2("4.3 Exemplo numérico")
P("Rampa a 500 m ao norte da base e apogeu de 500 m. No apogeu, n = 500 m, e = 0, u = 500 m: az = 0° (norte) e el = atan2(500, 500) = <b>45°</b>. "
  "Na subida a 100 m/s, a elevação muda a cerca de v/d ≈ 100/700 rad/s ≈ <b>8°/s</b>, bem abaixo do limite de 200°/s. Como o alvo fica perto do "
  "azimute da rampa, o flip só acontece se o vento levar o foguete para trás do tracker.")

# 5 calibração
H1("5. Calibração em campo: BASE e ALINHAR")
story.append(timeline_diagram())
P("Figura 5 — Sequência de operação conjunta.", "cap")
table([["Passo", "Onde está a placa", "O que fazer", "O que o tracker grava"],
       ["BASE (IO27, segurar 2 s)", "<b>em cima do tracker</b>, ligada e com fix 3D", "esperar ≥ 6 satélites; segurar o botão", "homeLat, homeLon, homeAlt (média de 20 pacotes, mínimo 10, timeout 15 s)"],
       ["Levar à rampa", "sendo carregada, <b>ligada</b>", "não desligar a placa", "—"],
       ["ALINHAR (BOOT/IO0, 2 s)", "na rampa, com fix", "pan 90° e tilt 0°; girar o tripé até a antena mirar a rampa", "azFront, padAlt, baroAtPad, padDist (10 pacotes, mínimo 5, exige ≥ 30 m)"],
       ["Depois", "na rampa", "<b>não mexer no tripé</b>; conferir az/el no OLED", "tudo fica na flash (NVS): sobrevive se o tracker reiniciar"]],
      [30, 38, 50, 52])
B(["Bipes do tracker: 2 bipes = BASE OK; 3 bipes = ALINHADO; 1 bipe longo = falhou (sem fix, ou rampa a menos de 30 m).",
   "Se a placa do foguete for <b>reiniciada</b> depois do ALINHAR, refaça o ALINHAR (por causa da referência do barômetro).",
   "Se o tracker for movido, refaça os <b>dois</b> passos."])

# 6 voo
H1("6. Durante o voo: o que acontece em cada fase")
table([["Fase", "Placa F-500 v2", "Pacote", "tracker_rx"],
       ["Rampa", "GPS com fix, barômetro estável", "fix=1, baro=1, 5 Hz", "aponta para a rampa (el ≈ 0°)"],
       ["Propulsão", "GPS pode <b>perder o fix</b> (> 4 g)", "fix=0, baro=1", "<b>modo barômetro</b>: última posição + altura baro, sem predição"],
       ["Coasting", "GPS recupera o fix em segundos", "fix=1", "volta ao GPS + predição"],
       ["Apogeu", "disparo PYRO1/PYRO2", "vD ≈ 0", "el máxima; flip se o vento levar o foguete para trás"],
       ["Descida", "paraquedas, a cerca de 5–15 m/s", "fix=1", "segue a deriva do vento"],
       ["Pouso", "parado, continua transmitindo", "v ≈ 0", "aponta para o local de pouso; lat/lon no OLED e no CSV"]],
      [22, 48, 32, 68])
callout("Link perdido",
        "Se nenhum pacote chegar por 2 s (LINK_LOST_MS), o tracker dá um bipe a cada 2 s e mantém a última predição por até 1,5 s, depois congela. "
        "<b>Nenhum dado se perde</b>: a placa grava tudo no microSD e na flash, e o campo <font face='Courier'>seq</font> mostra no CSV exatamente quais pacotes faltaram. "
        "Eles podem ser recuperados do cartão depois do voo.", GREEN)

# 7 falhas
H1("7. Falhas na interação e o que fazer")
table([["Sintoma", "Causa provável", "Solução"],
       ["Nenhum pacote no tracker", "parâmetros LoRa diferentes, antena solta, RFM95W de 433/868 MHz", "conferir a seção 2.1; usar módulo 915 MHz; testar na bancada a 1 m"],
       ["BASE falha (bipe longo)", "placa sem fix 3D ou menos de 10 pacotes em 15 s", "esperar ≥ 6 satélites; céu aberto"],
       ["ALINHAR falha", "rampa a menos de 30 m da base", "afastar o tracker (ideal: 300–500 m)"],
       ["Antena aponta para o lado errado", "PAN_DIR/TILT_DIR invertidos ou tripé mexido", "inverter o sinal no firmware; refazer ALINHAR"],
       ["Altura errada sem GPS", "placa reiniciou depois do ALINHAR, ou baroRel foi zerado", "refazer ALINHAR; não zerar baroRel no pacote"],
       ["Antena atrasada", "LEAD_S pequeno ou servo lento", "aumentar LEAD_S para 0,2–0,3 s; servo mais rápido"],
       ["Bateria \"5,10 V\" no OLED", "vbat saturado (2S)", "enviar por célula (seção 3)"],
       ["RSSI caindo na descida", "antena do foguete na horizontal / polarização", "antena ao longo do corpo; normal até ~25 dB"]],
      [42, 60, 68])

# 8 melhorias
H1("8. Melhorias recomendadas")
H2("8.1 Pacote de status (compatível com o tracker atual)")
P("Um segundo pacote, a 1 Hz, com outro byte mágico, leva o que o pacote principal não tem. O tracker atual o <b>ignora sozinho</b>, porque o tamanho ou o "
  "magic é diferente, então nada quebra. Uma versão nova do tracker pode mostrá-lo no OLED.")
code(["struct __attribute__((packed)) StatusPacket {   // 12 bytes, 1 Hz",
      "  uint8_t  magic;      // 0xA6  (o tracker atual descarta: não é 0xA5)",
      "  uint8_t  state;      // PREPARO, RAMPA, PROPULSAO, COAST, APOGEU, DESCIDA, POUSO",
      "  uint16_t seq;",
      "  uint8_t  pyro;       // bit0/1 = continuidade, bit2/3 = disparado",
      "  uint8_t  votes;      // bits: baro / IMU / GPS / timer indicaram apogeu",
      "  int16_t  maxAlt;     // dm, apogeu registrado",
      "  uint8_t  sdOk;       // 1 = gravando no microSD",
      "  uint8_t  vcell;      // 20 mV por célula",
      "  uint16_t crc16;      // CRC extra (opcional)",
      "};"])
H2("8.2 Outras ideias")
B(["<b>Tracker com GPS próprio</b> (um NEO-M8N de R$ 60): dispensa o passo BASE com a placa em cima e evita erro se o tracker for montado depois.",
   "<b>Registrar a última posição na flash do tracker</b>: se o tracker reiniciar depois do pouso, a posição de resgate não se perde.",
   "<b>Antena do VTX no próprio pan/tilt</b>: uma antena patch de 5,8 GHz montada junto da Yagi aumenta muito o alcance do vídeo (vale para receptores com entrada de antena externa).",
   "<b>Placa F-500 v2 como tracker reserva</b>: como os pinos de rádio são os mesmos, uma placa sem ignitores (J9/J10 vazios, ARME aberto) pode receber os pacotes em emergência. "
   "Isso exige um firmware próprio que <b>nunca</b> use IO32/IO33."])

# 9 testes
H1("9. Testes de integração antes do voo")
table([["#", "Teste", "Como", "Critério"],
       ["1", "Bancada", "placa e tracker a 1 m; ver o CSV", "seq contínuo, RSSI > −50 dBm, campos coerentes"],
       ["2", "Simulação dos servos", "tracker com SIMULATE = 1", "movimento suave; flip correto"],
       ["3", "Campo: BASE + ALINHAR", "procedimento da seção 5 no campo de lançamento", "2 e 3 bipes; az/el plausíveis"],
       ["4", "Caminhada", "andar com a placa em volta do tracker a ~100 m", "a antena acompanha; flip ao passar por trás"],
       ["5", "Drone/pipa (opcional)", "placa erguida a 100–300 m", "elevação correta; GPS e barômetro coerentes"],
       ["6", "Alcance", "placa a ≥ 1,5 km, em visada", "> 90 % dos pacotes; margem > 20 dB"],
       ["7", "Perda de GPS", "cobrir a antena do GPS durante o teste 4", "tracker em modo barômetro sem pular"],
       ["8", "Reboot", "reiniciar a placa depois do ALINHAR", "conferir o erro de altura → reforça a regra de não reiniciar"]],
      [8, 36, 66, 60])

# apêndice
H1("Apêndice — Constantes dos dois firmwares")
table([["Constante", "Valor", "Arquivo", "Significado"],
       ["TX_HZ / GPS_NAV_HZ", "5 / 5", "foguete_tx", "taxa do pacote e do GPS"],
       ["LORA_POWER_DBM", "14", "foguete_tx", "potência (o RFM95W vai até 20 dBm)"],
       ["DYN_MODEL_AIRBORNE4g", "—", "foguete_tx", "modelo dinâmico do GPS para foguete"],
       ["LEAD_S", "0,15 s", "tracker_rx", "adiantamento para compensar atrasos"],
       ["MAX_PREDICT_S", "1,5 s", "tracker_rx", "limite da extrapolação"],
       ["LINK_LOST_MS", "2000 ms", "tracker_rx", "tempo até o aviso de link perdido"],
       ["SLEW_DEG_S", "200 °/s", "tracker_rx", "velocidade máxima dos servos"],
       ["Histerese do flip", "95° / 85°", "tracker_rx", "entra e sai do modo flip"],
       ["SERVO_MIN/MAX_US", "500 / 2500 µs", "tracker_rx", "faixa de pulso dos servos de 180°"]],
      [40, 26, 26, 78])

class Doc(BaseDocTemplate):
    def afterFlowable(self, f):
        if hasattr(f, "_toc"):
            lvl, txt = f._toc; key = "h%d" % id(f)
            self.canv.bookmarkPage(key); self.canv.addOutlineEntry(txt, key, lvl, closed=lvl > 0)
            self.notify("TOCEntry", (lvl, txt, self.page, key))
def deco(c, d):
    c.saveState()
    c.setFillColor(NAVY); c.rect(0, A4[1] - 9 * mm, A4[0], 9 * mm, fill=1, stroke=0)
    c.setFillColor(GREEN); c.rect(0, A4[1] - 10 * mm, A4[0], 1 * mm, fill=1, stroke=0)
    c.setFont("Bold", 8.5); c.setFillColor(colors.white); c.drawString(20 * mm, A4[1] - 6 * mm, "F-500 v2 + ANTENA TRACKER")
    c.setFont("Body", 8); c.drawRightString(A4[0] - 20 * mm, A4[1] - 6 * mm, "UTFPR Rocket · documentação de integração")
    c.setFillColor(GREY); c.drawRightString(A4[0] - 20 * mm, 10 * mm, f"{d.page}")
    c.drawString(20 * mm, 10 * mm, "917 MHz · SF7 · BW250 · 26 B @ 5 Hz")
    c.restoreState()
def cover(c, d):
    c.saveState(); c.setFillColor(NAVY); c.rect(0, A4[1] - 14 * mm, A4[0], 14 * mm, fill=1, stroke=0)
    c.setFillColor(GREEN); c.rect(0, A4[1] - 15.5 * mm, A4[0], 1.5 * mm, fill=1, stroke=0); c.restoreState()
doc = Doc(OUT, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=18 * mm, bottomMargin=17 * mm,
          title="F-500 v2 + Antena Tracker — Integração", author="UTFPR Rocket")
fr = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")
doc.addPageTemplates([PageTemplate("cover", [fr], onPage=cover), PageTemplate("normal", [fr], onPage=deco)])
story.insert(1, NextPageTemplate("normal"))
doc.multiBuild(story)
print("ok", OUT)
