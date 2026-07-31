"""maze.cell module."""
from maze.walls import Walls
from maze.coordinate import Coordinate


class Cell:
    """Represents a single cell in the maze grid.

    Each cell has a coordinate, a flag indicating if it is a wall,
    a flag indicating if it is occupied, and walls on each side.

    Attributes:
        coordinate (Coordinate): The position of this cell in the grid.
        is_wall (bool): Whether this cell is a wall.
        occupied (bool): Whether this cell is currently occupied.
        walls (Walls): The wall states for each direction.
    """

    def __init__(self, coordinate: Coordinate) -> None:
        """Initialize a Cell with the given coordinate.

        Args:
            coordinate (Coordinate): The position of this cell in the grid.
        """
        self.coordinate = coordinate
        self.is_wall = False
        self.occupied = False
        self.walls = Walls()

    def __str__(self) -> str:
        """Return the string representation of the cell's coordinate.

        Returns:
            str: String representation of the cell's coordinate.
        """
        return str(self.coordinate)
