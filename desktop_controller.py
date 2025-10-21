import pyautogui
import os
import time
import sys
import pyperclip
from PIL import Image

def minimise_all_windows():
    """
    Minimises all visible windows using Windows+D shortcut.
    This helps ensure the desktop is visible before starting automation.
    """
    try:
        # Use Windows+D shortcut to show desktop
        pyautogui.hotkey('win', 'd')
        return True
    except Exception as e:
        print(f"Error minimizing windows: {e}")
        return False

def _get_center_coords_from_pixel_coords(coords: list):
    """
    Converts a list of pixel coordinates [x, y] to a center point.
    Currently, it just returns the coordinates as is, assuming they are the center.
    """
    if not coords or len(coords) != 2:
        return None, None
    
    try:
        x, y = [int(c) for c in coords]
        return x, y
    except (ValueError, TypeError) as e:
        print(f"Error converting pixel coordinates '{coords}': {e}")
        return None, None



def _get_hotkeys(key_str: str):
    """
    Converts a key string into a list of keys that pyautogui can use.
    Handles common aliases and platform differences.
    """
    key_map = {
        'return': 'enter',
        'ctrl': 'ctrl',
        'shift': 'shift',
        'alt': 'alt',
        'page down': 'pagedown',
        'page up': 'pageup',
        'meta': 'win' if sys.platform == 'win32' else 'command',
        'win': 'win',
        'command': 'command',
        'cmd': 'cmd',
        ',': ',',
        'arrowup': 'up',
        'arrowdown': 'down',
        'arrowleft': 'left',
        'arrowright': 'right',
    }
    
    keys = key_str.lower().split()
    
    processed_keys = []
    for key in keys:
        processed_keys.append(key_map.get(key, key))
        
    return processed_keys

def take_screenshot(session_dir):
    """Takes a screenshot and saves it to the specified session directory."""
    # The session directory is created by the runner script
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join(session_dir, f"screenshot_{timestamp}.png")
    
    # Take a screenshot
    screenshot = pyautogui.screenshot()
    
    # Get logical screen size
    logical_width, logical_height = pyautogui.size()
    
    # Get physical screenshot size
    physical_width, physical_height = screenshot.size
    
    # If there's a scaling factor, resize the image to the logical resolution
    if physical_width != logical_width or physical_height != logical_height:
        print(f"Screen scaling detected. Resizing screenshot from {physical_width}x{physical_height} to {logical_width}x{logical_height}.")
        screenshot = screenshot.resize((logical_width, logical_height), Image.Resampling.LANCZOS)

    screenshot.save(screenshot_path)
    return screenshot_path

def execute_action(action_data):
    """
    Executes a desktop action based on the parsed action data.
    """
    action_type = action_data.get("action")
    params = action_data.get("params", {})

    try:
        if action_type in ["click", "left_double", "right_single"]:
            x, y = _get_center_coords_from_pixel_coords(params.get("start_box"))
            if x is None or y is None:
                print("Could not determine coordinates for click action.")
                return "failed"
            
            pyautogui.moveTo(x, y, duration=0.2)

            if action_type == "click":
                pyautogui.mouseDown()
                time.sleep(0.1)
                pyautogui.mouseUp()
            elif action_type == "left_double":
                pyautogui.doubleClick()
            elif action_type == "right_single":
                pyautogui.rightClick()

        elif action_type == "type":
            content = params.get("content", "")
            
            # Use clipboard for reliability on Windows
            pyautogui.hotkey('ctrl', 'a') # Select all
            time.sleep(0.1)
            pyautogui.press('backspace') # Delete
            time.sleep(0.1)

            content_to_type = content.strip()
            press_enter = False
            if content_to_type.endswith('\\n') or content_to_type.endswith('\n'):
                press_enter = True
                if content_to_type.endswith('\\n'):
                    content_to_type = content_to_type[:-2]
                else:
                    content_to_type = content_to_type[:-1]

            if sys.platform == "win32":
                original_clipboard = pyperclip.paste()
                pyperclip.copy(content_to_type)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.1)
                pyperclip.copy(original_clipboard)
            else: # For MacOS and Linux
                pyautogui.write(content_to_type, interval=0.01)

            if press_enter:
                pyautogui.press('enter')

        elif action_type == "scroll":
            x, y = _get_center_coords_from_pixel_coords(params.get("start_box"))
            if x is not None and y is not None:
                pyautogui.moveTo(x, y, duration=0.2)

            direction = params.get("direction", "down")
            scroll_amount = -500 if direction == "down" else 500
            pyautogui.scroll(scroll_amount)

        elif action_type == "drag":
            start_x, start_y = _get_center_coords_from_pixel_coords(params.get("start_box"))
            end_x, end_y = _get_center_coords_from_pixel_coords(params.get("end_box"))

            if None in [start_x, start_y, end_x, end_y]:
                print(f"Could not determine coordinates for drag operation.")
                return "failed"
            
            pyautogui.moveTo(start_x, start_y, duration=0.2)
            pyautogui.dragTo(end_x, end_y, duration=1.0, button='left')

        elif action_type == "hotkey":
            keys_str = params.get("key", "enter")
            keys = _get_hotkeys(keys_str)
            if not keys:
                print("Invalid hotkey specification.")
                return "failed"
            pyautogui.hotkey(*keys)

        elif action_type == "wait":
            print("Waiting for 5 seconds...")
            time.sleep(5)
            
        elif action_type == "finished":
            print("Task marked as finished.")
            return "stop"

        elif action_type == "authenticate":
            print("Action 'authenticate' triggered. User authentication (OTP/mobile number) required.")
            return "authenticate"

        elif action_type == "call_user":
            print("Action 'call_user' triggered. Pausing operation and waiting for user input.")
            return "call_user"

        else:
            print(f"Unknown action type: {action_type}")
            return "failed"

    except Exception as e:
        print(f"Error executing action {action_type}: {e}")
        return "failed"
        
    time.sleep(2) # Increased delay to ensure UI updates
    return "continue" 