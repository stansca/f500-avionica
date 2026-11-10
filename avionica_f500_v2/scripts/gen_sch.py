"""Gera o esquemático em blocos: fios dentro de cada bloco, labels globais entre blocos,
símbolos de alimentação para GND/+5V/+3V3, retângulos tracejados e títulos.
Uso: gen_sch.py <projeto> <saida.kicad_sch> [nets_forcadas_label separadas por vírgula]"""
import sys, os, uuid, copy, math
sys.path.insert(0, os.path.dirname(__file__))
from sexp import Sym, dump, find, findall
from symlib import get_symbol, pins
from design import COMPS, BLOCKS, TEXT_NOTES

PROJ, OUT = sys.argv[1], sys.argv[2]
FORCE_LABEL = set(sys.argv[3].split(",")) if len(sys.argv) > 3 and sys.argv[3] else set()
NS = uuid.UUID("6b3f0c1e-5000-4f00-a000-f500f500f50b")
def U(s): return str(uuid.uuid5(NS, s))
ROOT = U("root-sheet")
S = Sym
POWER = {"GND": "power:GND", "+5V": "power:+5V", "+3V3": "power:+3V3"}
EPS = 1e-6

def r2(v): return round(v * 100) / 100
def eff(size=1.27, justify=None, hide=False, bold=False):
    f = [S("font"), [S("size"), size, size]]
    if bold: f.append([S("bold"), S("yes")])
    e = [S("effects"), f]
    if justify: e.append([S("justify"), *[S(j) for j in justify.split()]])
    if hide: e.append([S("hide"), S("yes")])
    return e

def rot(x, y, r):
    c, s = round(math.cos(math.radians(r))), round(math.sin(math.radians(r)))
    return x * c - y * s, x * s + y * c

def body_bbox(sym, X, Y, r):
    xs, ys = [], []
    def add(x, y):
        a, b = rot(x, y, r); xs.append(X + a); ys.append(Y - b)
    def walk(node, unit):
        for i in node:
            if not isinstance(i, list) or not i: continue
            if i[0] == "symbol":
                u = int(i[1].rsplit("_", 2)[-2]);
                if u in (0, 1): walk(i, u)
            elif i[0] == "rectangle":
                s_, e_ = find(i, "start"), find(i, "end"); add(float(s_[1]), float(s_[2])); add(float(e_[1]), float(e_[2]))
            elif i[0] in ("polyline", "bezier"):
                for p in findall(find(i, "pts"), "xy"): add(float(p[1]), float(p[2]))
            elif i[0] == "circle":
                c_ = find(i, "center"); rr = float(find(i, "radius")[1])
                add(float(c_[1]) - rr, float(c_[2]) - rr); add(float(c_[1]) + rr, float(c_[2]) + rr)
            elif i[0] == "arc":
                for k in ("start", "mid", "end"):
                    p = find(i, k); add(float(p[1]), float(p[2]))
    walk(sym, 0)
    if not xs: return None
    return (min(xs), min(ys), max(xs), max(ys))

# ---------- coleta símbolos e pinos ----------
lib_symbols = [S("lib_symbols")]
seen = set()
items = []          # elementos do esquemático
pin_pts = []        # (x, y, net, ref, num, outward_angle, blk)
bodies = []         # bboxes
inst_list = []

def add_lib(lib):
    if lib in seen: return
    seen.add(lib)
    s2 = copy.deepcopy(get_symbol(lib)); s2[1] = lib; lib_symbols.append(s2)

