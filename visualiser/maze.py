"""visualiser.refactored.maze module.

Provides the MazeEngine: maze model construction, grid building and
solution path computation. It is composed into the App class.
"""
from typing import Any, Callable
import random

from maze.cell import Cell
from maze.grid import Grid
from maze.algorithms.generator.randomised_prim import Prim
from maze.algorithms.generator.dfs import DFS
from maze.algorithms.generator.wilson import Wilson
from maze.algorithms.solution.bfs import BFS
from config.parser import Config
from visualiser.layout import Layout
from visualiser.context import WindowContext


class MazeEngine:
    """Builds the maze grid and solves it."""

    def __init__(
            self,
            ctx: WindowContext,
            render_cb: Callable[[Cell, bool], None],
    ) -> None:
        """Initialize the maze engine.

        Args:
            ctx (WindowContext): The shared window context.
            render_cb (Callable[[Cell, bool], None]): Called whenever a
                cell is generated, so the grid can stream renders.
        """
        self.ctx = ctx
        self._render_cb = render_cb

    def config_images(self) -> None:
        """Recompute the layout, rebuild the grid and wire the callback."""
        ctx = self.ctx
        ctx.layout = Layout.compute(ctx.fields, ctx.config,
                                    ctx.win_width, ctx.win_height)
        cfg = ctx.config.model_copy(update={
            "width": ctx.layout.grid_width,
            "height": ctx.layout.grid_height,
            "entry": ctx.layout.entry,
            "exit": ctx.layout.exit,
        })
        ctx.grid = self._build_grid(cfg)
        ctx.grid.event = self._render_cb

    def _build_grid(self, config: Config) -> Any:
        if config.seed is not None:
            random.seed(config.seed)
        grid = Grid(config)
        if self.ctx.algorithm == "dfs":
            return DFS(grid)
        if self.ctx.algorithm == "wilson":
            return Wilson(grid)
        return Prim(grid)

    def _solve_path(self) -> None:
        """Compute the solution path using BFS."""
        try:
            solver = BFS(self.ctx.grid.grid)
            self.ctx.solution_path = solver.solve()
        except Exception:
            self.ctx.solution_path = []