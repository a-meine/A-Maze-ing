"""visualiser.refactored.menu module.

Provides the Menu: construction and redrawing of the UI widgets (buttons
and input fields). It is composed into the App class. The actions the
buttons trigger are injected via an ``actions`` mapping so the menu never
depends on the surrounding application.
"""
from typing import Callable

from visualiser.widgets import Button, InputField
from visualiser.constants import (
    GREEN,
    RED,
    INACTIVE_GRAY,
)
from visualiser.context import WindowContext

ALGO_LABELS = {"dfs": "DFS", "prim": "Prim", "wilson": "Wil"}


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
                ``regen``, ``toggle_path``, ``cycle_color``,
                ``cycle_wall``, ``run_all``, ``close``).
        """
        self.ctx = ctx
        self.actions = actions

    def _style_algo_buttons(self) -> None:
        """Colour the algorithm buttons: active is green, others not-clicked.

        Every call resets all three buttons to INACTIVE_GRAY and highlights
        only the one matching the current ``ctx.algorithm``.
        """
        for btn in self.ctx.algo_buttons:
            is_active = btn.label == ALGO_LABELS.get(self.ctx.algorithm)
            btn.color_normal = GREEN if is_active else INACTIVE_GRAY
            btn.color_pressed = RED if is_active else INACTIVE_GRAY

    def _set_algorithm(self, algo: str) -> None:
        """Set the maze generation algorithm and update button colours.

        Args:
            algo (str): The algorithm name ('dfs', 'prim' or 'wilson').
        """
        ctx = self.ctx
        ctx.algorithm = algo
        self._style_algo_buttons()
        self.redraw_buttons()

    def menu(self) -> None:
        """Set up the menu buttons and input fields (stacked layout)."""
        ctx = self.ctx
        actions = self.actions
        algo_buttons = [
            Button(100, 475, 85, 30, "DFS",
                   INACTIVE_GRAY, INACTIVE_GRAY,
                   action=lambda: self._set_algorithm("dfs")),
            Button(190, 475, 85, 30, "Prim",
                   GREEN, RED,
                   action=lambda: self._set_algorithm("prim")),
            Button(280, 475, 85, 30, "Wil",
                   GREEN, RED,
                   action=lambda: self._set_algorithm("wilson"))
            ]
        ctx.algo_buttons = algo_buttons
        self._style_algo_buttons()
        ctx.buttons = [
            Button(100, 90, 220, 30, "Apply",
                   GREEN, RED, action=actions["apply_settings"]),
            Button(100, 130, 220, 30, "Regen",
                   GREEN, RED, action=actions["regen"]),
            Button(100, 170, 220, 30, "Hide",
                   GREEN, RED, action=actions["toggle_path"]),
            Button(100, 565, 220, 30, "Maroon",
                   GREEN, RED, action=actions["cycle_color"]),
            Button(100, 605, 220, 30, "Gray",
                   GREEN, RED, action=actions["cycle_wall"]),
            Button(100, 645, 220, 30, "CRAZY",
                   GREEN, RED, action=actions["run_all"]),
            Button(150, 1000, 130, 28, "exit",
                   GREEN, RED, action=actions["close"]),
            *algo_buttons,
        ]
        ctx.fields = [
            InputField(150, 255, 70, 24, "W",
                       str(ctx.config.width)),
            InputField(150, 295, 70, 24, "H",
                       str(ctx.config.height)),
            InputField(150, 355, 22, 20, "",
                       str(ctx.config.entry[0])),
            InputField(178, 355, 22, 20, "",
                       str(ctx.config.entry[1])),
            InputField(150, 395, 22, 20, "",
                       str(ctx.config.exit[0])),
            InputField(178, 395, 22, 20, "",
                       str(ctx.config.exit[1])),
        ]

    def redraw_menu(self) -> None:
        """Redraw the entire menu overlay onto the window."""
        self.render_menu()

    def render_menu(self) -> None:
        """Compose the menu widgets and present the whole scene."""
        self._compose_widgets()
        self.ctx.present_scene()

    def _compose_widgets(self) -> None:
        """Paint all widget rectangles into the menu canvas."""
        ctx = self.ctx
        l = ctx.layout
        for btn in ctx.buttons:
            btn.paint(ctx.menu_canvas_img, ctx.m, l.menu_x, l.maze_offset_y)
        for field in ctx.fields:
            field.paint(ctx.menu_canvas_img, ctx.m, l.menu_x, l.maze_offset_y)

    def redraw_buttons(self) -> None:
        """Redraw all buttons onto the window."""
        self.render_menu()

    def redraw_fields(self) -> None:
        """Redraw all input fields onto the window."""
        self.render_menu()

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
