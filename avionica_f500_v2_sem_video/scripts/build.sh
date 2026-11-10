#!/bin/bash
# Regenera esquemático, projeto e PCB a partir de design.py + pcb_pos.py.
# ATENÇÃO: sobrescreve o .kicad_pcb — depois de começar a rotear, use "Atualizar PCB a partir do esquemático" no KiCad.
set -e
D="$(cd "$(dirname "$0")" && pwd)"; P="$(cd "$D/.." && pwd)"; N=avionica_f500_v2_sem_video
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3
cd "$D"
{ cat "$D/pcbway_modelo.kicad_dru"; printf '\n(rule "SMA de borda encosta na borda"\n(constraint edge_clearance (min 0mm))\n(condition "A.memberOfFootprint('"'"'J3'"'"') || B.memberOfFootprint('"'"'J3'"'"')"))\n\n(rule "SMD baixo embaixo do DevKit ESP32"\n(constraint courtyard_clearance (min 0mm))\n(severity ignore)\n(condition "A.Reference == '"'"'U1'"'"' || B.Reference == '"'"'U1'"'"'"))\n'; } > "$P/$N.kicad_dru"
python3 verify.py $N "$P/$N.kicad_sch" /tmp/$N.net
$KPY gen_pcb.py "$P/$N.kicad_pcb" /tmp/$N.net "$P/F500v2.pretty" 2>&1 | grep -v -e Fontconfig -e assert
python3 gen_pro.py "$P/$N.kicad_pro" "$D/pcbway_modelo.kicad_pro"
$K sch erc -o /tmp/$N-erc.rpt "$P/$N.kicad_sch" 2>&1 | grep -i viola
$K pcb drc --schematic-parity -o /tmp/$N-drc.rpt "$P/$N.kicad_pcb" 2>&1 | grep -E 'viola|parid|desconec'
