from dataclasses import dataclass
from typing import Callable


@dataclass
class InputField:
    x: int
    y: int
    w: int
    h: int
    label: str
    text: str = ""
    focused: bool = False
    action: Callable[..., None] | None = None
    # coordinate: bool = False

    def contains(self, mx: int, my: int) -> bool:
        return (self.x <= mx < self.x + self.w) and (
            self.y <= my < self.y + self.h)
