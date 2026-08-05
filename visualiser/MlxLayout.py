"""visualiser.MlxLayout module.

Provides the MlxLayout class: an offscreen image buffer with direct
pixel access, used as a render target for UI widgets and frames.
"""
from typing import Any

from visualiser.MlxColor import MlxColor
from visualiser.TextBlock import TextBlock


class MlxLayout:
    """Represents a rectangular offscreen rendering surface.

    Wraps an mlx image buffer, providing direct pixel access and
    deferred text rendering. The layout is blitted to the window via
    render() and only repainted when marked dirty.

    Attributes:
        mlx (Any): The Mlx instance.
        mlx_ptr (Any): The mlx pointer.
        win_ptr (Any): The window pointer.
        width (int): The width of the layout in pixels.
        height (int): The height of the layout in pixels.
        x (int): The x position of the layout in the window.
        y (int): The y position of the layout in the window.
        image_ptr (Any): The underlying mlx image pointer.
        pixels (Any): The pixel buffer as returned by mlx_get_data_addr.
        bytes_per_pixel (int): The number of bytes per pixel.
        size_line (int): The number of bytes per image row.
        text_blocks (list[TextBlock]): Text drawn on top of the image.
        is_rendered (bool): Whether the layout is up to date.
    """

    def __init__(
            self,
            mlx: Any,
            mlx_ptr: Any,
            win_ptr: Any,
            width: int,
            height: int,
            x: int = 0,
            y: int = 0,
    ) -> None:
        """Initialize an offscreen image buffer for the given size.

        Args:
            mlx (Any): The Mlx instance.
            mlx_ptr (Any): The mlx pointer.
            win_ptr (Any): The window pointer.
            width (int): The width of the layout in pixels.
            height (int): The height of the layout in pixels.
            x (int): The x position of the layout in the window.
                Defaults to 0.
            y (int): The y position of the layout in the window.
                Defaults to 0.
        """
        self.mlx = mlx
        self.mlx_ptr = mlx_ptr
        self.win_ptr = win_ptr
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.image_ptr = self.mlx.mlx_new_image(self.mlx_ptr, width, height)
        if not self.image_ptr:
            raise RuntimeError("mlx_new_image failed")
        data, bpp, size_line, _format = self.mlx.mlx_get_data_addr(
            self.image_ptr)
        self.pixels = data
        self.bytes_per_pixel = bpp // 8
        self.size_line = size_line
        self.text_blocks: list[TextBlock] = []
        self.is_rendered = False

    @staticmethod
    def _to_rgb(color: tuple[int, int, int] | int) -> tuple[int, int, int]:
        """Convert an MlxColor or RGB tuple into an RGB tuple.

        Args:
            color (tuple[int, int, int] | int): The color as an MlxColor
                0xFFRRGGBB integer or an (r, g, b) tuple.

        Returns:
            tuple[int, int, int]: The (r, g, b) tuple.
        """
        if isinstance(color, int):
            return MlxColor.to_rgb(color)
        return color

    def set_pixel(
            self, x: int, y: int, color: tuple[int, int, int] | int) -> None:
        """Set a single pixel to the given color.

        Args:
            x (int): The x position of the pixel.
            y (int): The y position of the pixel.
            color (tuple[int, int, int] | int): The color as an MlxColor
                0xFFRRGGBB integer or an (r, g, b) tuple.
        """
        r, g, b = self._to_rgb(color)
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return
        offset = y * self.size_line + x * self.bytes_per_pixel
        self.pixels[offset + 0] = b
        self.pixels[offset + 1] = g
        self.pixels[offset + 2] = r
        self.pixels[offset + 3] = 255
        self.is_rendered = False

    def fill_rect(
            self,
            x: int,
            y: int,
            w: int,
            h: int,
            color: tuple[int, int, int] | int) -> None:
        """Fill a rectangle with the given color.

        Args:
            x (int): The x position of the rectangle.
            y (int): The y position of the rectangle.
            w (int): The width of the rectangle.
            h (int): The height of the rectangle.
            color (tuple[int, int, int] | int): The color as an MlxColor
                0xFFRRGGBB integer or an (r, g, b) tuple.
        """
        r, g, b = self._to_rgb(color)
        x = max(0, min(x, self.width - 1))
        y = max(0, min(y, self.height - 1))
        w = max(0, min(w, self.width - x))
        h = max(0, min(h, self.height - y))
        for py in range(y, y + h):
            offset = py * self.size_line + x * self.bytes_per_pixel
            for px in range(w):
                index = offset + px * self.bytes_per_pixel
                self.pixels[index + 0] = b
                self.pixels[index + 1] = g
                self.pixels[index + 2] = r
                self.pixels[index + 3] = 255
        self.is_rendered = False

    def fill_border(
            self,
            thickness: int,
            color: tuple[int, int, int] | int) -> None:
        """Fill the outer border of the layout with the given color.

        Args:
            thickness (int): The thickness of the border in pixels.
            color (tuple[int, int, int] | int): The color as an MlxColor
                0xFFRRGGBB integer or an (r, g, b) tuple.
        """
        for y in range(thickness):
            self.fill_rect(0, y, self.width, thickness, color)
        for y in range(thickness, self.height - thickness):
            self.fill_rect(0, y, thickness, 1, color)
            self.fill_rect(self.width - thickness, y, thickness, 1, color)
        for y in range(self.height - thickness, self.height):
            self.fill_rect(0, y, self.width, thickness, color)

    def add_text(self, text_block: TextBlock) -> None:
        """Queue a TextBlock to be drawn on top of the layout.

        Args:
            text_block (TextBlock): The text block to draw.
        """
        self.text_blocks.append(text_block)
        self.is_rendered = False

    def clear_text(self) -> None:
        """Remove all queued TextBlocks from the layout."""
        self.text_blocks = []

    def move_to(self, x: int, y: int) -> None:
        """Move the layout to a new position in the window.

        Args:
            x (int): The new x position.
            y (int): The new y position.
        """
        self.x = x
        self.y = y
        self.is_rendered = False

    def render(self) -> None:
        """Blit the layout image and its text blocks onto the window."""
        self.is_rendered = True
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, self.image_ptr, self.x, self.y)
        for text_block in self.text_blocks:
            self.mlx.mlx_string_put(
                self.mlx_ptr, self.win_ptr,
                text_block.x + self.x, text_block.y + self.y,
                text_block.color, text_block.text)

    def destroy(self) -> None:
        """Free the underlying mlx image."""
        if not self.image_ptr:
            return
        self.mlx.mlx_destroy_image(self.mlx_ptr, self.image_ptr)
        self.image_ptr = None