"""visualiser.refactored.input module.

Provides the InputHandler: mlx event hook handlers for the keyboard and
mouse. It is composed into the App class, delegating focus handling to
the Menu and closing via an injected callback.
"""
from typing import Any, Callable

from visualiser.constants import (
    KEY_BACKSPACE,
    KEY_0,
    KEY_9,
)
from visualiser.context import WindowContext
from visualiser.menu import Menu


class InputHandler:
    """Handles mouse and keyboard events."""

    def __init__(
            self,
            ctx: WindowContext,
            menu: Menu,
            on_close: Callable[..., None],
    ) -> None:
        """Initialize the input handler.

        Args:
            ctx (WindowContext): The shared window context.
            menu (Menu): The menu, used for focus handling and redraws.
            on_close (Callable[..., None]): Invoked when the window
                should close (ESC key).
        """
        self.ctx = ctx
        self.menu = menu
        self.on_close = on_close

    def start_mouse_hook(
            self, button: int, x: int, y: int, _: Any
    ) -> None:
        """Handle mouse click events.

        Args:
            button (int): The mouse button that was clicked.
            x (int): The x coordinate of the click.
            y (int): The y coordinate of the click.
            _ (Any): Additional data passed by the hook.
        """
        if button != 1:
            return
        if self.menu._focus_field_at(x, y):
            self.menu.redraw_fields()
            return
        for btn in self.ctx.buttons:
            if btn.contains(x, y):
                btn.pressed = True
                self.menu.redraw_buttons()
                if btn.action:
                    btn.action()
                btn.pressed = False
                self.menu.redraw_buttons()
                return
        self.menu._clear_focus()
        self.menu.redraw_fields()

    def start_key_hook(self, keynum: int, _: Any) -> None:
        """Handle keyboard events.

        Args:
            keynum (int): The key code that was pressed.
            _ (Any): Additional data passed by the hook.
        """
        # if keynum == KEY_ESC:
        #     self.on_close(None)
        #     return
        active = self.menu._active_field()
        if active is None:
            return
        if keynum == KEY_BACKSPACE:
            active.text = active.text[:-1]
            self.menu.redraw_fields()
        elif (KEY_0 <= keynum <= KEY_9) and len(active.text) < 2:
            active.text += chr(keynum)
            self.menu.redraw_fields()
