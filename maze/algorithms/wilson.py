from typing import Callable
from maze.algorithms.maze_algorithm import MazeAlgorithm
from maze.cell import Cell
from config.base import ConfigBase


class Wilson(MazeAlgorithm):
    def __init__(self, config: ConfigBase) -> None:
        super().__init__(config)
        self.__occupied_cells = 1

    def __process_cell(self, cell: Cell):
        cell.occupied = True
        self.__occupied_cells += 1

    def generate_maze(self,
                      fn: Callable[[Cell], None] | None = None) -> None:
        cell = self._start_cell
        while cell != self._end_cell:
            next_cell = self._get_next_move(cell)
            if next_cell is None:
                self._clean()
                self.__occupied_cells = 1
                cell = self._start_cell
                continue
            self.__process_cell(next_cell)
            if fn is not None:
                fn(next_cell)
            cell = next_cell
        self.grid.show()
        while self.__occupied_cells < self._total_cells:
            cell = self._get_random_cell()
            if cell.occupied:
                continue
            self.__process_cell(cell)
            while self.__occupied_cells < self._total_cells:
                next_cell = self._get_next_move(cell, include_occupied=True)
                if next_cell is None or next_cell.occupied:
                    break
                self.__process_cell(next_cell)
                cell = next_cell
        self._clean()


if __name__ == "__main__":
    config = ConfigBase()
    config.width = 5
    config.height = 5
    config.entry = (0, 0)
    config.exit = (config.width - 1, config.height - 1)
    wilson = Wilson(config)
    wilson.generate_maze()
    wilson.grid.show()
