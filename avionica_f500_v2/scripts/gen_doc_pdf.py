import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
                                Image, PageBreak, KeepTogether, NextPageTemplate, CondPageBreak)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon, Group
from reportlab.graphics import renderPDF

F = "/System/Library/Fonts/Supplemental/"
pdfmetrics.registerFont(TTFont("Body", F + "Arial Unicode.ttf"))
pdfmetrics.registerFont(TTFont("Bold", F + "Arial Bold.ttf"))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily("Body", normal="Body", bold="Bold", italic="Body", boldItalic="Bold")

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # pasta do projeto, relativa ao script
OUT = PROJ + "/docs/Avionica_F-500_v2_Documentacao.pdf"
SCH_IMG = "/private/tmp/claude-501/-Users-joaoscacchetti/dbc86579-630d-4506-9d29-0b21625bdfb7/scratchpad/pdf/esquematico.pdf.png"

NAVY = colors.HexColor("#14213D"); ORANGE = colors.HexColor("#E76F24"); GREY = colors.HexColor("#5C6370")
LIGHT = colors.HexColor("#EEF1F6"); GREEN = colors.HexColor("#2A9D8F"); RED = colors.HexColor("#C0392B")
YEL = colors.HexColor("#F4D35E")

ss = {}
ss["body"] = ParagraphStyle("body", fontName="Body", fontSize=10, leading=14.2, alignment=TA_JUSTIFY, spaceAfter=6)
ss["bul"] = ParagraphStyle("bul", parent=ss["body"], leftIndent=12, bulletIndent=2, spaceAfter=3, alignment=TA_LEFT)
ss["h1"] = ParagraphStyle("h1", fontName="Bold", fontSize=18, leading=22, textColor=NAVY, spaceBefore=4, spaceAfter=10)
ss["h2"] = ParagraphStyle("h2", fontName="Bold", fontSize=13, leading=17, textColor=ORANGE, spaceBefore=10, spaceAfter=5)
ss["h3"] = ParagraphStyle("h3", fontName="Bold", fontSize=10.5, leading=14, textColor=NAVY, spaceBefore=6, spaceAfter=3)
ss["cell"] = ParagraphStyle("cell", fontName="Body", fontSize=8.6, leading=11)
ss["cellb"] = ParagraphStyle("cellb", fontName="Bold", fontSize=8.6, leading=11, textColor=colors.white)
ss["cap"] = ParagraphStyle("cap", fontName="Body", fontSize=8.5, leading=11, textColor=GREY, alignment=TA_CENTER, spaceAfter=8)
ss["box"] = ParagraphStyle("box", parent=ss["body"], fontSize=9.6, leading=13.5, spaceAfter=0)
ss["toc1"] = ParagraphStyle("toc1", fontName="Body", fontSize=11, leading=17, leftIndent=0)
ss["toc2"] = ParagraphStyle("toc2", fontName="Body", fontSize=9.5, leading=13, leftIndent=14, textColor=GREY)

story = []
def P(t, s="body"): story.append(Paragraph(t, ss[s]))
def H1(t):
    story.append(CondPageBreak(60 * mm)); p = Paragraph(t, ss["h1"]); p._toc = (0, t); story.append(p)
def H2(t):
    story.append(CondPageBreak(35 * mm)); p = Paragraph(t, ss["h2"]); p._toc = (1, t); story.append(p)
def H3(t): story.append(Paragraph(t, ss["h3"]))
def B(items):
    for it in items: story.append(Paragraph(it, ss["bul"], bulletText="•"))
    story.append(Spacer(1, 3))
def SP(h=4): story.append(Spacer(1, h * mm))

def table(rows, widths, head=True, zebra=True, fs=None):
    data = []
    for i, r in enumerate(rows):
        data.append([Paragraph(str(c), ss["cellb"] if (head and i == 0) else ss["cell"]) for c in r])
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1 if head else 0)
    st = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C9CED6")),
          ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
          ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    if head: st.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
    if zebra:
        for i in range(1 if head else 0, len(rows)):
            if i % 2 == 0: st.append(("BACKGROUND", (0, i), (-1, i), LIGHT))
    t.setStyle(TableStyle(st)); story.append(t); SP(3)

