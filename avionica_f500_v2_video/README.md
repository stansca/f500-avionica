# Aviônica F-500 v2 — rev. C-V (com vídeo ao vivo 2,4 GHz)

Variante da [rev. B](../avionica_f500_v2/) que leva em conta o documento **"Transmissão de vídeo"** (câmera Global Shutter → Pi Zero 2W → ADRV1CRR-BOB + ADRV9361-Z7035 → FEM SKY85333-11 → filtro ZVBP-2400-S+ → antena Taoglas FXP73, 802.11 OFDM em 2,4 GHz, UDP multicast). A variante sem vídeo está em [`../avionica_f500_v2_sem_video/`](../avionica_f500_v2_sem_video/).

Feita a partir da PCB da rev. B **com o roteamento manual preservado** (`scripts/delta_pcb.py`). Só foram apagadas as trilhas da antiga chave da câmera.

## O que mudou em relação à rev. B (bloco 3)
| rev. B (câmera DJI/Walksnail) | rev. C-V (vídeo do PDF) |
|---|---|
| Q3 AO3401A chaveava VBAT da câmera (até ~1,6 A) pelo J4 | **Removidos Q3, R3, C10, C11.** O vídeo do PDF consome vários ampères em 5 V e **não passa por esta placa** |
| J4: VBAT_CAM, GND, TX, RX | **J4 (JST-XH 4):** 1 `VID_OFF` · 2 GND · 3 `PI_RXD` · 4 `PI_TXD` |
| Q4 AO3400A acionava o gate do Q3 | **Q4 AO3400A em dreno aberto:** com IO4 em HIGH, puxa para GND o pino EN do regulador do vídeo e desliga o vídeo |
| UART direta | **R20/R21 1 kΩ em série** na UART: protegem a Pi quando ela está desligada e a ESP32 transmite (alimentação parasita pelos diodos de proteção) |

**Pinos:** IO4 = `VID_OFF` (antigo CAM_EN), IO25 = `VID_TX` → GPIO15 (RXD) da Pi, IO13 = `VID_RX` ← GPIO14 (TXD) da Pi. Tudo em 3,3 V nos dois lados.

### Por que a alimentação do vídeo fica fora da placa
- **Consumo:** a Pi Zero 2W pede fonte de 5 V/2,5 A. A ADRV1CRR-BOB recebe 5 V e gera os rails do ADRV9361. O PDF diz que o SOM consome 240–820 mA transmitindo. O FEM a +28 dBm consome algumas centenas de mA. Somando, o vídeo precisa de **um regulador 5 V de ≥5 A**.
- **Limite da rev. B:** a chave principal (JST-XH, 3 A), o diodo SS34 (3 A) e o buck MP1584 (3 A) da aviônica não aguentam essa carga.
- **Recomendação:** **bateria 2S própria para o vídeo + regulador 5 V/5 A com pino EN** (ex.: Pololu D36V50F5). O GND do vídeo é ligado ao GND desta placa pelo pino 2 do J4, que é a referência da UART.
- **Independência:** com a ESP32 em reset ou boot, o R4 segura o Q4 desligado e o EN fica solto. **O vídeo funciona mesmo se a aviônica falhar**, e uma falha no vídeo não derruba a recuperação.
- **Confira a lógica do EN do regulador escolhido.** O esperado é EN com pull-up interno, em que nível baixo desliga.

### Desligar sem corromper o SD da Pi
Antes de puxar o `VID_OFF`, a ESP32 manda `SHUTDOWN` pela UART e espera ~10 s. A Pi deve rodar um serviço que lê a serial e executa `poweroff`.

### O que fica em outras placas (conforme o PDF)
- **FEM SKY85333-11** (substituto do SKY85354-11, que foi descontinuado) numa placa de RF própria: microfita/CPW de 50 Ω, LGA 3 × 5 mm. Os sinais de TX/RX enable vêm do SDR, não da ESP32.
- **Filtro de cavidade ZVBP-2400-S+** (SMA) e antena Taoglas FXP73 (U.FL/MHF I), colada em seção radiotransparente.

### Pontos do PDF que precisam de atenção
1. **Canal Wi-Fi:** o filtro passa só **2375–2425 MHz**. Com 20 MHz de largura, só o **canal 1** (2401–2423 MHz) cabe inteiro na banda. Os canais 6 e 11 seriam cortados.
2. **Potência:** o PDF fala em +28 dBm (FEM em MCS0, EIRP 33 dBm) e, em outros trechos, em "1 W (+30 dBm)" (EIRP 35 dBm). As duas ficam abaixo de 36 dBm (Res. ANATEL 680/2017), mas o projeto precisa fixar uma delas e travar a atenuação do AD9361.
3. **Norma:** o texto cita 802.11g/n (OFDM 20 MHz) e, no item do detector, 802.11ax. Vale padronizar em g/n.
4. **Escala:** o PDF mira 4 km de distância, e o F-500 sobe ~500 m. Confira peso e volume (BOB + SOM + Pi + filtro de cavidade + bateria) contra a seção de carga útil.
5. **Interferência:** o PA de 2,4 GHz perto da antena do GPS (1575 MHz) e do LoRa (917 MHz) pode dessensibilizar os receptores. Afaste as antenas e mantenha o Wi-Fi/BT da ESP32 desligado.

