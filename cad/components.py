"""Visual stand-in parts (not printed): MX switch + keycap, thumbwheel,
SHIFT button, and a PCB blank. Each is authored in a local frame with a
single mate so the assembly can place it from params. These need not be
watertight — they exist to make the assembly read as a real device.
"""

from build123d import *
import machine_params as M


# ------------------------------------------------------------------ MX switch + keycap
def switch():
    """Local frame: z=0 at the deck top face. Body hangs down, keycap rises up."""
    lower = Pos(0, 0, -M.SWITCH_BELOW) * Box(
        14, 14, M.SWITCH_BELOW, align=(Align.CENTER, Align.CENTER, Align.MIN))
    housing = Box(M.SWITCH_BODY, M.SWITCH_BODY, 6.0,
                  align=(Align.CENTER, Align.CENTER, Align.MIN))
    cap = Pos(0, 0, 4.0) * Box(
        M.KEYCAP, M.KEYCAP, M.KEYCAP_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    cap = fillet(cap.edges().filter_by(Axis.Z), 1.5)
    return lower + housing + cap


SWITCH_MATES = {"mount": Location((0, 0, 0))}   # deck-top contact, world placed per key


# ------------------------------------------------------------------ thumbwheel
def thumbwheel():
    """Local frame: disc centered at origin, axis along Y (rolls up/down)."""
    disc = Rot(90, 0, 0) * Cylinder(M.WHEEL_R, M.WHEEL_T)
    # knurl hint: a slightly proud center rib
    rib = Rot(90, 0, 0) * Cylinder(M.WHEEL_R + 0.4, M.WHEEL_T * 0.35)
    disc = disc + rib
    # tiny encoder body behind it (inside, +X)
    body = Pos(M.WHEEL_R - M.WHEEL_PROTRUDE + 4, 0, 0) * Box(8, 12, 12)
    return disc + body


WHEEL_MATES = {"axis": Location((0, 0, 0))}


# ------------------------------------------------------------------ SHIFT button
def button():
    """Local frame: cap centered at origin, axis along X (pokes out -X)."""
    cap = Rot(0, 90, 0) * Cylinder(M.BTN_D / 2, 6.0)
    return cap


BTN_MATES = {"face": Location((0, 0, 0))}


# ------------------------------------------------------------------ PCB blank
def pcb():
    """Local frame: z=0 at PCB bottom. Footprint inset from the cavity walls."""
    board = Box(M.CAV_X - 3, M.CAV_Y - 3, M.PCB_T,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
    # MCU blob + USB connector hint on top
    mcu = Pos(15, -8, M.PCB_T) * Box(12, 17, 1.2,
                                     align=(Align.CENTER, Align.CENTER, Align.MIN))
    usb = Pos(M.USB_X, -M.CAV_Y / 2 + 4, M.PCB_T) * Box(
        9, 7, 3.2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return board + mcu + usb


PCB_MATES = {"origin": Location((0, 0, 0))}