def callout(title, text, color=ORANGE):
    inner = [Paragraph(f"<b>{title}</b>", ParagraphStyle("ct", parent=ss["box"], textColor=color, fontName="Bold")),
             Paragraph(text, ss["box"])]
    t = Table([[inner]], colWidths=[170 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF6EF") if color == ORANGE else LIGHT),
                           ("LINEBEFORE", (0, 0), (0, -1), 3, color), ("LEFTPADDING", (0, 0), (-1, -1), 8),
                           ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story.append(t); SP(3)

def img(path, w_mm, caption=None):
    from reportlab.lib.utils import ImageReader
    ir = ImageReader(path); iw, ih = ir.getSize()
    w = w_mm * mm; h = w * ih / iw
    story.append(Image(path, width=w, height=h))
    if caption: P(caption, "cap")

# ---------- diagramas ----------
def box(d, x, y, w, h, title, sub="", fill=LIGHT, stroke=NAVY, tc=NAVY):
    d.add(Rect(x, y, w, h, rx=4, ry=4, fillColor=fill, strokeColor=stroke, strokeWidth=1))
    d.add(String(x + w / 2, y + h - 12, title, fontName="Bold", fontSize=8.2, fillColor=tc, textAnchor="middle"))
    for i, s in enumerate(sub.split("\n") if sub else []):
        d.add(String(x + w / 2, y + h - 23 - 9 * i, s, fontName="Body", fontSize=6.8, fillColor=GREY, textAnchor="middle"))
def arrow(d, x1, y1, x2, y2, label="", color=GREY, lw=1):
    d.add(Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=lw))
    import math
    a = math.atan2(y2 - y1, x2 - x1); L = 5
    d.add(Polygon([x2, y2, x2 - L * math.cos(a - 0.4), y2 - L * math.sin(a - 0.4), x2 - L * math.cos(a + 0.4), y2 - L * math.sin(a + 0.4)],
                  fillColor=color, strokeColor=color))
    if label:
        d.add(String((x1 + x2) / 2 + 3, (y1 + y2) / 2 + 3, label, fontName="Body", fontSize=6.3, fillColor=color))

def block_diagram():
    d = Drawing(170 * mm, 120 * mm)
    W = 170 * mm
    # MCU
    box(d, 190, 150, 105, 70, "ESP32-DevKitC", "MCU dual-core 240 MHz\nmáquina de estados\nwatchdog + RTC RAM", fill=colors.HexColor("#DDE6F5"))
    # left: power
    box(d, 5, 270, 110, 60, "BATERIA LiPo 2S", "XT30 · 7,4 V nominal\nchave principal (J2)", fill=colors.HexColor("#FDE8D7"), stroke=ORANGE)
    box(d, 5, 190, 110, 58, "ALIMENTAÇÃO", "SS34 (anti-inversão)\n470 µF hold-up\nMP1584 5 V → LDO 3V3", fill=colors.HexColor("#FDE8D7"), stroke=ORANGE)
    box(d, 5, 105, 110, 62, "RECUPERAÇÃO", "chave de ARME (J8)\nPYRO1 apogeu · PYRO2 backup\ncontinuidade nos 2 canais", fill=colors.HexColor("#F9D6D2"), stroke=RED)
    box(d, 5, 20, 110, 62, "CÂMERA / VTX", "VBAT chaveado (CAM_EN)\nUART MSP (OSD/gravação)\ngrava a bordo + transmite", fill=colors.HexColor("#E3F2EF"), stroke=GREEN)
    # right
    box(d, 370, 270, 105, 60, "LoRa RFM95W", "917 MHz · SF7 BW250\n26 B @ 5 Hz → tracker\nSMA 50 Ω", fill=colors.HexColor("#DDE6F5"))
    box(d, 370, 190, 105, 58, "GPS u-blox M8N", "UART2 · 5 Hz\nposição, vN/vE/vD", fill=colors.HexColor("#DDE6F5"))
    box(d, 370, 105, 105, 62, "SENSORES", "BMP280 (I2C 0x76)\nIMU no J5 (I2C)\nVBAT ÷5,5 no ADC", fill=colors.HexColor("#DDE6F5"))
    box(d, 370, 20, 105, 62, "LOG / SINALIZAÇÃO", "microSD (SPI) · flash interna\nLEDs + buzzer", fill=colors.HexColor("#DDE6F5"))
    # arrows
    arrow(d, 60, 270, 60, 248, "VBAT", ORANGE, 1.4)
    arrow(d, 115, 220, 190, 205, "+5V / +3V3", ORANGE, 1.4)
    arrow(d, 190, 165, 115, 140, "FIRE / SENSE", RED)
    arrow(d, 190, 158, 115, 60, "CAM_EN / UART1", GREEN)
    arrow(d, 295, 205, 370, 290, "SPI", NAVY)
    arrow(d, 370, 215, 295, 195, "UART2", NAVY)
    arrow(d, 370, 135, 295, 175, "I2C / ADC", NAVY)
    arrow(d, 295, 160, 370, 55, "SPI / GPIO", NAVY)
    arrow(d, 60, 190, 60, 167, "VBAT_SW→ARME", RED)
    # ground segment
    box(d, 190, 270, 105, 60, "SOLO", "tracker_rx (antena pan/tilt)\nóculos do VTX (DVR)", fill=colors.white, stroke=GREY)
    arrow(d, 370, 305, 295, 305, "rádio 917 MHz", NAVY)
    arrow(d, 115, 40, 240, 270, "vídeo 5,8 GHz", GREEN)
    return d

def data_diagram():
    d = Drawing(170 * mm, 76 * mm)
    box(d, 5, 75, 100, 110, "SENSORES", "BMP280 100 Hz\nIMU 200–500 Hz\nGPS 5 Hz\nVBAT / continuidade 10 Hz\nestado da máquina", fill=LIGHT)
    box(d, 150, 115, 90, 65, "BUFFER RAM", "registros com CRC16\nring buffer 2×32 kB\n(tarefa de alta prioridade)", fill=colors.HexColor("#DDE6F5"))
    box(d, 290, 140, 180, 45, "1  microSD  (log COMPLETO)", "todos os campos, taxa máxima · flush 1 s", fill=colors.HexColor("#E3F2EF"), stroke=GREEN)
    box(d, 290, 82, 180, 45, "2  Flash interna  (log ESSENCIAL)", "LittleFS ~1,5 MB · 20 Hz · sobrevive se o SD falhar", fill=colors.HexColor("#E3F2EF"), stroke=GREEN)
    box(d, 290, 30, 180, 45, "3  Rádio LoRa  (RESUMO ao vivo)", "pacote de 26 B · 5 Hz · o que não cabe fica no 1 e no 2", fill=colors.HexColor("#FDE8D7"), stroke=ORANGE)
    arrow(d, 105, 140, 150, 145, "", NAVY, 1.2)
    arrow(d, 240, 160, 290, 162, "", GREEN, 1.2)
    arrow(d, 240, 140, 290, 104, "", GREEN, 1.2)
    arrow(d, 240, 125, 290, 52, "", ORANGE, 1.2)
    d.add(String(8, 12, "Câmera: vídeo gravado no cartão da própria câmera + DVR nos óculos (canal independente da aviônica)",
                 fontName="Body", fontSize=7.2, fillColor=GREY))
    d.add(String(8, 2, "Tracker: grava em CSV no solo tudo o que recebe (cópia em terra dos dados de telemetria)",
                 fontName="Body", fontSize=7.2, fillColor=GREY))
    return d

def fsm_diagram():
    d = Drawing(170 * mm, 52 * mm)
    st = [("PREPARO", "solo, desarmado"), ("RAMPA", "armado, pronto"), ("PROPULSÃO", "a > 3 g por 100 ms"),
          ("COASTING", "motor apagou"), ("APOGEU", "PYRO1 → PYRO2"), ("DESCIDA", "paraquedas"), ("POUSO", "beep + GPS")]
    w, h, gap = 62, 40, 9.5
    for i, (a, b) in enumerate(st):
        x = 4 + i * (w + gap)
        col = RED if a == "APOGEU" else (ORANGE if a in ("PROPULSÃO", "COASTING") else NAVY)
        d.add(Rect(x, 70, w, h, rx=5, ry=5, fillColor=colors.white, strokeColor=col, strokeWidth=1.3))
        d.add(String(x + w / 2, 70 + h - 15, a, fontName="Bold", fontSize=7.2, fillColor=col, textAnchor="middle"))
        d.add(String(x + w / 2, 70 + 10, b, fontName="Body", fontSize=5.6, fillColor=GREY, textAnchor="middle"))
        if i < len(st) - 1: arrow(d, x + w, 90, x + w + gap, 90, "", GREY)
    d.add(String(4, 40, "Transições com confirmação dupla (dois sensores ou sensor + tempo) e janelas mínimas de tempo; o estado fica",
                 fontName="Body", fontSize=7, fillColor=GREY))
    d.add(String(4, 29, "salvo na RTC RAM e na flash: se o ESP32 reiniciar no ar, ele volta ao estado em que estava e não repete nem perde disparos.",
                 fontName="Body", fontSize=7, fillColor=GREY))
    return d

# ================= CONTEÚDO =================
# capa
story.append(Spacer(1, 18 * mm))
story.append(Paragraph("AVIÔNICA F-500 v2", ParagraphStyle("t", fontName="Bold", fontSize=30, leading=34, textColor=NAVY)))
story.append(Paragraph("Computador de bordo com telemetria para antena tracker, câmera digital e recuperação redundante",
                       ParagraphStyle("st", fontName="Body", fontSize=14, leading=19, textColor=ORANGE, spaceAfter=10)))
story.append(Paragraph("Documentação do projeto · rev. B · UTFPR Rocket · 08/11/2026",
                       ParagraphStyle("st2", fontName="Body", fontSize=10.5, textColor=GREY, spaceAfter=10)))
img(PROJ + "/docs/pcb_3d.png", 165)
callout("Princípio do projeto: redundância acima de tudo",
        "Nenhuma falha isolada pode impedir a abertura do paraquedas nem causar perda dos dados do voo. "
        "A recuperação conta com <b>duas cargas</b>, <b>três fontes de detecção de apogeu</b> e um <b>temporizador de segurança</b>. "
        "Os dados ficam guardados em <b>quatro lugares</b>: rádio, cartão microSD, memória flash interna e o registro do tracker em solo. "
        "O vídeo vai por um <b>canal separado</b>. "
        "<b>Quando o rádio não comporta todos os dados, eles continuam salvos no microSD e na flash.</b>")
story.append(PageBreak())

# sumário
story.append(Paragraph("Sumário", ss["h1"]))
toc = TableOfContents(); toc.levelStyles = [ss["toc1"], ss["toc2"]]; story.append(toc)
story.append(PageBreak())

# 1
H1("1. Visão geral")
P("A Aviônica F-500 v2 é o computador de bordo do foguete F-500, projetado para um apogeu de aproximadamente "
  "<b>500 m</b>. Ela substitui a placa F-500 v1 (projeto <i>rayquasa</i>) e foi refeita segundo o Guia de PCB das correções do "
  "Payload 2026: esquemático em blocos, regras de fabricação do PCBWay, desacoplamento de 100 nF em cada alimentação "
  "e placa de até 100 × 100 mm.")
H2("1.1 Objetivos")
table([["#", "Objetivo", "Como a placa atende"],
       ["O1", "Recuperar o foguete inteiro", "2 canais pirotécnicos, detecção de apogeu por 3 sensores + temporizador, chave de arme física"],
       ["O2", "Acompanhar o voo ao vivo pela antena tracker", "LoRa 917 MHz com <b>o mesmo pacote e os mesmos pinos do tracker_rx</b>: o tracker não precisa mudar"],
       ["O3", "Filmar e transmitir a subida", "conector para câmera/VTX digital (DJI O4 / Walksnail) com alimentação controlada e UART"],
       ["O4", "Não perder dados", "log completo no microSD, log essencial na flash interna, resumo pelo rádio, cópia no tracker"],
       ["O5", "Localizar o foguete após o pouso", "GPS contínuo pelo rádio, buzzer de localização e LEDs de estado"]],
      [10, 52, 108])
H2("1.2 Especificações da placa")
table([["Item", "Valor"],
       ["Dimensões", "60 × 100 mm, 2 camadas, FR-4 1,6 mm, cobre 1 oz, 4 furos M3 nos cantos"],
       ["Fabricação", "Regras do PCBWay importadas (trilha/isolação mín. 0,127 mm, via 0,5/0,3 mm, anel 0,25 mm)"],
       ["Montagem", "SMD 0805 / SOT-23 / SMA com pads HandSolder (dá para soldar no ferro) + módulos em barra de pinos"],
       ["Alimentação", "LiPo 2S (6,4–8,4 V) por XT30; buck 5 V 3 A; 3,3 V pelo LDO do DevKit"],
       ["Consumo estimado", "≈ 0,54 A de VBAT na eletrônica + até ≈ 1,6 A na câmera + pulso de ≈ 3 A nos ignitores"],
       ["Rádio", "RFM95W (SX1276) 917 MHz, até +20 dBm, antena externa por SMA de borda"],
       ["Componentes", "58 itens (lista em docs/BOM.csv)"]],
      [38, 132])
story.append(PageBreak())
H2("1.3 Arquitetura")
story.append(block_diagram())
P("Figura 1 — Diagrama de blocos. Laranja: energia; vermelho: recuperação; verde: vídeo; azul: dados.", "cap")

# 2 redundância
H1("2. Filosofia de redundância")
P("A falha mais grave em um foguete é o paraquedas não abrir. Em seguida vem perder os dados do voo, que são justamente o que "
  "permite entender e corrigir a falha. Por isso cada função crítica tem pelo menos duas vias independentes, e sempre que possível "
  "elas usam <b>princípios físicos diferentes</b> (redundância dissimilar). Assim, o mesmo defeito não derruba as duas vias.")
table([["Função crítica", "Via principal", "Via de backup", "Último recurso"],
       ["Detectar o apogeu", "Barômetro BMP280 (altitude passou do pico e caiu Δh)", "IMU no J5 (velocidade vertical integrada ≤ 0) e GPS (vD > 0)",
        "Temporizador: tempo de apogeu da simulação OpenRocket + margem"],
       ["Abrir o paraquedas", "PYRO1 dispara no apogeu", "PYRO2 dispara 2 s depois (ou após 15 m de queda), em carga separada",
        "Altímetro comercial independente, com bateria própria (recomendado)"],
       ["Energia da lógica", "LiPo 2S → buck", "470 µF + diodo SS34 seguram a lógica durante o pulso do ignitor",
        "Brownout do ESP32 + estado salvo na RTC RAM"],
       ["Guardar os dados", "microSD: tudo, na taxa máxima", "Flash interna do ESP32: essencial a 20 Hz", "Telemetria + CSV do tracker em solo"],
       ["Localizar após o pouso", "Último GPS recebido pelo tracker", "Buzzer e LEDs", "Vídeo/DVR e rastreio visual"],
       ["Vídeo", "Gravação a bordo, no cartão da câmera", "DVR nos óculos (transmissão 5,8 GHz)", "—"]],
      [30, 45, 52, 43])
callout("Regra de ouro dos dados",
        "O rádio leva só o <b>resumo</b>: 26 bytes a 5 Hz. Isso é suficiente para o tracker apontar a antena e para acompanhar o voo. "
        "<b>Todo o resto</b> vai para o microSD, na taxa máxima, e uma cópia essencial vai para a flash interna. "
        "Se o enlace cair, se o pacote for curto demais ou se o rádio falhar, nenhum dado se perde. Nada é descartado só porque não coube no pacote.",
        GREEN)
H2("2.1 Por que três fontes para o apogeu")
B(["<b>Barômetro:</b> é preciso e direto. Porém sofre com rajadas de pressão (efeito Venturi) e com o salto de pressão no transônico, "
   "e erra se a ventilação do compartimento for mal dimensionada.",
   "<b>IMU:</b> não depende de pressão, então não é afetada por esses problemas. Em compensação acumula erro de integração. "
   "Num voo curto (~10 s até o apogeu), esse erro é aceitável.",
   "<b>GPS:</b> fornece a velocidade vertical (vD) diretamente. Por outro lado, perde o fix sob alta aceleração e tem latência de 200 ms. "
   "Por isso entra como confirmação.",
   "<b>Votação:</b> a carga 1 dispara quando <b>2 de 3</b> fontes indicam apogeu, ou quando o barômetro indica com confirmação de 300 ms. "
   "O temporizador dispara de qualquer jeito se nenhuma fonte tiver disparado até T<sub>apogeu</sub> + 2 s.",
   "<b>Bloqueios de segurança:</b> nada dispara antes de a decolagem ser detectada (a > 3 g por 100 ms). "
   "Também não dispara antes do tempo mínimo de queima do motor nem com a chave de ARME aberta."])

# 3 módulos
H1("3. Módulos: o que cada um faz")
P("Cada bloco abaixo corresponde a um bloco tracejado do esquemático. Para cada um, a tabela mostra a função, como ele se liga ao "
  "ESP32 e qual o seu papel na redundância.")

def modulo(nome, func, itens, red, cuidados=None):
    H2(nome)
    P(func)
    table([["Componente", "Detalhe"]] + itens, [42, 128])
    callout("Papel na redundância", red, GREEN)
    if cuidados: B(cuidados)

modulo("3.1 Alimentação e medição da bateria (bloco 1)",
       "Recebe a bateria e distribui energia para todo o sistema. A tensão da bateria é medida o tempo todo, para registro e para a decisão de "
       "lançar ou não.",
       [["J1 · XT30", "Entrada da LiPo 2S. O conector tem polaridade mecânica, então não encaixa invertido"],
        ["J2 · chave principal", "Chave externa (de parafuso ou slide) acessível pelo lado de fora do foguete; liga toda a eletrônica"],
        ["D1 · SS34", "Diodo Schottky de 3 A: protege contra bateria invertida e impede que o pulso dos ignitores puxe a lógica para baixo"],
        ["C1 470 µF + C2 10 µF", "Reserva de energia (hold-up) depois do diodo: segura a lógica durante a queda de tensão no disparo"],
        ["U2 · MP1584EN", "Buck 5 V / 3 A, eficiência de ~90 %; alimenta o ESP32, o GPS e o buzzer (C3/C4 na saída)"],
        ["LDO do DevKit", "Gera os 3,3 V do ESP32, do rádio, do BMP280 e do microSD"],
        ["R1/R2/C5", "Divisor 100k/22k (÷5,545) + filtro → IO34 (ADC): mede a VBAT"]],
       "O diodo e o banco de capacitores separam o lado da <b>lógica</b> do lado dos <b>ignitores</b>. Um ignitor em curto ou o "
       "pico de corrente do disparo não reinicia o computador. A chave de arme é alimentada <b>antes</b> do diodo, justamente "
       "para que o pulso não passe pelo lado da lógica.",
       ["Antes do voo, a VBAT deve estar ≥ 7,6 V (3,8 V/célula). O firmware bloqueia o arme abaixo de 7,2 V.",
        "A furação do footprint do MP1584 é uma suposição (±9,5 × ±6,5 mm). Confira com o módulo comprado."])

modulo("3.2 Microcontrolador ESP32-DevKitC (bloco 4)",
       "É o cérebro do sistema. Lê todos os sensores, roda a máquina de estados do voo, decide os disparos, monta o pacote de "
       "telemetria e grava os logs. O núcleo 1 cuida dos sensores e das decisões de voo; o núcleo 0 cuida do rádio, do cartão e da câmera.",
       [["Placa", "ESP32-DevKitC-32E em barra fêmea, deitado, com a USB na borda direita para gravar o firmware com a placa montada"],
        ["Desacoplamento", "C6 100 nF no 3V3 e C7 100 nF no 5V, junto aos pinos"],
        ["Pinos de disparo", "IO32/IO33: pinos sem função de boot, então não há risco de disparo durante a inicialização"],
        ["Antena Wi-Fi", "Área sem cobre embaixo; o Wi-Fi só é usado em solo, para baixar os logs"]],
       "Há um <b>watchdog</b> por tarefa: se uma tarefa travar, o chip reinicia. O estado do voo é salvo na <b>RTC RAM</b> e na flash. "
       "Depois de um reset no ar, o ESP32 retoma o estado anterior: não repete um disparo já feito e não perde o próximo. "
       "Os pinos PYRO são forçados a nível baixo na primeira linha do setup().")

modulo("3.3 Telemetria LoRa (bloco 2)",
       "Envia ao solo, ao vivo, a posição, a altitude e a velocidade do foguete. O tracker usa esses dados para apontar a antena. "
       "O rádio foi escolhido para ser <b>100 % compatível com o tracker_rx que já existe</b>.",
       [["U3 · RFM95W", "SX1276, 917 MHz, SF7, BW 250 kHz, CR 4/5. Pinos SCK18/MISO19/MOSI23/NSS5/DIO0-26/RST14, iguais aos do tracker"],
        ["J3 · SMA", "Antena externa de 915 MHz (dipolo ou monopolo de ¼ de onda), trilha de 50 Ω curta"],
        ["C8/C9", "10 µF + 100 nF junto ao pino 3,3 V do módulo (o pico de TX chega a 120 mA)"],
        ["Pacote", "26 bytes: lat, lon, altitude GPS, altitude barométrica, vN/vE/vD, satélites, VBAT, flags, contador"],
        ["Capacidade", "≈ 10,9 kbit/s brutos; 26 B a 5 Hz ocupa ~16 % do canal (33 ms no ar a cada 200 ms)"]],
       "O rádio <b>não é</b> o registro oficial do voo. Ele é a via ao vivo. O tracker continua apontando por <b>predição</b> "
       "(até 1,5 s) e pelo barômetro quando o GPS perde o fix. Depois do pouso, o rádio continua enviando a posição por até 2 horas, "
       "e isso é fundamental para achar o foguete.",
       ["Com 2S, envie a VBAT <b>por célula</b> (o campo tem passo de 20 mV, máx. 5,1 V) para manter o protocolo do tracker.",
        "Opcional: um 2º pacote, a cada 1 s, com estado da máquina, continuidade e status do SD. O tracker antigo ignora esse pacote, porque o byte mágico é diferente."])

modulo("3.4 Sensores, GPS e log (bloco 5)",
       "Mede o voo e guarda tudo.",
       [["U4 · BMP280", "Barômetro I2C (0x76) com 100 nF próprio; altitude relativa com resolução de ~0,2 m. Precisa de furos de ventilação no compartimento"],
        ["J5 · I2C extra", "Para a <b>IMU</b> (3V3/GND/SDA/SCL). Recomendada: BMI088 ou ICM-42688 (±24 g / ±16 g). <b>Obrigatória para a redundância do apogeu</b>"],
        ["J6 · GPS (cabo)", "u-blox NEO-M8N a 5 V, UART2 (IO16/IO17), modo AIRBORNE 4 g, 5 Hz. A antena fica na ogiva, com vista para o céu"],
        ["J7 · microSD", "Soquete Molex 104031 a 3,3 V direto no SPI (CS em IO15), pull-ups de 10 k, 10 µF + 100 nF"],
        ["Flash interna", "~1,5 MB em LittleFS no próprio ESP32: segunda cópia do log, sem hardware extra"]],
       "<b>Três</b> fontes de altitude/velocidade (barômetro, IMU e GPS) e <b>dois</b> meios de armazenamento (microSD e flash). "
       "Se o cartão soltar com o impacto ou corromper, a flash ainda guarda a curva do voo a 20 Hz.")

modulo("3.5 Recuperação: 2 canais pirotécnicos (bloco 6)",
       "Aciona as cargas de ejeção do paraquedas.",
       [["J8 · chave de ARME", "Chave física separada que leva VBAT aos ignitores. Desligada, <b>é impossível disparar</b>, mesmo com firmware defeituoso"],
        ["Q1/Q2 · AO3400A", "MOSFET N de porta lógica (3,3 V); 5,7 A contínuos, 30 A de pulso: acende qualquer e-match"],
        ["R9/R13 100 Ω, R10/R14 10 k", "Resistor de porta + pull-down: o MOSFET fica desligado enquanto o ESP32 está em reset ou sem firmware"],
        ["R11/R12, R15/R16", "Divisor 100k/22k → IO35/IO36: lê a <b>continuidade</b> do ignitor (≈ 1,5 V = ligado, 0 V = aberto)"],
        ["J9/J10 · bornes", "Bornes de parafuso de 3,5 mm: o fio do ignitor não solta com a vibração"]],
       "Dois canais com <b>cargas e ignitores separados</b>. A falha de um ignitor, de um MOSFET ou de uma carga não impede a abertura. "
       "A continuidade é verificada na rampa (o buzzer indica o resultado) e registrada no log. "
       "Para redundância total, recomenda-se um <b>altímetro comercial independente</b>, com bateria própria, ligado a uma terceira carga.",
       ["PYRO1: apogeu (votação 2 de 3). PYRO2: 2 s depois, ou após 15 m de queda, ou T<sub>apogeu</sub> + 3 s pelo temporizador.",
        "Dispare por 1 s (corrente limitada pela bateria). Depois, o firmware trava o canal e registra o disparo."])

modulo("3.6 Câmera / VTX digital (bloco 3)",
       "Filma a subida em alta resolução e transmite o vídeo ao vivo para o solo.",
       [["Q3 · AO3401A + Q4 · AO3400A", "Chave de alimentação: o ESP32 liga a câmera pelo IO4 (CAM_EN). Ela fica desligada na espera e liga na contagem"],
        ["C10 100 µF + C11 100 nF", "Reserva junto ao conector, para os picos de corrente do transmissor"],
        ["J4 · conector", "VBAT_CAM, GND, TX (IO25) e RX (IO13): UART1 para MSP/OSD"],
        ["Câmera sugerida", "DJI O4 Air Unit (grava 4K a bordo e transmite 1080p para os óculos), Walksnail Avatar ou FPV analógica + RunCam Split"]],
       "O vídeo é um <b>canal independente</b> da aviônica. Ele é gravado no cartão da própria câmera e, ao mesmo tempo, no DVR dos óculos. "
       "Pelo MSP, o ESP32 envia altitude e velocidade para o OSD, então o vídeo também serve como registro de telemetria. "
       "Uma falha da câmera não afeta a recuperação, porque a alimentação é chaveada e separada por MOSFET.",
       ["A antena do VTX precisa ficar em seção de fibra de vidro, papelão ou plástico (fibra de carbono e alumínio bloqueiam o sinal) e longe da antena LoRa.",
        "O VTX esquenta sem fluxo de ar: ligue só na contagem (T−60 s) e confira a faixa de entrada (2S)."])

modulo("3.7 Sinalização (bloco 7)",
       "Mostra o estado do sistema sem precisar de computador, o que é essencial na rampa.",
       [["D2 · LED verde (IO2)", "Pisca = solo OK; aceso = armado e pronto; piscada dupla = gravando no SD"],
        ["D3 · LED vermelho (IO12)", "Aceso = falha (SD, sensor, bateria baixa ou continuidade aberta)"],
        ["BZ1 · buzzer ativo + Q5", "Códigos de bipes (tabela na seção 6.3) e bipe de localização após o pouso"]],
       "Permite checar a continuidade e o estado de cada sensor <b>sem abrir o foguete</b>, o que reduz o erro humano na rampa.")

# 4 dados
H1("4. Estratégia de dados: rádio, microSD e flash")
P("O rádio não tem banda para tudo. O voo completo gera cerca de 6 kB/s (IMU a 200 Hz, barômetro a 100 Hz, GPS, estados). "
  "Já o LoRa em SF7/BW250 transmite, na prática, menos de 1 kB/s, e o tracker espera 5 Hz. Por isso os dados seguem quatro "
  "caminhos com prioridades diferentes:")
story.append(data_diagram())
P("Figura 2 — Caminho dos dados. O que não cabe no rádio fica gravado no microSD e na flash interna.", "cap")
H2("4.1 O que vai para cada lugar")
table([["Dado", "Taxa", "microSD", "Flash", "Rádio"],
       ["Aceleração e giro (IMU)", "200–500 Hz", "✔ completo", "20 Hz", "—"],
       ["Pressão / altitude barométrica", "100 Hz", "✔", "20 Hz", "5 Hz (altitude)"],
       ["GPS (lat, lon, alt, vN/vE/vD, sats, fix)", "5 Hz", "✔", "✔", "✔ 5 Hz"],
       ["Estado da máquina e eventos (decolagem, apogeu, disparos)", "evento", "✔", "✔", "flags + pacote de status"],
       ["Continuidade PYRO1/2, VBAT, temperatura", "10 Hz", "✔", "2 Hz", "VBAT 5 Hz"],
       ["Votos de apogeu (baro/IMU/GPS/timer)", "evento", "✔", "✔", "status"],
       ["Status do SD / contadores de erro", "1 Hz", "✔", "✔", "status 1 Hz"]],
      [62, 22, 26, 22, 38])
H2("4.2 Como evitar perder o log do cartão")
B(["<b>Um arquivo novo a cada boot</b> (FLIGHT_000.BIN, 001…). Nunca se sobrescreve um voo anterior.",
   "<b>Registros binários com cabeçalho, carimbo de tempo e CRC16</b>: um trecho corrompido não estraga o resto do arquivo.",
   "<b>Escrita em blocos de 512 B a partir de um buffer duplo na RAM</b> e flush a cada 1 s. Mesmo que o cartão desconecte no impacto, perde-se no máximo 1 s.",
   "<b>O cartão nunca bloqueia o voo</b>: a gravação roda numa tarefa separada. Se o SD falhar, a tarefa de voo continua, o LED vermelho acende e a flash assume.",
   "<b>Gravação em alta taxa começa no ARME</b> e dura até 10 min depois do pouso. Fora disso, em solo, grava a 1 Hz para não encher o cartão.",
   "<b>Na flash interna</b>, um buffer circular com os últimos ~8 min a 20 Hz. Ele é congelado no pouso, para não ser sobrescrito.",
   "<b>Pós-voo</b>: retire o cartão ou baixe pelo Wi-Fi do ESP32 (ponto de acesso só em solo, com o sistema desarmado)."])
callout("Se o rádio cair no meio do voo",
        "Nada se perde. O microSD e a flash continuam gravando, o tracker continua apontando por predição e pelo último dado "
        "recebido, e o pacote volta assim que o enlace se recupera. Os dados que faltarem no CSV do tracker podem ser recuperados do SD "
        "depois, porque o contador <i>seq</i> mostra exatamente quais pacotes faltaram.", GREEN)

# 5 operação
H1("5. Como o sistema será usado (conceito de operação)")
story.append(fsm_diagram())
P("Figura 3 — Máquina de estados do voo.", "cap")
table([["Estado", "O que a placa faz", "Sai do estado quando"],
       ["PREPARO", "Autoteste (sensores, SD, rádio, GPS), log a 1 Hz, telemetria a 1 Hz, câmera desligada", "chave de ARME fechada + continuidade OK + VBAT OK"],
       ["RAMPA (armado)", "Log em alta taxa, telemetria a 5 Hz, liga a câmera em T−60 s, zera a altitude na pressão da rampa", "a > 3 g por 100 ms (com confirmação do barômetro subindo)"],
       ["PROPULSÃO", "Bloqueio total de disparos; mede aceleração e velocidade", "aceleração < 1 g (motor apagou) e t > tempo mínimo de queima"],
       ["COASTING", "Votação de apogeu ativa; temporizador de segurança correndo", "2 de 3 fontes indicam apogeu, ou timer"],
       ["APOGEU", "PYRO1 imediato → PYRO2 após 2 s ou 15 m de queda", "os dois disparos feitos e registrados"],
       ["DESCIDA", "Mede a taxa de descida (paraquedas abriu?), telemetria a 5 Hz", "altitude estável ±2 m por 5 s"],
       ["POUSO", "Congela a flash, fecha os arquivos, bipe de localização, GPS por rádio a 1 Hz por 2 h, desliga a câmera após 2 min", "chave principal desligada"]],
      [26, 82, 62])
H2("5.1 Sequência na rampa")
B(["<b>1.</b> Integrar a aviônica com a chave de ARME <b>aberta</b> e os ignitores já instalados nas cargas.",
   "<b>2.</b> Ligar a chave principal: LED verde pisca, 1 bipe longo = autoteste OK. Conferir no tracker se os pacotes chegam.",
   "<b>3.</b> Esperar o fix 3D do GPS (≥ 6 satélites). No tracker: <b>BASE</b> (2 s), com o foguete sobre a base, e depois <b>ALINHAR</b>, com o foguete na rampa.",
   "<b>4.</b> Fechar a chave de ARME: bipes de continuidade (seção 6.3). Se não houver continuidade em algum canal, <b>não lance</b>.",
   "<b>5.</b> Em T−60 s, o ESP32 liga a câmera: conferir a imagem nos óculos e se a gravação começou.",
   "<b>6.</b> Lançamento. Depois do pouso: seguir o bipe e a última posição do GPS, <b>abrir a chave de ARME primeiro</b>, depois desligar a principal e retirar o SD."])

# 6 falhas
H1("6. Análise de falhas (FMEA simplificada)")
table([["Falha", "Efeito sem proteção", "Mitigação no projeto", "Resultado"],
       ["Barômetro dá leitura falsa (rajada/transônico)", "Disparo precoce", "Votação 2 de 3 + bloqueio na propulsão + filtro", "Ignorado"],
       ["Barômetro morre", "Sem apogeu", "IMU + GPS + timer", "Recupera"],
       ["IMU ausente ou com falha", "Perde 1 voto", "Barômetro + GPS; timer", "Recupera"],
       ["GPS sem fix", "Tracker sem posição", "Tracker usa barômetro + predição; SD guarda tudo", "Voo OK"],
       ["Ignitor 1 aberto/queimado", "Paraquedas não abre", "PYRO2 em carga separada; continuidade checada na rampa", "Recupera"],
       ["MOSFET em curto", "Disparo no solo", "Chave de ARME física; arme só na rampa", "Seguro"],
       ["ESP32 reinicia no ar", "Perde estado / disparo", "Estado salvo na RTC RAM e na flash; watchdog; brownout", "Retoma"],
       ["Queda de tensão no disparo", "Reset da lógica", "Diodo SS34 + 470 µF; ARME antes do diodo", "Sem reset"],
       ["microSD solta/corrompe", "Perde o log", "Flash interna + telemetria + CSV do tracker; CRC por registro", "Dados salvos"],
       ["Rádio cai", "Sem dados ao vivo", "SD + flash gravam tudo; tracker prediz", "Dados salvos"],
       ["Câmera trava/curta", "Pode afetar a energia", "Alimentação chaveada (AO3401A); canal independente", "Isolado"],
       ["Bateria descarregada", "Tudo desliga", "Bloqueio de arme < 7,2 V; VBAT na telemetria", "Não lança"],
       ["Firmware com bug no disparo", "Não abre", "Altímetro comercial independente (recomendado)", "Recupera*"]],
      [40, 30, 72, 28])
P("* Exige o altímetro comercial de backup, que fica fora desta placa.", "cap")
H2("6.1 Pontos únicos de falha que ainda existem")
B(["<b>Uma única bateria</b> para a lógica e os ignitores. Mitigação: usar um altímetro comercial com bateria própria ligado a uma terceira carga. Numa futura rev. C, considerar uma entrada de bateria separada para os pyros.",
   "<b>Um único microcontrolador.</b> Mitigação: watchdog + retomada de estado + altímetro comercial independente.",
   "<b>A IMU não está soldada na placa</b> (vai no J5). Ela precisa estar instalada em <b>todo</b> voo; sem ela, a votação cai para 2 fontes."])
H2("6.2 Testes antes do voo")
table([["Teste", "Como", "Critério"],
       ["Disparo em bancada", "Ignitor de teste (ou lâmpada) nos 2 canais, com simulação de voo", "os 2 canais acendem na ordem certa"],
       ["Câmara de vácuo", "Pote + bomba de vácuo: simula subida e descida no barômetro", "apogeu detectado, PYRO1 → PYRO2"],
       ["HIL (hardware-in-the-loop)", "Injetar dados do OpenRocket no firmware (modo simulação)", "estados e disparos corretos, incluindo sensor falhando"],
       ["Alcance do rádio", "Tracker a ≥ 1 km com a antena do foguete", "pacotes > 90 %, RSSI com margem"],
       ["Queda do SD", "Tirar o cartão com o sistema gravando", "o voo continua, a flash assume, o LED acende"],
       ["Brownout", "Fonte de bancada caindo para 6 V + pulso de 3 A", "sem reset da lógica"],
       ["Duração", "Ligado na rampa por 2 h", "bateria > 7,4 V ao final"]],
      [38, 82, 50])
H2("6.3 Códigos do buzzer")
table([["Bipes", "Significado"],
       ["1 longo", "Autoteste OK (solo, desarmado)"],
       ["N curtos repetidos", "Armado: N = canais com continuidade (2 = tudo OK, 1 = falta um, 0 = nenhum)"],
       ["Contínuo rápido", "Erro grave (sensor ou SD): não lançar"],
       ["3 bipes a cada 5 s", "Pousado: bipe de localização"]],
      [40, 130])

# 7 checklist
story.append(CondPageBreak(130 * mm))
H1("7. Checklist de lançamento")
chk = [["☐", "Bateria 2S carregada (≥ 8,2 V) e presa; XT30 travado"], ["☐", "microSD formatado (FAT32), inserido e com espaço"],
       ["☐", "IMU instalada no J5 e presa"], ["☐", "Antena LoRa e antena do GPS conectadas; antena do VTX na seção não condutiva"],
       ["☐", "Ignitores instalados nas 2 cargas, chave de ARME ABERTA"], ["☐", "Altímetro comercial de backup armado (se usado)"],
       ["☐", "Chave principal ligada: 1 bipe longo e LED verde piscando"], ["☐", "Tracker recebendo pacotes (seq subindo); BASE e ALINHAR feitos"],
       ["☐", "GPS com fix 3D (≥ 6 satélites)"], ["☐", "Chave de ARME fechada: 2 bipes (continuidade nos 2 canais)"],
       ["☐", "LED vermelho apagado"], ["☐", "T−60 s: câmera ligada, imagem nos óculos e DVR gravando"]]
table([["", "Item"]] + chk, [10, 160], zebra=True)

# 8 apêndices
H1("8. Apêndices")
H2("8.1 Pinagem do ESP32")
table([["Função", "GPIO", "Observação"],
       ["LoRa SCK / MISO / MOSI / NSS", "18 / 19 / 23 / 5", "igual ao tracker_rx (VSPI)"], ["LoRa DIO0 / RST / DIO1", "26 / 14 / 39", ""],
       ["microSD CS", "15", "SPI compartilhado"], ["GPS RX / TX (UART2)", "16 / 17", "J6, 5 V"], ["I2C SDA / SCL", "21 / 22", "BMP280 + IMU (J5)"],
       ["CAM_EN / CAM TX / CAM RX", "4 / 25 / 13", "J4, UART1"], ["PYRO1 / PYRO2", "32 / 33", "pinos sem função de boot"],
       ["Continuidade PYRO1 / PYRO2", "35 / 36", "só entrada"], ["VBAT (÷5,545)", "34", ""], ["LED verde / vermelho / buzzer", "2 / 12 / 27", ""]],
      [60, 35, 75])
H2("8.2 Larguras de trilha (calculadora do KiCad, 1 oz, ΔT = 10 °C)")
table([["Classe", "Nets", "Corrente", "Trilha"],
       ["Bateria", "VBAT_IN, VBAT_SW, VBAT, VBAT_CAM, GND", "≈ 2,2 A", "1,2 mm"], ["Pyro", "VBAT_ARM, PYRO1_D, PYRO2_D", "≈ 3 A (pulso de 1 s)", "1,0 mm"],
       ["Alim_5V", "+5V", "≈ 0,55 A", "0,6 mm"], ["Alim_3V3", "+3V3", "≈ 0,48 A", "0,5 mm"], ["RF_50ohm", "LORA_ANT", "—", "2,8 mm (50 Ω)"],
       ["Default", "sinais", "< 20 mA", "0,25 mm"]], [26, 74, 38, 32])
H2("8.3 Estado atual e próximos passos")
B(["<b>Pronto:</b> esquemático (0 erros no ERC), PCB posicionada de 60 × 100 mm (paridade 0), BOM e header de pinos.",
   "<b>Falta:</b> rotear as 89 ligações, conferir a furação do MP1584, escrever o firmware (máquina de estados, votação, logs SD + flash) e fazer os testes da seção 6.2.",
   "<b>Recomendado:</b> altímetro comercial independente; IMU BMI088/ICM-42688 no J5; antena de 915 MHz sintonizada; voo de teste com carga de teste em vez de paraquedas real."])
H2("8.4 Vistas da placa e esquemático")
img(PROJ + "/docs/pcb_top.png", 95, "Figura 4 — Vista superior da PCB (60 × 100 mm).")
story.append(PageBreak())
img(SCH_IMG.replace("esquematico.pdf.png", "esq_rot.png"), 168, "Figura 5 — Esquemático em blocos (página girada; versão vetorial em docs/esquematico.pdf).")

# ---------- template ----------
class Doc(BaseDocTemplate):
    def afterFlowable(self, f):
        if hasattr(f, "_toc"):
            lvl, txt = f._toc; key = "h%d" % id(f)
            self.canv.bookmarkPage(key); self.canv.addOutlineEntry(txt, key, lvl, closed=lvl > 0)
            self.notify("TOCEntry", (lvl, txt, self.page, key))

def deco(c, d):
    c.saveState()
    c.setFillColor(NAVY); c.rect(0, A4[1] - 9 * mm, A4[0], 9 * mm, fill=1, stroke=0)
    c.setFillColor(ORANGE); c.rect(0, A4[1] - 10 * mm, A4[0], 1 * mm, fill=1, stroke=0)
    c.setFont("Bold", 8.5); c.setFillColor(colors.white)
    c.drawString(20 * mm, A4[1] - 6 * mm, "AVIÔNICA F-500 v2 · rev. B")
    c.setFont("Body", 8); c.drawRightString(A4[0] - 20 * mm, A4[1] - 6 * mm, "UTFPR Rocket · documentação do projeto")
    c.setFillColor(GREY); c.setFont("Body", 8)
    c.drawRightString(A4[0] - 20 * mm, 10 * mm, f"{d.page}")
    c.drawString(20 * mm, 10 * mm, "Redundância acima de tudo")
    c.restoreState()
def cover(c, d):
    c.saveState(); c.setFillColor(NAVY); c.rect(0, A4[1] - 14 * mm, A4[0], 14 * mm, fill=1, stroke=0)
    c.setFillColor(ORANGE); c.rect(0, A4[1] - 15.5 * mm, A4[0], 1.5 * mm, fill=1, stroke=0); c.restoreState()

doc = Doc(OUT, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=18 * mm, bottomMargin=17 * mm,
          title="Aviônica F-500 v2 — Documentação", author="UTFPR Rocket", subject="Computador de bordo do foguete F-500")
fr = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")
doc.addPageTemplates([PageTemplate("cover", [fr], onPage=cover), PageTemplate("normal", [fr], onPage=deco)])
story.insert(1, NextPageTemplate("normal"))
doc.multiBuild(story)
print("ok", OUT)
