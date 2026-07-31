from maze.algorithms.generator.base import GeneratorBase
from maze.cell import Cell
from maze.grid import Grid


class DFS(GeneratorBase):
    def __init__(self, grid: Grid) -> None:
        super().__init__(grid)
        self.__occupied_cells = 0

    def __process_cell(self, cell: Cell) -> None:
        if cell.occupied:
            self._trigger_event(cell)
            return
        cell.occupied = True
        self.__occupied_cells += 1
        self._trigger_event(cell)

    def generate_maze(self) -> None:
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
    dfs = DFS(Grid.Build(50, 50))
    dfs.generate_maze()
    dfs.grid.show()
