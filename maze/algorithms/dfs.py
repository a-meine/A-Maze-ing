import random

from maze.cell import Cell
from maze.grid import Grid


def generate_maze(width: int, height: int):
    grid = Grid(width, height)
    return grid


def get_next_move(cell: Cell) -> Cell | None:
    available_walls = grid.available_cell(cell.coordinate)
    if not available_walls:
        return None
    next_wall = random.choice(available_walls)
    grid.open_wall(cell.coordinate, next_wall)
    next_cell = grid.get_neighbor(cell, next_wall)
    return next_cell


def is_full(grid: Grid):
    for y in range(grid.height):
        for x in range(grid.width):
            if not grid[y][x].occupied:
                return False
    return True


if __name__ == "__main__":
    width = 10
    height = 10
    grid = Grid(width, height)
    history: list[Cell] = []
    x = random.randint(0, width - 1)
    y = random.randint(0, height - 1)
    start: Cell = grid[y][x]
    start.occupied = True
    history.append(start)
    while True:
        while True:
            cell = get_next_move(start)
            if cell is None:
                break
            cell.occupied = True
            start = cell
            history.append(start)
        if is_full(grid):
            break
        start = history.pop()
    grid.show()
