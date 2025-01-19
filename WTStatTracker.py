from datetime import datetime
from time import sleep
from pynput import keyboard
import pyperclip
from src.console_manager import ConsoleManager
from src.console_printer import ConsolePrinter
from src.deep_battle_parser import BattleParser
from src.file_manager import FileManager
from src.filter_manager import FilterManager
from src.stat_display_manager import StatDisplayManager
from src.ui_manager import UIManager

pressed_keys = set()


class WTStatTracker:
    def __init__(self):
        self.battles = []
        self.ui_manager = UIManager()
        self.stats = StatDisplayManager()
        self.file_manager = FileManager()
        self.filter_manager = FilterManager()
        self.console_manager = ConsoleManager(self)
        self.today_date = datetime.now().strftime("%Y-%m-%d")
        self.load_battles()
        self.console_mode = False  # Tracks if we are in console mode
        self.command_filter = None  # Filter for battles (e.g., ground, air)

    def load_battles(self):
        """Load battles from file."""
        try:
            self.battles = self.file_manager.read_result(self.today_date)
        except FileNotFoundError:
            print(f"No saved battles found for {self.today_date}. Starting fresh.")
        except Exception as e:
            print(f"Error loading battles: {e}")

    def apply_filters_and_update(self):
        """Apply filters and update the stats display."""
        filtered_battles = self.filter_manager.apply_filters(self.battles)
        self.stats.update_stats(filtered_battles)

    def handle_clipboard_parsing(self):
        """Handle parsing of clipboard content."""
        self.ui_manager.show_popup("Parsing battle info...", "parsing_popup", 10)
        sleep(0.5)

        clipboard_text = pyperclip.paste()
        print("Clipboard Text:", clipboard_text)

        battle_info = BattleParser.parse_battle_info(clipboard_text)

        if not battle_info:
            self.ui_manager.close_popup("parsing_popup")
            return

        # Check for duplicates
        if any(
            b["Duration"] == battle_info["Duration"]
            and b["Kills"] == battle_info["Kills"]
            for b in self.battles
        ):
            self.ui_manager.close_popup("parsing_popup")
            return

        print("Parsed Battle Info:", battle_info)
        self.battles.append(battle_info)
        self.apply_filters_and_update()
        self.ui_manager.close_popup("parsing_popup")
        self.stats.update_stats(self.battles)

    def handle_results_saving(self):
        """Save results to file."""
        self.file_manager.save_result(self.today_date, self.battles)
        self.ui_manager.show_popup("Results saved to the file", "summary_popup", 2)

    def display_battle_list(self):
        """Display battles and summary."""
        ConsolePrinter.print_battle_list(self.battles)
        ConsolePrinter.print_summary(self.battles)

    def run(self):
        """Run the main application loop."""
        print(
            "Press 'ctrl+c' to parse battle info from clipboard. Press 'esc' to exit. Press '`' for console."
        )
        self.stats.start()
        sleep(1)
        self.stats.update_stats(self.battles)

        def on_press(key):
            if key in pressed_keys:
                return

            pressed_keys.add(key)
            try:
                if hasattr(key, "char"):
                    unicode_order = get_unicode_order_from_char(key.char)
                    if is_ctrl_unicode(key.char):
                        ctrl_char = character_from_ctrl_unicode(unicode_order)
                        if ctrl_char == "c":  # Ctrl+C detected
                            pressed_keys.clear()
                            self.handle_clipboard_parsing()

                    elif key.char == "`":  # Toggle console mode
                        if self.console_manager.running:
                            print("Exiting console mode...")
                            self.console_manager.stop_console()
                        else:
                            print("Entering console mode...")
                            self.console_manager.run_console()

                    elif key.char == "l" and not self.console_manager.running:
                        self.display_battle_list()

                if key == keyboard.Key.home:
                    self.handle_results_saving()
                elif key == keyboard.Key.end:
                    print("Exiting...")
                    return False

            except AttributeError:
                pass

        def on_release(key):
            pressed_keys.discard(key)

        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()



# If unicode number is 0-31 or 127, then it is a control unicode.
# Because pynput only registers/only fails to convert the alphabet, this will not return True for the other six control codes.
def is_ctrl_unicode(code: str) -> bool:
    """Check if the unicode is a control character."""
    if not code or len(code) != 1:  # Ensure code is not None and has length 1
        return False
    return 0 < ord(code) < 26


# param: char
def get_unicode_order_from_char(char: str) -> int:
    if char is None or type(char) is not str:
        return -1

    if not char:
        return -1

    if len(char) != 1:
        return -1

    return ord(char)


# Returns the character from control + character unicode.
# Example: ctrl + A -> (pynput) -> \u0001 -> (This method) -> a
# There are 32 ctrl combinations, but pynput does not r1egister/struggle the non-alphabetic codes, so they will not be considered.
def character_from_ctrl_unicode(order: int) -> str:
    if not 0 < order < 26:
        return
    pool = "abcdefghijklmnopqrstuvwxyz"
    assert len(pool) == 26
    return pool[order - 1]
