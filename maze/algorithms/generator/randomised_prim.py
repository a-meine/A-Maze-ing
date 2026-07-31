from maze.algorithms.generator.base import GeneratorBase
from maze.cell import Cell
from maze.grid import Grid
from maze.direction import Direction
import random


class Prim(GeneratorBase):
    def __init__(self, grid: Grid) -> None:
        super().__init__(grid)

    def neighbors(self, cell: Cell) -> list[Cell]:
        all_neighbors = [
            self.grid.get_neighbor(cell, Direction.EAST),
            self.grid.get_neighbor(cell, Direction.WEST),
            self.grid.get_neighbor(cell, Direction.SOUTH),
            self.grid.get_neighbor(cell, Direction.NORTH),
        ]
        return [n for n in all_neighbors if n is not None]

    def generate_maze(self) -> None:
        start = self._get_random_cell()
        visited = [start]
        self._trigger_event(start)
        queue: list[Cell] = self.neighbors(start)

        while queue:
            for _c in queue:
                self._trigger_event(_c, False)
            cell = random.choice(queue)
            queue.remove(cell)

            visited_neighbors = [
                n for n in self.neighbors(cell) if n in visited]
            if len(visited_neighbors):
                proc_cell = random.choice(visited_neighbors)
                direction = self.get_direction(proc_cell, cell)
                self.grid.open_wall(proc_cell.coordinate, direction)
                visited.append(cell)
                cell.occupied = True
                self._trigger_event(cell, True)
                for n in self.neighbors(cell):
                    if n not in visited and n not in queue:
                        queue.append(n)


if __name__ == "__main__":
    prim = Prim(Grid.Build(11, 11))
    prim.generate_maze()
    prim.grid.show()
