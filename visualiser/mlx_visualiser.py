
# from mlx import Mlx
from mlx import Mlx
import ctypes
from typing import Any


def rgb(r: int, g: int, b: int) -> int:
    """Return 32-bit RGBA color as C int: 0xRRGGBB00 (alpha=0)."""
    return (r << 24) | (g << 16) | (b << 8) | 0


CYAN = rgb(0, 255, 255)


class Window:
    """
    This class is intended to organise the whole process of intialising,
    hooks and loop in one place. This help with scaling later on.
    """
    def __init__(self) -> None:
        self.m = Mlx()
        self.mlx_ptr = self.m.mlx_init()
        self.win_ptr = self.m.mlx_new_window(self.mlx_ptr, 1200, 1600,
                                             "a_maze_ing")
        self.m.mlx_clear_window(self.mlx_ptr, self.win_ptr)
        self.m.mlx_string_put(self.mlx_ptr, self.win_ptr,
                              ctypes.c_uint(int(20/2)), 20, 255, "A-Maze-ing")
        self.m.mlx_string_put(self.mlx_ptr, self.win_ptr, 100,
                              100, ctypes.c_uint(CYAN), "F10: Quit")
        (ret, w, h) = self.m.mlx_get_screen_size(self.mlx_ptr)
        print(f"Got screen size: {w} x {h} .")

    def img(self, dummy) -> None:
        (img, w, h) = self.m.mlx_png_file_to_image(self.mlx_ptr,
                                                   "./stock_image.png")
        if not img:
            print("mlx_png_file_to_image failed")
            return
        self.m.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr, img, 0, 0)

    def maze_image(self):
        self.m.mlx_pixel_put(self.mlx_ptr, self.win_ptr, 0, 0, CYAN)
        # self.maze = self.m.mlx_new_image(self.mlx_ptr, w, h)
        # self.m.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr, self.maze, 0, 0)

    def mymouse(self, button, x, y, mystuff) -> None:
        """
        All mouse event triggers are defined here
        """
        print(f"Got mouse event! button {button} at {x},{y}.")

    def mykey(self, keynum: int, mystuff: Any) -> None:
        """
        all key events are defined here
        """
        print(f"Got key {keynum}, and got my stuff back:")
        print(mystuff)
        if keynum == 32:
            self.m.mlx_mouse_hook(self.win_ptr, None, "hello")
        if keynum == 65479:
            self.gere_close(None)

    def gere_close(self, dummy) -> None:
        """
        dummy param is aplcaeholder to statify the scalback singature
        to be used in mlx_hook()
        """
        self.m.mlx_loop_exit(self.mlx_ptr)

    def run(self) -> None:
        stuff = [4, 7]
        self.img(None)
        # self.maze_image()
        self.m.mlx_key_hook(self.win_ptr, self.mykey, stuff)
        self.m.mlx_mouse_hook(self.win_ptr, self.mymouse, None)
        self.m.mlx_hook(self.win_ptr, 33, 0, self.gere_close, None)
        self.m.mlx_loop(self.mlx_ptr)


if __name__ == "__main__":
    window = Window()
    window.run()