pwr_n = [0]
def place_symbol(c, X, Y, r, unit=1, ref=None, value=None, flags=False, fp="", ds=""):
    lib = c["lib"]; add_lib(lib)
    sym = get_symbol(lib)
    ref = ref or c["ref"]
    uid = U(f"sym-{ref}") if unit == 1 else U(f"sym-{ref}-{unit}")
    props = {p[1]: p for p in findall(sym, "property")}
    is_virtual = ref.startswith("#")
    inst = [S("symbol"), [S("lib_id"), lib], [S("at"), X, Y, r], [S("unit"), unit],
            [S("exclude_from_sim"), S("no")], [S("in_bom"), S("no" if (is_virtual or ref[0] == "H") else "yes")],
            [S("on_board"), S("yes")], [S("dnp"), S("no")], [S("uuid"), uid]]
    if ds == "" and "Datasheet" in props: ds = props["Datasheet"][2]
    for name, val, hide in (("Reference", ref, is_virtual), ("Value", value or c.get("value", ""), False),
                            ("Footprint", fp, True), ("Datasheet", ds, True), ("Description", "", True)):
        p = props.get(name)
        at = find(p, "at") if p is not None else [0, 0, 0, 0]
        ax, ay = rot(float(at[1]), float(at[2]), r)
        pang = (float(at[3]) if len(at) > 3 else 0)
        if r in (90, 270): pang = (pang + 90) % 180
        e = copy.deepcopy(find(p, "effects")) if p is not None else eff()
        e = [x for x in e if not (isinstance(x, list) and x and x[0] == "hide")]
        if hide: e.append([S("hide"), S("yes")])
        inst.append([S("property"), name, val, [S("at"), r2(X + ax), r2(Y - ay), pang], e])
    pl = [p for p in pins(sym) if p["unit"] in (0, unit)]
    for p in pl:
        inst.append([S("pin"), p["num"], [S("uuid"), U(f"pin-{ref}-{p['num']}")]])
    inst.append([S("instances"), [S("project"), PROJ, [S("path"), "/" + ROOT, [S("reference"), ref], [S("unit"), unit]]]])
    inst_list.append(inst)
    return sym, pl

for c in COMPS:
    sym = get_symbol(c["lib"])
    allp = pins(sym)
    for k in c["pins"]:
        if k not in {p["num"] for p in allp}: raise SystemExit(f"pino inexistente {c['ref']}.{k}")
    units = sorted({p["unit"] for p in allp if p["unit"] > 0}) or [1]
    X0, Y0, r = c["sch"]
    for ui, unit in enumerate(units):
        X, Y = X0, Y0 + 7.62 * ui
        sym, pl = place_symbol(c, X, Y, r, unit, fp=c["fp"], ds=c.get("ds", ""))
        bb = body_bbox(sym, X, Y, r)
        if bb: bodies.append((bb, c["ref"]))
        seenpt = set()
        for p in pl:
            net = c["pins"].get(p["num"])
            if net is None: raise SystemExit(f"pino sem net {c['ref']}.{p['num']}")
            dx, dy = rot(p["x"], p["y"], r)
            px, py = r2(X + dx), r2(Y - dy)
            if (px, py) in seenpt: continue
            seenpt.add((px, py))
            out = (p["ang"] + r + 180) % 360
            pin_pts.append(dict(x=px, y=py, net=net, ref=c["ref"], num=p["num"], out=out, blk=c["blk"]))

# ---------- roteamento simples de fios dentro dos blocos ----------
segs = []   # dict(a=(x,y), b=(x,y), net)
def on_seg(pt, s, interior=False):
    (x1, y1), (x2, y2) = s["a"], s["b"]
    x, y = pt
    if abs(x1 - x2) < EPS:
        if abs(x - x1) > EPS: return False
        lo, hi = sorted((y1, y2))
        return (lo + EPS < y < hi - EPS) if interior else (lo - EPS <= y <= hi + EPS)
    else:
        if abs(y - y1) > EPS: return False
        lo, hi = sorted((x1, x2))
        return (lo + EPS < x < hi - EPS) if interior else (lo - EPS <= x <= hi + EPS)

def seg_hits_box(a, b, box, m=0.4):
    x1, y1, x2, y2 = box[0] + m, box[1] + m, box[2] - m, box[3] - m
    if x1 >= x2 or y1 >= y2: return False
    lx, hx = sorted((a[0], b[0])); ly, hy = sorted((a[1], b[1]))
    return not (hx < x1 or lx > x2 or hy < y1 or ly > y2)

def overlap_colinear(a, b, s):
    (x1, y1), (x2, y2) = s["a"], s["b"]
    if abs(a[0] - b[0]) < EPS and abs(x1 - x2) < EPS and abs(a[0] - x1) < EPS:
        lo1, hi1 = sorted((a[1], b[1])); lo2, hi2 = sorted((y1, y2)); return min(hi1, hi2) > max(lo1, lo2) + EPS
    if abs(a[1] - b[1]) < EPS and abs(y1 - y2) < EPS and abs(a[1] - y1) < EPS:
        lo1, hi1 = sorted((a[0], b[0])); lo2, hi2 = sorted((x1, x2)); return min(hi1, hi2) > max(lo1, lo2) + EPS
    return False

