"""Bottom shell: a shallow tray that closes the underside.

Local frame: XY centered on body origin, z=0 at the tray underside (world z=0),
up to z=SEAM_Z. The internals (PCB) hang from the top shell, so this is mostly
a base cover / future battery door.
"""

from build123d import *
import machine_params as M


def part():
    p = Box(M.BODY_X, M.BODY_Y, M.H_BOT,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
    p = fillet(p.edges().filter_by(Axis.Z), radius=4.0)

    # hollow from the floor up, open at the seam (overshoot above it)
    cav_h = (M.H_BOT - M.FLOOR_T) + 1.0
    cavity = Pos(0, 0, M.FLOOR_T) * Box(
        M.CAV_X, M.CAV_Y, cav_h,
        align=(Align.CENTER, Align.CENTER, Align.MIN))
    p -= cavity
    return p


MATES = {
    "seam": Location((0, 0, M.SEAM_Z)),   # top rim where the top shell lands
}


if __name__ == "__main__":
    p = part()
    bb = p.bounding_box()
    print(f"bottom_shell: solids={len(p.solids())} valid={p.is_valid()} "
          f"vol={p.volume:.0f} "
          f"bbox=({bb.size.X:.1f},{bb.size.Y:.1f},{bb.size.Z:.1f})")
