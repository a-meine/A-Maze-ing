from maze.cell import Cell
from maze.grid import Grid


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

    def solve(self) -> list[Cell]:
        self._grid.clean()
        start = self._grid.start
        start.occupied = True
        nodes = [Node(start)]
        end = self._grid.end
        i = 0
        while i == len(nodes) - 1:
            parent = nodes[i]
            cell = parent.cell
            for direction in self._grid.available_direction(cell.coordinate):
                next_node = self._grid.get_neighbor(cell, direction)
                assert next_node is not None
                next_node.occupied = True
                node = Node(next_node)
                node.parent_node = parent
                nodes.append(node)
                if next_node == end:
                    break
            if nodes[-1].cell == end:
                break
            i += 1
        self._grid.clean()
        node = nodes[-1]
        path: list[Cell] = []
        while node.parent_node == node:
            path.append(node.cell)
            node = node.parent_node
        path.reverse()
        return path
