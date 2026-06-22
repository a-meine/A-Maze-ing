import random
from config.base import ConfigBase
from abc import ABC, abstractmethod
from typing import Callable
from maze.cell import Cell
from maze.grid import Grid
from maze.direction import Direction


class MazeAlgorithm(ABC):
    event: Callable[[Cell], None] | None = None

    def __init__(self, config: ConfigBase) -> None:
        self._grid = Grid(config.width, config.height)
        (x, y) = config.entry
        self._start_cell = self.grid[y][x]
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
    def generate_maze(self) -> None:
        pass

    def get_neighbor(self, cell: Cell, direction: Direction) -> Cell:
        next_cell = self.grid.get_neighbor(cell, direction)
        assert next_cell is not None
        return next_cell

    def _get_random_direction(
                self, cell: Cell, include_occupied: bool = False
            ) -> Direction | None:
        available_walls = self.grid.available_direction(
            cell.coordinate, include_occupied
        )
        if not available_walls:
            return None
        return random.choice(available_walls)

    def _get_random_cell(
                self, include_occupied: bool = False
            ) -> Cell:
        x = random.randint(0, self.width - 1)
        y = random.randint(0, self.height - 1)
        cell = self[y][x]
        if include_occupied or not cell.occupied:
            return cell
        return self._get_random_cell(include_occupied)

    def _clean(self) -> None:
        for y in range(self.height):
            for x in range(self.width):
                self[y][x].occupied = False
        self._start_cell.occupied = True

    def _trigger_event(self, cell: Cell):
        if self.event is not None:
            self.event(cell)
