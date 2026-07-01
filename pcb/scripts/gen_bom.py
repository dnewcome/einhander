#!/usr/bin/env python3
"""gen_bom.py — build a JLCPCB-format assembly BOM from a routed KiCad board.

Reads every footprint's (Reference, Value, Footprint) from the .kicad_pcb, maps a
LCSC part number to each, groups identical parts, and writes a CSV with the columns
JLCPCB's assembly uploader expects:  Comment, Designator, Footprint, LCSC Part #, Note

LCSC numbers come from two places:
  * ICs / connectors — the `supplierPartNumbers` baked into imports/*.tsx (matched by Value).
  * generic passives — a small table of JLCPCB BASIC parts keyed by value + package.
Hand-soldered / mechanical parts (keyswitches, headers, tactiles) get a blank LCSC and a
Note so you can mark them Do-Not-Place in the JLC PCBA step.

    python3 gen_bom.py index.circuit.kicad_pcb [-o fab/einhander-bom.csv] [--imports imports]
"""
import argparse
import csv
import glob
import os
import re
from collections import defaultdict

# JLCPCB BASIC parts (stock-checked) keyed by (value, package-substring in footprint)
PASSIVES = {
    ("100nF", "0402"): "C1525", ("1uF", "0402"): "C52923", ("15pF", "0402"): "C1548",
    ("10uF", "0805"): "C15850", ("1uF", "0805"): "C28323", ("100nF", "0805"): "C49678",
    ("1k", "0402"): "C11702", ("5.1k", "0402"): "C25905", ("10k", "0402"): "C25744",
}
# footprint patterns that are hand-soldered / not JLC-assembled -> blank LCSC + note
HAND = [
    (r"chip$", "Cherry MX / Kailh keyswitch — hand solder"),
    (r"pin_?header|pinrow", "pin header — hand solder"),
    (r"push_?button|pushbutton", "tactile switch — hand solder or verify footprint"),
]


def norm(v):
    return v.replace("Ω", "").replace("µ", "u").strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("board")
    ap.add_argument("-o", "--out", default=None)
    ap.add_argument("--imports", default="imports")
    a = ap.parse_args()

    # LCSC from imports/*.tsx: manufacturerPartNumber -> first C-number
    ic = {}
    for f in glob.glob(os.path.join(a.imports, "*.tsx")):
        t = open(f).read()
        m = re.search(r'manufacturerPartNumber="([^"]+)"', t)
        c = re.search(r'"(C\d{3,})"', t)
        if m and c:
            ic[m.group(1)] = c.group(1)

    t = open(a.board).read()
    fps = re.findall(
        r'\(footprint "([^"]+)".*?\(property "Reference" "([^"]*)".*?\(property "Value" "([^"]*)"',
        t, re.S)

    groups = defaultdict(lambda: {"refs": [], "fp": "", "lcsc": "", "note": ""})
    for fp, ref, val in fps:
        if not ref or ref.startswith("REF"):
            continue
        val_n = norm(val)
        lcsc, note = "", ""
        if val in ic:                                   # imported IC/connector
            lcsc = ic[val]
        else:
            for (pv, pkg), pn in PASSIVES.items():      # passive by value + package
                if val_n == norm(pv) and pkg in fp:
                    lcsc = pn
                    break
        if not lcsc:
            for pat, n in HAND:                          # hand-solder / mechanical
                if re.search(pat, fp):
                    note = n
                    break
        key = (val, fp, lcsc)
        g = groups[key]
        g["refs"].append(ref); g["fp"] = fp; g["lcsc"] = lcsc; g["note"] = note

    def sortkey(item):
        (val, fp, lcsc), g = item
        return (0 if lcsc else 1, g["refs"][0][:2], val)

    out = a.out or os.path.join("fab", os.path.splitext(os.path.basename(a.board))[0] + "-bom.csv")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #", "Note"])
        n_asm = n_hand = 0
        for (val, fp, lcsc), g in sorted(groups.items(), key=sortkey):
            refs = ",".join(sorted(g["refs"], key=lambda r: (r[:2], r)))
            pkg = fp.split(":")[-1]
            w.writerow([val or "(no value)", refs, pkg, lcsc, g["note"]])
            n_asm += len(g["refs"]) if lcsc else 0
            n_hand += len(g["refs"]) if not lcsc else 0
    print(f"wrote {out}: {len(groups)} lines | {n_asm} assembled parts, {n_hand} hand-solder/DNP")


if __name__ == "__main__":
    main()
