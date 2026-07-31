"""maze.algorithms.generator.base module."""
import random
from abc import ABC, abstractmethod
from typing import Callable
from maze.cell import Cell
from maze.grid import Grid
from maze.direction import Direction


class GeneratorBase(ABC):
    """Abstract base class for maze generator algorithms.

    Provides common functionality for maze generation including
    grid access, neighbor lookup, and event triggering.

    Attributes:
        event (Callable[[Cell, bool], None] | None): Callback invoked
            when a cell is processed.
    """

    event: Callable[[Cell, bool], None] | None = None

    def __init__(self, grid: Grid) -> None:
        """Initialize the generator with a grid.

        Args:
            grid (Grid): The grid to generate the maze on.
        """
        self._grid = grid

    def __getitem__(self, pos: int) -> list[Cell]:
        """Get a row of cells by index.

        Args:
            pos (int): The row index.

        Returns:
            list[Cell]: The row of cells at the given index.
        """
        return self.grid[pos]

    def __setitem__(self, pos: int, value: list[Cell]) -> None:
        """Set a row of cells by index.

        Args:
            pos (int): The row index.
            value (list[Cell]): The row of cells to set.
        """
        self.grid[pos] = value

    @property
    def width(self) -> int:
        """Get the width of the grid.

        Returns:
            int: The grid width.
        """
        return self.grid.width

    @property
    def height(self) -> int:
        """Get the height of the grid.

        Returns:
            int: The grid height.
        """
        return self.grid.height

    @property
    def grid(self) -> Grid:
        """Get the grid instance.

        Returns:
            Grid: The grid being used for maze generation.
        """
        return self._grid

    @abstractmethod
    def generate_maze(self) -> None:
        """Generate a maze on the grid.

        This abstract method must be implemented by subclasses.
        """

    def get_neighbor(self, cell: Cell, direction: Direction) -> Cell:
        """Get the neighboring cell in the specified direction.

        Args:
            cell (Cell): The source cell.
            direction (Direction): The direction to look.

        Returns:
            Cell: The neighboring cell.
        """
        next_cell = self.grid.get_neighbor(cell, direction)
        assert next_cell is not None
        return next_cell

    def get_direction(self, cell_1: Cell, cell_2: Cell) -> Direction:
        """Get the direction from cell_1 to cell_2.

        Args:
            cell_1 (Cell): The starting cell.
            cell_2 (Cell): The target cell.

        Returns:
            Direction: The direction from cell_1 to cell_2.
        """
        direction = self.grid.get_direction(cell_1, cell_2)
        assert direction is not None
        return direction

    def _get_random_direction(
            self, cell: Cell, include_occupied: bool = False
    ) -> Direction | None:
        """Get a random available direction from a cell.

        Args:
            cell (Cell): The source cell.
            include_occupied (bool): Whether to include occupied cells.
                Defaults to False.

        Returns:
            Direction | None: A random available direction, or None
                if no directions are available.
        """
        available_walls = self.grid.available_direction(
            cell.coordinate, include_occupied
        )
        if not available_walls:
            return None
        return random.choice(available_walls)

    def _get_random_cell(
            self, include_occupied: bool = False
    ) -> Cell:
        """Get a random non-wall cell from the grid.

        Args:
            include_occupied (bool): Whether to include occupied cells.
                Defaults to False.

        Returns:
            Cell: A random non-wall cell.
        """
        x = random.randint(0, self.width - 1)
        y = random.randint(0, self.height - 1)
        cell = self[y][x]
        if (include_occupied or not cell.occupied) and not cell.is_wall:
            return cell
        return self._get_random_cell(include_occupied)

    def _trigger_event(self, cell: Cell, sync: bool = True) -> None:
        """Trigger the event callback for a cell.

        Args:
            cell (Cell): The cell that was processed.
            sync (bool): Whether to synchronize rendering.
                Defaults to True.
        """
        if self.event is not None:
            try:
                self.event(cell, sync)
            except Exception as ex:
                print(ex)