from mlx import Mlx
import time
from maze.cell import Cell
from maze.grid import Grid
from maze.algorithms.generator.randomised_prim import Prim
from maze.algorithms.generator.dfs import DFS
from maze.algorithms.solution.bfs import BFS
from config.parser import Config, load_config
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
    def __init__(self, config: Config) -> None:
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

    def _build_grid(self):
        grid = Grid(self.config)
        if self.algorithm == "dfs":
            return DFS(grid)
        return Prim(grid)

    def config_images(self):
        self.layout = Layout.compute(
            self.fields, self.config, self.win_width, self.win_height
        )
        self.grid = self._build_grid()
        self.grid.event = self.render

    def apply_settings(self):
        self.config_images()
        self.initialise_images()
        self.redraw_menu()
        self.render_grid()

    def _solve_path(self):
        try:
            solver = BFS(self.grid.grid)
            self.solution_path = solver.solve()
        except Exception:
            self.solution_path = []

    def _make_tile(self, color, margin_x=0, margin_y=0):
        l = self.layout
        img = self.m.mlx_new_image(
            self.mlx_ptr, l.tile_width, l.tile_height)
        fill_image(self.m, img, l.tile_width, l.tile_height,
                   color, margin_x, margin_y)
        return img

    def _make_solid_image(self, w, h, color=MED_GRAY):
        img = self.m.mlx_new_image(self.mlx_ptr, w, h)
        fill_image(self.m, img, w, h, color)
        return img

    def initialise_images(self):
        l = self.layout
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

    def _render_walls(self, cell, rx, ry):
        l = self.layout
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

    def _render_entry_exit(self, cell, px, py):
        coord = (cell.coordinate.x, cell.coordinate.y)
        if coord == self.layout.entry:
            self.m.mlx_put_image_to_window(
                self.mlx_ptr, self.win_ptr, self.entry_cell, px, py)
        if coord == self.layout.exit:
            self.m.mlx_put_image_to_window(
                self.mlx_ptr, self.win_ptr, self.exit_cell, px, py)

    def _render_cell_state(self, cell, px, py):
        if cell.occupied:
            self.m.mlx_put_image_to_window(
                self.mlx_ptr, self.win_ptr, self.next_cell_img_ptr, px, py)
            self.m.mlx_put_image_to_window(
                self.mlx_ptr, self.win_ptr, self.cell_img_ptr, px, py)
            self._render_entry_exit(cell, px, py)
        else:
            self.m.mlx_put_image_to_window(
                self.mlx_ptr, self.win_ptr, self.next_cell_img_ptr, px, py)

    def render(self, cell: Cell, sync: bool = True):
        l = self.layout
        rx = 2 * cell.coordinate.x + 1
        ry = 2 * cell.coordinate.y + 1
        px = l.offset_x + rx * l.tile_width
        py = l.offset_y + ry * l.tile_height

        self._render_walls(cell, rx, ry)
        if sync:
            self.m.mlx_sync(self.mlx_ptr, self.m.SYNC_WIN_FLUSH,
                            self.win_ptr)
        self._render_cell_state(cell, px, py)

    def render_grid(self):
        l = self.layout
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

    def _render_path(self):
        l = self.layout
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

    def _set_algorithm(self, algo):
        self.algorithm = algo
        for btn in self.algo_buttons:
            is_active = btn.label.lower() == algo
            btn.color_normal = GREEN if is_active else INACTIVE_GRAY
            btn.color_pressed = RED if is_active else INACTIVE_GRAY
        self.redraw_buttons()

    def menu(self):
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

    def redraw_menu(self):
        l = self.layout
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

    def redraw_buttons(self):
        for btn in self.buttons:
            btn.draw(self.m, self.mlx_ptr, self.win_ptr)
        self.m.mlx_sync(self.mlx_ptr, self.m.SYNC_WIN_COMPLETED,
                        self.win_ptr)

    def redraw_fields(self):
        for field in self.fields:
            field.draw(self.m, self.mlx_ptr, self.win_ptr)
        self.m.mlx_sync(self.mlx_ptr, self.m.SYNC_WIN_COMPLETED,
                        self.win_ptr)

    def _focus_field_at(self, x, y):
        clicked = False
        for field in self.fields:
            if field.contains(x, y):
                field.focused = True
                clicked = True
            else:
                field.focused = False
        return clicked

    def _clear_focus(self):
        for field in self.fields:
            field.focused = False

    def _active_field(self):
        for field in self.fields:
            if field.focused:
                return field
        return None

    def start_mouse_hook(self, button, x, y, mystuff):
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

    def start_key_hook(self, keynum, mystuff):
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

    def toggle_path(self):
        self.show_path = not self.show_path
        for btn in self.buttons:
            if btn.action == self.toggle_path:
                btn.label = "Hide Path" if self.show_path else "Show Path"
        self.redraw_buttons()
        self.render_grid()

    def regen(self):
        self.apply_settings()
        self.grid.generate_maze()
        self._solve_path()
        self._render_path()

    def close(self, dummy) -> None:
        print("closing...")
        self.m.mlx_loop_exit(self.mlx_ptr)

    def run(self) -> None:
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
