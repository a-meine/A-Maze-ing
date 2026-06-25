
from dataclasses import dataclass
from typing import Callable


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

    def contains(self, mx: int, my: int) -> bool:
        return (self.x <= mx < self.x + self.w) and (
            self.y <= my < self.y + self.h)
