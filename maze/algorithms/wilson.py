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
        # Part 1
        start = self._get_random_cell()
        start.occupied = True
        destination = self._get_random_cell()
        path = [start]
        cell = start
        while cell != destination:
            direction = self._get_random_direction(cell)
            if direction is None:
                cell = path.pop()
                while cell == start:
                    cell.occupied = False
                    self.__occupied_cells -= 1
                    self._trigger_event(cell)
                    cell = path.pop()
                continue
            cell = self.get_neighbor(cell, direction)
            self.__process_cell(cell)
            path.append(cell)
        while self.__occupied_cells < self._total_cells:
            for cell in self.find_path():
                self.__process_cell(cell)

    # Part 2
    def find_path(self):
        start = self._get_random_cell()
        path = [start]
        cell = start
        while cell.occupied:
            direction = self._get_random_direction(cell, True)
            if direction is None:
                path = [start]
                cell = start
                continue
            cell = self.get_neighbor(cell, direction)
            if cell.occupied:
                break
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
