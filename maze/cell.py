from maze.walls import Walls
from maze.coordinate import Coordinate


class Cell:

    def __init__(self, coordinate: Coordinate):
        self.coordinate = coordinate
        self.occupied = False
        self.walls = Walls()

    def __repr__(self) -> str:
        return str(self.coordinate)
