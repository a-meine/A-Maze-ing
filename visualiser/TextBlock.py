"""visualiser.TextBlock module."""


class TextBlock:
    """Represents a piece of text to be drawn on a layout.

    Attributes:
        x (int): The x position relative to the owning layout.
        y (int): The y position relative to the owning layout.
        color (int): The text color as an MlxColor 0xRRGGBB integer.
        text (str): The string to display.
    """

    def __init__(self, x: int, y: int, color: int, text: str) -> None:
        """Initialize a TextBlock with position, color and text.

        Args:
            x (int): The x position relative to the owning layout.
            y (int): The y position relative to the owning layout.
            color (int): The text color as an MlxColor 0xRRGGBB integer.
            text (str): The string to display.
        """
        self.x = x
        self.y = y
        self.color = color
        self.text = text
