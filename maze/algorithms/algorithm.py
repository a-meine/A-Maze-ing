from abc import ABC, abstractmethod
from typing import Callable
from maze.cell import Cell
from maze.grid import Grid


class Algorithm(ABC):
    _grid: Grid

    def __init__(self, width: int, height: int) -> None:
        self._grid = Grid(width, height)

    def __getitem__(self, pos: int) -> list[Cell]:
        return self._grid[pos]

    def __setitem__(self, pos: int, value: list[Cell]) -> None:
        self._grid[pos] = value

    @property
    def width(self) -> int:
        return self._grid.width

    @property
    def height(self) -> int:
        return self._grid.height

    @property
    def grid(self) -> Grid:
        return self._grid

    @abstractmethod
    def generate_maze(self,
                      fn: Callable[[Cell], None] | None = None) -> None:
        pass
