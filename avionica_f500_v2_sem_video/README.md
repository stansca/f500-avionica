# Aviônica F-500 v2 — rev. C-SV (sem vídeo)

Variante da [rev. B](../avionica_f500_v2/) **sem nada de filmagem/transmissão de vídeo**: segunda opção, mais simples, leve e barata. A variante com vídeo 2,4 GHz está em [`../avionica_f500_v2_video/`](../avionica_f500_v2_video/).

Feita a partir da PCB da rev. B **com o roteamento manual preservado** (`scripts/delta_pcb.py`).

## O que mudou em relação à rev. B
- **Removido o bloco 3 inteiro (câmera/VTX):**
  - J4 (conector da câmera);
  - Q3 AO3401A e Q4 AO3400A (chave de alimentação);
  - R3, R4, C10 (100 µF) e C11;
  - as trilhas dessas nets e as sobras de VBAT que iam até o Q3/R3.
- **IO4, IO13 e IO25 ficaram livres** e estão marcados como não conectados no esquemático.
- **Consumo de VBAT:** cai para **~0,6 A contínuo**, mais o pulso dos ignitores. Sem os ~1,6 A da câmera, a chave principal, o SS34 e o buck sobram com folga.
- **Firmware:** o teste de bancada perdeu a opção `0` (câmera), e `pinos_f500_v2.h` não tem mais `PIN_CAM_*`.
- **Serigrafia:** "rev.C-SV (sem video)". O texto "CAM" saiu. A área do canto superior esquerdo ficou livre.

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
- **Conectores:** XT30 para a bateria, bornes de 3,5 mm para os ignitores e JST-XH para chaves, GPS, I2C.
- **microSD:** soquete Molex 104031 a 3,3 V direto. Isso elimina o problema de MISO do módulo SD com level shifter.
- **MOSFETs:** AO3400A nos ignitores (pulso de 30 A).
- **Embaixo do DevKit**, que fica em barra fêmea de 8,5 mm, ficam só SMD baixos: o divisor da bateria, os resistores dos LEDs e o driver do buzzer. Há uma regra de DRC que libera essa sobreposição de courtyard.
- Lista completa em `docs/BOM.csv`.

## Estado (09/11/2026)
- ERC: **0 erros** (os mesmos 6 avisos de tipo de pino da rev. B). Paridade esquemático↔PCB: **0**.
- DRC: nenhum tipo de erro novo em relação à rev. B. Continuam os avisos de serigrafia, as ligações por rotear e duas trilhas soltas que já existiam na rev. B (I2C_SDA e um toco de SPI_MOSI).
- Firmware de teste compila (core esp32).

## Antes de fabricar
- **Conferir a furação do módulo MP1584** com o módulo comprado. O footprint `F500v2:MP1584_Modulo` tem pads a ±9,5 × ±6,5 mm, o que é suposição.
- Confirmar que o tubo comporta 60 × 100 mm.
- O firmware não muda em relação à rev. A: use `firmware/pinos_f500_v2.h`. Mande a tensão da bateria por célula para o pacote continuar compatível com o tracker.

## Regenerar
`scripts/delta_pcb.py` aplica mudanças do `design.py` na PCB já roteada sem perder trilhas (é o que gerou esta variante). `scripts/build.sh` gera tudo do zero a partir de `scripts/design.py` (netlist e blocos) e `scripts/pcb_pos.py` (posições). Ele confere a netlist e roda ERC/DRC. **Ele sobrescreve a PCB**: depois de começar a rotear, edite pelo KiCad.

> `docs/Avionica_F-500_v2_Documentacao.pdf` descreve a rev. B, com a câmera DJI. As diferenças estão neste README. O PDF da antena tracker continua válido.
