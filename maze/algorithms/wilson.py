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
        prev: None | Cell = None
        for cell in self.find_path(is_first_run=True):
            if prev is not None:
                direction = self.get_direction(prev, cell)
                self.grid.open_wall(cell.coordinate, direction)
            self.__process_cell(cell)
            prev = cell
        while self.__occupied_cells < self._total_cells:
            for cell in self.find_path():
                if prev is not None:
                    direction = self.get_direction(prev, cell)
                    self.grid.open_wall(cell.coordinate, direction)
                self.__process_cell(cell)
                prev = cell

    def find_path(self, is_first_run: bool = False):
        start = self._get_random_cell()
        start.occupied = True
        destination = self._get_random_cell()
        start.occupied = False
        path = [start]
        cell = start
        while (not is_first_run and cell.occupied) or destination == cell:
            direction = self._get_random_direction(cell, True)
            if direction is None:
                path = [start]
                cell = start
                continue
            cell = self.get_neighbor(cell, direction)
            if (not is_first_run and cell.occupied) or destination == cell:
                break
            if cell in path:
                while cell != path.pop():
                    continue
                continue
            path.append(cell)
        return path


if __name__ == "__main__":
    config = ConfigBase()
    config.width = 5
    config.height = 5
    config.entry = (0, 0)
    config.exit = (config.width - 1, config.height - 1)
    wilson = Wilson(config)
    wilson.generate_maze()
    wilson.grid.show()
