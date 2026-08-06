"""visualiser.refactored.context module.

Provides the WindowContext: a concrete shared-state service that owns the
mlx lifecycle and exposes thin drawing helpers. The refactored components
(Renderer, MazeEngine, Menu, InputHandler) all receive a WindowContext via
their constructor instead of reaching into a shared ``self``.

Because the state below belongs to a single window, it lives here as the
shared object that components read and write. Only the behaviour methods
are split across components; the state is intentionally central.
"""
from typing import Any

from mlx import Mlx
from maze.cell import Cell
from config.parser import Config
from visualiser.layout import Layout
from visualiser.widgets import Button, InputField
from visualiser.constants import PATTERN_COLORS


class WindowContext:
    """Concrete shared state and mlx lifecycle for the visualiser.

    Owns the native mlx pointers, the configuration and every piece of
    runtime state the components need. Also provides small helpers so
    components don't juggle ``mlx_ptr``/``win_ptr`` directly.
    """

    win_width: int = 1920
    win_height: int = 1080

    m: Mlx
    mlx_ptr: Any
    win_ptr: Any

    config: Config
    render_delay: float
    entry: tuple[int, int]
    exit: tuple[int, int]
    algorithm: str
    solution_path: list[Cell]
    show_path: bool
    pattern_color: int
    pattern_index: int

    layout: Layout
    grid: Any

    buttons: list[Button]
    algo_buttons: list[Button]
    fields: list[InputField]

    background_img: Any
    maze_background_img: Any
    menu_canvas_img: Any
    maze_canvas_img: Any

    def __init__(self, m: Mlx, config: Config) -> None:
        """Initialise the mlx instance and window.

        Args:
            m (Mlx): The mlx instance.
            config (Config): The application configuration.
        """
        self.m = m
        self.config = config
        self.mlx_ptr = m.mlx_init()
        self.win_ptr = m.mlx_new_window(
            self.mlx_ptr, self.win_width, self.win_height, "a_maze_ing"
        )
        self.clear()

        self.render_delay = 0.00
        self.entry = config.entry
        self.exit = config.exit
        self.algorithm = "dfs"
        self.solution_path = []
        self.show_path = True
        self.pattern_color = PATTERN_COLORS[0]
        self.pattern_index = 0
        self.buttons = []
        self.algo_buttons = []
        self.fields = []

    def new_image(self, w: int, h: int) -> Any:
        """Create a new image buffer of the given size.

        Args:
            w (int): The width of the image.
            h (int): The height of the image.

        Returns:
            Any: The created image pointer.
        """
        return self.m.mlx_new_image(self.mlx_ptr, w, h)

    def put_img(self, img: Any, x: int, y: int) -> None:
        """Put an image onto the window at the given position.

        Args:
            img (Any): The image pointer.
            x (int): The x position.
            y (int): The y position.
        """
        self.m.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, img, x, y)

    def put_string(self, x: int, y: int, color: int, text: str) -> None:
        """Put a text string onto the window.

        Args:
            x (int): The x position.
            y (int): The y position.
            color (int): The packed 0xRRGGBB color.
            text (str): The string to render.
        """
        self.m.mlx_string_put(self.mlx_ptr, self.win_ptr, x, y, color, text)

    def sync(self, mode: int) -> None:
        """Synchronise the window with the given sync mode.

        Args:
            mode (int): One of ``SYNC_WIN_FLUSH`` / ``SYNC_WIN_COMPLETED``.
        """
        self.m.mlx_sync(self.mlx_ptr, mode, self.win_ptr)

    def present_scene(self) -> None:
        """Present the whole UI in a single sync batch.

        Blits the background, maze backdrop, menu canvas and maze canvas,
        then draws every widget label on top. This keeps the total number
        of draw calls per frame below the mlx draw-queue limit so the full
        scene (menu included) is flushed together.
        """
        l = self.layout
        self.put_img(self.background_img, 0, 0)
        self.put_img(self.maze_background_img,
                     l.maze_offset_x + l.relative_x_offset, l.maze_offset_y)
        self.put_img(self.menu_canvas_img, l.menu_x, l.maze_offset_y)
        self.put_img(self.maze_canvas_img, l.offset_x, l.offset_y)
        for btn in self.buttons:
            btn.put_label(self.m, self.mlx_ptr, self.win_ptr)
        for field in self.fields:
            field.put_label(self.m, self.mlx_ptr, self.win_ptr)
        self.sync(self.m.SYNC_WIN_COMPLETED)

    def clear(self) -> None:
        """Clear the window."""
        self.m.mlx_clear_window(self.mlx_ptr, self.win_ptr)