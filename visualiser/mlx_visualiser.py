"""visualiser.mlx_visualiser module.

Provides the Window class for visualising the maze
using the mlx library.
"""
from mlx import Mlx
from typing import Any
# import time
from maze.cell import Cell
from maze.grid import Grid
from maze.algorithms.generator.randomised_prim import Prim
from maze.algorithms.generator.dfs import DFS
from maze.algorithms.solution.bfs import BFS
from config.parser import Config, load_config
from maze.encoding import write_output
from visualiser.widgets import Button, InputField, fill_image
from visualiser.layout import Layout

KEY_ESC = 65307
KEY_BACKSPACE = 65288
KEY_0 = 48
KEY_9 = 57

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
MAGENTA = (255, 0, 255)
CYAN = (0, 255, 255)
GRAY = (50, 50, 50)
MED_GRAY = (128, 128, 128)
INACTIVE_GRAY = (100, 100, 100)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)


class Window:
    """Main window class for the maze visualiser.

    Manages the mlx window, rendering, and user interaction
    for maze generation and solving.

    Attributes:
        win_width (int): The window width in pixels.
        win_height (int): The window height in pixels.
        config (Config): The application configuration.
        m (Mlx): The mlx instance.
        mlx_ptr (Any): The mlx pointer.
        win_ptr (Any): The window pointer.
        render_delay (float): The delay between renders in seconds.
        entry (tuple[int, int]): The entry point coordinates.
        exit (tuple[int, int]): The exit point coordinates.
        algorithm (str): The current maze generation algorithm.
        solution_path (list[Cell]): The computed solution path.
        show_path (bool): Whether to display the solution path.
    """

    def __init__(self, config: Config) -> None:
        """Initialize the window with the given configuration.

        Sets up the mlx instance, creates the window,
        and initializes display parameters.

        Args:
            config (Config): The application configuration.
        """
        self.win_width = 1800
        self.win_height = 1200
        self.config = config
        print(config)

        self.m = Mlx()
        self.mlx_ptr = self.m.mlx_init()
        self.win_ptr = self.m.mlx_new_window(
            self.mlx_ptr, self.win_width, self.win_height, "a_maze_ing"
        )
        self.m.mlx_clear_window(self.mlx_ptr, self.win_ptr)

        self.render_delay = 0.001
        self.entry = config.entry
        self.exit = config.exit
        self.algorithm = "prim"
        self.solution_path: list[Cell] = []
        self.show_path = True

    def _build_grid(self) -> Any:
        """Build a maze generator based on the current algorithm setting.

        Returns:
            Any: The maze generator instance (DFS or Prim).
        """
        grid = Grid(self.config)
        if self.algorithm == "dfs":
            return DFS(grid)
        return Prim(grid)

    def config_images(self) -> None:
        """Configure all image resources for rendering.

        Computes the layout, builds the grid, and sets
        up the render callback.
        """
        self.layout = Layout.compute(
            self.fields, self.config, self.win_width, self.win_height
        )
        self.grid = self._build_grid()
        self.grid.event = self.render

    def apply_settings(self) -> None:
        """Apply current UI settings and rebuild the display.

        Reconfigures images, reinitialises resources,
        redraws the menu, and re-renders the grid.
        """
        self.config_images()
        self.initialise_images()
        self.redraw_menu()
        self.render_grid()

    def _solve_path(self) -> None:
        """Compute the solution path using BFS."""
        try:
            solver = BFS(self.grid.grid)
            self.solution_path = solver.solve()
        except Exception:
            self.solution_path = []

    def _make_tile(
            self,
            color: tuple[int, int, int],
            margin_x: int = 0,
            margin_y: int = 0,
    ) -> Any:
        """Create a tile image with the given color.

        Args:
            color (tuple[int, int, int]): The RGB color for the tile.
            margin_x (int): Horizontal margin. Defaults to 0.
            margin_y (int): Vertical margin. Defaults to 0.

        Returns:
            Any: The created image pointer.
        """
        l: Layout = self.layout
        img = self.m.mlx_new_image(
            self.mlx_ptr, l.tile_width, l.tile_height)
        fill_image(self.m, img, l.tile_width, l.tile_height,
                   color, margin_x, margin_y)
        return img

    def _make_solid_image(
            self,
            w: int,
            h: int,
            color: tuple[int, int, int] = MED_GRAY,
    ) -> Any:
        """Create a solid-colour image of the given size.

        Args:
            w (int): The width of the image.
            h (int): The height of the image.
            color (tuple[int, int, int]): The RGB fill color.
                Defaults to MED_GRAY.

        Returns:
            Any: The created image pointer.
        """
        img = self.m.mlx_new_image(self.mlx_ptr, w, h)
        fill_image(self.m, img, w, h, color)
        return img

    def initialise_images(self) -> None:
        """Initialise all image resources for rendering."""
        l: Layout = self.layout
        self.cell_img_ptr = self._make_tile(WHITE)
        self.entry_cell = self._make_tile(GREEN)
        self.next_cell_img_ptr = self._make_tile(MAGENTA)
        self.exit_cell = self._make_tile(CYAN)
        self.empty_cell_img = self._make_tile(
            GRAY, l.tile_width // 20, l.tile_height // 20)
        self.path_cell_img = self._make_tile(YELLOW)
        self.background_img = self._make_solid_image(
            self.win_width, self.win_height, WHITE)
        self.maze_background_img = self._make_solid_image(l.maze_w, l.maze_h)
        self.menu_background_img = self._make_solid_image(l.menu_w, l.menu_h)

    def _render_walls(self, cell: Cell, rx: int, ry: int) -> None:
        """Render the walls of a cell onto the window.

        Args:
            cell (Cell): The cell whose walls to render.
            rx (int): The rendered x position.
            ry (int): The rendered y position.
        """
        l: Layout = self.layout
        walls = [
            (cell.walls.east,  rx + 1, ry),
            (cell.walls.south, rx,     ry + 1),
            (cell.walls.north, rx,     ry - 1),
            (cell.walls.west,  rx - 1, ry),
        ]
        for has_wall, tx, ty in walls:
            if has_wall:
                continue
            self.m.mlx_put_image_to_window(
                self.mlx_ptr, self.win_ptr, self.cell_img_ptr,
                l.offset_x + tx * l.tile_width,
                l.offset_y + ty * l.tile_height)

    def _render_entry_exit(self, cell: Cell, px: int, py: int) -> None:
        """Render the entry and exit markers for a cell.

        Args:
            cell (Cell): The cell to check for entry/exit.
            px (int): The pixel x position.
            py (int): The pixel y position.
        """
        coord = (cell.coordinate.x, cell.coordinate.y)
        if coord == self.layout.entry:
            self.m.mlx_put_image_to_window(
                self.mlx_ptr, self.win_ptr, self.entry_cell, px, py)
        if coord == self.layout.exit:
            self.m.mlx_put_image_to_window(
                self.mlx_ptr, self.win_ptr, self.exit_cell, px, py)

    def _render_cell_state(self, cell: Cell, px: int, py: int) -> None:
        """Render the state of a cell (occupied or not).

        Args:
            cell (Cell): The cell to render.
            px (int): The pixel x position.
            py (int): The pixel y position.
        """
        if cell.occupied:
            self.m.mlx_put_image_to_window(
                self.mlx_ptr, self.win_ptr, self.next_cell_img_ptr, px, py)
            self.m.mlx_put_image_to_window(
                self.mlx_ptr, self.win_ptr, self.cell_img_ptr, px, py)
            self._render_entry_exit(cell, px, py)
        else:
            self.m.mlx_put_image_to_window(
                self.mlx_ptr, self.win_ptr, self.next_cell_img_ptr, px, py)

    def render(self, cell: Cell, sync: bool = True) -> None:
        """Render a single cell onto the window.

        Args:
            cell (Cell): The cell to render.
            sync (bool): Whether to synchronise the display.
                Defaults to True.
        """
        l: Layout = self.layout
        rx = 2 * cell.coordinate.x + 1
        ry = 2 * cell.coordinate.y + 1
        px = l.offset_x + rx * l.tile_width
        py = l.offset_y + ry * l.tile_height

        self._render_walls(cell, rx, ry)
        if sync:
            self.m.mlx_sync(self.mlx_ptr, self.m.SYNC_WIN_FLUSH,
                            self.win_ptr)
        self._render_cell_state(cell, px, py)

    def render_grid(self) -> None:
        """Render the entire maze grid onto the window."""
        l: Layout = self.layout
        for y in range(l.rend_tiles_y):
            for x in range(l.rend_tiles_x):
                px = l.offset_x + x * l.tile_width
                py = l.offset_y + y * l.tile_height
                self.m.mlx_put_image_to_window(
                    self.mlx_ptr, self.win_ptr,
                    self.empty_cell_img, px, py)
            self.m.mlx_sync(self.mlx_ptr, self.m.SYNC_WIN_FLUSH,
                            self.win_ptr)
        self.m.mlx_sync(self.mlx_ptr, self.m.SYNC_WIN_FLUSH,
                        self.win_ptr)
        self._render_path()

    def _render_path(self) -> None:
        """Render the solution path onto the window."""
        l: Layout = self.layout
        if self.show_path:
            for cell in self.solution_path:
                rx = 2 * cell.coordinate.x + 1
                ry = 2 * cell.coordinate.y + 1
                px = l.offset_x + rx * l.tile_width
                py = l.offset_y + ry * l.tile_height
                self.m.mlx_put_image_to_window(
                    self.mlx_ptr, self.win_ptr,
                    self.path_cell_img, px, py)
                self._render_entry_exit(cell, px, py)

    def _set_algorithm(self, algo: str) -> None:
        """Set the maze generation algorithm and update button colours.

        Args:
            algo (str): The algorithm name ('dfs' or 'prim').
        """
        self.algorithm = algo
        for btn in self.algo_buttons:
            is_active = btn.label.lower() == algo
            btn.color_normal = GREEN if is_active else INACTIVE_GRAY
            btn.color_pressed = RED if is_active else INACTIVE_GRAY
        self.redraw_buttons()

    def menu(self) -> None:
        """Set up the menu buttons and input fields."""
        algo_buttons = [
            Button(205, 490, 50, 30, "DFS",
                   INACTIVE_GRAY, INACTIVE_GRAY,
                   action=lambda: self._set_algorithm("dfs")),
            Button(260, 490, 50, 30, "Prim",
                   GREEN, RED,
                   action=lambda: self._set_algorithm("prim")),
        ]
        self.algo_buttons = algo_buttons
        self.buttons = [
            Button(200, 150, 200, 40, "Apply Settings",
                   GREEN, RED, action=self.apply_settings),
            Button(200, 210, 200, 40, "Re-Generate",
                   GREEN, RED, action=self.regen),
            Button(200, 270, 200, 40, "Hide Path",
                   GREEN, RED, action=self.toggle_path),
            Button(250, 560, 150, 30, "exit",
                   GREEN, RED,
                   action=lambda: self.close(None)),
            *algo_buttons,
        ]
        self.fields = [
            InputField(200, 300, 70, 30, "width",
                       str(self.config.width)),
            InputField(450, 300, 70, 30, "height",
                       str(self.config.height)),
            InputField(200, 400, 20, 20, "",
                       str(self.config.entry[0])),
            InputField(223, 400, 20, 20, "",
                       str(self.config.entry[1])),
            InputField(200, 450, 20, 20, "",
                       str(self.config.exit[0])),
            InputField(223, 450, 20, 20, "",
                       str(self.config.exit[1])),
        ]

    def redraw_menu(self) -> None:
        """Redraw the entire menu overlay onto the window."""
        l: Layout = self.layout
        self.m.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, self.background_img, 0, 0)
        self.m.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, self.menu_background_img,
            l.menu_x, l.maze_offset_y)
        self.m.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, self.maze_background_img,
            l.maze_offset_x + l.relative_x_offset, l.maze_offset_y)

        self.m.mlx_string_put(self.mlx_ptr, self.win_ptr,
                              200, 480, 0xFFFFFF, "Algorithm:")
        self.redraw_buttons()
        self.redraw_fields()
        self.m.mlx_sync(self.mlx_ptr, self.m.SYNC_WIN_COMPLETED,
                        self.win_ptr)

    def redraw_buttons(self) -> None:
        """Redraw all buttons onto the window."""
        for btn in self.buttons:
            btn.draw(self.m, self.mlx_ptr, self.win_ptr)
        self.m.mlx_sync(self.mlx_ptr, self.m.SYNC_WIN_COMPLETED,
                        self.win_ptr)

    def redraw_fields(self) -> None:
        """Redraw all input fields onto the window."""
        for field in self.fields:
            field.draw(self.m, self.mlx_ptr, self.win_ptr)
        self.m.mlx_sync(self.mlx_ptr, self.m.SYNC_WIN_COMPLETED,
                        self.win_ptr)

    def _focus_field_at(self, x: int, y: int) -> bool:
        """Focus the input field at the given coordinates.

        Args:
            x (int): The x coordinate.
            y (int): The y coordinate.

        Returns:
            bool: True if a field was focused.
        """
        clicked = False
        for field in self.fields:
            if field.contains(x, y):
                field.focused = True
                clicked = True
            else:
                field.focused = False
        return clicked

    def _clear_focus(self) -> None:
        """Clear focus from all input fields."""
        for field in self.fields:
            field.focused = False

    def _active_field(self) -> InputField | None:
        """Get the currently focused input field.

        Returns:
            InputField | None: The active field, or None if none focused.
        """
        for field in self.fields:
            if field.focused:
                return field
        return None

    def start_mouse_hook(
            self, button: int, x: int, y: int, mystuff: Any
    ) -> None:
        """Handle mouse click events.

        Args:
            button (int): The mouse button that was clicked.
            x (int): The x coordinate of the click.
            y (int): The y coordinate of the click.
            mystuff (Any): Additional data passed by the hook.
        """
        if button != 1:
            return
        if self._focus_field_at(x, y):
            self.redraw_fields()
            return
        for btn in self.buttons:
            if btn.contains(x, y):
                btn.pressed = True
                self.redraw_buttons()
                if btn.action:
                    btn.action()
                btn.pressed = False
                self.redraw_buttons()
                return
        self._clear_focus()
        self.redraw_fields()

    def start_key_hook(self, keynum: int, mystuff: Any) -> None:
        """Handle keyboard events.

        Args:
            keynum (int): The key code that was pressed.
            mystuff (Any): Additional data passed by the hook.
        """
        if keynum == KEY_ESC:
            self.close(None)
            return
        active = self._active_field()
        if active is None:
            return
        if keynum == KEY_BACKSPACE:
            active.text = active.text[:-1]
            self.redraw_fields()
        elif KEY_0 <= keynum <= KEY_9:
            active.text += chr(keynum)
            self.redraw_fields()

    def toggle_path(self) -> None:
        """Toggle the visibility of the solution path."""
        self.show_path = not self.show_path
        for btn in self.buttons:
            if btn.action == self.toggle_path:
                btn.label = "Hide Path" if self.show_path else "Show Path"
        self.redraw_buttons()
        self.render_grid()

    def regen(self) -> None:
        """Regenerate the maze and update the display."""
        self.apply_settings()
        self.grid.generate_maze()
        self._solve_path()
        write_output(self.grid.grid, self.config, self.solution_path)
        self._render_path()

    def close(self, dummy: Any) -> None:
        """Close the window and exit the application.

        Args:
            dummy (Any): Placeholder parameter for the mlx hook callback.
        """
        print("closing...")
        self.m.mlx_loop_exit(self.mlx_ptr)

    def run(self) -> None:
        """Start the main event loop of the visualiser.

        Sets up the menu, generates and solves the maze,
        and enters the mlx event loop.
        """
        self.menu()
        self.regen()
        self.m.mlx_hook(self.win_ptr, 33, 0, self.close, None)
        self.m.mlx_key_hook(self.win_ptr, self.start_key_hook, "hi there")
        self.m.mlx_mouse_hook(self.win_ptr, self.start_mouse_hook, None)
        self.m.mlx_loop(self.mlx_ptr)


if __name__ == "__main__":
    import sys

    if len(sys.argv[1:]) != 1:
        print("No config file given")
        print("Usage: python3 -m visualiser.mlx_visualiser_v2 config.txt")
        exit(0)

    config = load_config(sys.argv[1])
    Window(config).run()