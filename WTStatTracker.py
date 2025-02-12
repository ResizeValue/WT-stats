#!/usr/bin/env python3
import os
import logging
import traceback
from datetime import datetime
from time import sleep
from threading import Timer, Thread
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import queue

import pyperclip
from pynput import keyboard

# For Windows only – install via pip install pywin32
try:
    import win32gui
except ImportError:
    win32gui = None

# Local modules – adjust these imports as needed
from src.char_helper import CharHelper
from src.console_manager import ConsoleManager
from src.deep_battle_parser import BattleParser
from src.file_manager import FileManager
from src.filter_manager import FilterManager
from src.ui.ui_manager import UIManager
from src.version_manager import VersionManager  # Adjust if needed

# Configuration constants (set these appropriately)
CURRENT_VERSION = "1.0.0"
REPO_OWNER = "YourRepoOwner"
REPO_NAME = "YourRepoName"

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def is_war_thunder_in_focus():
    """
    Check if the currently active window is War Thunder.
    This function uses win32gui and is only available on Windows.
    Adjust the title check as necessary.
    """
    if win32gui is None:
        logger.warning(
            "win32gui is not available; cannot check window focus on this OS."
        )
        return True  # Fallback: assume true if we can't check
    try:
        hwnd = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(hwnd)
        logger.debug("Active window title: %s", window_title)
        return "War Thunder" in window_title
    except Exception as e:
        logger.error("Error checking window focus: %s", e)
        return False


class WTStatTracker:
    def __init__(self):
        self.ui_manager = UIManager(self)
        self.filter_manager = FilterManager(self)
        self.console_manager = ConsoleManager(self)
        self.console_mode = False
        self._battles = []
        self._save_timer = None

        # Executor for parsing tasks (e.g., clipboard parsing)
        self.executor = ThreadPoolExecutor(max_workers=1)

        # Queue for hotkey-triggered parsing requests
        self.parsing_queue = queue.Queue()
        # Start the background thread to process parsing requests
        self.queue_thread = Thread(target=self.process_parsing_requests, daemon=True)
        self.queue_thread.start()

        self.hotkeys = None

    def get_battles(self):
        return self.filter_manager.apply_filters(self._battles)

    def set_battles(self, battles):
        self._battles = battles
        self.ui_manager.update()

    def new_session(self):
        """Start a new session."""
        self._battles = []
        self.ui_manager.update()
        FileManager.auto_save(self._battles)

    def handle_clipboard_parsing(self, text):
        """Handle parsing of clipboard content using the thread pool."""
        popup_id = self.ui_manager.popup_manager.show_popup("Parsing battle info...", 5)
        logger.info("Starting parsing of battle info from clipboard.")

        future = self.executor.submit(BattleParser.parse_battle_info, text)
        timeout_seconds = 5

        try:
            battle_info = future.result(timeout=timeout_seconds)
        except TimeoutError:
            logger.error(
                "Parsing battle info timed out after %s seconds.", timeout_seconds
            )
            self.ui_manager.popup_manager.close_popup(popup_id)
            return
        except Exception:
            logger.error("Error during parsing:\n%s", traceback.format_exc())
            self.ui_manager.popup_manager.close_popup(popup_id)
            return

        if not battle_info:
            self.ui_manager.popup_manager.close_popup(popup_id)
            return

        # Check for duplicate battles by comparing key attributes.
        if any(
            b.get("Duration") == battle_info.get("Duration")
            and b.get("Kills") == battle_info.get("Kills")
            for b in self._battles
        ):
            logger.info("Duplicate battle info detected. Ignoring.")
            self.ui_manager.popup_manager.close_popup(popup_id)
            return

        logger.info("Parsed Battle Info: %s", battle_info)
        self._battles.append(battle_info)
        self.ui_manager.update()
        self.ui_manager.popup_manager.close_popup(popup_id)
        self.start_save_timer()

    def process_parsing_requests(self):
        """Background thread that processes parsing requests from the queue."""
        while True:
            request = self.parsing_queue.get()
            if request:
                sleep(0.3)  # Brief delay to let the popup appear
                clipboard_text = pyperclip.paste()
                print(clipboard_text)
                self.handle_clipboard_parsing(clipboard_text)
                self.parsing_queue.task_done()

    def trigger_parsing_request(self):
        """
        Callback for Ctrl+C: logs the event, checks if War Thunder is in focus,
        and if so, adds a parsing request to the queue.
        """
        if not is_war_thunder_in_focus():
            logger.info("War Thunder window is not in focus. Skipping parsing request.")
            return

        logger.info(
            "War Thunder is in focus. Ctrl+C pressed. Adding parsing request to the queue."
        )

        self.parsing_queue.put(("parse_clipboard"))

    def start_save_timer(self):
        """Start (or reset) a timer to auto-save battle data."""
        if self._save_timer:
            self._save_timer.cancel()
            logger.info("Save timer reset.")
        self._save_timer = Timer(10, self.save_battles)
        self._save_timer.start()
        logger.info("Save timer started.")

    def save_battles(self):
        """Auto-save the battles and notify the user."""
        FileManager.auto_save(self._battles)
        self._save_timer = None
        self.ui_manager.popup_manager.show_popup("Battles saved", 2)

    def toggle_console_mode(self):
        """Toggle the console mode on or off."""
        if self.console_manager.running:
            logger.info("Exiting console mode...")
            self.console_manager.stop_console()
        else:
            logger.info("Entering console mode...")
            self.console_manager.run_console()

    def print_battle_list(self):
        """Print the battle list and summary (if not in console mode)."""
        if not self.console_manager.running:
            ConsoleManager.print_battle_list(self.get_battles())
            ConsoleManager.print_summary(self.get_battles())

    def save_results(self):
        """Save the current battles to a results file."""
        today = datetime.now().strftime("%Y-%m-%d")
        FileManager.save_result(today, self._battles)

    def run(self):
        """Run the main application loop."""
        logger.info("Starting UI Manager...")
        self.ui_manager.start()
        sleep(1)
        self._battles = FileManager.auto_load()
        self.ui_manager.update()

        # Define hotkey actions using pynput's GlobalHotKeys.
        hotkey_actions = {
            "<ctrl>+c": self.trigger_parsing_request,  # Now adds a parsing request to the queue.
            # "\\": self.toggle_console_mode,
            # "l": self.print_battle_list,
            # "<home>": self.save_results,
            "<end>": self.stop,
        }
        self.hotkeys = keyboard.GlobalHotKeys(hotkey_actions)
        logger.info("Hotkeys registered. Waiting for key presses...")
        self.hotkeys.start()
        self.hotkeys.join()

    def stop(self):
        """Gracefully stop the application."""
        logger.info("Exiting... Stopping WTStatTracker.")
        if self.hotkeys:
            self.hotkeys.stop()
        sleep(1)
        logger.info("Application stopped.")
        # Shutdown executor and exit the process.
        self.executor.shutdown(wait=False)
        os._exit(0)


# --- Main Entry Point ---
if __name__ == "__main__":
    try:
        version_manager = VersionManager(CURRENT_VERSION, REPO_OWNER, REPO_NAME)
        version_manager.check_for_updates()
    except Exception as e:
        logger.error("Version manager error: %s", e)

    tracker = WTStatTracker()
    try:
        tracker.run()
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received. Exiting...")
    except Exception as e:
        logger.error("An unexpected error occurred: %s", e)
