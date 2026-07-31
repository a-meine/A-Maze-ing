"""maze.direction module."""
from enum import Enum


class Direction(Enum):
    """Enum representing the four cardinal directions.

    Attributes:
        NORTH: The north direction.
        EAST: The east direction.
        WEST: The west direction.
        SOUTH: The south direction.
    """

    NORTH = "North"
    EAST = "East"
    WEST = "West"
    SOUTH = "South"