"""maze package: reusable maze generation, solving and encoding.

Public API:
    MazeGenerator - single facade to generate, solve and export a maze.
    Grid         - the 2D grid model.
    DFS, Prim, Wilson - the perfect-maze generators.
    BFS          - the shortest-path solver.
"""
from maze.maze_generator import MazeGenerator
from maze.grid import Grid
from maze.algorithms.generator.dfs import DFS
from maze.algorithms.generator.randomised_prim import Prim
from maze.algorithms.generator.wilson import Wilson
from maze.algorithms.solution.bfs import BFS

__all__ = [
    "MazeGenerator",
    "Grid",
    "DFS",
    "Prim",
    "Wilson",
    "BFS",
]