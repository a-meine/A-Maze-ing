"""maze.grid module."""
from collections.abc import Iterator
from config.base import ConfigBase
from maze.cell import Cell
from maze.coordinate import Coordinate
from maze.direction import Direction


class Grid:
    """Represents the maze grid of cells.

    Attributes:
        width (int): The width of the grid in cells.
        height (int): The height of the grid in cells.
        _grid (list[list[Cell]]): The 2D list of cells.
        start (Cell): The entry cell of the maze.
        end (Cell): The exit cell of the maze.
        total_cells (int): The total number of non-wall cells.
    """

    def __init__(self, config: ConfigBase) -> None:
        """Initialize the grid from a configuration object.

        Creates a grid of cells, sets up the entry and exit points,
        and applies the wall_42 pattern if dimensions allow.

        Args:
            config (ConfigBase): The configuration with grid dimensions,
                entry and exit coordinates.
        """
        self.width = config.width
        self.height = config.height
        self._grid: list[list[Cell]] = [
            [Cell(Coordinate(x, y)) for x in range(self.width)]
            for y in range(self.height)
        ]
        self._42_cells: list[Cell] = []
        self.__wall_42()
        (x, y) = config.entry
        self.start = self._grid[y][x]
        (x, y) = config.exit
        self.end = self._grid[y][x]
        self.total_cells = sum(
            1
            for row in self._grid
            for cell in row
            if not cell.is_wall
        )

    def __getitem__(self, pos: int) -> list[Cell]:
        """Get a row of cells by index.

        Args:
            pos (int): The row index.

        Returns:
            list[Cell]: The row of cells at the given index.
        """
        return self._grid[pos]

    def __setitem__(self, pos: int, value: list[Cell]) -> None:
        """Set a row of cells by index.

        Args:
            pos (int): The row index.
            value (list[Cell]): The row of cells to set.
        """
        self._grid[pos] = value

    def __set_wall(
            self,
            coordinate: Coordinate,
            wall: Direction,
            close: bool
    ) -> None:
        """Set the wall state for a cell and its neighbor.

        Updates the wall on the specified side of the cell and
        the opposite wall on the neighboring cell.

        Args:
            coordinate (Coordinate): The coordinate of the cell.
            wall (Direction): The direction of the wall to set.
            close (bool): True to close the wall, False to open it.
        """
        cell = self._grid[coordinate.y][coordinate.x]
        neighbor = self.get_neighbor(cell, wall)
        if neighbor is None:
            return
        if wall == Direction.NORTH:
            cell.walls.north = close
            neighbor.walls.south = close
        elif wall == Direction.EAST:
            cell.walls.east = close
            neighbor.walls.west = close
        elif wall == Direction.SOUTH:
            cell.walls.south = close
            neighbor.walls.north = close
        elif wall == Direction.WEST:
            cell.walls.west = close
            neighbor.walls.east = close

    def open_wall(self, coordinate: Coordinate, wall: Direction) -> None:
        """Open a wall on the specified side of a cell.

        Args:
            coordinate (Coordinate): The coordinate of the cell.
            wall (Direction): The direction of the wall to open.
        """
        self.__set_wall(coordinate, wall, False)

    def close_wall(self, coordinate: Coordinate, wall: Direction) -> None:
        """Close a wall on the specified side of a cell.

        Args:
            coordinate (Coordinate): The coordinate of the cell.
            wall (Direction): The direction of the wall to close.
        """
        self.__set_wall(coordinate, wall, True)

    def get_neighbor(self, cell: Cell, direction: Direction) -> Cell | None:
        """Get the neighboring cell in the specified direction.

        Returns None if the neighbor is out of bounds or is a wall.

        Args:
            cell (Cell): The source cell.
            direction (Direction): The direction to look.

        Returns:
            Cell | None: The neighboring cell, or None if not available.
        """
        result: Cell | None = None
        if direction == Direction.NORTH and cell.coordinate.y != 0:
            result = self._grid[cell.coordinate.y - 1][cell.coordinate.x]
        elif (direction == Direction.EAST and
              cell.coordinate.x != self.width - 1):
            result = self._grid[cell.coordinate.y][cell.coordinate.x + 1]
        elif (direction == Direction.SOUTH and
                cell.coordinate.y != self.height - 1):
            result = self._grid[cell.coordinate.y + 1][cell.coordinate.x]
        elif direction == Direction.WEST and cell.coordinate.x != 0:
            result = self._grid[cell.coordinate.y][cell.coordinate.x - 1]
        else:
            return None
        if result.is_wall:
            return None
        return result

    def get_direction(self, cell_1: Cell, cell_2: Cell) -> Direction | None:
        """Get the direction from cell_1 to cell_2.

        Args:
            cell_1 (Cell): The starting cell.
            cell_2 (Cell): The target cell.

        Returns:
            Direction | None: The direction from cell_1 to cell_2,
                or None if they are not adjacent.
        """
        if (
            cell_1.coordinate.y - 1 == cell_2.coordinate.y and
            cell_1.coordinate.x == cell_2.coordinate.x
        ):
            return Direction.NORTH
        elif (
            cell_1.coordinate.x + 1 == cell_2.coordinate.x and
            cell_1.coordinate.y == cell_2.coordinate.y
        ):
            return Direction.EAST
        elif (
            cell_1.coordinate.y + 1 == cell_2.coordinate.y and
            cell_1.coordinate.x == cell_2.coordinate.x
        ):
            return Direction.SOUTH
        elif (
            cell_1.coordinate.x - 1 == cell_2.coordinate.x and
            cell_1.coordinate.y == cell_2.coordinate.y
        ):
            return Direction.WEST
        else:
            return None

    def available_direction(
            self, source: Coordinate, include_occupied: bool = False
    ) -> list[Direction]:
        """Get the list of available directions from a source cell.

        Args:
            source (Coordinate): The source coordinate.
            include_occupied (bool): Whether to include occupied cells.
                Defaults to False.

        Returns:
            list[Direction]: The list of available directions.
        """
        usable: list[Direction] = []
        cell = self._grid[source.y][source.x]
        for direction in Direction:
            neighbor = self.get_neighbor(cell, direction)
            if (
                neighbor is not None and
                (include_occupied or not neighbor.occupied)
            ):
                usable.append(direction)
        return usable

    def show(self) -> None:
        """Display the grid visually in the terminal."""
        print("§" + "---§" * self.width)
        for row in self._grid:
            line = "|"
            for cell in row:
                if cell.is_wall:
                    line += " # "
                elif cell.occupied:
                    line += " . "
                else:
                    line += "   "
                if cell.walls.east:
                    line += "|"
                else:
                    line += " "
            print(line)
            line = "§"
            for cell in row:
                if cell.walls.south:
                    line += "---§"
                else:
                    line += "   §"
            print(line)

    def __mark_42_wall(self, x: int, y: int) -> None:
        """Mark the cell at (x, y) as part of the '42' wall pattern."""
        cell = self._grid[y][x]
        cell.is_wall = True
        self._42_cells.append(cell)

    def __wall_42(self) -> None:
        """Draw a '42' wall pattern in the center of the grid if large enough."""
        fourtytwo_wall_height = 6
        fourtytwo_wall_width = 8
        if (
            self.width >= fourtytwo_wall_width
            and self.height > fourtytwo_wall_height
        ):
            x = (self.width // 2) - ((fourtytwo_wall_width - 1) // 2)
            y = (self.height // 2) - ((fourtytwo_wall_height - 1) // 2)
            # letter 4
            self.__mark_42_wall(x, y)
            self.__mark_42_wall(x, y + 1)
            self.__mark_42_wall(x, y + 2)
            self.__mark_42_wall(x + 1, y + 2)
            self.__mark_42_wall(x + 2, y + 2)
            self.__mark_42_wall(x + 2, y + 3)
            self.__mark_42_wall(x + 2, y + 4)
            # letter 2
            self.__mark_42_wall(x + 4, y)
            self.__mark_42_wall(x + 5, y)
            self.__mark_42_wall(x + 6, y)
            self.__mark_42_wall(x + 6, y + 1)
            self.__mark_42_wall(x + 6, y + 2)
            self.__mark_42_wall(x + 5, y + 2)
            self.__mark_42_wall(x + 4, y + 2)
            self.__mark_42_wall(x + 4, y + 3)
            self.__mark_42_wall(x + 4, y + 4)
            self.__mark_42_wall(x + 5, y + 4)
            self.__mark_42_wall(x + 6, y + 4)
        else:
            print("Skipping 42 '42' pattern, size too small")
    def pattern_cells(self) -> list[Cell]:
        """Return the cells that make up the '42' wall pattern."""
        return self._42_cells

    def __iter__(self) -> Iterator[Cell]:
        """Iterate over all non-wall cells in the grid.

        Yields:
            Cell: The next non-wall cell.
        """
        for row in self._grid:
            for cell in row:
                if not cell.is_wall:
                    yield cell

    def clean(self) -> None:
        """Clear the occupied flag on all cells in the grid."""
        for cell in self:
            cell.occupied = False

    @classmethod
    def build(cls, width: int, height: int) -> "Grid":
        config = ConfigBase()
        config.width = width
        config.height = height
        config.entry = (0, 0)
        config.exit = (config.width - 1, config.height - 1)
        return cls(config)


if __name__ == "__main__":
    grid: Grid = Grid.build(4, 4)
    grid.open_wall(Coordinate(0, 0), Direction.SOUTH)
    grid.open_wall(Coordinate(0, 1), Direction.SOUTH)
    grid.open_wall(Coordinate(0, 2), Direction.SOUTH)
    grid.open_wall(Coordinate(0, 3), Direction.EAST)
    grid.open_wall(Coordinate(1, 3), Direction.NORTH)
    grid.open_wall(Coordinate(1, 2), Direction.NORTH)
    grid.open_wall(Coordinate(1, 1), Direction.NORTH)
    grid.open_wall(Coordinate(1, 0), Direction.EAST)
    grid.show()