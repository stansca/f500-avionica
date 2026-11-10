import sys, os, uuid
sys.path.insert(0, os.path.dirname(__file__))
import pcbnew
from design import COMPS, PCB_POS, BOARD_W, BOARD_H, NETCLASSES
OUT = sys.argv[1]
NETLIST = sys.argv[2]
import re
_t = re.sub(r"\s+", " ", open(NETLIST).read())
PADNET = {}
for blk in _t[_t.find("(nets"):].split("(net (code")[1:]:
    nm = re.search(r'\(name "([^"]*)"', blk).group(1)
    for r, p in re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', blk):
        PADNET[(r, p)] = nm
NS = uuid.UUID("6b3f0c1e-5000-4f00-a000-f500f500f500")
def U(s): return str(uuid.uuid5(NS, s))
JS = os.path.expanduser("~/Documents/KiCad/biblioteca-js/footprints/")
STD = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/"
mm = pcbnew.FromMM
b = pcbnew.BOARD()
nets = {}
def net(n):
    if n not in nets:
        ni = pcbnew.NETINFO_ITEM(b, n); b.Add(ni); nets[n] = ni
    return nets[n]
for c in COMPS:
    lib, name = c["fp"].split(":")
    fp = pcbnew.FootprintLoad((JS if lib.startswith("JS_") else STD) + lib + ".pretty", name)
    assert fp, c["fp"]
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    fp.SetReference(c["ref"]); fp.SetValue(c["value"])
    fp.SetPath(pcbnew.KIID_PATH("/" + U("sym-" + c["ref"])))
    b.Add(fp)
    for it in fp.GraphicalItems():
        if isinstance(it, pcbnew.PCB_TEXT) and "${12->5}" in it.GetText(): it.SetText("12V->5V")
    pos = PCB_POS[c["ref"]]
    if pos[0] == "pad1":
        _, x, y, rot = pos
        fp.SetOrientationDegrees(rot)
        p1 = [p for p in fp.Pads() if p.GetNumber() == "1"][0].GetPosition()
        fp.Move(pcbnew.VECTOR2I(mm(x) - p1.x, mm(y) - p1.y))
    else:
        x, y, rot = pos
        fp.SetOrientationDegrees(rot)
        bb = fp.GetBoundingBox(False)
        fp.Move(pcbnew.VECTOR2I(mm(x) - bb.GetX(), mm(y) - bb.GetY()))
    for p in fp.Pads():
        n = PADNET.get((c["ref"], p.GetNumber()))
        if n:
            p.SetNet(net(n))
# contorno
def seg(x1, y1, x2, y2, layer=pcbnew.Edge_Cuts, w=0.1):
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1))); s.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
    s.SetLayer(layer); s.SetWidth(mm(w)); b.Add(s)
W, H = BOARD_W, BOARD_H
for a in [(0, 0, W, 0), (W, 0, W, H), (W, H, 0, H), (0, H, 0, 0)]: seg(*a)
# planos de GND nas duas faces
for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
    z = pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(net("GND"))
    o = z.Outline(); o.NewOutline()
    for (x, y) in [(0, 0), (W, 0), (W, H), (0, H)]: o.Append(mm(x), mm(y))
    z.SetLocalClearance(mm(0.4)); z.SetMinThickness(mm(0.25))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(mm(0.5)); z.SetThermalReliefSpokeWidth(mm(0.6))
    z.SetAssignedPriority(0); b.Add(z)
# textos de serigrafia
def txt(s, x, y, size=1.2, layer=pcbnew.F_SilkS, bold=False):
    t = pcbnew.PCB_TEXT(b); t.SetText(s); t.SetLayer(layer)
    t.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y))); t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    t.SetTextThickness(mm(size * 0.15)); t.SetBold(bold); b.Add(t); return t
for t, x, y in [("AVIONICA F-500 v2", 30, 52), ("UTFPR ROCKET 2026", 30, 56), ("LoRa 917MHz | tracker", 30, 60)]:
    tt = txt(t, x, y, 1.5, pcbnew.B_SilkS, True); tt.SetMirrored(True)
for t, x, y in [("PYRO1", 6, 156.5), ("PYRO2", 17.5, 156.5), ("BAT 2S", 29.5, 156.5), ("SW", 41, 158.5),
                ("ARM", 33, 150.5), ("CAM", 11.6, 8.0), ("GPS", 26.5, 8.0), ("I2C", 49.3, 33), ("ANT", 57, 26),
                ("USB", 30, 88), ("SD", 3, 87.5)]:
    txt(t, x, y, 1.0, bold=True)
ds = b.GetDesignSettings()
ds.m_TrackMinWidth = mm(0.25); ds.m_MinClearance = mm(0.2); ds.m_ViasMinSize = mm(0.6)
b.SetCopperLayerCount(2)
pcbnew.SaveBoard(OUT, b)
# preenche zonas
b = pcbnew.LoadBoard(OUT)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(OUT, b)
print("pcb ok", len(COMPS), "fps,", len(nets), "nets")
