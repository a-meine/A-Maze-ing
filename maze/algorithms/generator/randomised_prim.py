"""maze.algorithms.generator.randomised_prim module."""
from maze.algorithms.generator.base import GeneratorBase
from maze.cell import Cell
from maze.grid import Grid
from maze.direction import Direction
import random


class Prim(GeneratorBase):
    """Randomised Prim's maze generation algorithm.

    Uses a randomised version of Prim's algorithm to generate
    a perfect maze by growing from a starting cell.
    """

    def __init__(self, grid: Grid) -> None:
        """Initialize the Prim generator with a grid.

        Args:
            grid (Grid): The grid to generate the maze on.
        """
        super().__init__(grid)

    def neighbors(self, cell: Cell) -> list[Cell]:
        """Get all valid neighboring cells of a given cell.

        Args:
            cell (Cell): The source cell.

        Returns:
            list[Cell]: A list of neighboring cells that are
                within grid bounds and not walls.
        """
        all_neighbors = [
            self.grid.get_neighbor(cell, Direction.EAST),
            self.grid.get_neighbor(cell, Direction.WEST),
            self.grid.get_neighbor(cell, Direction.SOUTH),
            self.grid.get_neighbor(cell, Direction.NORTH),
        ]
        return [n for n in all_neighbors if n is not None]

    def generate_maze(self) -> None:
        """Generate a maze using Randomised Prim's algorithm.

        Starts from a random cell, maintains a frontier of
        candidate walls, and carves passages by randomly
        selecting walls that connect to unvisited cells.
        """
        start = self._get_random_cell()
        visited: set[Cell] = {start}
        self._trigger_event(start)
        queue: list[Cell] = self.neighbors(start)
        self.frontier: set[Cell] = set(queue)

        while queue:
            cell = random.choice(queue)
            queue.remove(cell)
            self.frontier.discard(cell)

            visited_neighbors = [
                n for n in self.neighbors(cell) if n in visited]
            if visited_neighbors:
                proc_cell = random.choice(visited_neighbors)
                direction = self.get_direction(proc_cell, cell)
                self.grid.open_wall(proc_cell.coordinate, direction)
                visited.add(cell)
                cell.occupied = True
                self._trigger_event(cell, True)
                for n in self.neighbors(cell):
                    if n not in visited and n not in self.frontier:
                        self.frontier.add(n)
                        queue.append(n)


if __name__ == "__main__":
    prim = Prim(Grid.build(11, 11))
    prim.generate_maze()
    prim.grid.show()