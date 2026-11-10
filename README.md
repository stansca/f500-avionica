# F-500 — projetos do foguete

Repositórios relacionados: [f500-video-2g4](https://github.com/stansca/f500-video-2g4) · [placa-estatico](https://github.com/stansca/placa-estatico) · [rocket-arduino](https://github.com/stansca/rocket-arduino) · [kicad-biblioteca-js](https://github.com/stansca/kicad-biblioteca-js)

Tudo do F-500 (apogeu ~500 m) fica nesta pasta.

## Placas

| Placa | Pasta | Estado |
|---|---|---|
| Aviônica v1 (rayquasa) | [`rayquasa/`](rayquasa/) | final, só THT |
| Aviônica v2 rev. B (câmera DJI/Walksnail) | [`avionica_f500_v2/`](avionica_f500_v2/) | posicionada; **roteamento manual em andamento** |
| Aviônica v2 **rev. C-V** (controle do vídeo 2,4 GHz) | [`avionica_f500_v2_video/`](avionica_f500_v2_video/) | variante da rev. B, roteamento preservado |
| Aviônica v2 rev. C-SV (sem vídeo) | [`avionica_f500_v2_sem_video/`](avionica_f500_v2_sem_video/) | variante da rev. B, roteamento preservado |
| **RF-FEM 2,4 GHz** (vídeo) | [f500-video-2g4 / placa_rf_fem](https://github.com/stansca/f500-video-2g4/tree/main/Hardware/placa_rf_fem) | gerada; cadeia de RF traçada, falta rotear alimentação/controle |
| **Alimentação do vídeo** | [f500-video-2g4 / placa_alim_video](https://github.com/stansca/f500-video-2g4/tree/main/Hardware/placa_alim_video) | gerada; falta rotear |

As duas placas do vídeo ficam dentro de `video_2g4_f500/Hardware/` porque compartilham a biblioteca de símbolos (`Hardware/biblioteca/`) e o gerador (`Hardware/gerador/`). A estrutura segue o padrão dos repositórios da equipe (Hardware / Firmware / Software).

## Sistema de vídeo ao vivo 2,4 GHz

Repositório [f500-video-2g4](https://github.com/stansca/f500-video-2g4) (localmente em `video_2g4_f500/`): placas RF-FEM e de alimentação, software da Pi Zero 2W, dos SDRs (openwifi) e do notebook, e firmware da ESP32.
Documento completo: [Video_2G4_F500_Documentacao.pdf](https://github.com/stansca/f500-video-2g4/blob/main/docs/Video_2G4_F500_Documentacao.pdf).

```
avionica_f500_v2_video (J4) ──XH-4──> placa_alim_video (J2) ──> Pi Zero 2W / ADRV1CRR-BOB / placa_rf_fem
```
