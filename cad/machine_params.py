"""einhander — one-handed groovebox / MIDI controller.

SINGLE SOURCE OF TRUTH for every shared dimension + the place() mate helper.
Nothing downstream re-types a number that lives here.

Coordinate convention (world frame, right-handed device):
    +X = across the four fingers (column direction). Right = pinky side.
    +Y = "front" (away from palm, where the fingertips reach).
    -Y = "back"  (palm / wrist side).
    +Z = up (out of the top deck).
    World z=0 = underside of the bottom tray. Device grows upward.

Grip model: held in the right hand like a bar. Four fingers curl over the
back edge onto the 2x4 key deck (one column per finger, near/far per row).
The thumb wraps the LEFT (-X) wall and works the thumbwheel + SHIFT button.
"""

from math import sqrt
from build123d import Location, Pos, Rot  # noqa: F401  (re-exported for parts)


def place(solid, frm: Location, onto: Location):
    """Snap `solid` so its local mate `frm` coincides with world Location `onto`."""
    return (onto * frm.inverse()) * solid


# ---------------------------------------------------------------- key matrix
KEY_COLS = 4            # across the fingers (X)
KEY_ROWS = 2            # near / far per finger (Y)
KEY_PITCH = 19.05       # MX standard 0.75"
KEY_CUTOUT = 14.0       # MX plate cutout (square)
KEYCAP = 18.0           # 1u keycap footprint
KEYCAP_H = 9.0          # keycap height above deck
SWITCH_BODY = 15.6      # MX upper housing
SWITCH_BELOW = 5.0      # housing depth below deck top -> sets PCB plane

# center-to-center span of the matrix
KEYFIELD_X = (KEY_COLS - 1) * KEY_PITCH      # 57.15
KEYFIELD_Y = (KEY_ROWS - 1) * KEY_PITCH      # 19.05

# ---------------------------------------------------------------- body / shell
MARGIN_L = 12.0   # left (thumb) margin: keycap edge -> inner wall (wheel room)
MARGIN_R = 5.0    # right (pinky) margin
MARGIN_F = 9.0    # front margin
MARGIN_B = 24.0   # back (palm) margin — enlarged for the MCU band / routing room
WALL = 2.5
DECK_T = 1.5      # top plate thickness (MX snap-fit needs ~1.5)
FLOOR_T = 2.0

# inner cavity, centered on the body origin
CAV_X = KEYFIELD_X + KEYCAP + MARGIN_L + MARGIN_R
CAV_Y = KEYFIELD_Y + KEYCAP + MARGIN_F + MARGIN_B
BODY_X = CAV_X + 2 * WALL
BODY_Y = CAV_Y + 2 * WALL

# the matrix is pushed off-center so the thumb side gets the extra room
KEY_CENTER_X = (MARGIN_L - MARGIN_R) / 2.0   # +ve -> matrix shifts toward pinky
KEY_CENTER_Y = (MARGIN_B - MARGIN_F) / 2.0   # +ve -> matrix shifts toward front

# ---------------------------------------------------------------- heights
H_TOTAL = 26.0                     # shell height (keycaps extra)
SEAM_Z = 7.0                       # split plane: bottom tray height
H_BOT = SEAM_Z                     # bottom shell height
H_TOP = H_TOTAL - SEAM_Z           # top shell height (19)

DECK_TOP_Z = H_TOTAL                       # world z of deck top face
DECK_UNDER_Z = H_TOTAL - DECK_T            # 24.5
PCB_T = 1.6
PCB_TOP_Z = DECK_UNDER_Z - SWITCH_BELOW    # 19.5  (switch sits on plate, solders to PCB)
PCB_BOT_Z = PCB_TOP_Z - PCB_T


def key_xy(col, row):
    """World (x, y) of a switch center."""
    x = KEY_CENTER_X + (col - (KEY_COLS - 1) / 2.0) * KEY_PITCH
    y = KEY_CENTER_Y + (row - (KEY_ROWS - 1) / 2.0) * KEY_PITCH
    return x, y


KEY_XY = [key_xy(c, r) for r in range(KEY_ROWS) for c in range(KEY_COLS)]

# ---------------------------------------------------------------- thumb cluster (left wall)
WHEEL_R = 8.0          # dia 16 thumbwheel
WHEEL_T = 6.0          # rim width (along Y)
WHEEL_PROTRUDE = 2.5   # how far the rim pokes past the outer wall (-X)
WHEEL_Y = 6.0          # toward front
WHEEL_Z = 15.0         # mid-height
# wheel axis runs along Y (front-back); thumb rolls it up/down through a side slot
WHEEL_CX = -BODY_X / 2 + (WHEEL_R - WHEEL_PROTRUDE)   # disc center x (inside)

# slot in the left wall: narrow in Y (rim width), tall in Z (exposed chord)
WHEEL_SLOT_W = WHEEL_T + 1.5
WHEEL_SLOT_H = 2 * sqrt(WHEEL_R**2 - (WHEEL_R - WHEEL_PROTRUDE) ** 2) + 2.5

BTN_D = 8.0            # SHIFT button cap diameter
BTN_Y = -14.0          # toward back (palm); thumb slides wheel<->button along Y
BTN_Z = 15.0

# ---------------------------------------------------------------- USB-C (back wall)
USB_W = 11.0
USB_H = 5.0
USB_X = 0.0
USB_Z = PCB_TOP_Z      # connector body rides on top of the PCB
