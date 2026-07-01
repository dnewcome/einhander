"""Top shell: key deck + walls, with the 2x4 switch cutouts, the thumbwheel
slot + SHIFT button hole in the left wall, and the USB-C cutout in the back wall.

Local frame: XY centered on body origin, z=0 at the seam (its own underside),
growing up to z=H_TOP. World placement adds SEAM_Z in the assembly.
"""

from build123d import *
import machine_params as M


def part():
    # outer block, base (seam) at z=0
    p = Box(M.BODY_X, M.BODY_Y, M.H_TOP,
            align=(Align.CENTER, Align.CENTER, Align.MIN))

    # soften the four vertical corners for the hand (before any cuts)
    p = fillet(p.edges().filter_by(Axis.Z), radius=4.0)

    # hollow it: leave the deck on top + walls all around, open at the seam
    cav_h = (M.H_TOP - M.DECK_T) + 1.0          # overshoot below the seam
    cavity = Pos(0, 0, -1.0) * Box(
        M.CAV_X, M.CAV_Y, cav_h,
        align=(Align.CENTER, Align.CENTER, Align.MIN))
    p -= cavity

    # 8 switch cutouts through the deck (overshoot in Z)
    deck_mid = M.H_TOP - M.DECK_T / 2
    for (kx, ky) in M.KEY_XY:
        p -= Pos(kx, ky, deck_mid) * Box(
            M.KEY_CUTOUT, M.KEY_CUTOUT, M.DECK_T + 2.0)

    # thumbwheel slot in the left wall (-X): narrow in Y, tall in Z
    wheel_z_local = M.WHEEL_Z - M.SEAM_Z
    p -= Pos(-M.BODY_X / 2, M.WHEEL_Y, wheel_z_local) * Box(
        2 * M.WALL + 4, M.WHEEL_SLOT_W, M.WHEEL_SLOT_H)

    # SHIFT button hole in the left wall (-X), axis along X
    btn_z_local = M.BTN_Z - M.SEAM_Z
    p -= (Pos(-M.BODY_X / 2, M.BTN_Y, btn_z_local) * Rot(0, 90, 0)
          * Cylinder(M.BTN_D / 2 + 0.25, 2 * M.WALL + 4))

    # USB-C cutout in the back wall (-Y)
    usb_z_local = M.USB_Z - M.SEAM_Z
    p -= Pos(M.USB_X, -M.BODY_Y / 2, usb_z_local) * Box(
        M.USB_W, 2 * M.WALL + 4, M.USB_H)

    return p


MATES = {
    # seam ring: mate this onto the bottom shell's seam in the assembly
    "seam": Location((0, 0, 0)),
}


if __name__ == "__main__":
    p = part()
    bb = p.bounding_box()
    print(f"top_shell: solids={len(p.solids())} valid={p.is_valid()} "
          f"vol={p.volume:.0f} "
          f"bbox=({bb.size.X:.1f},{bb.size.Y:.1f},{bb.size.Z:.1f})")
