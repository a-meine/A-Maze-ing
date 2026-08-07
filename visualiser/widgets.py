"""visualiser.widgets module.

Provides reusable UI widget components for the visualiser.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from mlx import Mlx

from visualiser.MlxColor import MlxColor

def fill_image(
        m: Mlx, img: int, w: int, h: int,
        color: tuple[int, int, int] | int,
        margin_x: int = 0, margin_y: int = 0) -> None:
    """Fill an image buffer with a solid color.

    Args:
        m (Mlx): The Mlx instance.
        img (int): The image buffer to fill.
        w (int): The width of the image.
        h (int): The height of the image.
        color (tuple[int, int, int] | int): The RGB color as a tuple
            or an MlxColor 0xFFRRGGBB integer.
        margin_x (int): Horizontal margin to skip. Defaults to 0.
        margin_y (int): Vertical margin to skip. Defaults to 0.
    """
    if isinstance(color, int):
        color = MlxColor.to_rgb(color)
    data, bpp, size_line, _ = m.mlx_get_data_addr(img)
    r, g, b = color
    for y in range(margin_y, h - margin_y):
        for x in range(margin_x, w - margin_x):
            index = y * size_line + x * (bpp // 8)
            data[index + 0] = b
            data[index + 1] = g
            data[index + 2] = r
            data[index + 3] = 255


def fill_rect_image(
        m: Mlx, img: int, x: int, y: int, w: int, h: int,
        color: tuple[int, int, int] | int) -> None:
    """Fill a rectangular region (x, y, w, h) of an existing image buffer.

    Args:
        m (Mlx): The Mlx instance.
        img (int): The image buffer to fill.
        x (int): The x position of the rectangle.
        y (int): The y position of the rectangle.
        w (int): The width of the rectangle.
        h (int): The height of the rectangle.
        color (tuple[int, int, int] | int): The color as an MlxColor
            integer or an (r, g, b) tuple.
    """
    data, bpp, size_line, _ = m.mlx_get_data_addr(img)
    if isinstance(color, int):
        color = MlxColor.to_rgb(color)
    r, g, b = color
    bpp8 = bpp // 8
    for yy in range(y, y + h):
        row = yy * size_line
        start = row + x * bpp8
        for xx in range(w):
            i = start + xx * bpp8
            data[i + 0] = b
            data[i + 1] = g
            data[i + 2] = r
            data[i + 3] = 255


FOCUSED_COLOR = MlxColor.BLUE
UNFOCUSED_COLOR = MlxColor.OVERLAY_2


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
        action (Callable[..., None] | None): The callback action.
    """

    x: int
    y: int
    w: int
    h: int
    label: str
    color_normal: tuple[int, int, int] | int
    color_pressed: tuple[int, int, int] | int
    pressed: bool = False
    action: Callable[..., None] | None = None

    def contains(self, mx: int, my: int) -> bool:
        """Check if the given coordinates are inside the button bounds.

        Args:
            mx (int): The x coordinate to check.
            my (int): The y coordinate to check.

        Returns:
            bool: True if the coordinates are inside the button bounds.
        """
        return (
            self.x <= mx < self.x + self.w and self.y <= my < self.y + self.h)

    def current_color(self) -> tuple[int, int, int] | int:
        """Return the colour to draw, depending on pressed state."""
        return self.color_pressed if self.pressed else self.color_normal

    def paint(self, img: int, m: Mlx, ox: int = 0, oy: int = 0) -> None:
        """Fill the button rectangle into a shared canvas image.

        Args:
            img (Any): The shared canvas image.
            m (Any): The Mlx instance.
            ox (int): Horizontal offset of the canvas in the window.
            oy (int): Vertical offset of the canvas in the window.
        """
        fill_rect_image(m, img, self.x - ox, self.y - oy,
                        self.w, self.h, self.current_color())

    def put_label(self, m: Mlx, mlx_ptr: int, win_ptr: int) -> None:
        """Draw the button label onto the window.

        Args:
            m (Any): The Mlx instance.
            mlx_ptr (Any): The mlx pointer.
            win_ptr (Any): The window pointer.
        """
        m.mlx_string_put(mlx_ptr, win_ptr, self.x + 5, self.y + 8,
                         MlxColor.to_hex(MlxColor.WHITE), self.label)


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
        return (
            self.x <= mx < self.x + self.w and self.y <= my < self.y + self.h)

    def paint(self, img: int, m: Mlx, ox: int = 0, oy: int = 0) -> None:
        """Fill the input field rectangle into a shared canvas image.

        Args:
            img (Any): The shared canvas image.
            m (Any): The Mlx instance.
            ox (int): Horizontal offset of the canvas in the window.
            oy (int): Vertical offset of the canvas in the window.
        """
        color = FOCUSED_COLOR if self.focused else UNFOCUSED_COLOR
        fill_rect_image(m, img, self.x - ox, self.y - oy,
                        self.w, self.h, color)

    def put_label(self, m: Mlx, mlx_ptr: int, win_ptr: int) -> None:
        """Draw the input field label and text onto the window.

        Args:
            m (Any): The Mlx instance.
            mlx_ptr (Any): The mlx pointer.
            win_ptr (Any): The window pointer.
        """
        m.mlx_string_put(mlx_ptr, win_ptr,
                         self.x + self.w, self.y + 5,
                         MlxColor.to_hex(MlxColor.WHITE), self.label)
        m.mlx_string_put(mlx_ptr, win_ptr,
                         self.x, self.y + 2,
                         MlxColor.to_hex(MlxColor.WHITE), self.text)