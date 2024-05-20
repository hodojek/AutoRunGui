import os
import sys
import json
from typing import Optional

import tkinter as tk
import tkinter.ttk as ttk

from auto_run import AutoRun, get_toggle_key, set_toggle_key

TITLE = "Auto Run"
ICON_FILE = "icon.ico"
LAYOUTS_FILE = "layouts.json"


def get_abs_file_path(file_path) -> str:
    # Get the file from the tmp directory made by pyinstaller if this runs as an executable
    # Get the file from current directory otherwise
    return os.path.join(getattr(sys, "_MEIPASS", os.path.abspath(".")), file_path)


def setup_layout(frm: ttk.Frame, layout: str):
    with open(get_abs_file_path(LAYOUTS_FILE)) as f:
        layout = json.load(f)[layout]
    for widget in layout:
        eval(f"ttk.{widget['type']}")(frm, **widget["args"]).grid(**widget["grid"])


class Window(tk.Tk):
    LAYOUT = "window"
    BTN_QUIT = "btn_quit"
    LBL_STATUS = "lbl_status"
    BTN_ENABLE = "btn_enable"
    BTN_OVERLAY = "btn_overlay"
    LBL_TOGGLE_KEY = "lbl_toggle_key"
    BTN_REBIND_TOGGLE_KEY = "btn_rebind_toggle_key"

    CONFIG_DISABLED = {"text": "disabled", "foreground": "darkred"}
    CONFIG_ENABLED = {"text": "enabled", "foreground": "darkgreen"}

    def __init__(self):
        super(Window, self).__init__()

        self.auto_run = AutoRun()

        # Setup window
        self.title(TITLE)
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.resizable(False, False)
        self.iconbitmap(get_abs_file_path(ICON_FILE))

        self.overlay: Optional[OverlayWindow] = None

        # Create window layout
        self.frm = ttk.Frame(self, padding=20)
        self.frm.grid()

        # Set variables
        # TODO: Remove hardcoded strings later
        self.var_toggle_key = tk.StringVar(self, value=get_toggle_key())
        self.var_disable_enable = tk.StringVar(self, value="Enable")
        self.var_overlay_enabled = tk.BooleanVar(self, value=False)
        self.var_toggle_key_button = tk.StringVar(self, value="Rebind")

        self.setup_layout()

        self.lbl_status: ttk.Label = self.frm.nametowidget(self.LBL_STATUS)
        self.btn_enable: ttk.Button = self.frm.nametowidget(self.BTN_ENABLE)

        self.update()
        self.auto_run.add_toggle_key_listener(get_toggle_key(), self.on_toggle)
    
    def setup_layout(self):
        setup_layout(self.frm, self.LAYOUT)
         
        self.frm.nametowidget(self.LBL_STATUS).config(**self.CONFIG_DISABLED)
        self.frm.nametowidget(self.BTN_ENABLE).config(
            textvariable=self.var_disable_enable,
            command=self.on_toggle
        )
        self.frm.nametowidget(self.LBL_TOGGLE_KEY).config(
            textvariable=self.var_toggle_key
        )
        self.frm.nametowidget(self.BTN_REBIND_TOGGLE_KEY).config(
            textvariable=self.var_toggle_key_button, 
            command=self.on_rebind_toggle_key
        )
        self.frm.nametowidget(self.BTN_OVERLAY).config(
            variable=self.var_overlay_enabled,
            command=self.on_toggle_overlay
        )
        self.frm.nametowidget(self.BTN_QUIT).config(
            command=self.on_exit
        )

    def on_exit(self):
        self.auto_run.exit_run()
        self.destroy()

    def on_rebind_toggle_key(self):
        if self.auto_run.is_active:
            self.on_toggle()
        self.auto_run.remove_listeners()
        self.auto_run.add_any_key_listener(self._rebind_toggle_key)
        self.ui_disable_rebind_toggle_key()

    def _rebind_toggle_key(self, keyboard_event):
        set_toggle_key(keyboard_event.name)
        self.auto_run.remove_listeners()
        self.auto_run.add_toggle_key_listener(get_toggle_key(), self.on_toggle)
        self.ui_enable_rebind_toggle_key()

    def on_toggle(self, *_):
        self.auto_run.toggle_run()
        if self.auto_run.is_active:
            self.ui_set_status_enabled()
        else:
            self.ui_set_status_disabled()

    def on_toggle_overlay(self):
        if self.var_overlay_enabled.get():
            self.overlay = OverlayWindow(tk.Toplevel(self), self)
        else:
            self.overlay.destroy()
            self.overlay = None

    def ui_disable_rebind_toggle_key(self):
        self.var_toggle_key.set("...")
        self.btn_enable.state(["disabled"])
        self.var_toggle_key_button.set("Press any key...")

    def ui_enable_rebind_toggle_key(self):
        self.var_toggle_key.set(get_toggle_key())
        self.btn_enable.state(["!disabled"])
        self.var_toggle_key_button.set("Rebind")
    
    def ui_set_status_enabled(self):
        if self.overlay is not None:
            self.overlay.lbl_status.config(**self.CONFIG_ENABLED)
        self.lbl_status.config(**self.CONFIG_ENABLED)
        self.var_disable_enable.set("Disable")
    
    def ui_set_status_disabled(self):
        if self.overlay is not None:
            self.overlay.lbl_status.config(**self.CONFIG_DISABLED)
        self.lbl_status.config(**self.CONFIG_DISABLED)
        self.var_disable_enable.set("Enable")


class OverlayWindow:
    CORNER_TOP_RIGHT = 1

    LAYOUT = "overlay"
    LBL_STATUS = "lbl_status"
    LBL_TOGGLE_KEY = "lbl_toggle_key"

    def __init__(self, root: tk.Toplevel, master: Window):
        self.root = root
        self.master = master

        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-alpha", 0.8)
        self.root.overrideredirect(True)

        self.frm = ttk.Frame(self.root, padding=4)
        self.frm.grid()

        setup_layout(self.frm, self.LAYOUT)

        self.frm.nametowidget(self.LBL_STATUS).config(
            **(self.master.CONFIG_ENABLED if self.master.auto_run.is_active else self.master.CONFIG_DISABLED)
        )
        self.frm.nametowidget(self.LBL_TOGGLE_KEY).config(
            textvariable=self.master.var_toggle_key
        )

        self.lbl_status = self.frm.nametowidget(self.LBL_STATUS)

        self.root.update()
        self.move_to_corner(self.CORNER_TOP_RIGHT)

    def destroy(self):
        self.root.destroy()

    def move_to_corner(self, corner: int):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = self.root.winfo_width()
        height = self.root.winfo_height()

        # TODO: Add more corners
        if corner == self.CORNER_TOP_RIGHT:
            self.root.geometry(f"+{screen_width-width-5}+5")


def main(): 
    window = Window()
    window.mainloop()


if __name__ == '__main__':
    main()