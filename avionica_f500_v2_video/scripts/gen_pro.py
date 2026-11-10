"""Projeto KiCad com as configurações de placa importadas do modelo PCBWay (2 camadas, 1 oz) + classes de rede."""
import json, sys, os, copy
sys.path.insert(0, os.path.dirname(__file__))
from design import NETCLASSES, DEFAULT_TRACK
pw = json.load(open(sys.argv[2]))
pro = copy.deepcopy(pw)
pro["meta"]["filename"] = os.path.basename(sys.argv[1])
base = copy.deepcopy(pw["net_settings"]["classes"][0])
classes = []
d = copy.deepcopy(base); d.update(name="Default", track_width=DEFAULT_TRACK, clearance=0.2, via_diameter=0.6, via_drill=0.3)
classes.append(d)
patterns = []
for i, (n, c) in enumerate(NETCLASSES.items()):
    x = copy.deepcopy(base); x.update(name=n, track_width=c["track"], clearance=c["clearance"], via_diameter=c["via_dia"],
                                      via_drill=c["via_drill"], priority=i)
    classes.append(x); patterns += [{"netclass": n, "pattern": p} for p in c["nets"]]
classes[0]["priority"] = 2147483647
pro["net_settings"]["classes"] = classes
pro["net_settings"]["netclass_patterns"] = patterns
pro["net_settings"].pop("netclass_assignments", None)
ds = pro["board"]["design_settings"]
ds["track_widths"] = [0.0, 0.25, 0.5, 0.6, 1.0, 1.2, 2.8]
ds["via_dimensions"] = [{"diameter": 0.0, "drill": 0.0}, {"diameter": 0.6, "drill": 0.3}, {"diameter": 0.8, "drill": 0.4}, {"diameter": 1.0, "drill": 0.5}]
erc = pro.setdefault("erc", {})
erc.setdefault("rule_severities", {})["pin_to_pin"] = "warning"
# matriz padrão do KiCad, com saída x saída-de-alimentação rebaixado para aviso
# (o símbolo do módulo buck da biblioteca JS tipa OUT+/OUT- como "output")
pm = [[0,0,0,0,0,0,1,0,0,0,0,2],[0,2,0,1,0,0,1,0,1,2,2,2],[0,0,0,0,0,0,1,0,1,0,1,2],[0,1,0,0,0,0,1,1,2,1,1,2],
      [0,0,0,0,0,0,1,0,0,0,0,2],[0,0,0,0,0,0,0,0,0,0,0,2],[1,1,1,1,1,0,1,1,1,1,1,2],[0,0,0,1,0,0,1,0,0,0,0,2],
      [0,1,1,2,0,0,1,0,2,2,2,2],[0,2,0,1,0,0,1,0,2,0,0,2],[0,2,1,1,0,0,1,0,2,0,0,2],[2,2,2,2,2,2,2,2,2,2,2,2]]
erc["pin_map"] = pm
pro["sheets"] = []
pro["text_variables"] = {}
json.dump(pro, open(sys.argv[1], "w"), indent=2)
print("pro ok (regras PCBWay importadas)")