def seg_ok(a, b, net, blkbox):
    if abs(a[0] - b[0]) < EPS and abs(a[1] - b[1]) < EPS: return True
    t = {"a": a, "b": b}
    for p in pin_pts:
        if p["net"] != net and on_seg((p["x"], p["y"]), t): return False
        if p["net"] == net and on_seg((p["x"], p["y"]), t, interior=True): return False
    for s in segs:
        if s["net"] != net:
            if overlap_colinear(a, b, s) or on_seg(s["a"], t) or on_seg(s["b"], t) or on_seg(a, s) or on_seg(b, s):
                return False
        elif overlap_colinear(a, b, s): return False
    for bb, _ in bodies:
        if seg_hits_box(a, b, bb): return False
    if blkbox and not (blkbox[0] < min(a[0], b[0]) and max(a[0], b[0]) < blkbox[2]
                       and blkbox[1] < min(a[1], b[1]) and max(a[1], b[1]) < blkbox[3]): return False
    return True

def split_at(pt, net):
    for s in list(segs):
        if s["net"] == net and on_seg(pt, s, interior=True):
            segs.remove(s); segs.append(dict(a=s["a"], b=pt, net=net)); segs.append(dict(a=pt, b=s["b"], net=net))
            return

wired = set()   # (ref, num) com fio
clusters = {}
for p in pin_pts:
    if p["net"].startswith("NC") or p["net"] in POWER: continue
    clusters.setdefault((p["net"], p["blk"]), []).append(p)
net_blocks = {}
for (n, b) in clusters: net_blocks.setdefault(n, set()).add(b)

for (net, blk), P in sorted(clusters.items(), key=lambda kv: len(kv[1])):
    if len(P) < 2 or net in FORCE_LABEL: continue
    box = BLOCKS[blk][1] if blk else None
    tree_pts = [(P[0]["x"], P[0]["y"])]; done = {0}
    progress = True
    while progress and len(done) < len(P):
        progress = False
        best = None
        for i, p in enumerate(P):
            if i in done: continue
            src = (p["x"], p["y"])
            cands = list(tree_pts)
            for s in segs:
                if s["net"] != net: continue
                (x1, y1), (x2, y2) = s["a"], s["b"]
                cands.append((min(max(src[0], min(x1, x2)), max(x1, x2)), min(max(src[1], min(y1, y2)), max(y1, y2))))
            for t in cands:
                routes = []
                if abs(src[0] - t[0]) < EPS or abs(src[1] - t[1]) < EPS: routes.append([src, t])
                else: routes += [[src, (t[0], src[1]), t], [src, (src[0], t[1]), t]]
                for rt in routes:
                    if all(seg_ok(rt[k], rt[k + 1], net, box) for k in range(len(rt) - 1)):
                        L = sum(abs(rt[k][0] - rt[k + 1][0]) + abs(rt[k][1] - rt[k + 1][1]) for k in range(len(rt) - 1))
                        if best is None or L < best[0]: best = (L, i, rt, t)
        if best:
            L, i, rt, t = best
            split_at(t, net)
            for k in range(len(rt) - 1):
                if rt[k] != rt[k + 1]:
                    split_at(rt[k], net); segs.append(dict(a=rt[k], b=rt[k + 1], net=net))
            tree_pts += rt
            wired.add((P[i]["ref"], P[i]["num"])); wired.add((P[0]["ref"], P[0]["num"]))
            done.add(i); progress = True
    for i in done:
        if len(done) > 1: wired.add((P[i]["ref"], P[i]["num"]))

