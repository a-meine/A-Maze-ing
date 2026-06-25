import random

from maze.cell import Cell
from maze.grid import Grid


class DFS:
    @property
    def width(self):
        return self._grid.width

    @property
    def height(self):
        return self._grid.height

    def __getitem__(self, pos: int) -> list[Cell]:
        return self._grid[pos]

    def __setitem__(self, pos: int, value: list[Cell]):
        self._grid[pos] = value

    _grid: Grid

    def __init__(self, width: int, height: int):
        self._grid = Grid(width, height)

    def get_next_move(self, cell: Cell) -> Cell | None:
        available_walls = self._grid.available_cell(cell.coordinate)
        if not available_walls:
            return None
        next_wall = random.choice(available_walls)
        self._grid.open_wall(cell.coordinate, next_wall)
        next_cell = self._grid.get_neighbor(cell, next_wall)
        return next_cell

    def is_full(self):
        for y in range(self.height):
            for x in range(self.width):
                if not self._grid[y][x].occupied:
                    return False
        return True

    def generate_maze(self):
        history: list[Cell] = []
        # random.seed(42)
        x = random.randint(0, self.width - 1)
        y = random.randint(0, self.height - 1)
        start: Cell = self._grid[y][x]
        yield start
        start.occupied = True
        history.append(start)
        while True:
            while True:
                cell = self.get_next_move(start)
                if cell is None:
                    break
                cell.occupied = True
                start = cell
                history.append(start)
                yield cell
            if self.is_full():
                break
            start = history.pop()
        # grid.show()
