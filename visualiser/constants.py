"""visualiser.refactored.constants module.

Shared constants for the refactored visualiser: key codes,
window events and the MlxColor palette aliases used across modules.
"""
from visualiser.MlxColor import MlxColor

WIN_WIDTH: int = 1920
WIND_HEIGHT: int = 1000

KEY_ESC = 65307
KEY_BACKSPACE = 65288
KEY_0 = 48
KEY_9 = 57
WIN_CLOSE = 33

WHITE = MlxColor.WHITE
GREEN = MlxColor.GREEN
MAGENTA = MlxColor.PINK
PINK = MlxColor.PINK
CYAN = MlxColor.SKY
GRAY = MlxColor.OVERLAY_2
MED_GRAY = MlxColor.OVERLAY_0
INACTIVE_GRAY = MlxColor.OVERLAY_1
RED = MlxColor.RED
YELLOW = MlxColor.YELLOW



PATTERN_COLORS = (
    MlxColor.MAROON,
    MlxColor.MAUVE,
    MlxColor.SAPPHIRE,
)
PATTERN_NAMES = ("Maroon", "Mauve", "Sapphire")

WALL_COLORS = (
    MlxColor.OVERLAY_2,
    MlxColor.TEAL,
    MlxColor.SAPPHIRE,
    MlxColor.MAROON,
    MlxColor.MAUVE,
)
WALL_NAMES = ("Gray", "Teal", "Sapphire", "Maroon", "Mauve")
