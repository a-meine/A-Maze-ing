from maze.cell import Cell
from maze.grid import Grid
from maze.direction import Direction


class Node():
    def __init__(self, cell: Cell) -> None:
        self.cell = cell
        self.parent_node = self


class BFS():
    def __init__(self, grid: Grid) -> None:
        self._grid = grid

    def _clean(self) -> None:
        for cell in self._grid:
            cell.occupied = False

    def _wall_is_open(self, cell: Cell, direction: Direction) -> bool:
        if direction == Direction.NORTH:
            return not cell.walls.north
        if direction == Direction.EAST:
            return not cell.walls.east
        if direction == Direction.SOUTH:
            return not cell.walls.south
        if direction == Direction.WEST:
            return not cell.walls.west
        return False

    def solve(self) -> list[Cell]:
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
