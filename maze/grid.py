from maze.cell import Cell
from maze.coordinate import Coordinate
from maze.direction import Direction


class Grid:
    width: int
    height: int
    _grid: list[list[Cell]] = []

    def __getitem__(self, pos: int) -> list[Cell]:
        return self._grid[pos]

    def __setitem__(self, pos: int, value: list[Cell]):
        self._grid[pos] = value

    def __init__(self, width, height):
        self.width = width
        self.height = height
        for y in range(height):
            new_cells = []
            for x in range(width):
                new_cell = Cell(Coordinate(x, y))
                new_cells.append(new_cell)
            self._grid.append(new_cells)

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

    def get_neighbor(self, cell: Cell, wall: Direction) -> Cell | None:
        if wall == Direction.NORTH and cell.coordinate.y != 0:
            return self._grid[cell.coordinate.y - 1][cell.coordinate.x]
        elif wall == Direction.EAST and cell.coordinate.x != self.width - 1:
            return self._grid[cell.coordinate.y][cell.coordinate.x + 1]
        elif wall == Direction.SOUTH and cell.coordinate.y != self.height - 1:
            return self._grid[cell.coordinate.y + 1][cell.coordinate.x]
        elif wall == Direction.WEST and cell.coordinate.x != 0:
            return self._grid[cell.coordinate.y][cell.coordinate.x - 1]
        else:
            return None

    def available_cell(self, source: Coordinate):
        usable: list[Direction] = []
        cell = self._grid[source.y][source.x]
        for direction in Direction:
            neighbor = self.get_neighbor(cell, direction)
            if neighbor is not None and not neighbor.occupied:
                usable.append(direction)
        return usable

    def show(self):
        print("§" + "---§" * self.width)
        for y in range(self.height):
            line = "|"
            for x in range(self.width):
                if self[y][x].occupied:
                    line += " . "
                else:
                    line += "   "
                if self._grid[y][x].walls.east:
                    line += "|"
                else:
                    line += " "
            print(line)
            line = "§"
            for x in range(self.width):
                if self._grid[y][x].walls.south:
                    line += "---§"
                else:
                    line += "   §"
            print(line)


if __name__ == "__main__":
    grid = Grid(4, 4)
    grid.open_wall(Coordinate(0, 0), Direction.SOUTH)
    grid.open_wall(Coordinate(0, 1), Direction.SOUTH)
    grid.open_wall(Coordinate(0, 2), Direction.SOUTH)
    grid.open_wall(Coordinate(0, 3), Direction.EAST)
    grid.open_wall(Coordinate(1, 3), Direction.NORTH)
    grid.open_wall(Coordinate(1, 2), Direction.NORTH)
    grid.open_wall(Coordinate(1, 1), Direction.NORTH)
    grid.open_wall(Coordinate(1, 0), Direction.EAST)
    grid.show()