# ---------- labels, símbolos de alimentação e no_connect ----------
labels = []
labeled_cluster = set()
for p in pin_pts:
    net = p["net"]; key = (p["ref"], p["num"])
    if net.startswith("NC"):
        labels.append([S("no_connect"), [S("at"), p["x"], p["y"]], [S("uuid"), U(f"nc-{key}")]]); continue
    if net in POWER:
        pwr_n[0] += 1
        o = p["out"]
        r = (o - 270) % 360 if net == "GND" else (o - 90) % 360
        place_symbol({"lib": POWER[net]}, p["x"], p["y"], r, ref=f"#PWR0{pwr_n[0]:02d}", value=net)
        continue
    need = (key not in wired) or (len(net_blocks[net]) > 1 and (net, p["blk"]) not in labeled_cluster)
    if not need: continue
    labeled_cluster.add((net, p["blk"]))
    o = p["out"]
    just = "left" if o in (0, 90) else "right"
    labels.append([S("global_label"), net, [S("shape"), S("passive")], [S("at"), p["x"], p["y"], o],
                   [S("fields_autoplaced"), S("yes")], eff(1.27, just), [S("uuid"), U(f"lab-{key}")],
                   [S("property"), "Intersheetrefs", "${INTERSHEET_REFS}", [S("at"), p["x"], p["y"], 0], eff(hide=True)]])

# PWR_FLAG (ERC): bandeira + símbolo de alimentação no mesmo ponto
for i, net in enumerate(["GND", "+5V", "+3V3"]):
    fx, fy = 27.94 + 15.24 * i, 182.88
    place_symbol({"lib": "power:PWR_FLAG"}, fx, fy, 0, ref=f"#FLG0{i+1}", value="PWR_FLAG")
    pwr_n[0] += 1
    place_symbol({"lib": POWER[net]}, fx, fy, 0 if net == "GND" else 180, ref=f"#PWR0{pwr_n[0]:02d}", value=net)

# ---------- fios e junções ----------
wires = []
ends = {}
for s in segs:
    wires.append([S("wire"), [S("pts"), [S("xy"), *s["a"]], [S("xy"), *s["b"]]],
                  [S("stroke"), [S("width"), 0], [S("type"), S("default")]], [S("uuid"), U(f"w-{s['a']}-{s['b']}-{s['net']}")]])
    for e in (s["a"], s["b"]): ends[e] = ends.get(e, 0) + 1
pinset = {(p["x"], p["y"]) for p in pin_pts}
junctions = [[S("junction"), [S("at"), *pt], [S("diameter"), 0], [S("color"), 0, 0, 0, 0], [S("uuid"), U(f"j-{pt}")]]
             for pt, n in ends.items() if n + (1 if pt in pinset else 0) >= 3]

# ---------- blocos tracejados, títulos e notas ----------
deco = []
for k, (title, (x1, y1, x2, y2)) in BLOCKS.items():
    deco.append([S("rectangle"), [S("start"), x1 + 1.27, y1 + 1.27], [S("end"), x2 - 1.27, y2 - 1.27],
                 [S("stroke"), [S("width"), 0.3], [S("type"), S("dash")], [S("color"), 0, 0, 132, 1]],
                 [S("fill"), [S("type"), S("none")]], [S("uuid"), U("blk-" + k)]])
    deco.append([S("text"), title, [S("exclude_from_sim"), S("no")], [S("at"), x1 + 3.81, y1 + 6.35, 0],
                 eff(2.54, "left", bold=True), [S("uuid"), U("tit-" + k)]])
for i, t in enumerate(TEXT_NOTES):
    deco.append([S("text"), t, [S("exclude_from_sim"), S("no")], [S("at"), 171.45, 198.12 + 6.35 * i, 0],
                 eff(1.8 if i else 2.2, "left", bold=(i == 0)), [S("uuid"), U(f"note-{i}")]])

sch = [S("kicad_sch"), [S("version"), 20250114], [S("generator"), "eeschema"], [S("generator_version"), "9.0"],
       [S("uuid"), ROOT], [S("paper"), "A3"],
       [S("title_block"), [S("title"), "Aviônica F-500 v2 rev.B — telemetria p/ tracker + câmera"],
        [S("date"), "2026-11-08"], [S("rev"), "B"], [S("company"), "UTFPR Rocket"],
        [S("comment"), 1, "Esquemático em blocos conforme o Guia de PCB (correções Payload 2026)"]],
       lib_symbols, *deco, *junctions, *wires, *labels, *inst_list,
       [S("sheet_instances"), [S("path"), "/", [S("page"), "1"]]], [S("embedded_fonts"), S("no")]]
open(OUT, "w").write(dump(sch) + "\n")
nw = sum(1 for k in clusters if len(clusters[k]) > 1)
print(f"sch ok: {len(COMPS)} comps, {len(segs)} fios, {len(labels)} labels/nc, {pwr_n[0]} símbolos de alimentação")
