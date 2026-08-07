"""maze.maze_generator module.

Public facade for generating and solving mazes. It wraps the grid builders,
the generators and the BFS solver behind one importable class so the maze
logic can be reused from a future project.
"""
import random
from typing import Any

from maze.config import ConfigBase
from maze.grid import Grid
from maze.algorithms.generator.dfs import DFS
from maze.algorithms.generator.randomised_prim import Prim
from maze.algorithms.generator.wilson import Wilson
from maze.algorithms.solution.bfs import BFS
from maze.encoding import cell_to_hex, path_to_direction_string

VALID_ALGORITHMS = ("dfs", "prim", "wilson")


class MazeGenerator:
    """Single interface to generate, solve and export a maze.

    Args:
        width (int): The width of the maze in cells.
        height (int): The height of the maze in cells.
        entry (tuple[int, int]): The entry cell coordinates.
        exit (tuple[int, int]): The exit cell coordinates.
        perfect (bool): Whether the maze must be perfect (always True now).
        seed (int | None): Optional seed for reproducible generation.
        algorithm (str): One of 'dfs', 'prim' or 'wilson'.

    Raises:
        ValueError: If any dimension, coordinate or algorithm is invalid.
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int] = (0, 0),
        exit: tuple[int, int] | None = None,
        perfect: bool = True,
        seed: int | None = None,
        algorithm: str = "dfs",
    ) -> None:
        """Initialize the generator with validated parameters."""
        exit = (width - 1, height - 1) if exit is None else exit
        self._validate(width, height, entry, exit, algorithm)
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.perfect = perfect
        self.seed = seed
        self.algorithm = algorithm
        self._grid: Grid | None = None
        self._solution: list[tuple[int, int]] = []
        self._directions: str = ""

    @staticmethod
    def _validate(
        width: int,
        height: int,
        entry: tuple[int, int],
        exit: tuple[int, int],
        algorithm: str,
    ) -> None:
        """Validate the generation parameters, raising ValueError on failure.

        Args:
            width (int): The maze width.
            height (int): The maze height.
            entry (tuple[int, int]): The entry cell.
            exit (tuple[int, int]): The exit cell.
            algorithm (str): The algorithm name.

        Raises:
            ValueError: If any parameter is invalid.
        """
        if width <= 0 or height <= 0:
            raise ValueError("width and height must be positive")
        if algorithm not in VALID_ALGORITHMS:
            raise ValueError(f"algorithm must be one of {VALID_ALGORITHMS}")
        if (
            None in entry or None in exit
            or not all(isinstance(v, int) for v in entry + exit)
        ):
            raise ValueError("entry and exit must be integer coordinates")
        if entry[0] < 0 or entry[1] < 0 or exit[0] < 0 or exit[1] < 0:
            raise ValueError("entry and exit must be non-negative")
        if entry[0] >= width or entry[1] >= height:
            raise ValueError("entry is outside the maze bounds")
        if exit[0] >= width or exit[1] >= height:
            raise ValueError("exit is outside the maze bounds")
        if entry == exit:
            raise ValueError("entry and exit must be different cells")

    def _config(self) -> ConfigBase:
        """Return a ConfigBase built from the given parameters."""
        cfg = ConfigBase()
        cfg.width = self.width
        cfg.height = self.height
        cfg.entry = self.entry
        cfg.exit = self.exit
        cfg.perfect = self.perfect
        cfg.seed = self.seed
        return cfg

    @property
    def maze(self) -> Grid:
        """Return the generated grid, generating it on first access."""
        if self._grid is None:
            self.generate()
        assert self._grid is not None
        return self._grid

    def generate(self) -> "MazeGenerator":
        """Generate the maze, solve it, and return self for chaining.

        Returns:
            MazeGenerator: self, with the maze and solution populated.

        Raises:
            ValueError: If entry or exit intersect the '42' wall pattern.
        """
        if self.seed is not None:
            random.seed(self.seed)
        cfg = self._config()
        grid = Grid(cfg)
        if grid.start.is_wall or grid.end.is_wall:
            raise ValueError("entry or exit cannot be inside the '42' pattern")
        algorithm = self._build_algorithm(grid)
        algorithm.generate_maze()
        algorithm.grid.clean()
        solution = BFS(grid).solve()
        self._grid = grid
        self._solution = [(cell.coordinate.x, cell.coordinate.y)
                          for cell in solution]
        if len(solution) < 2:
            self._directions = ""
        else:
            self._directions = path_to_direction_string(solution, grid)
        return self

    def _build_algorithm(self, grid: Grid) -> Any:
        """Build the generator instance for the selected algorithm.

        Args:
            grid (Grid): The grid to generate on.

        Returns:
            Any: The concrete generator instance.
        """
        if self.algorithm == "prim":
            return Prim(grid)
        if self.algorithm == "wilson":
            return Wilson(grid)
        return DFS(grid)

    @property
    def solution(self) -> list[tuple[int, int]]:
        """Return the shortest path from entry to exit as coordinates."""
        if not self._solution:
            self.generate()
        return self._solution

    @property
    def directions(self) -> str:
        """Return the shortest path as an 'NESW' direction string."""
        if not self._solution:
            self.generate()
        return self._directions

    def hex_rows(self) -> list[str]:
        """Return the maze encoded as one hex string per row of cells.

        Returns:
            list[str]: The WIDTH-char hex encoding for each of the height rows.
        """
        grid = self.maze
        return [
            "".join(cell_to_hex(cell) for cell in grid[y])
            for y in range(grid.height)
        ]