import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from design import NETCLASSES
def nc(name, track, clearance, via_dia, via_drill):
    return {"name": name, "track_width": track, "clearance": clearance, "via_diameter": via_dia, "via_drill": via_drill,
            "microvia_diameter": 0.3, "microvia_drill": 0.1, "diff_pair_width": 0.2, "diff_pair_gap": 0.25,
            "diff_pair_via_gap": 0.25, "wire_width": 6, "bus_width": 12, "line_style": 0, "schematic_color": "rgba(0, 0, 0, 0.000)",
            "pcb_color": "rgba(0, 0, 0, 0.000)", "priority": 2147483647 if name == "Default" else 0}
classes = [nc("Default", 0.3, 0.2, 0.7, 0.35)]
patterns = []
for i, (n, d) in enumerate(NETCLASSES.items()):
    c = nc(n, d["track"], d["clearance"], d["via_dia"], d["via_drill"]); c["priority"] = i; classes.append(c)
    patterns += [{"netclass": n, "pattern": p} for p in d["nets"]]
pro = {
  "board": {"design_settings": {"rules": {"min_clearance": 0.2, "min_track_width": 0.25, "min_via_diameter": 0.6,
            "min_through_hole_diameter": 0.3, "min_copper_edge_clearance": 0.3, "min_hole_clearance": 0.25}}},
  "erc": {"rule_severities": {"pin_to_pin": "warning", "power_pin_not_driven": "error"}},
  "meta": {"filename": "avionica_f500_v2.kicad_pro", "version": 3},
  "net_settings": {"classes": classes, "meta": {"version": 4}, "netclass_patterns": patterns},
  "schematic": {"legacy_lib_dir": "", "legacy_lib_list": []},
  "sheets": [["6b3f0c1e", "Root"]],
  "text_variables": {}
}
json.dump(pro, open(sys.argv[1], "w"), indent=2)
print("pro ok")
