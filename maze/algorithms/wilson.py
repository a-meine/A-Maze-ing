from typing import Callable
from maze.algorithms.maze_algorithm import MazeAlgorithm
from maze.cell import Cell
from config.base import ConfigBase


class Wilson(MazeAlgorithm):

    def generate_maze(self,
                      fn: Callable[[Cell], None] | None = None) -> None:
        cursor = self._get_random_cell()
        cursor.occupied = True
        occupied_cells = 1
        total_cells = self.width * self.height
        while occupied_cells < total_cells:
            next_cell = self._get_next_move(cursor)
            if next_cell is None:
                while True:
                    next_cell = self._get_random_cell()
                    if self.grid.available_direction(next_cell.coordinate):
                        break
            next_cell.occupied = True
            occupied_cells += 1
            cursor = next_cell
            if fn is not None:
                fn(cursor)


if __name__ == "__main__":
    config = ConfigBase()
    config.width = 5
    config.height = 5
    wilson = Wilson(config)
    wilson.generate_maze()
    wilson.grid.show()
