"""Gera o esquemático e confere a netlist exportada pelo KiCad contra design.py; nets com erro viram label."""
import subprocess, sys, re, os
sys.path.insert(0, os.path.dirname(__file__))
from design import COMPS
K = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
proj, out, net = sys.argv[1], sys.argv[2], sys.argv[3]
want = {}
for c in COMPS:
    for p, n in c["pins"].items():
        if not n.startswith("NC"): want.setdefault(n, set()).add((c["ref"], p))
force = {"VBAT"}   # VBAT agora fica só no bloco 1: label forçado mantém o nome (classe Bateria)
for it in range(6):
    r = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "gen_sch.py"), proj, out, ",".join(sorted(force))],
                       capture_output=True, text=True)
    print(r.stdout.strip(), r.stderr.strip()[-500:])
    subprocess.run([K, "sch", "export", "netlist", "--format", "kicadsexpr", "-o", net, out], capture_output=True)
    t = re.sub(r"\s+", " ", open(net).read())
    got = {}
    for blk in t[t.find("(nets"):].split("(net (code")[1:]:
        nm = re.search(r'\(name "([^"]*)"', blk).group(1).lstrip("/")
        nodes = set(re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', blk))
        nodes = {x for x in nodes if not x[0].startswith("#")}
        if nodes and not nm.startswith("unconnected"): got[nm] = nodes
    bad = set()
    gotsets = {frozenset(v): k for k, v in got.items()}
    for n, nodes in want.items():
        if frozenset(nodes) not in gotsets: bad.add(n)
    if len(got) != len(want): print("nº de nets difere", len(got), len(want))
    if not bad:
        print("netlist OK na iteração", it); break
    print("divergências:", sorted(bad)); force |= {b for b in bad if b in want}
else:
    sys.exit("netlist não convergiu")
