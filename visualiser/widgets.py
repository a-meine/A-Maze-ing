"""visualiser.widgets module.

Provides reusable UI widget components for the visualiser.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from MlxColor import MlxColor


def fill_image(
        m: Any, img: Any, w: int, h: int,
        color: tuple[int, int, int] | int,
        margin_x: int = 0, margin_y: int = 0) -> None:
    """Fill an image buffer with a solid color.

    Args:
        m (Any): The Mlx instance.
        img (Any): The image buffer to fill.
        w (int): The width of the image.
        h (int): The height of the image.
        color (tuple[int, int, int] | int): The RGB color as a tuple
            or an MlxColor 0xFFRRGGBB integer.
        margin_x (int): Horizontal margin to skip. Defaults to 0.
        margin_y (int): Vertical margin to skip. Defaults to 0.
    """
    if isinstance(color, int):
        color = MlxColor.to_rgb(color)
    data, bpp, size_line, endian = m.mlx_get_data_addr(img)
    r, g, b = color
    for y in range(margin_y, h - margin_y):
        for x in range(margin_x, w - margin_x):
            index = y * size_line + x * (bpp // 8)
            data[index + 0] = b
            data[index + 1] = g
            data[index + 2] = r
            data[index + 3] = 255


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
    color_normal: tuple[int, int, int]
    color_pressed: tuple[int, int, int]
    pressed: bool = False
    action: Callable[..., None] | None = None

    _img = None
    _last_pressed: bool | None = None

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

    def draw(self, m: Any, mlx_ptr: Any, win_ptr: Any) -> None:
        """Draw the button onto the window.

        Args:
            m (Any): The Mlx instance.
            mlx_ptr (Any): The mlx pointer.
            win_ptr (Any): The window pointer.
        """
        if self._img is None or self._last_pressed != self.pressed:
            self._img = m.mlx_new_image(mlx_ptr, self.w, self.h)
            color = self.color_pressed if self.pressed else self.color_normal
            fill_image(m, self._img, self.w, self.h, color)
            self._last_pressed = self.pressed

        m.mlx_put_image_to_window(mlx_ptr, win_ptr,
                                  self._img, self.x, self.y)
        m.mlx_string_put(mlx_ptr, win_ptr,
                         self.x + 5, self.y + 8,
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

    _img = None
    _last_focused: bool | None = None

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

    def draw(self, m: Any, mlx_ptr: Any, win_ptr: Any) -> None:
        """Draw the input field onto the window.

        Args:
            m (Any): The Mlx instance.
            mlx_ptr (Any): The mlx pointer.
            win_ptr (Any): The window pointer.
        """
        if self._img is None or self._last_focused != self.focused:
            self._img = m.mlx_new_image(mlx_ptr, self.w, self.h)
            color = FOCUSED_COLOR if self.focused else UNFOCUSED_COLOR
            fill_image(m, self._img, self.w, self.h, color)
            self._last_focused = self.focused

        m.mlx_put_image_to_window(mlx_ptr, win_ptr,
                                  self._img, self.x, self.y)
        m.mlx_string_put(mlx_ptr, win_ptr,
                         self.x + self.w, self.y + 5,
                         MlxColor.to_hex(MlxColor.WHITE), self.label)
        m.mlx_string_put(mlx_ptr, win_ptr,
                         self.x, self.y + 2,
                         MlxColor.to_hex(MlxColor.WHITE), self.text)