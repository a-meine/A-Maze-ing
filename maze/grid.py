"""
This module defines the grid component: cell calss etc..
"""


class Walls:
    """
    This intialses each cell with a closed wall on each
    side, the maze_gen will open the paths accordingly
    """
    east: bool = True
    west: bool = True
    north: bool = True
    south: bool = True


class Cell:
    """
    This class defines the each cell in a grid ...
    """
    def __init__(self, coordinate):
        """
        initilaises the neccasary attributes of a Cell object
        """
        self.coordinate: tuple[int, int] = coordinate
        # Occupied: bool
        # self.Walls: Walls

    def __repr__(self) -> str:
        """
        This funtion show the created cells in a readable format
        instaed of <__main__.Cell object at 0x7c013c7627a0>
        """
        return str(self.coordinate)


# def initialize_maze(self) -> list[list[Cell]]:
class Grid:
    """
    This class stores the grid and other attributes
    """
    def __init__(self, width, height):
        """
        To avoid calling a seperate init_maze() we are auto-intialise
        the gird for each maze object
        """
        self.cells: list[list[Cell]] = []
        grid: list[list[Cell]] = []
        for y in range(height):
            row: list[Cell] = []
            for x in range(width):
                new_cell = Cell((x, y))
                row.append(new_cell)
            grid.append(row)
        self.cells = grid


print(Grid(6, 7).cells)
