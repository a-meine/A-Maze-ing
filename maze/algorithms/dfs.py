from typing import Callable
from maze.algorithms.maze_algorithm import MazeAlgorithm
from config.base import ConfigBase
from maze.cell import Cell


class DFS(MazeAlgorithm):
    def __init__(self, config: ConfigBase) -> None:
        super().__init__(config)
        self.__occupied_cells = 1

    def __process_cell(self, cell: Cell):
        cell.occupied = True
        self.__occupied_cells += 1
        self._trigger_event(cell)

    def generate_maze(self,
                      fn: Callable[[Cell], None] | None = None) -> None:
        cell = self._start_cell
        history = [cell]
        while self.__occupied_cells < self._total_cells:
            direction = self._get_random_direction(cell)
            if direction is None:
                cell = history.pop()
                continue
            self.grid.open_wall(cell.coordinate, direction)
            cell = self.get_neighbor(cell, direction)
            self.__process_cell(cell)
            if self.grid.available_direction(cell.coordinate):
                history.append(cell)
        self._clean()


if __name__ == "__main__":
    config = ConfigBase()
    config.width = 5
    config.height = 5
    config.entry = (0, 0)
    config.exit = (config.width - 1, config.height - 1)
    dfs = DFS(config)
    dfs.generate_maze()
    dfs.grid.show()
