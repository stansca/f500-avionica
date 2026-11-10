# Aviônica F-500 v2 — rev. B

Computador de bordo do foguete F-500 (apogeu de ~500 m), refeito segundo o **Guia de PCB das correções do Payload 2026** (`~/Obsidian/Anexos/Payload 2026 Correções.md`). A rev. A, mais antiga (60 × 170 mm, só THT), está em `_revA_antiga/`.

**Funções:**
- telemetria RFM95W 917 MHz compatível com o `tracker_rx` (mesmos pinos e pacote);
- conector de câmera/VTX digital com alimentação chaveada e UART;
- 2 canais pirotécnicos com continuidade e chave de arme;
- BMP280, GPS por cabo, microSD e conector I2C extra.

## O que mudou para seguir o guia
| Guia | Rev. B |
|---|---|
| Esquemático em blocos, ligados por labels globais | 7 blocos com borda tracejada e título. Dentro de cada bloco, as ligações são fios; entre blocos, labels globais. GND/+5V/+3V3 usam símbolos de alimentação |
| Valor e datasheet dos componentes | Todos têm valor. Os CIs têm datasheet (ESP32, RFM95W, BMP280, MP1584, AO3400A/AO3401A, SS34, microSD) |
| 100 nF junto de cada alimentação | ESP32 (3V3 e 5V), RFM95W (10 µF + 100 nF), BMP280, microSD (10 µF + 100 nF), GPS, câmera e saída do buck |
| Regras do fabricante | Configurações do modelo **PCBWay** (2 camadas, 1 oz) importadas no `.kicad_pro`, com o `.kicad_dru` do PCBWay |
| Trilhas pela corrente | Classes de rede (tabela abaixo). Estimativa de corrente anotada no esquemático |
| Até 100 × 100 mm | **60 × 100 mm**: cabe na faixa mais barata e num tubo de ~75 mm |
| Componentes ruidosos longe do rádio | Buck embaixo, LoRa e GPS em cima, separados pelo ESP32. Área sem cobre sob a antena do ESP32 |

## Estimativa de corrente (pior caso)
- **Consumo em 5 V** (via buck): ESP32 250 mA + RFM95W 120 mA + microSD 100 mA + GPS 45 mA + buzzer 30 mA + sensores 6 mA ≈ **550 mA**.
- **Entrada do buck** (80 % de eficiência, 2S descarregada em 6,4 V): **0,54 A**.
- **Câmera DJI O4**: até ~1,6 A.
- **Pulso do ignitor**: ~3 A.

| Classe | Nets | Trilha |
|---|---|---|
| Bateria | VBAT_IN, VBAT_SW, VBAT, VBAT_CAM, GND | 1,2 mm |
| Pyro | VBAT_ARM, PYRO1_D, PYRO2_D | 1,0 mm |
| Alim_5V / Alim_3V3 | +5V / +3V3 | 0,6 / 0,5 mm |
| RF_50ohm | LORA_ANT | 2,8 mm, curta, com GND em volta |
| Default | sinais | 0,25 mm |

## Peças
- **Montagem:** SMD 0805/SOT-23/SMA com pads *HandSolder*, que dá para soldar no ferro.
- **Módulos:** ESP32-DevKitC, RFM95W, BMP280 e MP1584EN.
- **Conectores:** XT30 para a bateria, bornes de 3,5 mm para os ignitores e JST-XH para chaves, GPS, I2C e câmera.
- **microSD:** soquete Molex 104031 a 3,3 V direto. Isso elimina o problema de MISO do módulo SD com level shifter.
- **MOSFETs:** AO3400A nos ignitores (pulso de 30 A) e AO3401A na câmera.
- **Embaixo do DevKit**, que fica em barra fêmea de 8,5 mm, ficam só SMD baixos: o divisor da bateria, os resistores dos LEDs e o driver do buzzer. Há uma regra de DRC que libera essa sobreposição de courtyard.
- Lista completa em `docs/BOM.csv`.

## Estado
- ERC: **0 erros**. Ficam 6 avisos de tipo de pino, que vêm dos símbolos de módulo da biblioteca JS. Paridade esquemático↔PCB: **0**.
- DRC: os únicos erros são as **89 ligações por rotear**. O resto são avisos de serigrafia dos footprints de biblioteca.
- **Falta rotear.** Ordem sugerida:
  1. LORA_ANT, do pino 9 do RFM até o SMA, curta.
  2. Bateria → chave → SS34 → buck. O GND do buck vai num ponto único até o plano.
  3. Pyro e câmera.
  4. Sinais, à mão ou pelo Freerouting.
  5. Preencher as zonas (tecla B).

## Antes de fabricar
- **Conferir a furação do módulo MP1584** com o módulo comprado. O footprint `F500v2:MP1584_Modulo` tem pads a ±9,5 × ±6,5 mm, o que é suposição.
- Confirmar que a faixa de entrada da câmera aceita 2S (6,4–8,4 V) e que o tubo comporta 60 × 100 mm.
- O firmware não muda em relação à rev. A: use `firmware/pinos_f500_v2.h`. Mande a tensão da bateria por célula para o pacote continuar compatível com o tracker.

## Regenerar
`scripts/build.sh` gera tudo a partir de `scripts/design.py` (netlist e blocos) e `scripts/pcb_pos.py` (posições). Ele confere a netlist e roda ERC/DRC. **Ele sobrescreve a PCB**: depois de começar a rotear, edite pelo KiCad.
