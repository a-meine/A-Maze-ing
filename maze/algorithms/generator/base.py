import random
from abc import ABC, abstractmethod
from typing import Callable
from maze.cell import Cell
from maze.grid import Grid
from maze.direction import Direction


class GeneratorBase(ABC):
    event: Callable[[Cell, bool], None] | None = None

    def __init__(self, grid: Grid) -> None:
        self._grid = grid

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

    def get_direction(self, cell_1: Cell, cell_2: Cell) -> Direction:
        direction = self.grid.get_direction(cell_1, cell_2)
        assert direction is not None
        return direction

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
        cell = random.choice([cell for cell in self.grid if not cell.occupied or include_occupied])
        return cell

    def _trigger_event(self, cell: Cell, sync: bool = True) -> None:
        if self.event is not None:
            try:
                self.event(cell, sync)
            except Exception as ex:
                print(ex)
