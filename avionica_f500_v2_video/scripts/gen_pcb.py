import sys, os, uuid, re
sys.path.insert(0, os.path.dirname(__file__))
import pcbnew
from design import COMPS, BOARD_W, BOARD_H
from pcb_pos import P as PCB_POS
OUT, NETLIST, FPLIB = sys.argv[1], sys.argv[2], sys.argv[3]
NS = uuid.UUID("6b3f0c1e-5000-4f00-a000-f500f500f50b")
def U(s): return str(uuid.uuid5(NS, s))
JS = os.path.expanduser("~/Documents/KiCad/biblioteca-js/footprints/")
STD = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/"
mm = pcbnew.FromMM
t = re.sub(r"\s+", " ", open(NETLIST).read())
PADNET = {}
for blk in t[t.find("(nets"):].split("(net (code")[1:]:
    nm = re.search(r'\(name "([^"]*)"', blk).group(1)
    pass
DSHEET = {}
for cb in t[t.find("(components"):t.find("(libparts")].split("(comp (ref")[1:]:
    m = re.match(r' "([^"]+)"', cb); d = re.search(r'\(datasheet "([^"]*)"\)', cb)
    if m and d: DSHEET[m.group(1)] = d.group(1)
for blk in t[t.find("(nets"):].split("(net (code")[1:]:
    nm = re.search(r'\(name "([^"]*)"', blk).group(1)
    for r, p in re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', blk):
        PADNET[(r, p)] = nm
b = pcbnew.BOARD()
nets = {}
def net(n):
    if n not in nets:
        ni = pcbnew.NETINFO_ITEM(b, n); b.Add(ni); nets[n] = ni
    return nets[n]
for c in COMPS:
    lib, name = c["fp"].split(":")
    path = FPLIB if lib == "F500v2" else (JS if lib.startswith("JS_") else STD) + lib + ".pretty"
    fp = pcbnew.FootprintLoad(path, name); assert fp, c["fp"]
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    fp.SetReference(c["ref"]); fp.SetValue(c["value"])
    ds_ = DSHEET.get(c["ref"], "")
    if ds_ and ds_ != "~": fp.GetField(pcbnew.FIELD_T_DATASHEET).SetText(ds_)
    fp.SetPath(pcbnew.KIID_PATH("/" + U("sym-" + c["ref"])))
    b.Add(fp)
    for it in fp.GraphicalItems():
        if isinstance(it, pcbnew.PCB_TEXT) and "${12->5}" in it.GetText(): it.SetText("12V->5V")
    pos = PCB_POS[c["ref"]]
    if pos[0] in ("pad1", "c"):
        mode, x, y, r = pos
        fp.SetOrientationDegrees(r)
        ref = fp.GetPosition() if mode == "c" else [p for p in fp.Pads() if p.GetNumber() == "1"][0].GetPosition()
        fp.Move(pcbnew.VECTOR2I(mm(x) - ref.x, mm(y) - ref.y))
    else:
        x, y, r = pos
        fp.SetOrientationDegrees(r)
        bb = fp.GetBoundingBox(False)
        fp.Move(pcbnew.VECTOR2I(mm(x) - bb.GetX(), mm(y) - bb.GetY()))
    for p in fp.Pads():
        if c["ref"] == "J1" and p.GetNumber() == "":   # pinos de fixação do XT30: anel mínimo PCBWay 0,25 mm
            d = p.GetDrillSize(); p.SetSize(pcbnew.VECTOR2I(d.x + mm(0.6), d.y + mm(0.6)))
        n = PADNET.get((c["ref"], p.GetNumber()))
        if n: p.SetNet(net(n))
W, H, R = BOARD_W, BOARD_H, 2.0
def seg(x1, y1, x2, y2):
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1))); s.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
    s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1)); b.Add(s)
