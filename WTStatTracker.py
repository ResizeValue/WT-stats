from datetime import datetime
import os
from threading import Event, Thread
from time import sleep
import traceback
from pynput import keyboard
import keyboard as kb
import pyperclip
from src.char_helper import CharHelper
from src.console_manager import ConsoleManager
from src.deep_battle_parser import BattleParser
from src.file_manager import FileManager
from src.filter_manager import FilterManager
from src.ui.ui_manager import UIManager

pressed_keys = set()


class WTStatTracker:
    def __init__(self):
        self.ui_manager = UIManager(self)
        self.filter_manager = FilterManager(self)
        self.console_manager = ConsoleManager(self)

        self.console_mode = False
        self.listener = None
        self._battles = []

    def get_battles(self):
        return self.filter_manager.apply_filters(self._battles)

    def set_battles(self, battles):
        self._battles = battles

    def new_session(self):
        """Start a new session."""
        self._battles = []
        self.ui_manager.update()
        FileManager.auto_save(self._battles)

    def handle_clipboard_parsing(self):
        """Handle parsing of clipboard content with a timeout."""
        
        popup_id = self.ui_manager.popup_manager.show_popup(
            "Parsing battle info...", 5
        )
        
        sleep(0.5)

        clipboard_text = pyperclip.paste()
        print("Parsing battle info...")

        # Define a container for the result
        result = {"battle_info": None, "error": None}
        finished_event = Event()

        def parse_task():
            """Run the parsing task."""
            try:
                result["battle_info"] = BattleParser.parse_battle_info(clipboard_text)
            except Exception as e:
                result["error"] = traceback.format_exc()
            finally:
                finished_event.set()  # Notify that parsing is complete

        # Start the parsing thread
        thread = Thread(target=parse_task)
        thread.start()

        # Wait for the thread to finish with a timeout
        timeout_seconds = 5
        if not finished_event.wait(timeout_seconds):
            print(f"Parsing battle info timed out after {timeout_seconds} seconds.")
            self.ui_manager.popup_manager.close_popup(popup_id)
            return

        # Check for errors in parsing
        if result["error"]:
            print(f"Error during parsing: {result['error']}")
            self.ui_manager.popup_manager.close_popup(popup_id)
            return

        # Get the parsed battle info
        battle_info = result["battle_info"]
        if not battle_info:
            self.ui_manager.popup_manager.close_popup("parsing_popup")
            return

        # Check for duplicates
        if any(
            b["Duration"] == battle_info["Duration"]
            and b["Kills"] == battle_info["Kills"]
            for b in self._battles
        ):
            print("Duplicate battle info detected. Ignoring.")
            self.ui_manager.popup_manager.close_popup(popup_id)
            return

        print("Parsed Battle Info:", battle_info)
        self._battles.append(battle_info)
        self.ui_manager.update()
        self.ui_manager.popup_manager.close_popup(popup_id)
        FileManager.auto_save(self._battles)

    def run(self):
        """Run the main application loop."""
        print(
            "Press 'ctrl+c' to parse battle info from clipboard."
        )
        
        self.ui_manager.start()
        sleep(1)
        self._battles = FileManager.auto_load()
        self.ui_manager.update()

        def on_press(key):
            if key in pressed_keys:
                return

            pressed_keys.add(key)

            try:
                if hasattr(key, "char"):
                    unicode_order = CharHelper.get_unicode_order_from_char(key.char)

                    if CharHelper.is_ctrl_unicode(key.char):
                        ctrl_char = CharHelper.character_from_ctrl_unicode(
                            unicode_order
                        )
                        if ctrl_char == "c":  # Ctrl+C detected
                            pressed_keys.clear()
                            self.handle_clipboard_parsing()

                    elif key.char == "\\":  # Toggle console mode
                        if self.console_manager.running:
                            print("Exiting console mode...")
                            self.console_manager.stop_console()
                        else:
                            print("Entering console mode...")
                            self.console_manager.run_console()

                    elif key.char == "l" and not self.console_manager.running:
                        ConsoleManager.print_battle_list(self.get_battles())
                        ConsoleManager.print_summary(self.get_battles())

                if key == keyboard.Key.home:
                    today = datetime.now().strftime("%Y-%m-%d")
                    FileManager.save_result(today, self._battles)
                elif key == keyboard.Key.end:
                    print("Exiting...")
                    return False

            except Exception as e:
                print(f"Error processing key press: {e}")

        def on_release(key):
            pressed_keys.discard(key)

        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            self.listener = listener
            listener.join()

    def stop(self):
        """Gracefully stop the application."""
        print("Stopping WTStatTracker...")

        sleep(1)
        # Exit application
        print("Application stopped.")
        os._exit(0)
