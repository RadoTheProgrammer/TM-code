"""Print a message whenever the left or right mouse button is pressed.

Run with: python mouse_click_detector.py
Stop with Ctrl+C.
"""

import ctypes
import os
import time
from ctypes import wintypes


POLL_INTERVAL_SECONDS = 0.01
MOUSE_BUTTONS = {
    0x01: "Left",
    0x02: "Right",
}


def main() -> None:
    if os.name != "nt":
        raise OSError("This mouse click detector currently requires Windows.")

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    get_async_key_state = user32.GetAsyncKeyState
    get_async_key_state.argtypes = [wintypes.INT]
    get_async_key_state.restype = wintypes.SHORT
    was_pressed = {virtual_key: False for virtual_key in MOUSE_BUTTONS}

    print("Listening for left and right mouse clicks. Press Ctrl+C to stop.")
    try:
        while True:
            for virtual_key, button_name in MOUSE_BUTTONS.items():
                is_pressed = bool(get_async_key_state(virtual_key) & 0x8000)
                if is_pressed and not was_pressed[virtual_key]:
                    print(f"{button_name} mouse button clicked", flush=True)
                was_pressed[virtual_key] = is_pressed
            time.sleep(POLL_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
