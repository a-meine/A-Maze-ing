"""maze.coordinate module."""


class Coordinate:
    """Represents a 2D coordinate in the maze grid.

    Attributes:
        x (int): The x coordinate.
        y (int): The y coordinate.
    """

    def __init__(self, x: int, y: int) -> None:
        """Initialize a Coordinate with x and y values.

        Args:
            x (int): The x coordinate.
            y (int): The y coordinate.
        """
        self.x = x
        self.y = y

    def __str__(self) -> str:
        """Return the string representation of the coordinate.

        Returns:
            str: String representation in the format (x, y).
        """
        return f"({self.x}, {self.y})"