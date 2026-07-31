"""maze.encoding module.

Provides encoding and output functions for the maze.
"""
from maze.cell import Cell
from maze.grid import Grid
from config.parser import Config


def cell_to_hex(cell: Cell) -> str:
    """Convert a cell's wall configuration to a hex character.

    Maps the four wall states (north, east, south, west) to a
    bitmask and returns the corresponding hex digit.

    Args:
        cell (Cell): The cell to encode.

    Returns:
        str: A single uppercase hex character representing the wall state.
    """
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
    """Convert a path of cells to a directional string.

    Iterates through consecutive cells in the path and determines
    the direction of movement between them.

    Args:
        path (list[Cell]): The list of cells forming the path.
        grid (Grid): The grid containing the cells.

    Returns:
        str: A string of direction characters (N, E, S, W).
    """
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
    """Write the maze output to the configured output file.

    Encodes the maze grid as hex characters, then writes the entry
    point, exit point, and solution path directions to the file.

    Args:
        grid (Grid): The maze grid to encode.
        config (Config): The configuration containing the output file path.
        solution_path (list[Cell]): The solution path to encode as directions.
    """
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