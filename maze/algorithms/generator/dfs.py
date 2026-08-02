"""maze.algorithms.generator.dfs module."""
from maze.algorithms.generator.base import GeneratorBase
from maze.cell import Cell
from maze.grid import Grid


class DFS(GeneratorBase):
    """Depth-First Search maze generation algorithm.

    Uses a stack-based DFS traversal to carve paths through
    the maze grid.
    """

    def __init__(self, grid: Grid) -> None:
        """Initialize the DFS generator with a grid.

        Args:
            grid (Grid): The grid to generate the maze on.
        """
        super().__init__(grid)
        self.__occupied_cells = 0

    def __process_cell(self, cell: Cell) -> None:
        """Process a single cell during maze generation.

        If the cell is already occupied, triggers an event and returns.
        Otherwise marks the cell as occupied and increments the counter.

        Args:
            cell (Cell): The cell to process.
        """
        if cell.occupied:
            self._trigger_event(cell)
            return
        cell.occupied = True
        self.__occupied_cells += 1
        self._trigger_event(cell)

    def generate_maze(self) -> None:
        """Generate a maze using the Depth-First Search algorithm.

        Starts from the grid's entry point and carves paths by
        visiting unvisited neighbors, backtracking when no moves
        are available.
        """
        cell = self.grid.start
        history = [cell]
        while self.__occupied_cells < self.grid.total_cells:
            self._trigger_event(cell)
            direction = self._get_random_direction(cell)
            if direction is None:
                cell = history.pop()
                continue
            self.grid.open_wall(cell.coordinate, direction)
            neighbor = self.get_neighbor(cell, direction)
            self.__process_cell(neighbor)
            if self.grid.available_direction(cell.coordinate):
                history.append(cell)
            cell = neighbor
        self.__process_cell(cell)
        self.grid.clean()


if __name__ == "__main__":
    dfs = DFS(Grid.build(50, 50))
    dfs.generate_maze()
    dfs.grid.show()