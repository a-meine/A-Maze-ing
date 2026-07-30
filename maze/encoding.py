from maze.cell import Cell
from maze.grid import Grid
from config.parser import Config


def cell_to_hex(cell: Cell) -> str:
    bitmask = 0
    if cell.walls.north:
        bitmask |= 1 << 0
    if cell.walls.east:
        bitmask |= 1 << 1
    if cell.walls.south:
        bitmask |= 1 << 2
    if cell.walls.west:
        bitmask |= 1 << 3
    return format(bitmask, "X")


def path_to_direction_string(path: list[Cell], grid: Grid) -> str:
    if not path or len(path) < 2:
        return ""
    result: list[str] = []
    for i in range(len(path) - 1):
        dx = path[i + 1].coordinate.x - path[i].coordinate.x
        dy = path[i + 1].coordinate.y - path[i].coordinate.y
        if dx == 1:
            result.append("E")
        elif dx == -1:
            result.append("W")
        elif dy == 1:
            result.append("S")
        elif dy == -1:
            result.append("N")
    return "".join(result)


def write_output(
        grid: Grid, config: Config, solution_path: list[Cell]) -> None:
    path_str = path_to_direction_string(solution_path, grid)
    try:
        with open(config.output_file, "w") as f:
            for y in range(grid.height):
                for x in range(grid.width):
                    f.write(cell_to_hex(grid[y][x]))
                f.write("\n")
            f.write("\n")
            f.write(f"{config.entry[0]},{config.entry[1]}\n")
            f.write(f"{config.exit[0]},{config.exit[1]}\n")
            f.write(path_str + "\n")
    except OSError as e:
        print(e)
