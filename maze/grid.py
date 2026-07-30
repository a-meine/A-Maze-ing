from collections.abc import Iterator

from config.base import ConfigBase
from maze.cell import Cell
from maze.coordinate import Coordinate
from maze.direction import Direction


class Grid:

    def __init__(self, config: ConfigBase):
        self.width = config.width
        self.height = config.height
        self._grid: list[list[Cell]] = [
            [Cell(Coordinate(x, y)) for x in range(self.width)]
            for y in range(self.height)
        ]
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
        return self._grid[pos]

    def __setitem__(self, pos: int, value: list[Cell]) -> None:
        self._grid[pos] = value

    def __set_wall(
            self,
            coordinate: Coordinate,
            wall: Direction,
            close: bool
            ) -> None:
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
        self.__set_wall(coordinate, wall, False)

    def close_wall(self, coordinate: Coordinate, wall: Direction) -> None:
        self.__set_wall(coordinate, wall, True)

    def get_neighbor(self, cell: Cell, direction: Direction) -> Cell | None:
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
            self, source: Coordinate, include_occupied: bool = False) -> list[Direction]:
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

    def __wall_42(self) -> None:
        fourtytwo_wall_height = 6
        fourtytwo_wall_width = 8
        if (
            self.width >= fourtytwo_wall_width
            and self.height > fourtytwo_wall_height
        ):
            x = (self.width // 2) - ((fourtytwo_wall_width - 1) // 2)
            y = (self.height // 2) - ((fourtytwo_wall_height - 1) // 2)
            # letter 4
            self._grid[y][x].is_wall = True
            self._grid[y + 1][x].is_wall = True
            self._grid[y + 2][x].is_wall = True
            self._grid[y + 2][x + 1].is_wall = True
            self._grid[y + 2][x + 2].is_wall = True
            self._grid[y + 3][x + 2].is_wall = True
            self._grid[y + 4][x + 2].is_wall = True
            # letter 2
            self._grid[y][x + 4].is_wall = True
            self._grid[y][x + 5].is_wall = True
            self._grid[y][x + 6].is_wall = True
            self._grid[y + 1][x + 6].is_wall = True
            self._grid[y + 2][x + 6].is_wall = True
            self._grid[y + 2][x + 5].is_wall = True
            self._grid[y + 2][x + 4].is_wall = True
            self._grid[y + 3][x + 4].is_wall = True
            self._grid[y + 4][x + 4].is_wall = True
            self._grid[y + 4][x + 5].is_wall = True
            self._grid[y + 4][x + 6].is_wall = True

    def __iter__(self) -> Iterator[Cell]:
        for row in self._grid:
            for cell in row:
                if not cell.is_wall:
                    yield cell

    def clean(self) -> None:
        for cell in self:
            cell.occupied = False

    @classmethod
    def Build(cls, width: int, height: int) -> Grid:
        config = ConfigBase()
        config.width = width
        config.height = height
        config.entry = (0, 0)
        config.exit = (config.width - 1, config.height - 1)
        return cls(config)


if __name__ == "__main__":
    grid = Grid.Build(4, 4)
    grid.open_wall(Coordinate(0, 0), Direction.SOUTH)
    grid.open_wall(Coordinate(0, 1), Direction.SOUTH)
    grid.open_wall(Coordinate(0, 2), Direction.SOUTH)
    grid.open_wall(Coordinate(0, 3), Direction.EAST)
    grid.open_wall(Coordinate(1, 3), Direction.NORTH)
    grid.open_wall(Coordinate(1, 2), Direction.NORTH)
    grid.open_wall(Coordinate(1, 1), Direction.NORTH)
    grid.open_wall(Coordinate(1, 0), Direction.EAST)
    grid.show()
