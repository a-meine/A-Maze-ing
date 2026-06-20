import random
from config.base import ConfigBase
from abc import ABC, abstractmethod
from typing import Callable
from maze.cell import Cell
from maze.grid import Grid


class MazeAlgorithm(ABC):

    def __init__(self, config: ConfigBase) -> None:
        self._grid = Grid(config.width, config.height)
        (x, y) = config.entry
        self._start_cell = self.grid[y][x]
        self._start_cell.occupied = True
        (x, y) = config.exit
        self._end_cell = self.grid[y][x]
        self._total_cells = self.width * self.height

    def __getitem__(self, pos: int) -> list[Cell]:
        return self.grid[pos]

    def __setitem__(self, pos: int, value: list[Cell]) -> None:
        self.grid[pos] = value

    @property
    def width(self) -> int:
        return self.grid.width

    @property
    def height(self) -> int:
        return self.grid.height

    @property
    def grid(self) -> Grid:
        return self._grid

    @abstractmethod
    def generate_maze(self,
                      fn: Callable[[Cell], None] | None = None) -> None:
        pass

    def _get_next_move(self, cell: Cell) -> Cell | None:
        available_walls = self.grid.available_direction(cell.coordinate)
        if not available_walls:
            return None
        next_wall = random.choice(available_walls)
        self.grid.open_wall(cell.coordinate, next_wall)
        next_cell = self.grid.get_neighbor(cell, next_wall)
        return next_cell

    def _get_random_cell(self) -> Cell:
        x = random.randint(0, self.width - 1)
        y = random.randint(0, self.height - 1)
        return self[y][x]

    def _clean(self) -> None:
        for y in range(self.height):
            for x in range(self.width):
                self[y][x].occupied = False
        self._start_cell.occupied = True
