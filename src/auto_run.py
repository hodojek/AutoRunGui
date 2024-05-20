# You can run this file with python for cli only 

import os
import sys
import logging
from typing import Callable

import keyboard

from keyboard_simulator import PressKey, ReleaseKey, KEY_W, KEY_LSHIFT

PATH_TO_SAVE_FILE = os.path.join(os.getenv("AppData"), "AutoRunGui\\auto_run_toggle_key.txt")

logger = logging.getLogger("AutoRun")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


def get_toggle_key() -> str:
    if os.path.exists(PATH_TO_SAVE_FILE):
        with open(PATH_TO_SAVE_FILE) as f:
            toggle_key = f.read().strip() or "="  # return "=" is file is empty
        if toggle_key.lower() in ("w", "shift"):  # toggle key cannot be "w" or "shift"
            return "="
        if keyboard.key_to_scan_codes(toggle_key, error_if_missing=False):  # Check if key is valid
            return toggle_key
    return "="


def set_toggle_key(toggle_key: str):
    if not os.path.exists(os.path.dirname(PATH_TO_SAVE_FILE)):
        os.mkdir(os.path.dirname(PATH_TO_SAVE_FILE))
        logger.info(f"Created AppData directory: {os.path.dirname(PATH_TO_SAVE_FILE)}")
    with open(PATH_TO_SAVE_FILE, "w") as f:
        f.writelines([toggle_key.strip()])
        logger.info(f"Wrote {toggle_key!r} to save file: {PATH_TO_SAVE_FILE}")


class AutoRun:
    def __init__(self) -> None:
        self.is_active: bool = False

    def enter_run(self):
        logger.info("w+shift is PRESSED")
        PressKey(KEY_W)
        PressKey(KEY_LSHIFT)
        self.is_active = True

    def exit_run(self):
        logger.info("w+shift is released")
        ReleaseKey(KEY_W)
        ReleaseKey(KEY_LSHIFT)
        self.is_active = False

    def toggle_run(self, *_):
        if self.is_active:
            self.exit_run()
        else:
            self.enter_run()

    def add_toggle_key_listener(self, toggle_key: str, callback) -> Callable:
        return keyboard.on_press_key(toggle_key, callback=callback, suppress=True)

    def add_any_key_listener(self, callback) -> Callable:
        return keyboard.on_press(callback)

    def remove_listeners(self):
        keyboard.unhook_all()


def main():
    auto_run = AutoRun()
    toggle_key = get_toggle_key()

    logger.info(f"You can now enter the game | Toggle key: <{toggle_key}> | Exit program by: ctrl+c")

    try:
        auto_run.add_toggle_key_listener(toggle_key, callback=auto_run.toggle_run)
        keyboard.wait()
    except KeyboardInterrupt:
        logger.info("Exited program")
    finally:
        auto_run.exit_run()  # exit_run is here to release w and shift before closing, so they don't get stuck


if __name__ == "__main__":
    main()