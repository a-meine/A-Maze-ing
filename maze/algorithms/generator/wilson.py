from maze.algorithms.generator.base import GeneratorBase
from maze.cell import Cell
from maze.grid import Grid


class Wilson(GeneratorBase):
    def __init__(self, grid: Grid) -> None:
        super().__init__(grid)
        self.__occupied_cells = 0

    def __process_cell(self, cell: Cell) -> None:
        cell.occupied = True
        self._trigger_event(cell)
        self.__occupied_cells += 1

    def generate_maze(self) -> None:
        is_first_run = True
        while self.__occupied_cells < self.grid.total_cells:
            path = self.find_path(is_first_run)
            prev = path[0]
            for cell in path[1:]:
                direction = self.get_direction(prev, cell)
                self.grid.open_wall(prev.coordinate, direction)
                self.__process_cell(prev)
                prev = cell
            if is_first_run:
                is_first_run = False
                self.__process_cell(prev)
        self.grid.clean()

    def find_path(self, is_first_run: bool = False) -> list[Cell]:
        start = self._get_random_cell()
        destination = start
        if is_first_run:
            start.occupied = True
            destination = self._get_random_cell()
            start.occupied = False
        path = [start]
        cell = start
        while (not is_first_run and not cell.occupied) or destination != cell:
            direction = self._get_random_direction(cell, True)
            if direction is None:
                path = [start]
                cell = start
                continue
            cell = self.get_neighbor(cell, direction)
            if is_first_run:
                if destination == cell:
                    path.append(cell)
                    break
            else:
                if cell.occupied:
                    path.append(cell)
                    break
            if cell in path:
                while path[-1] != cell:
                    path.pop()
            else:
                path.append(cell)
        return path


if __name__ == "__main__":
    wilson = Wilson(Grid.Build(11, 11))
    wilson.generate_maze()
    wilson.grid.show()
