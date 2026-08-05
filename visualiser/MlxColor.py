class MlxColor:
    ROSEWATER = 0xFFDC8A78
    FLAMINGO = 0xFFDD7878
    PINK = 0xFFEA76CB
    MAUVE = 0xFF8839EF
    RED = 0xFFD20F39
    MAROON = 0xFFE64553
    PEACH = 0xFFFE640B
    YELLOW = 0xFFDF8E1D
    GREEN = 0xFF40A02B
    TEAL = 0xFF179299
    SKY = 0xFF04A5E5
    SAPPHIRE = 0xFF209FB5
    BLUE = 0xFF1E66F5
    LAVENDER = 0xFF7287FD
    TEXT = 0xFF4C4F69
    SUBTEXT_1 = 0xFF5C5F77
    SUBTEXT_0 = 0xFF6C6F85
    OVERLAY_2 = 0xFF7C7F93
    OVERLAY_1 = 0xFF8C8FA1
    OVERLAY_0 = 0xFF9CA0B0
    SURFACE_2 = 0xFFACB0BE
    SURFACE_1 = 0xFFBCC0CC
    SURFACE_0 = 0xFFCCD0DA
    BASE = 0xFFEFF1F5
    MANTLE = 0xFFE6E9EF
    CRUST = 0xFFDCE0E8
    WHITE = BASE
    BLACK = TEXT

    @classmethod
    def to_rgb(cls, color: int) -> tuple[int, int, int]:
        return ((color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF)

    @classmethod
    def to_hex(cls, color: int) -> int:
        return color & 0xFFFFFF
