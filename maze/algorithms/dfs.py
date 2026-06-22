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

    def generate_maze(self,
                      fn: Callable[[Cell], None] | None = None) -> None:
        cell = self._start_cell
        history = [cell]
        while self.__occupied_cells < self._total_cells:
            new_cell = self._get_next_move(cell)
            if new_cell is None:
                cell = history.pop()
                continue
            cell = new_cell
            self.__process_cell(cell)
            if self.grid.available_direction(cell.coordinate):
                history.append(cell)
            if fn is not None:
                fn(cell)
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
