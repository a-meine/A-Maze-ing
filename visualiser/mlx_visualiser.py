from mlx import Mlx
from maze.cell import Cell
from ctypes import c_uint
from typing import Any
import time


def rgb(r: int, g: int, b: int) -> int:
    return (r << 16) | (g << 8) | b


CYAN = rgb(214, 233, 160)
TILE_SIZE = 10


class Window:
    """
    This class is intended to organise the whole process of intialising,
    hooks and loop in one place. This help with scaling later on.
    """
    def __init__(self, win_width=800, win_height=600) -> None:
        self.win_width = 1600
        self.win_height = 1200
        self.m = Mlx()
        self.mlx_ptr = self.m.mlx_init()
        self.win_ptr = self.m.mlx_new_window(self.mlx_ptr,
                                             self.win_width,
                                             self.win_height,
                                             "a_maze_ing")
        self.m.mlx_clear_window(self.mlx_ptr, self.win_ptr)
        self.m.mlx_string_put(self.mlx_ptr, self.win_ptr,
                              c_uint(20//2), 20, 255, "A-Maze-ing")
        self.m.mlx_string_put(self.mlx_ptr, self.win_ptr, 100,
                              100, c_uint(CYAN), "F10: Quit")
        (ret, w, h) = self.m.mlx_get_screen_size(self.mlx_ptr)
        print(f"Got screen size: {w} x {h} .")

    def stock_image(self, dummy) -> None:
        (img, w, h) = self.m.mlx_png_file_to_image(self.mlx_ptr,
                                                   "./stock_image.png")
        if not img:
            print("mlx_png_file_to_image failed")
            return
        self.m.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr, img, 0, 0)

    def render_cell(self, offset_x: int, offset_y: int, cell: Cell):
        rx = 2 * cell.coordinate.x + 1
        ry = 2 * cell.coordinate.y + 1
        px = offset_x + rx * self.tile_width
        py = offset_y + ry * self.tile_height
        self.m.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, self.cell_img_ptr, px, py
        )
        if cell.walls.east:
            self.m.mlx_put_image_to_window(
                self.mlx_ptr, self.win_ptr, self.v_wall_img_ptr,
                offset_x + (rx + 1) * self.tile_width,
                offset_y + ry * self.tile_height
            )
        # south wall
        if cell.walls.south:
            self.m.mlx_put_image_to_window(
                self.mlx_ptr, self.win_ptr, self.h_wall_img_ptr,
                offset_x + rx * self.tile_width,
                offset_y + (ry + 1) * self.tile_height
            )
            self.m.mlx_sync(self.mlx_ptr, self.m.SYNC_WIN_COMPLETED,
                            self.win_ptr)
            time.sleep(1/15)

    def maze_image(self):
        from maze.algorithms.dfs import DFS

        width = 10
        height = 10
        mt_grid = DFS(width, height)

        rend_tiles_x = 2 * mt_grid.width + 1
        rend_tiles_y = 2 * mt_grid.height + 1
        
        maze_x = self.win_width // 10
        maze_y = self.win_height // 10
        maze_w = self.win_width - 2 * maze_x
        maze_h = self.win_height - 2 * maze_y

        self.tile_width = maze_w // rend_tiles_x
        self.tile_height = maze_h // rend_tiles_y

        grid_px_w = rend_tiles_x * self.tile_width
        grid_px_h = rend_tiles_y * self.tile_height

        offset_x = maze_x + (maze_w - grid_px_w) // 2
        offset_y = maze_y + (maze_h - grid_px_h) // 2

        self.draw_h_wall()
        self.draw_v_wall()
        self.draw_a_cell()
        self.draw_border(rend_tiles_x, rend_tiles_y)

        # draw background
        self.draw_backgroud()
        self.draw_maze_backgroud(maze_x, maze_y, maze_w, maze_h)
        self.m.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr,
                                       self.background_img, 0, 0)
        self.m.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr,
                                       self.maze_background_img, 0, 0)
        self.m.mlx_sync(self.mlx_ptr, self.m.SYNC_WIN_COMPLETED, self.win_ptr)

        mt_grid.generate_maze(
            lambda cell: self.render_cell(offset_x, offset_y, cell))
        mt_grid._grid.show()

    def draw_backgroud(self):
        self.background_img = self.m.mlx_new_image(self.mlx_ptr,
                                                   self.win_width,
                                                   self.win_height)
        data, bpp, size_line, endian = self.m.mlx_get_data_addr(
                                        self.background_img)

        for y in range(self.win_height):
            for x in range(self.win_width):
                index = y * size_line + x * (bpp // 8)
                data[index + 0] = 240
                data[index + 1] = 165
                data[index + 2] = 27
                data[index + 3] = 255

    def draw_maze_backgroud(self, maze_x, maze_y, maze_w, maze_h):
        self.maze_background_img = self.m.mlx_new_image(
            self.mlx_ptr, self.win_width, self.win_height)
        data, bpp, size_line, endian = self.m.mlx_get_data_addr(
            self.maze_background_img)
        for y in range(maze_y, maze_y + maze_h):
            for x in range(maze_x, maze_x + maze_w):
                index = y * size_line + x * (bpp // 8)
                data[index + 0] = 255
                data[index + 1] = 255
                data[index + 2] = 255
                data[index + 3] = 255

    def draw_border(self, rend_tiles_x, rend_tiles_y):
        self.border_cell = self.m.mlx_new_image(self.mlx_ptr, self.win_width,
                                                self.win_height)
        data, bpp, size_line, endian = self.m.mlx_get_data_addr(
                                        self.border_cell)
        # topy
        py = 0
        for w in range(0, rend_tiles_x):
            px = w * self.tile_width
            for y in range(self.tile_height):
                for x in range(self.tile_width):
                    index = (py + y) * size_line + (px + x) * (bpp // 8)
                    data[index + 0] = 0
                    data[index + 1] = 255
                    data[index + 2] = 0
                    data[index + 3] = 255

        # left
        px = 0
        for h in range(0, rend_tiles_y):
            py = h * self.tile_height
            for y in range(self.tile_height):
                for x in range(self.tile_width):
                    index = (py + y) * size_line + (px + x) * (bpp // 8)
                    data[index + 0] = 0
                    data[index + 1] = 255
                    data[index + 2] = 0
                    data[index + 3] = 255

        # # right
        px = (rend_tiles_x - 1) * self.tile_width
        for h in range(0, rend_tiles_y):
            py = h * self.tile_height
            for y in range(self.tile_height):
                for x in range(self.tile_width):
                    index = (py + y) * size_line + (px + x) * (bpp // 8)
                    data[index + 0] = 0
                    data[index + 1] = 255
                    data[index + 2] = 0
                    data[index + 3] = 255

        # # bottom
        py = (rend_tiles_y - 1) * self.tile_height
        for h in range(0, rend_tiles_y):
            px = h * self.tile_width
            for y in range(self.tile_height):
                for x in range(self.tile_width):
                    index = (py + y) * size_line + (px + x) * (bpp // 8)
                    data[index + 0] = 0
                    data[index + 1] = 255
                    data[index + 2] = 0
                    data[index + 3] = 255

    def draw_a_cell(self):
        self.cell_img_ptr = self.m.mlx_new_image(self.mlx_ptr, self.tile_width,
                                                 self.tile_height)
        data, bpp, size_line, endian = self.m.mlx_get_data_addr(
                                                self.cell_img_ptr)
        # this is to control the margin, now it is 0
        margin_y = self.tile_height // 1000
        # same s above
        margin_x = self.tile_width // 1000
        for y in range(margin_y, self.tile_height - margin_y):
            for x in range(margin_x, self.tile_width - margin_x):
                index = y * size_line + x * (bpp // 8)
                data[index + 0] = 176
                data[index + 1] = 60
                data[index + 2] = 132
                data[index + 3] = 255

    def draw_v_wall(self):
        self.v_wall_img_ptr = self.m.mlx_new_image(
            self.mlx_ptr, self.tile_width, self.tile_height)
        data, bpp, size_line, endian = self.m.mlx_get_data_addr(
                                        self.v_wall_img_ptr)

        thickness = max(1, self.tile_width // 1)
        for y in range(self.tile_height):
            for x in range(thickness):
                index = y * size_line + x * (bpp // 8)
                data[index + 0] = 0
                data[index + 1] = 0
                data[index + 2] = 0
                data[index + 3] = 255

    def draw_h_wall(self):
        self.h_wall_img_ptr = self.m.mlx_new_image(
            self.mlx_ptr, self.tile_width, self.tile_height)
        data, bpp, size_line, endian = self.m.mlx_get_data_addr(
                                        self.h_wall_img_ptr)

        thickness = max(1, self.tile_height // 1)
        for y in range(thickness):
            for x in range(self.tile_width):
                index = y * size_line + x * (bpp // 8)
                data[index + 0] = 0
                data[index + 1] = 0
                data[index + 2] = 0
                data[index + 3] = 255

    def mymouse(self, button, x, y, mystuff) -> None:
        """
        All mouse event triggers are defined here
        """
        print(f"Got mouse event! button {button} at {x},{y}.")

    def mykey(self, keynum: int, mystuff: Any) -> None:
        """
        all key events are defined here
        """
        if keynum == 65307:
            print("quiting..")
            self.gere_close(None)
            return
        print(f"Got key {keynum}, and got my stuff back:")
        print(mystuff)
        if keynum == 32:
            self.m.mlx_mouse_hook(self.win_ptr, None, "hello")

    def gere_close(self, dummy) -> None:
        """
        dummy param is aplcaeholder to statify the scalback singature
        to be used in mlx_hook()
        """
        self.m.mlx_loop_exit(self.mlx_ptr)

    def run(self) -> None:
        stuff = [4, 7]
        # self.stock_image(None)
        self.maze_image()
        self.m.mlx_key_hook(self.win_ptr, self.mykey, stuff)
        self.m.mlx_mouse_hook(self.win_ptr, self.mymouse, None)
        self.m.mlx_hook(self.win_ptr, 33, 0, self.gere_close, None)
        self.m.mlx_loop(self.mlx_ptr)


if __name__ == "__main__":
    window = Window()
    window.run()
