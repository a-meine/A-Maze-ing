"""visualiser.refactored.renderer module.

Provides the Renderer: all image creation and maze/path rendering onto
the mlx window. It is composed into the App class and receives the shared
WindowContext via its constructor, reading window resources from it.
"""
from typing import Any

from maze.cell import Cell
from visualiser.widgets import fill_image
from visualiser.constants import (
    WHITE,
    GREEN,
    MAGENTA,
    CYAN,
    GRAY,
    MED_GRAY,
    YELLOW,
)
from visualiser.context import WindowContext


class Renderer:
    """Renders the maze and the solution path."""

    def __init__(self, ctx: WindowContext) -> None:
        """Initialize the renderer.

        Args:
            ctx (WindowContext): The shared window context.
        """
        self.ctx = ctx

    def _make_tile(
            self,
            color: tuple[int, int, int] | int,
            margin_x: int = 0,
            margin_y: int = 0,
    ) -> Any:
        """Create a tile image with the given color.

        Args:
            color (tuple[int, int, int] | int): The RGB color as a tuple
                or an MlxColor 0xFFRRGGBB integer.
            margin_x (int): Horizontal margin. Defaults to 0.
            margin_y (int): Vertical margin. Defaults to 0.

        Returns:
            Any: The created image pointer.
        """
        ctx = self.ctx
        img = ctx.new_image(ctx.layout.tile_width, ctx.layout.tile_height)
        fill_image(ctx.m, img, ctx.layout.tile_width, ctx.layout.tile_height,
                   color, margin_x, margin_y)
        return img

    def _make_solid_image(
            self,
            w: int,
            h: int,
            color: tuple[int, int, int] | int = MED_GRAY,
    ) -> Any:
        """Create a solid-colour image of the given size.

        Args:
            w (int): The width of the image.
            h (int): The height of the image.
            color (tuple[int, int, int] | int): The RGB fill color
                or an MlxColor 0xFFRRGGBB integer. Defaults to MED_GRAY.

        Returns:
            Any: The created image pointer.
        """
        ctx = self.ctx
        img = ctx.new_image(w, h)
        fill_image(ctx.m, img, w, h, color)
        return img

    def initialise_images(self) -> None:
        """Initialise all image resources for rendering."""
        ctx = self.ctx
        l = ctx.layout
        ctx.cell_img_ptr = self._make_tile(WHITE)
        ctx.entry_cell = self._make_tile(GREEN)
        ctx.next_cell_img_ptr = self._make_tile(MAGENTA)
        ctx.exit_cell = self._make_tile(CYAN)
        ctx.empty_cell_img = self._make_tile(
            GRAY, l.tile_width // 20, l.tile_height // 20)
        ctx.path_cell_img = self._make_tile(YELLOW)
        ctx.background_img = self._make_solid_image(
            ctx.win_width, ctx.win_height, WHITE)
        ctx.maze_background_img = self._make_solid_image(l.maze_w, l.maze_h)
        ctx.menu_background_img = self._make_solid_image(l.menu_w, l.menu_h)

    def _render_walls(self, cell: Cell, rx: int, ry: int) -> None:
        """Render the walls of a cell onto the window.

        Args:
            cell (Cell): The cell whose walls to render.
            rx (int): The rendered x position.
            ry (int): The rendered y position.
        """
        ctx = self.ctx
        l = ctx.layout
        walls = [
            (cell.walls.east,  rx + 1, ry),
            (cell.walls.south, rx,     ry + 1),
            (cell.walls.north, rx,     ry - 1),
            (cell.walls.west,  rx - 1, ry),
        ]
        for has_wall, tx, ty in walls:
            if has_wall:
                continue
            ctx.put_img(
                ctx.cell_img_ptr,
                l.offset_x + tx * l.tile_width,
                l.offset_y + ty * l.tile_height)

    def _render_entry_exit(self, cell: Cell, px: int, py: int) -> None:
        """Render the entry and exit markers for a cell.

        Args:
            cell (Cell): The cell to check for entry/exit.
            px (int): The pixel x position.
            py (int): The pixel y position.
        """
        ctx = self.ctx
        coord = (cell.coordinate.x, cell.coordinate.y)
        if coord == ctx.layout.entry:
            ctx.put_img(ctx.entry_cell, px, py)
        if coord == ctx.layout.exit:
            ctx.put_img(ctx.exit_cell, px, py)

    def _render_cell_state(self, cell: Cell, px: int, py: int) -> None:
        """Render the state of a cell (occupied or not).

        Args:
            cell (Cell): The cell to render.
            px (int): The pixel x position.
            py (int): The pixel y position.
        """
        ctx = self.ctx
        if cell.occupied:
            ctx.put_img(ctx.next_cell_img_ptr, px, py)
            ctx.put_img(ctx.cell_img_ptr, px, py)
            self._render_entry_exit(cell, px, py)
        else:
            ctx.put_img(ctx.next_cell_img_ptr, px, py)

    def render(self, cell: Cell, sync: bool = True) -> None:
        """Render a single cell onto the window.

        Args:
            cell (Cell): The cell to render.
            sync (bool): Whether to synchronise the display.
                Defaults to True.
        """
        ctx = self.ctx
        l = ctx.layout
        rx = 2 * cell.coordinate.x + 1
        ry = 2 * cell.coordinate.y + 1
        px = l.offset_x + rx * l.tile_width
        py = l.offset_y + ry * l.tile_height

        self._render_walls(cell, rx, ry)
        if sync:
            ctx.sync(ctx.m.SYNC_WIN_FLUSH)
        self._render_cell_state(cell, px, py)

    def render_grid(self) -> None:
        """Render the entire maze grid onto the window."""
        ctx = self.ctx
        l = ctx.layout
        for y in range(l.rend_tiles_y):
            for x in range(l.rend_tiles_x):
                ctx.put_img(
                    ctx.empty_cell_img,
                    l.offset_x + x * l.tile_width,
                    l.offset_y + y * l.tile_height)
            ctx.sync(ctx.m.SYNC_WIN_FLUSH)
        ctx.sync(ctx.m.SYNC_WIN_FLUSH)
        self._render_path()

    def _blit_path(self, cell_img: Any, bridge_img: Any,
                   draw_markers: bool = True) -> None:
        """Draw the solution path cells and the passages between them.

        Path cells sit at odd render columns/rows (2x+1). The passage
        tiles connecting consecutive path cells are drawn at the
        intermediate render position so the route appears continuous.

        Args:
            cell_img (Any): Image used for each path cell.
            bridge_img (Any): Image used for the passage tiles between
                consecutive path cells.
            draw_markers (bool): Whether to redraw the entry/exit
                markers on top of each cell. Defaults to True.
        """
        ctx = self.ctx
        l = ctx.layout
        prev_coord: tuple[int, int] | None = None
        for cell in ctx.solution_path:
            rx = 2 * cell.coordinate.x + 1
            ry = 2 * cell.coordinate.y + 1
            px = l.offset_x + rx * l.tile_width
            py = l.offset_y + ry * l.tile_height
            ctx.put_img(cell_img, px, py)
            if draw_markers:
                self._render_entry_exit(cell, px, py)
            if prev_coord is not None:
                bx = (prev_coord[0] + px) // 2
                by = (prev_coord[1] + py) // 2
                ctx.put_img(bridge_img, bx, by)
            prev_coord = (px, py)

    def _render_path(self) -> None:
        """Render the solution path onto the window."""
        ctx = self.ctx
        if ctx.show_path:
            self._blit_path(ctx.path_cell_img, ctx.path_cell_img)
            ctx.sync(ctx.m.SYNC_WIN_FLUSH)
