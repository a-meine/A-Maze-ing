"""maze.algorithms.solution.bfs module."""
from maze.cell import Cell
from maze.grid import Grid
from maze.direction import Direction


class Node():
    """Represents a node in the BFS search tree.

    Attributes:
        cell (Cell): The cell this node represents.
        parent_node (Node): The parent node in the search tree.
            The root node is its own parent.
    """

    def __init__(self, cell: Cell) -> None:
        """Initialize a Node with the given cell.

        Args:
            cell (Cell): The cell this node represents.
        """
        self.cell = cell
        self.parent_node = self


class BFS():
    """Breadth-First Search maze solver algorithm.

    Finds the shortest path from the entry to the exit
    in the maze grid using BFS traversal.
    """

    def __init__(self, grid: Grid) -> None:
        """Initialize the BFS solver with a grid.

        Args:
            grid (Grid): The grid to solve.
        """
        self._grid = grid

    def _clean(self) -> None:
        """Clear the occupied flag on all cells in the grid."""
        for cell in self._grid:
            cell.occupied = False

    def _wall_is_open(self, cell: Cell, direction: Direction) -> bool:
        """Check whether a wall on the given side of a cell is open.

        Args:
            cell (Cell): The cell to check.
            direction (Direction): The direction of the wall to check.

        Returns:
            bool: True if the wall is open, False if closed.
        """
        if direction == Direction.NORTH:
            return not cell.walls.north
        if direction == Direction.EAST:
            return not cell.walls.east
        if direction == Direction.SOUTH:
            return not cell.walls.south
        if direction == Direction.WEST:
            return not cell.walls.west
        else:
            return False

    def solve(self) -> list[Cell]:
        """Solve the maze using Breadth-First Search.

        Finds the shortest path from the entry to the exit.

        Returns:
            list[Cell]: The solution path from entry to exit.
        """
        self._grid.clean()
        start = self._grid.start
        start.occupied = True
        nodes = [Node(start)]
        end = self._grid.end
        i = 0
        while i < len(nodes):
            parent = nodes[i]
            cell = parent.cell
            for direction in Direction:
                if self._wall_is_open(cell, direction):
                    next_node = self._grid.get_neighbor(cell, direction)
                    if next_node is not None and not next_node.occupied:
                        next_node.occupied = True
                        n = Node(next_node)
                        n.parent_node = parent
                        nodes.append(n)
                        if next_node == end:
                            break
            if nodes[-1].cell == end:
                break
            i += 1
        self._grid.clean()
        node = nodes[-1]
        path: list[Cell] = []
        while True:
            path.append(node.cell)
            if node.parent_node == node:
                break
            node = node.parent_node
        path.reverse()
        return path