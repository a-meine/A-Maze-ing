from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


def fill_image(m, img, w: int, h: int, color: tuple[int, int, int],
               margin_x: int = 0, margin_y: int = 0):
    data, bpp, size_line, endian = m.mlx_get_data_addr(img)
    r, g, b = color
    for y in range(margin_y, h - margin_y):
        for x in range(margin_x, w - margin_x):
            index = y * size_line + x * (bpp // 8)
            data[index + 0] = b
            data[index + 1] = g
            data[index + 2] = r
            data[index + 3] = 255


FOCUSED_COLOR = (80, 80, 220)
UNFOCUSED_COLOR = (80, 80, 80)


@dataclass
class Button:
    x: int
    y: int
    w: int
    h: int
    label: str
    color_normal: tuple[int, int, int]
    color_pressed: tuple[int, int, int]
    pressed: bool = False
    action: Callable | None = None
    
    _img = None
    _last_pressed: bool | None = None

    def contains(self, mx: int, my: int) -> bool:
        return self.x <= mx < self.x + self.w and self.y <= my < self.y + self.h

    def draw(self, m, mlx_ptr, win_ptr) -> None:
        if self._img is None or self._last_pressed != self.pressed:
            self._img = m.mlx_new_image(mlx_ptr, self.w, self.h)
            color = self.color_pressed if self.pressed else self.color_normal
            fill_image(m, self._img, self.w, self.h, color)
            self._last_pressed = self.pressed

        m.mlx_put_image_to_window(mlx_ptr, win_ptr,
                                  self._img, self.x, self.y)
        m.mlx_string_put(mlx_ptr, win_ptr,
                         self.x + 5, self.y + 8, 0xFFFFFF, self.label)


@dataclass
class InputField:
    x: int
    y: int
    w: int
    h: int
    label: str
    text: str = ""
    focused: bool = False
    action: Callable | None = None

    _img = None
    _last_focused: bool | None = None

    def contains(self, mx: int, my: int) -> bool:
        return self.x <= mx < self.x + self.w and self.y <= my < self.y + self.h

    def draw(self, m, mlx_ptr, win_ptr) -> None:
        if self._img is None or self._last_focused != self.focused:
            self._img = m.mlx_new_image(mlx_ptr, self.w, self.h)
            color = FOCUSED_COLOR if self.focused else UNFOCUSED_COLOR
            fill_image(m, self._img, self.w, self.h, color)
            self._last_focused = self.focused

        m.mlx_put_image_to_window(mlx_ptr, win_ptr,
                                  self._img, self.x, self.y)
        m.mlx_string_put(mlx_ptr, win_ptr,
                         self.x + self.w, self.y + 5, 0xFFFFFF, self.label)
        m.mlx_string_put(mlx_ptr, win_ptr,
                         self.x, self.y + 2, 0xFFFFFF, self.text)
