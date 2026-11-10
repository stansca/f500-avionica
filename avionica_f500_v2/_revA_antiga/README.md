# Aviônica F-500 v2

Computador de bordo para o foguete F-500 (apogeu de ~500 m). É a evolução da `rayquasa` (F-500 v1) com:

- **Telemetria compatível com a antena tracker**: RFM95W (SX1276) a 917 MHz nos **mesmos GPIOs do `tracker_rx`**, com o mesmo pacote de 26 bytes a 5 Hz.
- **Câmera/VTX digital**: conector próprio com VBAT 2S chaveado pelo ESP32 e UART para MSP/OSD.
- **2 canais de recuperação** com MOSFET de porta lógica, leitura de continuidade e chave de arme física.
- GPS por cabo, BMP280, microSD para log e conector I2C extra para IMU.

PCB de 2 camadas, **60 × 170 mm**, quase tudo THT ou módulo. A única peça SMD é o RFM95W, que tem bordas castelladas e dá para soldar no ferro. Os furos M3 ficam nas posições H1–H4.

## Arquivos
| Arquivo | O que é |
|---|---|
| `avionica_f500_v2.kicad_sch/.kicad_pcb/.kicad_pro` | Projeto KiCad 10 |
| `docs/esquematico.pdf`, `docs/pcb_*.png`, `docs/BOM.csv` | Saídas para revisão e compra |
| `firmware/pinos_f500_v2.h` | Pinagem para portar o `foguete_tx.ino` |
| `scripts/` | Gerador (`design.py` = netlist + posições). `build.sh` regenera **e sobrescreve a PCB** |

## Estado
- ERC: 0 erros. Ficam 7 avisos de tipo de pino, que vêm dos símbolos de módulo da biblioteca JS.
- Paridade esquemático ↔ PCB: 0 problemas.
- **Falta rotear.** São 71 ligações em ratsnest. Os planos de GND nas duas faces já estão criados.
- O DRC acusa 5 violações de "borda" no J3. Isso é esperado, porque o SMA de borda precisa encostar na borda. Exclua essas violações no DRC do KiCad. Os avisos de serigrafia sobre pad vêm dos footprints da biblioteca.

### Roteamento sugerido
1. Abra no KiCad. As classes de rede já estão configuradas: Potência com 1,0 mm (VBAT*, PYRO*_D, +5V, GND), 3V3 com 0,6 mm e RF com 2,8 mm.
2. Rote primeiro **à mão**: LORA_ANT (do pino 9 do RFM até o SMA, curto e reto, com GND dos dois lados), VBAT_SW→ARM→PYRO, VBAT→Q3→J9.
3. O resto pode ir no Freerouting (plugin do KiCad) ou à mão. Depois, preencha as zonas (B).

## Pinagem (ESP32-DevKitC)
| Função | GPIO | Observação |
|---|---|---|
| LoRa SCK/MISO/MOSI/NSS | 18/19/23/5 | igual ao tracker_rx |
| LoRa DIO0 / RST / DIO1 | 26 / 14 / 39 | |
| microSD CS | 15 | SPI compartilhado |
| GPS RX/TX (UART2) | 16/17 | conector J5 (5 V) |
| I2C SDA/SCL | 21/22 | BMP280 0x76 + J4 |
| CAM_EN / CAM TX / CAM RX | 4 / 25 / 13 | J9 |
| PYRO1 / PYRO2 | 32 / 33 | pinos sem função de boot (sem disparo no boot) |
| Continuidade PYRO1 / PYRO2 | 35 / 36 | só entrada |
| VBAT (÷5,545) | 34 | |
| LED verde / vermelho / buzzer | 2 / 12 / 27 | o LED + resistor mantém o IO12 em nível baixo no boot |

## Câmera que filma e transmite
O conector **J9** entrega VBAT 2S (6,4–8,4 V), GND, TX e RX. O ESP32 liga a alimentação pelo `CAM_EN` (P-MOSFET IRF9540N), então dá para deixar a câmera desligada na rampa e ligar só na contagem. A UART serve para emular MSP e mostrar altitude/velocidade no OSD ou acionar a gravação.

Opções, da mais completa para a mais barata:
1. **DJI O4 Air Unit / O4 Pro**: grava em alta resolução no próprio módulo e transmite digital para os óculos DJI. Os óculos têm saída para celular/PC, o que permite fazer live.
2. **Walksnail Avatar HD**: mesma ideia, mais barato.
3. **Câmera FPV analógica + VTX 5,8 GHz + gravação separada** (tipo RunCam Split): imagem pior, mas é barato e tem latência zero.

Confira no datasheet se a faixa de entrada do modelo escolhido aceita 2S. A antena do VTX precisa ficar numa seção **não condutiva** (fibra de vidro/papelão; fibra de carbono e alumínio bloqueiam) e longe da antena LoRa. O VTX esquenta muito sem fluxo de ar, então ligue só perto do lançamento.

## Antes de fabricar
- Confirme as dimensões físicas dos módulos (buck LM2596, SD, BMP280) com as peças que vocês têm.
- Confira se o tubo/sled comporta 60 × 170 mm.
- Os TO-220 de pé podem ser dobrados deitados para aguentar melhor a aceleração. Prenda os módulos com abraçadeira ou cola quente.
- O módulo de SD com level shifter às vezes não libera o MISO. Se o LoRa falhar com o SD encaixado, use um módulo sem shifter (3,3 V direto).
