"""visualiser.refactored.menu module.

Provides the Menu: construction and redrawing of the UI widgets (buttons
and input fields). It is composed into the App class. The actions the
buttons trigger are injected via an ``actions`` mapping so the menu never
depends on the surrounding application.
"""
from typing import Any, Callable

from visualiser.MlxColor import MlxColor
from visualiser.widgets import Button, InputField
from visualiser.constants import (
    GREEN,
    RED,
    INACTIVE_GRAY,
    WHITE,
)
from visualiser.context import WindowContext


class Menu:
    """Builds and redraws the menu widgets."""

    def __init__(
            self,
            ctx: WindowContext,
            actions: dict[str, Callable[..., None]],
    ) -> None:
        """Initialize the menu.

        Args:
            ctx (WindowContext): The shared window context.
            actions (dict[str, Callable[..., None]]): The callbacks the
                buttons trigger, keyed by name (``apply_settings``,
                ``regen``, ``toggle_path``, ``close``).
        """
        self.ctx = ctx
        self.actions = actions

    def _set_algorithm(self, algo: str) -> None:
        """Set the maze generation algorithm and update button colours.

        Args:
            algo (str): The algorithm name ('dfs', 'prim' or 'wilson').
        """
        ctx = self.ctx
        ctx.algorithm = algo
        for btn in ctx.algo_buttons:
            is_active = btn.label.lower() == algo
            btn.color_normal = GREEN if is_active else INACTIVE_GRAY
            btn.color_pressed = RED if is_active else INACTIVE_GRAY
        self.redraw_buttons()

    def menu(self) -> None:
        """Set up the menu buttons and input fields."""
        ctx = self.ctx
        actions = self.actions
        algo_buttons = [
            Button(50, 520, 100, 30, "DFS",
                   INACTIVE_GRAY, INACTIVE_GRAY,
                   action=lambda: self._set_algorithm("dfs")),
            Button(160, 520, 100, 30, "Prim",
                   GREEN, RED,
                   action=lambda: self._set_algorithm("prim")),
            Button(370, 520, 100, 30, "Wil",
                   GREEN, RED,
                   action=lambda: self._set_algorithm("wilson"))
            ]
        ctx.algo_buttons = algo_buttons
        ctx.buttons = [
            Button(100, 150, 200, 40, "Apply",
                   GREEN, RED, action=actions["apply_settings"]),
            Button(100, 210, 200, 40, "Re-Generate",
                   GREEN, RED, action=actions["regen"]),
            Button(100, 270, 200, 40, "Hide Path",
                   GREEN, RED, action=actions["toggle_path"]),
            Button(100, 950, 150, 30, "exit",
                   GREEN, RED, action=actions["close"]),
            *algo_buttons,
        ]
        ctx.fields = [
            InputField(50, 350, 70, 30, "width",
                       str(ctx.config.width)),
            InputField(200, 350, 70, 30, "height",
                       str(ctx.config.height)),
            InputField(50, 400, 20, 20, "",
                       str(ctx.config.entry[0])),
            InputField(73, 400, 20, 20, "",
                       str(ctx.config.entry[1])),
            InputField(50, 450, 20, 20, "",
                       str(ctx.config.exit[0])),
            InputField(73, 450, 20, 20, "",
                       str(ctx.config.exit[1])),
        ]

    def redraw_menu(self) -> None:
        """Redraw the entire menu overlay onto the window."""
        ctx = self.ctx
        l = ctx.layout
        ctx.put_img(ctx.background_img, 0, 0)
        ctx.put_img(ctx.menu_background_img, l.menu_x, l.maze_offset_y)
        ctx.put_img(
            ctx.maze_background_img,
            l.maze_offset_x + l.relative_x_offset, l.maze_offset_y)

        ctx.put_string(200, 480,
                       MlxColor.to_hex(WHITE), "Algorithm:")
        self.redraw_buttons()
        self.redraw_fields()
        ctx.sync(ctx.m.SYNC_WIN_COMPLETED)

    def redraw_buttons(self) -> None:
        """Redraw all buttons onto the window."""
        self._draw_widgets(self.ctx.buttons)

    def redraw_fields(self) -> None:
        """Redraw all input fields onto the window."""
        self._draw_widgets(self.ctx.fields)

    def _draw_widgets(self, widgets: list[Any]) -> None:
        """Draw a list of widgets and synchronise the window.

        Args:
            widgets (list[Any]): The widgets to draw.
        """
        ctx = self.ctx
        for widget in widgets:
            widget.draw(ctx.m, ctx.mlx_ptr, ctx.win_ptr)
        ctx.sync(ctx.m.SYNC_WIN_COMPLETED)

    def _focus_field_at(self, x: int, y: int) -> bool:
        """Focus the input field at the given coordinates.

        Args:
            x (int): The x coordinate.
            y (int): The y coordinate.

        Returns:
            bool: True if a field was focused.
        """
        clicked = False
        for field in self.ctx.fields:
            if field.contains(x, y):
                field.focused = True
                clicked = True
            else:
                field.focused = False
        return clicked

    def _clear_focus(self) -> None:
        """Clear focus from all input fields."""
        for field in self.ctx.fields:
            field.focused = False

    def _active_field(self) -> InputField | None:
        """Get the currently focused input field.

        Returns:
            InputField | None: The active field, or None if none focused.
        """
        for field in self.ctx.fields:
            if field.focused:
                return field
        return None
