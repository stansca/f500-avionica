"""Aplica no .kicad_pcb JÁ ROTEADO as mudanças de design.py, sem perder o roteamento feito à mão:
remove footprints que saíram, adiciona os novos (posições de pcb_pos.py), reatribui as nets de todos
os pads pela netlist, renomeia nets e apaga as trilhas das nets que deixaram de existir.
Uso: delta_pcb.py <pcb> <netlist> <F500v2.pretty> <apagar:net1,net2> <renomear:velha=nova,...> <texto_rev> <silk_cam>"""
import sys, os, re, uuid
sys.path.insert(0, os.path.dirname(__file__))
import pcbnew
from design import COMPS
from pcb_pos import P as PCB_POS

PCB, NETLIST, FPLIB = sys.argv[1], sys.argv[2], sys.argv[3]
APAGAR = set(filter(None, sys.argv[4].split(",")))
RENOMEAR = dict(x.split("=") for x in sys.argv[5].split(",") if x)
REV, SILK_CAM = sys.argv[6], sys.argv[7]
# opcional: "NET:x0,y0,x1,y1" -> apaga trilhas dessa net contidas na caixa (sobras que iam a pads removidos)
CAIXA = sys.argv[8] if len(sys.argv) > 8 else ""
JS = os.path.expanduser("~/Documents/KiCad/biblioteca-js/footprints/")
STD = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/"
mm = pcbnew.FromMM
NS = uuid.UUID("6b3f0c1e-5000-4f00-a000-f500f500f50b")

t = re.sub(r"\s+", " ", open(NETLIST).read())
PADNET = {}
for blk in t[t.find("(nets"):].split("(net (code")[1:]:
    nm = re.search(r'\(name "([^"]*)"', blk).group(1).lstrip("/")
    for r, p in re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', blk):
        PADNET[(r, p)] = nm

b = pcbnew.LoadBoard(PCB)
def net(n):
    ni = b.FindNet(n)
    if ni is None:
        ni = pcbnew.NETINFO_ITEM(b, n); b.Add(ni)
    return ni

want = {c["ref"]: c for c in COMPS}
# 1) footprints que saíram
for fp in list(b.GetFootprints()):
    if fp.GetReference() not in want:
        print("remove", fp.GetReference()); b.Delete(fp)
# 2) footprints novos
have = {fp.GetReference() for fp in b.GetFootprints()}
for ref, c in want.items():
    if ref in have: continue
    lib, name = c["fp"].split(":")
    path = FPLIB if lib == "F500v2" else (JS if lib.startswith("JS_") else STD) + lib + ".pretty"
    fp = pcbnew.FootprintLoad(path, name); assert fp, c["fp"]
    fp.SetFPID(pcbnew.LIB_ID(lib, name)); fp.SetReference(ref); fp.SetValue(c["value"])
    fp.SetPath(pcbnew.KIID_PATH("/" + str(uuid.uuid5(NS, "sym-" + ref))))
    b.Add(fp)
    pos = PCB_POS[ref]
    if pos[0] in ("pad1", "c"):
        mode, x, y, r = pos; fp.SetOrientationDegrees(r)
        rp = fp.GetPosition() if mode == "c" else [p for p in fp.Pads() if p.GetNumber() == "1"][0].GetPosition()
        fp.Move(pcbnew.VECTOR2I(mm(x) - rp.x, mm(y) - rp.y))
    else:
        x, y, r = pos; fp.SetOrientationDegrees(r)
        bb = fp.GetBoundingBox(False); fp.Move(pcbnew.VECTOR2I(mm(x) - bb.GetX(), mm(y) - bb.GetY()))
    print("adiciona", ref, c["value"])
# 3) valores e nets dos pads
for fp in b.GetFootprints():
    c = want[fp.GetReference()]
    if fp.GetValue() != c["value"]: fp.SetValue(c["value"])
    for p in fp.Pads():
        n = PADNET.get((fp.GetReference(), p.GetNumber()))
        p.SetNet(net(n) if n else b.FindNet(""))
# 4) trilhas: renomeia ou apaga
apagadas = 0
for tr in list(b.GetTracks()):
    n = tr.GetNetname()
    if n in RENOMEAR:
        tr.SetNet(net(RENOMEAR[n]))
    elif n in APAGAR:
        b.Delete(tr); apagadas += 1
    elif CAIXA and n == CAIXA.split(":")[0]:
        x0, y0, x1, y1 = map(float, CAIXA.split(":")[1].split(","))
        pts = [tr.GetPosition()] if tr.GetClass() == "PCB_VIA" else [tr.GetStart(), tr.GetEnd()]
        xs = [pcbnew.ToMM(q.x) for q in pts]; ys = [pcbnew.ToMM(q.y) for q in pts]
        if max(xs) > x0 and min(xs) >= x0 - 0.5 and max(xs) <= x1 and min(ys) >= y0 and max(ys) <= y1:
            b.Delete(tr); apagadas += 1
print("trilhas/vias apagadas:", apagadas)
# 5) serigrafia
for d in list(b.GetDrawings()):
    if isinstance(d, pcbnew.PCB_TEXT):
        s = d.GetText()
        if s.startswith("AVIONICA F-500 v2 rev."): d.SetText("AVIONICA F-500 v2 " + REV)
        elif s == "CAM":
            if SILK_CAM: d.SetText(SILK_CAM)
            else: b.Delete(d)
pcbnew.SaveBoard(PCB, b)
b = pcbnew.LoadBoard(PCB)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(PCB, b)
print("pcb ok:", len(list(b.GetFootprints())), "footprints,", len(list(b.GetTracks())), "trilhas/vias")
