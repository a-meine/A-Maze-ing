"""visualiser.refactored.app module.

Provides the App class: the orchestrator that composes the rendering,
maze, menu and input components on top of the shared WindowContext.
"""
from typing import Any
import sys
import time
from mlx import Mlx
from maze.encoding import write_output
from config.parser import Config, load_config
from visualiser.context import WindowContext
from visualiser.renderer import Renderer
from visualiser.maze import MazeEngine
from visualiser.menu import Menu
from visualiser.input import InputHandler
from visualiser.constants import (
    WIN_CLOSE,
    PATTERN_COLORS,
    PATTERN_NAMES,
    WALL_COLORS,
    WALL_NAMES,
)


class App:
    """Main application class for the maze visualiser.

    Owns the mlx lifecycle through the WindowContext and coordinates the
    Renderer, MazeEngine, Menu and InputHandler components for maze
    generation, rendering and user interaction.
    """

    def __init__(self, config: Config) -> None:
        """Initialize the application and its components.

        Args:
            config (Config): The application configuration.
        """
        self.ctx = WindowContext(Mlx(), config)
        self.renderer = Renderer(self.ctx)
        self.engine = MazeEngine(self.ctx, self.renderer.render)
        self.menu = Menu(self.ctx, {
            "apply_settings": self.apply_settings,
            "regen": self.regen,
            "toggle_path": self.toggle_path,
            "cycle_color": self.cycle_pattern_color,
            "cycle_wall": self.cycle_wall_color,
            "run_all": self.run_all,
            "close": self.close,
        })
        self.input_handler = InputHandler(self.ctx, self.menu, self.close)

    def apply_settings(self) -> None:
        """Apply current UI settings and rebuild the display.

        Reconfigures images, reinitialises resources,
        redraws the menu, and re-renders the grid.
        """
        self.ctx.solution_path = []
        self.engine.config_images()
        self.renderer.initialise_images()
        self.menu.redraw_menu()
        self.renderer.render_maze()

    def toggle_path(self) -> None:
        """Toggle the visibility of the solution path."""
        self.ctx.show_path = not self.ctx.show_path
        for btn in self.ctx.buttons:
            if btn.action == self.toggle_path:
                btn.label = "Hide" if self.ctx.show_path else "Show"
        self.menu.redraw_buttons()
        self.renderer.render_maze()

    def regen(self) -> None:
        """Regenerate the maze and update the display."""
        self.apply_settings()
        self.ctx.generator.generate_maze()
        self.engine._solve_path()
        write_output(self.ctx.generator.grid, self.ctx.config,
                     self.ctx.solution_path)
        self.renderer.render_maze()

    def _update_color_label(self) -> None:
        """Sync the '42 Colour' button label with the active colour."""
        name = PATTERN_NAMES[self.ctx.pattern_index]
        for btn in self.ctx.buttons:
            if btn.action == self.cycle_pattern_color:
                btn.label = name

    def cycle_pattern_color(self) -> None:
        """Cycle the '42' pattern colour and repaint the pattern."""
        colors = PATTERN_COLORS
        self.ctx.pattern_index = (self.ctx.pattern_index + 1) % len(colors)
        self.ctx.pattern_color = colors[self.ctx.pattern_index]
        self._update_color_label()
        self.menu.redraw_buttons()
        self.renderer.render_maze()

    def _update_wall_label(self) -> None:
        """Sync the 'Wall Colour' button label with the active colour."""
        name = WALL_NAMES[self.ctx.wall_index]
        for btn in self.ctx.buttons:
            if btn.action == self.cycle_wall_color:
                btn.label = name

    def cycle_wall_color(self) -> None:
        """Cycle the wall colour and repaint the maze."""
        colors = WALL_COLORS
        self.ctx.wall_index = (self.ctx.wall_index + 1) % len(colors)
        self.ctx.wall_color = colors[self.ctx.wall_index]
        self._update_wall_label()
        self.menu.redraw_buttons()
        self.renderer.render_maze()

    def run_all(self) -> None:
        """Run every algorithm once, cycling through all colour combinations.

        Generates a single maze per algorithm (DFS, Prim, Wilson) and then,
        without regenerating, steps through every pairing of the '42' pattern
        colour and the wall colour, pausing briefly between combinations.
        """
        for algo in ("dfs", "prim", "wilson"):
            self.menu._set_algorithm(algo)
            self.regen()
            for idx, p_color in enumerate(PATTERN_COLORS):
                self.ctx.pattern_index = idx
                self.ctx.pattern_color = p_color
                self._update_color_label()
                for widx, w_color in enumerate(WALL_COLORS):
                    self.ctx.wall_index = widx
                    self.ctx.wall_color = w_color
                    self._update_wall_label()
                    self.menu.redraw_buttons()
                    self.renderer.render_maze()
                    time.sleep(self.ctx.render_delay * 50)

    def close(self, _: Any = None) -> None:
        """Close the window and exit the application.

        Args:
            _: Placeholder parameter for the mlx hook callback.
        """
        print("closing...")
        self.ctx.m.mlx_loop_exit(self.ctx.mlx_ptr)

    def run(self) -> None:
        """Start the main event loop of the visualiser.

        Sets up the menu, generates and solves the maze,
        and enters the mlx event loop.
        """
        self.menu.menu()
        self.regen()
        self.ctx.m.mlx_hook(
            self.ctx.win_ptr, WIN_CLOSE, 0, self.close, None)
        self.ctx.m.mlx_key_hook(
            self.ctx.win_ptr, self.input_handler.start_key_hook, "hi there")
        self.ctx.m.mlx_mouse_hook(
            self.ctx.win_ptr, self.input_handler.start_mouse_hook, None)
        self.ctx.m.mlx_loop(self.ctx.mlx_ptr)


if __name__ == "__main__":
    config = load_config(sys.argv[1])
    App(config).run()
