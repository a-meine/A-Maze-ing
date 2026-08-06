"""visualiser.refactored.renderer module.

Provides the Renderer: maze and path rendering onto the mlx window.
The whole maze is composited into a single canvas image and presented
with exactly one draw call, avoiding the per-tile edge fringes and the
>64-draw Vulkan flush storm that the earlier per-image approach caused.

It is composed into the App class and receives the shared WindowContext
via its constructor, reading window resources from it.
"""
from typing import Any

from maze.cell import Cell
from maze.coordinate import Coordinate
from visualiser.widgets import fill_image
from visualiser.MlxColor import MlxColor
from visualiser.constants import (
    WHITE,
    GREEN,
    CYAN,
    GRAY,
    MED_GRAY,
    YELLOW,
)
from visualiser.context import WindowContext


class Renderer:
    """Renders the maze and the solution path onto a single canvas."""

    def __init__(self, ctx: WindowContext) -> None:
        """Initialize the renderer with the shared window context.

        Args:
            ctx (WindowContext): The shared window context.
        """
        self.ctx = ctx

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
        ctx.background_img = self._make_solid_image(
            ctx.win_width, ctx.win_height, WHITE)
        ctx.maze_background_img = self._make_solid_image(l.maze_w, l.maze_h)
        ctx.menu_canvas_img = self._new_menu_canvas()
        ctx.maze_canvas_img = self._new_maze_canvas()

    def _new_menu_canvas(self) -> Any:
        """Create the single canvas covering the menu panel region."""
        ctx = self.ctx
        l = ctx.layout
        img = ctx.new_image(l.menu_w, l.menu_h)
        fill_image(ctx.m, img, l.menu_w, l.menu_h, MED_GRAY)
        return img

    def _new_maze_canvas(self) -> Any:
        """Create the single canvas covering the whole tile region.

        Base fill is the wall colour so the border and any untouched
        tile show as walls.
        """
        ctx = self.ctx
        l = ctx.layout
        w = l.rend_tiles_x * l.tile_width
        h = l.rend_tiles_y * l.tile_height
        img = ctx.new_image(w, h)
        fill_image(ctx.m, img, w, h, MED_GRAY)
        return img

    @staticmethod
    def _to_rgb(color: tuple[int, int, int] | int) -> tuple[int, int, int]:
        """Normalise a colour (int MlxColor or RGB tuple) to RGB."""
        if isinstance(color, int):
            return MlxColor.to_rgb(color)
        return color

    def _paint_tile(
            self,
            data: Any,
            bpp: int,
            size_line: int,
            tx: int,
            ty: int,
            color: tuple[int, int, int] | int,
    ) -> None:
        """Paint the interior of tile (tx, ty) on the canvas buffer.

        The margin is left untouched so the MED_GRAY base shows through
        as the dividing walls, matching the old empty-cell look without
        creating per-tile edge fringes.
        """
        l = self.ctx.layout
        r, g, b = self._to_rgb(color)
        margin_x = l.tile_width // 2000
        margin_y = l.tile_height // 2000
        ox = tx * l.tile_width + margin_x
        oy = ty * l.tile_height + margin_y
        w = l.tile_width - 2 * margin_x
        h = l.tile_height - 2 * margin_y
        bpp8 = bpp // 8
        for yy in range(oy, oy + h):
            row = yy * size_line
            for xx in range(ox, ox + w):
                i = row + xx * bpp8
                data[i + 0] = b
                data[i + 1] = g
                data[i + 2] = r
                data[i + 3] = 255

    def _paint_cell(
            self,
            data: Any,
            bpp: int,
            size_line: int,
            coord: Coordinate,
            color: tuple[int, int, int] | int,
    ) -> None:
        """Paint the cell tile at (2*x+1, 2*y+1)."""
        self._paint_tile(data, bpp, size_line, 2 * coord.x + 1, 2 * coord.y + 1,
                         color)

    def _tile_color(self, tx: int, ty: int) -> tuple[int, int, int]:
        """Return the base colour for the render tile (tx, ty).

        Both-odd tiles are cell interiors (GRAY if a wall); a tile on a
        horizontal/vertical wall line is WHITE when the wall there is open.
        """
        l = self.ctx.layout
        grid = self.ctx.grid.grid
        if tx % 2 == 1 and ty % 2 == 1:
            cell = grid[ty // 2][tx // 2]
            return self._to_rgb(WHITE if not cell.is_wall else GRAY)
        if tx % 2 == 1:
            cy = ty // 2
            if cy <= 0 or cy >= l.grid_height:
                return self._to_rgb(GRAY)
            cell = grid[cy][tx // 2]
            return self._to_rgb(WHITE if not cell.walls.north else GRAY)
        if ty % 2 == 1:
            cx = tx // 2
            if cx <= 0 or cx >= l.grid_width:
                return self._to_rgb(GRAY)
            cell = grid[ty // 2][cx]
            return self._to_rgb(WHITE if not cell.walls.west else GRAY)
        return self._to_rgb(GRAY)

    def _paint_pattern(self, data: Any, bpp: int, size_line: int) -> None:
        """Overlay the '42' wall-pattern tiles with the current colour."""
        for cell in self.ctx.grid.grid.pattern_cells():
            self._paint_cell(data, bpp, size_line, cell.coordinate,
                             self.ctx.pattern_color)

    def _paint_path(self, data: Any, bpp: int, size_line: int) -> None:
        """Overlay the solution path cells and the passages between them."""
        if not self.ctx.show_path:
            return
        prev_tx: int | None = None
        prev_ty: int | None = None
        for cell in self.ctx.solution_path:
            tx = 2 * cell.coordinate.x + 1
            ty = 2 * cell.coordinate.y + 1
            if prev_tx is not None and prev_ty is not None:
                self._paint_tile(data, bpp, size_line,
                                 (prev_tx + tx) // 2, (prev_ty + ty) // 2,
                                 YELLOW)
            self._paint_tile(data, bpp, size_line, tx, ty, YELLOW)
            prev_tx, prev_ty = tx, ty

    def render_maze(self) -> None:
        """Compose the full maze into the canvas and present it once.

        Paints base tiles from grid state, then the '42' pattern colour,
        then the solution path and entry/exit markers, and finally presents
        the single canvas image.
        """
        ctx = self.ctx
        l = ctx.layout
        data, bpp, size_line, _ = \
            ctx.m.mlx_get_data_addr(ctx.maze_canvas_img)
        for ty in range(l.rend_tiles_y):
            for tx in range(l.rend_tiles_x):
                self._paint_tile(data, bpp, size_line, tx, ty,
                                 self._tile_color(tx, ty))
        grid = ctx.grid.grid
        self._paint_pattern(data, bpp, size_line)
        self._paint_path(data, bpp, size_line)
        self._paint_cell(data, bpp, size_line, grid.start.coordinate, GREEN)
        self._paint_cell(data, bpp, size_line, grid.end.coordinate, CYAN)
        ctx.present_scene()

    def render(self, cell: Cell, sync: bool = True) -> None:
        """Stream one generation step into the canvas and present once.

        Args:
            cell (Cell): The cell processed by the maze generator.
            sync (bool): Whether to synchronise the display. Defaults True.
        """
        ctx = self.ctx
        tx = 2 * cell.coordinate.x + 1
        ty = 2 * cell.coordinate.y + 1
        data, bpp, size_line, _ = \
            ctx.m.mlx_get_data_addr(ctx.maze_canvas_img)
        for has_wall, ntx, nty in [
                (cell.walls.east,  tx + 1, ty),
                (cell.walls.south, tx,     ty + 1),
                (cell.walls.north, tx,     ty - 1),
                (cell.walls.west,  tx - 1, ty),
        ]:
            self._paint_tile(data, bpp, size_line, ntx, nty,
                             GRAY if has_wall else WHITE)
        self._paint_tile(data, bpp, size_line, tx, ty, WHITE)
        ctx.present_scene()
