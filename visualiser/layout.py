"""visualiser.layout module."""
from dataclasses import dataclass
from typing import Any

from config.parser import Config


@dataclass
class Layout:
    """Represents the computed layout for rendering the maze and UI.

    Attributes:
        grid_width (int): The grid width in cells.
        grid_height (int): The grid height in cells.
        entry (tuple[int, int]): The entry point coordinates.
        exit (tuple[int, int]): The exit point coordinates.
        rend_tiles_x (int): The render tile count in x.
        rend_tiles_y (int): The render tile count in y.
        offset_x (int): The x offset for rendering.
        offset_y (int): The y offset for rendering.
        tile_width (int): The width of each tile in pixels.
        tile_height (int): The height of each tile in pixels.
        maze_w (int): The maze width in pixels.
        maze_h (int): The maze height in pixels.
        maze_offset_x (int): The x offset of the maze.
        maze_offset_y (int): The y offset of the maze.
        relative_x_offset (int): The relative x offset for layout.
        menu_x (int): The x position of the menu.
        menu_y (int): The y position of the menu.
        menu_w (int): The width of the menu.
        menu_h (int): The height of the menu.
    """

    grid_width: int
    grid_height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    rend_tiles_x: int
    rend_tiles_y: int
    offset_x: int
    offset_y: int
    tile_width: int
    tile_height: int
    maze_w: int
    maze_h: int
    maze_offset_x: int
    maze_offset_y: int
    relative_x_offset: int
    menu_x: int
    menu_y: int
    menu_w: int
    menu_h: int

    @classmethod
    def compute(
            cls,
            fields: list[Any],
            config: Config,
            win_width: int,
            win_height: int,
    ) -> "Layout":
        """Compute the layout based on UI fields and window dimensions.

        Calculates all positioning and sizing parameters for
        rendering the maze grid and menu within the window.

        Args:
            cls: The Layout class.
            fields (list[Any]): The list of input fields.
            config (Config): The application configuration.
            win_width (int): The window width in pixels.
            win_height (int): The window height in pixels.

        Returns:
            Layout: A new Layout instance with computed values.
        """
        grid_width = int(fields[0].text or config.width)
        grid_height = int(fields[1].text or config.height)
        entry = (int(fields[2].text), int(fields[3].text))
        exit_pt = (int(fields[4].text), int(fields[5].text))

        rend_tiles_x = 2 * grid_width + 1
        rend_tiles_y = 2 * grid_height + 1

        relative_x_offset = int(win_width * 0.28)

        maze_offset_x = 9
        maze_offset_y = int(win_height * 0.005)

        # maze_w = int(win_width * 0.8) - 2 * maze_offset_x
        maze_w = win_width - 2 * maze_offset_x - relative_x_offset
        maze_h = win_height - 2 * maze_offset_y

        tile_width = maze_w // rend_tiles_x
        tile_height = maze_h // rend_tiles_y

        grid_px_w = rend_tiles_x * tile_width
        grid_px_h = rend_tiles_y * tile_height

        offset_x = maze_offset_x + relative_x_offset + (maze_w - grid_px_w) // 2
        offset_y = maze_offset_y + (maze_h - grid_px_h) // 2

        # offset_x = (maze_offset_x + tile_width
        #             + (maze_w - tile_width * 2 - grid_px_w) // 2
        #             + relative_x_offset)
        # offset_y = (maze_offset_y + tile_height
        #             + (maze_h - tile_height * 2 - grid_px_h) // 2)

        menu_w = int(win_width * 0.28)
        menu_w = win_width - maze_w - 40
        menu_h = maze_h
        menu_x = int(maze_offset_x / 2)
        menu_y = maze_offset_y

        return cls(
            grid_width=grid_width,
            grid_height=grid_height,
            entry=entry,
            exit=exit_pt,
            rend_tiles_x=rend_tiles_x,
            rend_tiles_y=rend_tiles_y,
            offset_x=offset_x,
            offset_y=offset_y,
            tile_width=tile_width,
            tile_height=tile_height,
            maze_w=maze_w,
            maze_h=maze_h,
            maze_offset_x=maze_offset_x,
            maze_offset_y=maze_offset_y,
            relative_x_offset=relative_x_offset,
            menu_x=menu_x,
            menu_y=menu_y,
            menu_w=menu_w,
            menu_h=menu_h,
        )