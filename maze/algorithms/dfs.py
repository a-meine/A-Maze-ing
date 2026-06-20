import random
from typing import Callable
from maze.algorithms.algorithm import Algorithm
from maze.cell import Cell


class DFS(Algorithm):
    def __get_next_move(self, cell: Cell) -> Cell | None:
        available_walls = self.grid.available_cell(cell.coordinate)
        if not available_walls:
            return None
        next_wall = random.choice(available_walls)
        self.grid.open_wall(cell.coordinate, next_wall)
        next_cell = self.grid.get_neighbor(cell, next_wall)
        return next_cell

    def __get_random_cell(self) -> Cell:
        x = random.randint(0, self.width - 1)
        y = random.randint(0, self.height - 1)
        return self[y][x]

    def generate_maze(self,
                      fn: Callable[[Cell], None] | None = None) -> None:
        cursor = self.__get_random_cell()
        cursor.occupied = True
        occupied_cells = 1
        total_cells = self.width * self.height
        history = [cursor]
        while occupied_cells < total_cells:
            next_cell = self.__get_next_move(cursor)
            if next_cell is None:
                cursor = history.pop()
                continue
            next_cell.occupied = True
            occupied_cells += 1
            if self.grid.available_cell(cursor.coordinate):
                history.append(cursor)
            cursor = next_cell
            if fn is not None:
                fn(cursor)


if __name__ == "__main__":
    dfs = DFS(5, 5)
    dfs.generate_maze()
    dfs.grid.show()
