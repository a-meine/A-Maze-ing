"""visualiser.input_fields module."""
from dataclasses import dataclass
from typing import Callable


@dataclass
class InputField:
    """Represents an input field widget for text entry.

    Attributes:
        x (int): The x position of the input field.
        y (int): The y position of the input field.
        w (int): The width of the input field.
        h (int): The height of the input field.
        label (str): The label displayed for the field.
        text (str): The current text content.
        focused (bool): Whether the field is currently focused.
        action (Callable[..., None] | None): The callback action.
    """

    x: int
    y: int
    w: int
    h: int
    label: str
    text: str = ""
    focused: bool = False
    action: Callable[..., None] | None = None

    def contains(self, mx: int, my: int) -> bool:
        """Check if the given coordinates are inside the input field bounds.

        Args:
            mx (int): The x coordinate to check.
            my (int): The y coordinate to check.

        Returns:
            bool: True if the coordinates are inside the input field bounds.
        """
        return (self.x <= mx < self.x + self.w) and (
            self.y <= my < self.y + self.h)