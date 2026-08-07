"""maze.config module.

Defines a lightweight configuration base used by the maze package so that the
package does not depend on the application's ``config`` module and stays
reusable on its own.
"""


class ConfigBase:
    """Minimal maze configuration carried into the grid.

    Attributes:
        width (int): The width of the grid in cells.
        height (int): The height of the grid in cells.
        entry (tuple[int, int]): The entry cell coordinates.
        exit (tuple[int, int]): The exit cell coordinates.
        perfect (bool): Whether the maze must be perfect.
        seed (int | None): Optional reproducibility seed.
    """

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    perfect: bool
    seed: int | None