def arc(cx, cy, sx, sy, ang):
    a = pcbnew.PCB_SHAPE(b); a.SetShape(pcbnew.SHAPE_T_ARC)
    a.SetCenter(pcbnew.VECTOR2I(mm(cx), mm(cy))); a.SetStart(pcbnew.VECTOR2I(mm(sx), mm(sy)))
    a.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(ang, pcbnew.DEGREES_T), True)
    a.SetLayer(pcbnew.Edge_Cuts); a.SetWidth(mm(0.1)); b.Add(a)
seg(R, 0, W - R, 0); seg(W, R, W, H - R); seg(W - R, H, R, H); seg(0, H - R, 0, R)
arc(R, R, 0, R, 90); arc(W - R, R, W - R, 0, 90); arc(W - R, H - R, W, H - R, 90); arc(R, H - R, R, H, 90)
for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
    z = pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(net("GND"))
    o = z.Outline(); o.NewOutline()
    for (x, y) in [(0, 0), (W, 0), (W, H), (0, H)]: o.Append(mm(x), mm(y))
    z.SetLocalClearance(mm(0.3)); z.SetMinThickness(mm(0.25))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(mm(0.5)); z.SetThermalReliefSpokeWidth(mm(0.5)); b.Add(z)
# keepout de cobre embaixo da antena PCB do ESP32 (lado esquerdo do DevKit)
u1 = [f for f in b.GetFootprints() if f.GetReference() == "U1"][0]
bb = u1.GetBoundingBox(False)
ka = pcbnew.ZONE(b); ka.SetIsRuleArea(True); ka.SetLayerSet(pcbnew.LSET.AllCuMask())
ka.SetDoNotAllowZoneFills(True); ka.SetDoNotAllowTracks(False); ka.SetDoNotAllowVias(False); ka.SetDoNotAllowPads(False); ka.SetDoNotAllowFootprints(False)
ko = ka.Outline(); ko.NewOutline()
x0, y0, y1 = pcbnew.ToMM(bb.GetX()), pcbnew.ToMM(bb.GetY()), pcbnew.ToMM(bb.GetBottom())
for (x, y) in [(x0, y0 + 3), (x0 + 6.5, y0 + 3), (x0 + 6.5, y1 - 3), (x0, y1 - 3)]: ko.Append(mm(x), mm(y))
ka.SetZoneName("antena_ESP32"); b.Add(ka)
def txt(s, x, y, size=1.0, layer=pcbnew.F_SilkS, mirror=False):
    t = pcbnew.PCB_TEXT(b); t.SetText(s); t.SetLayer(layer)
    t.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y))); t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    t.SetTextThickness(mm(max(0.15, size * 0.15))); t.SetBold(True); t.SetMirrored(mirror); b.Add(t)
for s_, y in [("AVIONICA F-500 v2 rev.B", 44), ("UTFPR ROCKET 2026", 48), ("LoRa 917 MHz - tracker", 52), ("60 x 100 mm - PCBWay", 56)]:
    txt(s_, 30, y, 1.5, pcbnew.B_SilkS, True)
for s_, x, y in [("CAM", 24.5, 2.6), ("GPS", 4.2, 22.0), ("I2C", 4.2, 36.0), ("ANT", 57.2, 23.8), ("SD", 52, 21.2),
                 ("USB", 57.0, 66.8), ("J1 BAT 2S", 15.2, 90.6), ("J2 SW", 53.9, 84.4), ("J8 ARM", 45.4, 91.3),
                 ("J9 PYRO1", 27.5, 89.6), ("J10 PYRO2", 36.4, 89.6)]:
    txt(s_, x, y, 0.9)
for f in b.GetFootprints():
    if f.GetReference() in ("J2", "J8", "J9", "J10"): f.Reference().SetVisible(False)
b.SetCopperLayerCount(2)
pcbnew.SaveBoard(OUT, b)
b = pcbnew.LoadBoard(OUT)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(OUT, b)
print("pcb ok", len(COMPS), "fps,", len(nets), "nets")
