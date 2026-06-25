from mlx import Mlx
# from ctypes import c_uint
# from typing import Any
import time
from visualiser.buttons import Button
from visualiser.input_fields import InputField
from maze.algorithms.dfs import DFS
# import asyncio
from maze.config_parser import Config



def rgb(r: int, g: int, b: int) -> int:
    return (r << 16) | (g << 8) | b


CYAN = rgb(214, 233, 160)
TILE_SIZE = 10

# TODO: organise the draw() initia;ise()

class Window:
    """
    This class is intended to organise the whole process of intialising,
    hooks and loop in one place. This help with scaling later on.
    """
    def __init__(self, config: Config) -> None:
        """"""
        self.win_width = 1800
        self.win_height = 1200
        self.conifg = config
        self.m = Mlx()
        self.mlx_ptr = self.m.mlx_init()
        self.win_ptr = self.m.mlx_new_window(self.mlx_ptr,
                                             self.win_width,
                                             self.win_height,
                                             "a_maze_ing")
        self.m.mlx_clear_window(self.mlx_ptr, self.win_ptr)

        (ret, w, h) = self.m.mlx_get_screen_size(self.mlx_ptr)
        # print(f"Got screen size: {w} x {h} .")

        self.entry_ = self.conifg.entry
        self.exit_ = self.conifg.exit_
        self.menu()

    def conifg_images(self):

        self.grid_width = int(self.fields[0].text or self.conifg.width)
        self.grid_height = int(self.fields[1].text or self.conifg.height)

        self.entry_ = (int(self.fields[2].text), int(self.fields[3].text))
        self.exit_ = (int(self.fields[4].text), int(self.fields[5].text))

        self.mt_grid = DFS(self.grid_width, self.grid_height)

        maze_width_fscale = 0.8
        self.ralative_x_offset = int(self.win_width * 0.28)

        self.rend_tiles_x = 2 * self.mt_grid.width + 1
        self.rend_tiles_y = 2 * self.mt_grid.height + 1

        offset_factor = 0.1
        self.maze_offset_x = int(self.win_width * (offset_factor))
        self.maze_offset_y = int(self.win_height * (offset_factor))

        self.maze_w = int(self.win_width * maze_width_fscale
                          ) - 2 * self.maze_offset_x
        self.maze_h = self.win_height - 2 * self.maze_offset_y

        self.tile_width = self.maze_w // self.rend_tiles_x
        self.tile_height = self.maze_h // self.rend_tiles_y

        self.grid_px_w = self.rend_tiles_x * self.tile_width
        self.grid_px_h = self.rend_tiles_y * self.tile_height

        self.offset_x = self.maze_offset_x + self.tile_width + (
                self.maze_w - self.tile_width * 2 - self.grid_px_w
                ) // 2 + self.ralative_x_offset
        self.offset_y = self.maze_offset_y + self.tile_height + (
                    self.maze_h - self.tile_height * 2 - self.grid_px_h) // 2

        self.menu_offset_x = int(self.tile_width * 3)
        self.menu_offset_y = int(self.tile_width * 3)
        self.menu_x = int(self.maze_offset_x / 2)
        # menu_y
        self.menu_w = int(self.win_width * 0.3)
        # menu_h = int(self.win_height * 0.15)
        self.menu_h = self.maze_h

    def test(self):
        pass
    def image_manger(self):
        self.conifg_images()
        self.intialise_images()
        self.redraw_menu()

    def regen(self):
        self.image_manger()
        self.run_and_render_maze()

    def intialise_images(self):
        self.draw_a_cell()
        self.draw_entry()
        self.draw_exit()
        self.draw_border(int(self.win_width / self.tile_width),
                         int(self.win_height / self.tile_height))
        self.draw_backgroud()
        self.draw_maze_backgroud(self.maze_offset_x + self.ralative_x_offset,
                                 self.maze_offset_y,
                                 self.maze_w,
                                 self.maze_h)
        self.draw_menu_background(
            self.menu_w, self.menu_h, self.menu_offset_x, self.menu_offset_y)

    def run_and_render_maze(self):
        """"""
        self.image_manger()
        for cell in self.mt_grid.generate_maze():
            rx = 2 * cell.coordinate.x + 1
            ry = 2 * cell.coordinate.y + 1

            px = self.offset_x + rx * self.tile_width
            py = self.offset_y + ry * self.tile_height

            self.m.mlx_put_image_to_window(
                self.mlx_ptr, self.win_ptr, self.cell_img_ptr, px, py
            )
            if (cell.coordinate.x, cell.coordinate.y) == self.entry_:
                self.m.mlx_put_image_to_window(
                    self.mlx_ptr, self.win_ptr, self.entry_cell, px, py
                    )

            if (cell.coordinate.x, cell.coordinate.y) == self.exit_:
                self.m.mlx_put_image_to_window(
                    self.mlx_ptr, self.win_ptr, self.exit_cell, px, py
                    )

            # east
            if not cell.walls.east:
                self.m.mlx_put_image_to_window(
                    self.mlx_ptr, self.win_ptr, self.cell_img_ptr,
                    self.offset_x + (rx + 1) * self.tile_width,
                    self.offset_y + ry * self.tile_height
                )

            # south
            if not cell.walls.south:
                self.m.mlx_put_image_to_window(
                    self.mlx_ptr, self.win_ptr, self.cell_img_ptr,
                    self.offset_x + rx * self.tile_width,
                    self.offset_y + (ry + 1) * self.tile_height
                )

            # north
            if not cell.walls.north:
                self.m.mlx_put_image_to_window(
                    self.mlx_ptr, self.win_ptr, self.cell_img_ptr,
                    self.offset_x + rx * self.tile_width,
                    self.offset_y + (ry - 1) * self.tile_height
                )

            # west
            if not cell.walls.west:
                self.m.mlx_put_image_to_window(
                    self.mlx_ptr, self.win_ptr, self.cell_img_ptr,
                    self.offset_x + (rx - 1) * self.tile_width,
                    self.offset_y + ry * self.tile_height
                )
            self.m.mlx_sync(self.mlx_ptr, self.m.SYNC_WIN_FLUSH,
                            self.win_ptr)
            time.sleep(1/35)
        # mt_grid._grid.show()

    def menu(self):
        # register buttons
        self.buttons = [
            Button(
                200, 200, 300, 60, "Re-Generate", (0, 255, 0), (255, 0, 0),
                action=self.regen),
            Button(
                250, 550, 150, 30, "exit", (0, 255, 0), (255, 0, 0),
                action=lambda: self.gere_close(None))
            ]

        # register input fields
        self.fields = [
            InputField(200, 300, 70, 30, "width", str(self.conifg.width)),
            InputField(450, 300, 70, 30, "height", str(self.conifg.height)),
            InputField(200, 400, 20, 20, "", str(self.conifg.entry[0])),
            InputField(223, 400, 20, 20, "", str(self.conifg.entry[1])),
            InputField(200, 450, 20, 20, "", str(self.conifg.exit_[0])),
            InputField(223, 450, 20, 20, "", str(self.conifg.exit_[1]))
        ]

    def redraw_menu(self):
        self.m.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr,
                                       self.background_img, 0, 0)
        self.m.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr,
            self.menu_background_img,
            self.menu_x,
            self.maze_offset_y)
        self.m.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr,
            self.maze_background_img,
            self.maze_offset_x + self.ralative_x_offset,
            self.maze_offset_y)
        self.m.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr,
            self.border_cell,
            5,
            0)

        self.redraw_buttons()
        self.redraw_fileds()
        self.m.mlx_sync(self.mlx_ptr, self.m.SYNC_WIN_COMPLETED, self.win_ptr)

    def redraw_buttons(self):
        for btn in self.buttons:
            self.draw_button(btn)
        self.m.mlx_sync(self.mlx_ptr, self.m.SYNC_WIN_COMPLETED, self.win_ptr)

    def redraw_fileds(self):
        for field in self.fields:
            self.draw_input_field(field)
        self.m.mlx_sync(self.mlx_ptr, self.m.SYNC_WIN_COMPLETED, self.win_ptr)

    def start_mouse_hook(self, button, x, y, mystuff):
        if button != 1:
            return

        clicked_field = False

        for field in self.fields:
            if field.contains(x, y):
                field.focused = True
                clicked_field = True
            else:
                field.focused = False

        if clicked_field:
            self.redraw_fileds()
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

        for field in self.fields:
            field.focused = False

        self.redraw_fileds()

    def start_key_hook(self, keynum, mystuff):
        if keynum == 65307:
            self.gere_close(None)
            return
        active = None
        for field in self.fields:
            if field.focused:
                active = field
                break

        if active is None:
            return

        if keynum == 65288:  # backspace on Linux/X11 often
            active.text = active.text[:-1]
            self.redraw_fileds()
        elif 48 <= keynum <= 57:  # digits 0-9
            active.text += chr(keynum)
            # add a mechanishm to limit the size of input
            self.redraw_fileds()

    def draw_menu_background(self, menu_w, menu_h, menu_x, menu_y):
        self.menu_background_img = self.m.mlx_new_image(
            self.mlx_ptr, menu_w, menu_h)
        data, bpp, size_line, endian = self.m.mlx_get_data_addr(
            self.menu_background_img)

        for y in range(menu_h):
            for x in range(menu_w):
                index = y * size_line + x * (bpp // 8)
                data[index + 0] = 128
                data[index + 1] = 128
                data[index + 2] = 128
                data[index + 3] = 255

    def draw_backgroud(self):
        self.background_img = self.m.mlx_new_image(self.mlx_ptr,
                                                   self.win_width,
                                                   self.win_height)
        data, bpp, size_line, endian = self.m.mlx_get_data_addr(
                                        self.background_img)

        for y in range(self.win_height):
            for x in range(self.win_width):
                index = y * size_line + x * (bpp // 8)
                data[index + 0] = 255
                data[index + 1] = 255
                data[index + 2] = 255
                data[index + 3] = 255

    def draw_maze_backgroud(self, maze_x, maze_y, maze_w, maze_h):
        self.maze_background_img = self.m.mlx_new_image(
            self.mlx_ptr, maze_w, maze_h)
        data, bpp, size_line, endian = self.m.mlx_get_data_addr(
            self.maze_background_img)

        for y in range(maze_h):
            for x in range(maze_w):
                index = y * size_line + x * (bpp // 8)
                data[index + 0] = 128
                data[index + 1] = 128
                data[index + 2] = 128
                data[index + 3] = 255

    def draw_border(self, rend_tiles_x, rend_tiles_y):
        self.border_cell = self.m.mlx_new_image(self.mlx_ptr, self.win_width,
                                                self.win_height)
        data, bpp, size_line, endian = self.m.mlx_get_data_addr(
                                        self.border_cell)
        # top
        py = 0
        for w in range(0, rend_tiles_x):
            px = w * self.tile_width
            for y in range(4 * self.tile_height):
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
        for h in range(0, rend_tiles_x):
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
        margin_y = self.tile_height // 100000  # this is to control the margin
        margin_x = self.tile_width // 1000000  # same s above
        for y in range(margin_y, self.tile_height - margin_y):
            for x in range(margin_x, self.tile_width - margin_x):
                index = y * size_line + x * (bpp // 8)
                data[index + 0] = 255
                data[index + 1] = 255
                data[index + 2] = 255
                data[index + 3] = 255

    def draw_entry(self):
        self.entry_cell = self.m.mlx_new_image(self.mlx_ptr, self.tile_width,
                                               self.tile_height)
        data, bpp, size_line, endian = self.m.mlx_get_data_addr(
                                                self.entry_cell)
        margin_y = self.tile_height // 100000  # this is to control the margin
        margin_x = self.tile_width // 1000000  # same s above
        for y in range(margin_y, self.tile_height - margin_y):
            for x in range(margin_x, self.tile_width - margin_x):
                index = y * size_line + x * (bpp // 8)
                data[index + 0] = 0
                data[index + 1] = 255
                data[index + 2] = 0
                data[index + 3] = 255

    def draw_exit(self):
        self.exit_cell = self.m.mlx_new_image(self.mlx_ptr, self.tile_width,
                                              self.tile_height)
        data, bpp, size_line, endian = self.m.mlx_get_data_addr(
                                                self.exit_cell)
        margin_y = self.tile_height // 100000  # this is to control the margin
        margin_x = self.tile_width // 1000000  # same s above
        for y in range(margin_y, self.tile_height - margin_y):
            for x in range(margin_x, self.tile_width - margin_x):
                index = y * size_line + x * (bpp // 8)
                data[index + 0] = 0
                data[index + 1] = 255
                data[index + 2] = 255
                data[index + 3] = 255

    def draw_button(self, btn: Button):
        img = self.m.mlx_new_image(
            self.mlx_ptr,
            btn.w,
            btn.h)
        data, bpp, size_line, endian = self.m.mlx_get_data_addr(img)
        if btn.pressed:
            r, g, b = btn.color_pressed
        else:
            r, g, b = btn.color_normal

        for y in range(btn.h):
            for x in range(btn.w):
                index = y * size_line + x * (bpp // 8)
                data[index + 0] = b
                data[index + 1] = g
                data[index + 2] = r
                data[index + 3] = 255

        self.m.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr, img,
                                       btn.x, btn.y)
        self.m.mlx_string_put(self.mlx_ptr, self.win_ptr,
                              btn.x + 5, btn.y + 8, 0xFFFFFF,
                              btn.label)

    def draw_input_field(self, field: InputField):
        img = self.m.mlx_new_image(
            self.mlx_ptr,
            field.w,
            field.h)
        data, bpp, size_line, endian = self.m.mlx_get_data_addr(img)
        if field.focused:
            r, g, b = (80, 80, 220)
        else:
            r, g, b = (80, 80, 80)

        for y in range(field.h):
            for x in range(field.w):
                index = y * size_line + x * (bpp // 8)
                data[index + 0] = b
                data[index + 1] = g
                data[index + 2] = r
                data[index + 3] = 255

        self.m.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr, img,
                                       field.x, field.y)
        self.m.mlx_string_put(self.mlx_ptr, self.win_ptr,
                              field.x + field.w, field.y + 5,
                              0xFFFFFF,
                              field.label)
        self.m.mlx_string_put(
            self.mlx_ptr, self.win_ptr,
            field.x + 0, field.y + 2,
            0xFFFFFF,
            field.text)

    def gere_close(self, dummy) -> None:
        """
        dummy param is aplcaeholder to statify the scalback singature
        to be used in mlx_hook()
        """
        print("closing...")
        self.m.mlx_loop_exit(self.mlx_ptr)

    def run(self) -> None:
        self.image_manger()
        self.menu()
        self.run_and_render_maze()
        self.m.mlx_hook(self.win_ptr, 33, 0, self.gere_close, None)
        self.m.mlx_key_hook(self.win_ptr, self.start_key_hook, "hi there")
        self.m.mlx_mouse_hook(self.win_ptr, self.start_mouse_hook, None)
        self.m.mlx_loop(self.mlx_ptr)


if __name__ == "__main__":
    window = Window()
    window.run()


# to be discarded:
    # def mykey(self, keynum: int, mystuff: Any) -> None:
    #     """
    #     all key events are defined here
    #     """
    #     if keynum == 65307:
    #         print("quiting..")
    #         self.gere_close(None)
    #         return
    #     print(f"Got key {keynum}, and got my stuff back:")
    #     print(mystuff)
    #     if keynum == 32:
    #         # self.m.mlx_mouse_hook(self.win_ptr, None, "hello")
    #         self.run_and_render_maze()
    # def draw_v_wall(self):
    #     self.v_wall_img_ptr = self.m.mlx_new_image(
    #         self.mlx_ptr, self.tile_width, self.tile_height)
    #     data, bpp, size_line, endian = self.m.mlx_get_data_addr(
    #                                     self.v_wall_img_ptr)

    #     thickness = max(1, self.tile_width // 1)
    #     for y in range(self.tile_height):
    #         for x in range(thickness):
    #             index = y * size_line + x * (bpp // 8)
    #             data[index + 0] = 0
    #             data[index + 1] = 0
    #             data[index + 2] = 0
    #             data[index + 3] = 255

    # def draw_h_wall(self):
    #     self.h_wall_img_ptr = self.m.mlx_new_image(
    #         self.mlx_ptr, self.tile_width, self.tile_height)
    #     data, bpp, size_line, endian = self.m.mlx_get_data_addr(
    #                                     self.h_wall_img_ptr)

    #     thickness = max(1, self.tile_height // 1)
    #     for y in range(thickness):
    #         for x in range(self.tile_width):
    #             index = y * size_line + x * (bpp // 8)
    #             data[index + 0] = 0
    #             data[index + 1] = 0
    #             data[index + 2] = 0
    #             data[index + 3] = 255

    # def menu(self):
    #     self.start_btn_x = 250
    #     self.start_btn_y = 350
    #     self.start_btn_w = 150
    #     self.start_btn_h = 30
    #     self.start_button_pressed = False
    #     self.start_button = self.m.mlx_new_image(
    #         self.mlx_ptr, self.start_btn_w, self.start_btn_h)
    #     data, bpp, size_line, endian = self.m.mlx_get_data_addr(
    #         self.start_button)

    #     for y in range(30):
    #         for x in range(150):
    #             index = y * size_line + x * (bpp // 8)
    #             data[index + 0] = 255
    #             data[index + 1] = 0
    #             data[index + 2] = 0
    #             data[index + 3] = 255

    #     self.m.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr,
    #                                    self.start_button, self.start_btn_x,
    #                                    self.start_btn_y)
    #     self.m.mlx_string_put(self.mlx_ptr, self.win_ptr,
    #                           self.start_btn_x + 6, self.start_btn_y + 5,
    #                                  350,
    #                           "Generate Maze")

    # def update_start_button(self):
    # if not self.start_button:
    #     return
    # data, bpp, size_line, endian = self.m.mlx_get_data_addr(
    #                                 self.start_button)
    # for y in range(30):
    #     for x in range(150):
    #         index = y * size_line + x * (bpp // 8)
    #         if self.start_button_pressed:
    #             data[index + 0] = 0
    #             data[index + 1] = 255
    #             data[index + 2] = 0
    #             data[index + 3] = 255

    # self.m.mlx_put_image_to_window(
    #     self.mlx_ptr, self.win_ptr,
    #     self.start_button, self.start_btn_x, self.start_btn_y
    # )
    # self.m.mlx_string_put(
    #     self.mlx_ptr, self.win_ptr,
    #     self.start_btn_x + 10, self.start_btn_y + 10,
    #     0xFFFFFF, "Generate Maze"
    # )
    # def stock_image(self, dummy) -> None:
    #     (img, w, h) = self.m.mlx_png_file_to_image(self.mlx_ptr,
    #                                                "./stock_image.png")
    #     if not img:
    #         print("mlx_png_file_to_image failed")
    #         return
    #     self.m.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr, img, 0, 0)
