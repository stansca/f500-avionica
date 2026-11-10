import sys, os, uuid, copy
sys.path.insert(0, os.path.dirname(__file__))
from sexp import Sym, dump, find, findall
from symlib import get_symbol, pins
from design import COMPS, TEXT_NOTES

PROJ = sys.argv[1]  # nome do projeto
OUT = sys.argv[2]
NS = uuid.UUID("6b3f0c1e-5000-4f00-a000-f500f500f500")
def U(s): return str(uuid.uuid5(NS, s))
ROOT = U("root-sheet")
S = Sym

def eff(size=1.27, justify=None, hide=False):
    e = [S("effects"), [S("font"), [S("size"), size, size]]]
    if justify: e.append([S("justify"), *[S(j) for j in justify.split()]])
    if hide: e.append([S("hide"), S("yes")])
    return e

def snap(v): return round(v / 1.27) * 1.27

lib_symbols = [S("lib_symbols")]
seen = set()
body = []
labels = []

FLAGS = [dict(ref=f"#FLG0{i+1}", lib="power:PWR_FLAG", value="PWR_FLAG", fp="", pins={"1": n},
              sch=(345.44 + 12.7 * i, 233.68)) for i, n in enumerate(["GND", "+5V", "+3V3", "VBAT"])]
for c in COMPS + FLAGS:
    lib = c["lib"]
    sym = get_symbol(lib)
    if lib not in seen:
        seen.add(lib)
        s2 = copy.deepcopy(sym); s2[1] = lib
        for sub in findall(s2, "symbol"): pass
        lib_symbols.append(s2)
    pl = pins(sym)
    units = sorted({p["unit"] for p in pl if p["unit"] > 0}) or [1]
    for k in c["pins"]:
        if k not in {p["num"] for p in pl}:
            raise SystemExit(f"pino inexistente {c['ref']}.{k}")
    is_flag = c["ref"].startswith("#")
    for ui, unit in enumerate(units):
        X, Y = snap(c["sch"][0]), snap(c["sch"][1] + 7.62 * ui)
        uid = U(f"sym-{c['ref']}-{unit}") if unit > 1 else U("sym-" + c["ref"])
        props = {p[1]: p for p in findall(sym, "property")}
        def pat(name, hide=False):
            p = props.get(name)
            at = find(p, "at") if p is not None else [0, 0, 0]
            return [S("property"), name, None, [S("at"), X + float(at[1]), Y - float(at[2]), 0], eff(hide=hide)]
        inst = [S("symbol"), [S("lib_id"), lib], [S("at"), X, Y, 0], [S("unit"), unit],
                [S("exclude_from_sim"), S("no")], [S("in_bom"), S("no" if (c["ref"][0] in "H#") else "yes")],
                [S("on_board"), S("no" if is_flag else "yes")], [S("dnp"), S("no")], [S("uuid"), uid]]
        for name, val, hide in (("Reference", c["ref"], is_flag), ("Value", c["value"], is_flag),
                                ("Footprint", c["fp"], True), ("Datasheet", "", True), ("Description", "", True)):
            p = pat(name, hide); p[2] = val; inst.append(p)
        upins = [p for p in pl if p["unit"] in (0, unit)]
        for p in upins:
            inst.append([S("pin"), p["num"], [S("uuid"), U(f"pin-{c['ref']}-{p['num']}")]])
        inst.append([S("instances"), [S("project"), PROJ, [S("path"), "/" + ROOT, [S("reference"), c["ref"]], [S("unit"), unit]]]])
        body.append(inst)
        done = set()
        for p in upins:
            net = c["pins"].get(p["num"])
            if net is None:
                raise SystemExit(f"pino sem net: {c['ref']}.{p['num']} ({p['name']})")
            px, py = X + p["x"], Y - p["y"]
            key = (round(px, 2), round(py, 2))
            if key in done: continue
            done.add(key)
            if net.startswith("NC"):
                labels.append([S("no_connect"), [S("at"), px, py], [S("uuid"), U(f"nc-{c['ref']}-{p['num']}")]])
                continue
            a = int(p["ang"]) % 360
            lang, just = {0: (180, "right"), 180: (0, "left"), 90: (270, "right"), 270: (90, "left")}[a]
            kind = "global_label" if net in ("GND", "+5V", "+3V3", "VBAT") else "label"
            lab = [S(kind), net]
            if kind == "global_label":
                lab += [[S("shape"), S("passive")]]
            lab += [[S("at"), px, py, lang], eff(1.27, just), [S("uuid"), U(f"lab-{c['ref']}-{p['num']}")]]
            if kind == "global_label":
                lab.append([S("property"), "Intersheetrefs", "${INTERSHEET_REFS}", [S("at"), px, py, 0], eff(hide=True)])
            labels.append(lab)

texts = []
for (x, y), t in TEXT_NOTES:
    texts.append([S("text"), t, [S("exclude_from_sim"), S("no")], [S("at"), x, y, 0],
                  [S("effects"), [S("font"), [S("size"), 2.2, 2.2], [S("bold"), S("yes")]], [S("justify"), S("left")]],
                  [S("uuid"), U("txt-" + t)]])

sch = [S("kicad_sch"), [S("version"), 20250114], [S("generator"), "eeschema"], [S("generator_version"), "9.0"],
       [S("uuid"), ROOT], [S("paper"), "A3"],
       [S("title_block"), [S("title"), "Aviônica F-500 v2 — telemetria p/ tracker + câmera"],
        [S("date"), "2026-11-08"], [S("rev"), "2.0"], [S("company"), "UTFPR Rocket"]],
       lib_symbols, *texts, *labels, *body,
       [S("sheet_instances"), [S("path"), "/", [S("page"), "1"]]], [S("embedded_fonts"), S("no")]]

def clean(x):
    if isinstance(x, list): return [clean(i) for i in x if i is not None or True]
    return x
txt = dump(sch).replace(" None", ' ""')
open(OUT, "w").write(txt + "\n")
print("ok", len(COMPS), "componentes")
