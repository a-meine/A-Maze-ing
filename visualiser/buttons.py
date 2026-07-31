"""visualiser.buttons module."""

from dataclasses import dataclass
from typing import Callable
from typing import Any


@dataclass
class Button:
    """Represents a clickable button widget.

    Attributes:
        x (int): The x position of the button.
        y (int): The y position of the button.
        w (int): The width of the button.
        h (int): The height of the button.
        label (str): The text displayed on the button.
        color_normal (tuple[int, int, int]): The color when not pressed.
        color_pressed (tuple[int, int, int]): The color when pressed.
        pressed (bool): Whether the button is currently pressed.
        action (Callable[..., Any] | None): The callback action.
    """

    x: int
    y: int
    w: int
    h: int
    label: str
    color_normal: tuple[int, int, int]
    color_pressed: tuple[int, int, int]
    pressed: bool = False
    action: Callable[..., Any] | None = None

    def contains(self, mx: int, my: int) -> bool:
        """Check if the given coordinates are inside the button bounds.

        Args:
            mx (int): The x coordinate to check.
            my (int): The y coordinate to check.

        Returns:
            bool: True if the coordinates are inside the button bounds.
        """
        return (self.x <= mx < self.x + self.w) and (
            self.y <= my < self.y + self.h)