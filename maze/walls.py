"""maze.walls module."""


class Walls:
    """Represents the wall state of a cell on all four sides.

    Each side (north, east, south, west) has a boolean indicating
    whether a wall is present.

    Attributes:
        north (bool): Whether there is a wall on the north side.
        east (bool): Whether there is a wall on the east side.
        south (bool): Whether there is a wall on the south side.
        west (bool): Whether there is a wall on the west side.
    """

    def __init__(self) -> None:
        """Initialize all walls as present (True)."""
        self.north = True
        self.east = True
        self.west = True
        self.south = True