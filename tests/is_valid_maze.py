from typing import TypeVar
import unittest

from maze.algorithms.generator.base import GeneratorBase
from maze.algorithms.generator.dfs import DFS
from maze.algorithms.generator.randomised_prim import Prim
from maze.algorithms.generator.wilson import Wilson
from maze.grid import Grid


T = TypeVar("T", bound=GeneratorBase)

class TestGenerator(unittest.TestCase):
    def is_maze_has_open_area(self, generatorType: type[T]):
        for _ in range(1, 30):
            generator = generatorType(Grid.Build(50, 50))
            generator.generate_maze()
            for x in range(0, generator.grid.width - 3):
                for y in range(0, generator.grid.height - 3):
                    cell_center = generator[y + 1][x + 1]
                    cell_center_left = generator[y + 1][x]
                    cell_center_right = generator[y + 1][x + 2]
                    cell_top_center = generator[y][x + 1]
                    cell_bottom_center = generator[y + 2][x + 1]
                    self.assertFalse(
                        not cell_center.walls.east
                        and not cell_center.walls.west
                        and not cell_center.walls.north
                        and not cell_center.walls.south
                        and not cell_center_left.walls.north
                        and not cell_center_left.walls.south
                        and not cell_center_right.walls.north
                        and not cell_center_right.walls.south
                        and not cell_top_center.walls.east
                        and not cell_top_center.walls.west
                        and not cell_bottom_center.walls.east
                        and not cell_bottom_center.walls.west
                    )


class TestDFS(TestGenerator):
    def test_if_generate_valid_maze(self):
        self.is_maze_has_open_area(DFS)


class TestWilson(TestGenerator):
    def test_if_generate_valid_maze(self):
        self.is_maze_has_open_area(Wilson)


class TestPrim(TestGenerator):
    def test_if_generate_valid_maze(self):
        self.is_maze_has_open_area(Prim)


if __name__ == "__main__":
    unittest.main(verbosity=2)
