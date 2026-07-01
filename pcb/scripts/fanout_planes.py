#!/usr/bin/env python3
"""fanout_planes.py — connect unconnected GND/V3V3 pads to their inner plane with a
proper OFFSET fanout via (via placed just outboard of the pad + a short F.Cu trace),
so the via lands in clear copper instead of on the pad (via-in-pad bridges the
through-via's B.Cu ring onto neighbouring tracks -> false shorts).
"""
import json
import math
import re
import subprocess
import sys

import kipy
from kipy.board_types import Track, Via, BoardLayer
from kipy.geometry import Vector2

BOARD = sys.argv[1] if len(sys.argv) > 1 else "index.circuit.kicad_pcb"
PLANE = {"GND", "V3V3"}
OFF, VIA_PAD, VIA_DRILL, TRK_W = 750_000, 450_000, 250_000, 200_000  # nm

b = kipy.KiCad().get_board()
nets = {n.name: n for n in b.get_nets() if n.name}
padof, fpcenter = {}, {}
for fp in b.get_footprints():
    ref = fp.reference_field.text.value
    fpcenter[ref] = fp.position
    for pd in fp.definition.pads:
        padof[(ref, str(pd.number))] = (pd.position, pd.net.name if pd.net else "")

subprocess.run(["kicad-cli", "pcb", "drc", "--format", "json", "-o", "build/drc.json", BOARD],
               capture_output=True)
drc = json.load(open("build/drc.json"))

items, did, n = [], set(), 0
for v in drc.get("unconnected_items", []):
    pd = next((i.get("description", "") for i in v["items"] if i.get("description", "").startswith("Pad ")), "")
    m = re.match(r"Pad (\S+) \[(.+?)\] of (\S+)", pd)
    if not m:
        continue
    num, net, ref = m.group(1), m.group(2), m.group(3)
    if net not in PLANE or (ref, num) in did or (ref, num) not in padof:
        continue
    did.add((ref, num))
    pos, _ = padof[(ref, num)]
    c = fpcenter[ref]
    dx, dy = pos.x - c.x, pos.y - c.y
    d = math.hypot(dx, dy) or 1.0
    vp = Vector2.from_xy(int(pos.x + dx / d * OFF), int(pos.y + dy / d * OFF))
    via = Via(); via.position = vp; via.diameter = VIA_PAD; via.drill_diameter = VIA_DRILL; via.net = nets[net]
    tr = Track(); tr.start = pos; tr.end = vp; tr.width = TRK_W; tr.layer = BoardLayer.BL_F_Cu; tr.net = nets[net]
    items += [via, tr]; n += 1

created = b.create_items(items)
b.refill_zones(); b.save()
print(f"fanout_planes: {n} pads -> {n} vias + {n} traces, created={len(created)} -> saved")