## O que mudou para seguir o guia
| Guia | Rev. B |
|---|---|
| Esquemático em blocos, ligados por labels globais | 7 blocos com borda tracejada e título. Dentro de cada bloco, as ligações são fios; entre blocos, labels globais. GND/+5V/+3V3 usam símbolos de alimentação |
| Valor e datasheet dos componentes | Todos têm valor. Os CIs têm datasheet (ESP32, RFM95W, BMP280, MP1584, AO3400A/AO3401A, SS34, microSD) |
| 100 nF junto de cada alimentação | ESP32 (3V3 e 5V), RFM95W (10 µF + 100 nF), BMP280, microSD (10 µF + 100 nF), GPS e saída do buck |
| Regras do fabricante | Configurações do modelo **PCBWay** (2 camadas, 1 oz) importadas no `.kicad_pro`, com o `.kicad_dru` do PCBWay |
| Trilhas pela corrente | Classes de rede (tabela abaixo). Estimativa de corrente anotada no esquemático |
| Até 100 × 100 mm | **60 × 100 mm**: cabe na faixa mais barata e num tubo de ~75 mm |
| Componentes ruidosos longe do rádio | Buck embaixo, LoRa e GPS em cima, separados pelo ESP32. Área sem cobre sob a antena do ESP32 |

## Estimativa de corrente (pior caso)
- **Consumo em 5 V** (via buck): ESP32 250 mA + RFM95W 120 mA + microSD 100 mA + GPS 45 mA + buzzer 30 mA + sensores 6 mA ≈ **550 mA**.
- **Entrada do buck** (80 % de eficiência, 2S descarregada em 6,4 V): **0,54 A**.
- **Vídeo**: alimentado à parte (bateria + regulador 5 V/5 A próprios); por esta placa passam só mA.
- **Pulso do ignitor**: ~3 A.

| Classe | Nets | Trilha |
|---|---|---|
| Bateria | VBAT_IN, VBAT_SW, VBAT, GND | 1,2 mm |
| Pyro | VBAT_ARM, PYRO1_D, PYRO2_D | 1,0 mm |
| Alim_5V / Alim_3V3 | +5V / +3V3 | 0,6 / 0,5 mm |
| RF_50ohm | LORA_ANT | 2,8 mm, curta, com GND em volta |
| Default | sinais | 0,25 mm |

## Peças
- **Montagem:** SMD 0805/SOT-23/SMA com pads *HandSolder*, que dá para soldar no ferro.
- **Módulos:** ESP32-DevKitC, RFM95W, BMP280 e MP1584EN.
- **Conectores:** XT30 para a bateria, bornes de 3,5 mm para os ignitores e JST-XH para chaves, GPS, I2C e vídeo.
- **microSD:** soquete Molex 104031 a 3,3 V direto. Isso elimina o problema de MISO do módulo SD com level shifter.
- **MOSFETs:** AO3400A nos ignitores (pulso de 30 A) e no VID_OFF do vídeo (dreno aberto).
- **Embaixo do DevKit**, que fica em barra fêmea de 8,5 mm, ficam só SMD baixos: o divisor da bateria, os resistores dos LEDs e o driver do buzzer. Há uma regra de DRC que libera essa sobreposição de courtyard.
- Lista completa em `docs/BOM.csv`.

## Estado (09/11/2026)
- ERC: **0 erros** (os mesmos 6 avisos de tipo de pino da rev. B). Paridade esquemático↔PCB: **0**.
- DRC: nenhum tipo de erro novo em relação à rev. B. Continuam os avisos de serigrafia, as ligações por rotear e duas trilhas soltas que já existiam na rev. B (I2C_SDA e um toco de SPI_MOSI).
- Firmware de teste compila (core esp32).

## Antes de fabricar
- **Conferir a furação do módulo MP1584** com o módulo comprado. O footprint `F500v2:MP1584_Modulo` tem pads a ±9,5 × ±6,5 mm, o que é suposição.
- Confirmar a lógica do EN do regulador 5 V/5 A do vídeo e que o tubo comporta 60 × 100 mm e o conjunto de vídeo.
- O firmware não muda em relação à rev. A: use `firmware/pinos_f500_v2.h`. Mande a tensão da bateria por célula para o pacote continuar compatível com o tracker.

## Regenerar
`scripts/delta_pcb.py` aplica mudanças do `design.py` na PCB já roteada sem perder trilhas (é o que gerou esta variante). `scripts/build.sh` gera tudo do zero a partir de `scripts/design.py` (netlist e blocos) e `scripts/pcb_pos.py` (posições). Ele confere a netlist e roda ERC/DRC. **Ele sobrescreve a PCB**: depois de começar a rotear, edite pelo KiCad.

> `docs/Avionica_F-500_v2_Documentacao.pdf` descreve a rev. B, com a câmera DJI. As diferenças estão neste README. O PDF da antena tracker continua válido.
