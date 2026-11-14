# Guia de roteamento: F-500 v2 rev. C-V

Placa de 60 × 100 mm, 2 camadas. Coordenadas em mm, com origem no canto superior esquerdo, como no KiCad.
**Prioridade do projeto:** a telemetria LoRa vem primeiro. A antena e o terreno embaixo do RFM95W não podem ser sacrificados por nenhuma outra trilha.

O roteamento anterior foi apagado em 2026-11-14 (está no git, commit `19f1198`), por quatro motivos:
- diagonais longas cortavam os dois planos de GND;
- o GPS_TX e o GPS_RX passavam no B.Cu embaixo do RFM95W;
- havia só 1 via, sem costura de GND;
- a antena não estava roteada.

O posicionamento dos componentes foi mantido.

## Regras gerais
1. **B.Cu = plano de GND.** No B.Cu entram só pulos curtos (até ~10 mm), perpendiculares, para cruzar outra trilha. Nada de trilha longa nele, e **nada no B.Cu embaixo do RFM95W** (região x 34–52, y 1–18).
2. **F.Cu = sinais e potência**, em linhas retas na horizontal e na vertical, com cantos de 45°. Evite diagonais que atravessam a placa.
3. **Embaixo do DevKit (y 39–63) dá para rotear no F.Cu:** o módulo fica alto, sobre os headers. Use **canais verticais paralelos**, não diagonais.
4. **Larguras:** as classes já estão no `.kicad_pro`, então o KiCad aplica sozinho. Confira no canto da tela antes de rotear cada rede.

   | Classe | Largura | Redes |
   |---|---|---|
   | RF_50ohm | 2,8 mm | `Net-(J3-In)`: antena |
   | Bateria | 1,2 mm | VBAT_IN, VBAT_SW, VBAT, GND |
   | Pyro | 1,0 mm | VBAT_ARM, `Net-(J9-Pin_2)`, `Net-(J10-Pin_2)` |
   | Alim_5V | 0,6 mm | +5V |
   | Alim_3V3 | 0,5 mm | +3V3 |
   | Default | 0,25 mm | todos os sinais |

5. **Não use o autorouter.** Rotear à mão, na ordem abaixo, rende uma placa melhor.

## Ordem de roteamento

### 1. Antena: `Net-(J3-In)` (primeiro, sem concorrência)
- De **U3.9 (50,3; 16,8)** até **J3.1 (57,3; 16,8)**: estão na **mesma altura**, então é uma reta de 7 mm no F.Cu.
- O pad do RFM95W é mais estreito que 2,8 mm. Saia do pad com um "pescoço" curto, com no máximo 1 mm na largura do pad, e alargue para 2,8 mm.
- Com 7 mm (~4 % do comprimento de onda em 915 MHz), a impedância exata pesa pouco. O que importa é ser **curta, reta e com GND sólido embaixo** (B.Cu).
- **Cerca de vias de GND** dos dois lados, a cada ~2–3 mm, ligando o F.Cu ao plano do B.Cu, e vias nos pads de GND do SMA (J3.2 em y 12,6 e y 21,1).
- Nenhuma outra trilha encosta nesse trecho.

### 2. Potência principal (1,2 mm)
- **J1** (bateria 2S, em 12,7; 87,9) → **J2** (chave principal, em 52,5; 88,4) → **D1 SS34** (40,6; 69,8) → **C1 470 µF** (29,2; 71,8) e **C2** → entrada IN+ do **U2 MP1584** (12,1; 75,8).
- Puxe o **VBAT_IN** e o **VBAT_SW** pela faixa de baixo (y 82–90), longe do DevKit.
- **GND do buck:** o GND de entrada do U2, do C1 e o OUT− do U2 vão para **um ponto só**, com várias vias para o plano do B.Cu ao lado do U2. Siga o guia da equipe.

### 3. Pyros (1,0 mm), logo depois da potência
- **VBAT_ARM:** J2/J8 (chave de arme, em 44,2; 95,4) → J9.1 (25,8; 94,4) e J10.1 (34,6; 94,4). Reta horizontal em y ≈ 92.
- **`Net-(J9-Pin_2)`** → dreno do **Q1** (26,0; 79,7), e **`Net-(J10-Pin_2)`** → dreno do **Q2** (39,5; 79,7). São curtas e verticais.
- **Source do Q1 e do Q2 → GND com 2 ou mais vias** encostadas no pad. É por aí que passa o pulso de ~3 A do ignitor.
- **Gates:** PYRO1_FIRE vem de U1.J2_7 (26,6; 63,9) e PYRO2_FIRE de U1.J2_8 (29,1; 63,9), passando pelos resistores de 100 Ω até os gates. Desça reto (y 64 → 79).
- **SENSE** (R11/R15 de 100k e divisores de 22k): sinais finos, perto dos FETs.

