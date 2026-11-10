#!/bin/bash
# Regenera esquemático, projeto e PCB a partir de design.py.
# ATENÇÃO: sobrescreve o .kicad_pcb — NÃO rode depois de começar a rotear (use "Atualizar PCB a partir do esquemático" no KiCad).
set -e
D="$(cd "$(dirname "$0")" && pwd)"; P="$(cd "$D/.." && pwd)"; N=avionica_f500_v2
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3
cd "$D"
python3 gen_sch.py $N "$P/$N.kicad_sch"
python3 gen_pro.py "$P/$N.kicad_pro"
$K sch export netlist --format kicadsexpr -o /tmp/$N.net "$P/$N.kicad_sch" >/dev/null 2>&1
$KPY gen_pcb.py "$P/$N.kicad_pcb" /tmp/$N.net 2>&1 | grep -v -e Fontconfig -e assert
$K sch erc -o /tmp/$N-erc.rpt "$P/$N.kicad_sch" 2>&1 | grep -i viola
$K pcb drc --schematic-parity -o /tmp/$N-drc.rpt "$P/$N.kicad_pcb" 2>&1 | grep -E 'viola|parid|desconec'
