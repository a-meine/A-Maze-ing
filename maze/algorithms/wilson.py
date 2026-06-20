import random
from typing import Callable
from maze.coordinate import Coordinate
from maze.algorithms.maze_algorithm import MazeAlgorithm
from maze.direction import Direction
from maze.cell import Cell
from config.base import ConfigBase


class Wilson(MazeAlgorithm):
    def __init__(self, config: ConfigBase) -> None:
        super().__init__(config)
        self.__occupied_cells = 1

    def __process_cell(self, cell: Cell):
        cell.occupied = True
        self.__occupied_cells += 1

#   TODO

    def _get_next_move(self, cell: Cell) -> Cell | None:
        available_walls = self.grid.available_direction(cell.coordinate)
        if not available_walls:
            return None
        next_wall = random.choice(available_walls)
        self.grid.open_wall(cell.coordinate, next_wall)
        next_cell = self.grid.get_neighbor(cell, next_wall)
        return next_cell
#   TODO

    def available_direction(self, source: Coordinate):
        usable: list[Direction] = []
        cell = self._grid[source.y][source.x]
        for direction in Direction:
            neighbor = self.get_neighbor(cell, direction)
            if neighbor is not None and not neighbor.occupied:
                usable.append(direction)
        return usable

    def generate_maze(self,
                      fn: Callable[[Cell], None] | None = None) -> None:
        cell = self._start_cell
        self.__process_cell(cell)
        while cell != self._end_cell:
            next_cell = self._get_next_move(cell)
            if next_cell is None:
                self._clean()
                self.__occupied_cells = 1
                cell = self._start_cell
                continue
            self.__process_cell(cell)
            if fn is not None:
                fn(next_cell)
            cell = next_cell
        while self.__occupied_cells < self._total_cells:
            cell = self._get_random_cell()
            if cell.occupied:
                continue
            self.__process_cell(cell)



if __name__ == "__main__":
    config = ConfigBase()
    config.width = 5
    config.height = 5
    wilson = Wilson(config)
    wilson.generate_maze()
    wilson.grid.show()