### 4. +5V (0,6 mm) e +3V3 (0,5 mm)
- **+5V:** OUT+ do U2 → C3/C4 → **U1.J2_19 (57,0; 63,9)**. O pino de 5 V fica na **ponta direita** da fileira de baixo. Use um canal horizontal no F.Cu em y ≈ 66–67, entre o header e o bloco de potência, e passe também pelo buzzer.
- **+3V3:** sai de **U1.J2_1 (11,3; 63,9)**, na ponta esquerda de baixo, e vai para o RFM95W (U3), o BMP280, o microSD (J7), o GPS (J6) e o J5.
  - Suba pelo canal à esquerda **por dentro do DevKit** (x ≈ 12–13, embaixo do módulo). À esquerda dele fica a área sem cobre da antena do ESP32 (x 2–10, y 40–62).
  - Depois distribua em "árvore" por cima da fileira de cima (y ≈ 34–36).
  - Os capacitores de 10 µF + 100 nF ficam encostados em cada pino de alimentação: o via de GND do capacitor vai **no pad**.

### 5. LoRa: SPI e interrupções (sinais de 0,25 mm)
- **Curtas e quase verticais** (fileira de cima, y 38,5 → lado esquerdo do U3, x 35,2):
  - LORA_NSS: U1.J3_10 (34,2) → U3.5 (35,2; 10,8)
  - SPI_SCK: U1.J3_9 (31,6) → U3.4 (35,2; 8,8)
  - SPI_MISO: U1.J3_8 (29,1) → U3.2 (35,2; 4,8)
- **SPI_MOSI:** sai de U1.J3_2 (13,8; 38,5), na ponta esquerda. Leve por um canal horizontal em y ≈ 36 até x ≈ 33 e suba até U3.3 (35,2; 6,8).
- **Da fileira de baixo** (atravessam por baixo do DevKit, em canais verticais paralelos no F.Cu):
  - LORA_RST: U1.J2_12 (39,2; 63,9) → U3.6 (35,2; 12,8)
  - LORA_DIO0: U1.J2_10 (34,2; 63,9) → U3.14 (50,3; 6,8), no lado **direito** do U3
  - LORA_DIO1: U1.J2_4 (18,9; 63,9) → U3.15 (50,3; 4,8), no lado **direito** do U3
- **Cuidado com o DIO0 e o DIO1:** para chegar ao lado direito do U3, eles cruzam a altura da antena (y 16,8). Faça **um pulo curto no B.Cu, perpendicular**, com as vias a **≥3 mm** da trilha da antena (por exemplo, em x ≈ 53–54, vias em y ≈ 13 e y ≈ 21). É a única exceção permitida perto do RF.
- **Ramais para o microSD** (J7, em 53,2; 29,7, que divide o SPI): SCK, MISO e MOSI descem do U3 até o J7 pela região x 44–52, y 20–34. O **SD_CS** vai de U1.J3_16 (49,4; 38,5), bem perto.

### 6. GPS e I2C
- **GPS_RX/GPS_TX:** U1.J3_11/12 (36,7 e 39,2; 38,5) → **J6** (3,7; 18,5). Use um canal horizontal no F.Cu em y ≈ 34–36, por cima da fileira de cima e paralelo ao MOSI. **Nunca pelo B.Cu embaixo do U3** (era o erro anterior).
- **I2C_SCL/I2C_SDA:** U1.J3_3 (16,4) e U1.J3_6 (24,0) → BMP280 (módulo THT à esquerda do centro) e **J5** (3,7; 32,5). São curtas.

### 7. Vídeo (J4, em 11,0; 3,7) e restante
- **VID_CTRL** (IO4, U1.J3_13) → R4/Q4 → J4.1: é curta, porque o IO4 fica na fileira de cima.
- **VID_TX (IO25) e VID_RX (IO13)** ficam na fileira de **baixo** e o J4 fica no topo. Suba por um canal vertical embaixo do DevKit até a fileira de cima e daí até R20/R21 e o J4.
- **VBAT_SENSE:** divisor R1/R2 → U1.J2_5 (21,5; 63,9). É um sinal lento: pode ir pelo caminho que sobrar.
- **LEDs** (D2/D3), **buzzer** (BZ1 via Q5) e os pull-ups por último.

### 8. Fechamento
1. **Preencher as zonas** (tecla **B**).
2. **Costurar o GND:** vias entre o F.Cu e o B.Cu a cada ~5–8 mm na borda e nos espaços vazios, e mais densas perto do RFM95W e do SMA.
3. **DRC** com paridade: a meta é **0 erros, 0 desconectados**. Os avisos de serigrafia podem ser limpos no fim (`silk_over_copper` e `silk_overlap`, ~100 hoje).
4. Conferir **ilhas de cobre** isoladas e apagar as que não tiverem via.
5. Exportar os Gerbers só depois que o DRC estiver limpo.

## Opcional (melhoria de esquemático, não precisa agora)
- O LORA_RST, o DIO0 e o DIO1 estão na fileira de baixo do DevKit (IO14, IO26 e IO39), e por isso atravessam a placa. Mover para GPIOs livres da fileira de cima encurtaria muito, mas mudaria o esquemático e o firmware (`pinos_f500_v2.h`). Só vale se o roteamento por baixo do DevKit ficar apertado.
- Se o Wi-Fi e o BT do ESP32 ficarem sempre desligados (o README recomenda), a área sem cobre embaixo da antena do DevKit poderia virar um canal para a +3V3. Hoje ela fica como está.
