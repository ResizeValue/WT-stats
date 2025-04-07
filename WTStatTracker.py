import os
import logging
import traceback
from time import sleep
from threading import Timer, Thread
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import queue
import pyperclip
from pynput import keyboard

try:
    import win32gui
except ImportError:
    win32gui = None

from src.console_manager import ConsoleManager
from src.deep_battle_parser import BattleParser
from src.file_manager import FileManager
from src.filter_manager import FilterManager
from src.ui.ui_manager import UIManager

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


def is_war_thunder_in_focus():
    if win32gui is None:
        logger.warning("win32gui not available; assuming focus is valid.")
        return True
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
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.parsing_queue = queue.Queue()
        self.running = True
        self.hotkeys = None

        self.queue_thread = Thread(target=self.process_parsing_requests, daemon=True)

    def get_battles(self):
        return self.filter_manager.apply_filters(self._battles)

    def set_battles(self, battles):
        self._battles = battles
        self.ui_manager.update()

    def new_session(self):
        self._battles = []
        self.ui_manager.update()
        FileManager.auto_save(self._battles)

    def handle_clipboard_parsing(self, text):
        logger.info("Parsing clipboard text: %s", text)
        popup_id = self.ui_manager.popup_manager.show_popup("Parsing battle info...", 5)

        future = self.executor.submit(BattleParser.parse_battle_info, text)
        try:
            battle_info = future.result(timeout=5)
        except TimeoutError:
            logger.error("Parsing timed out.")
        except Exception as e:
            logger.error("Error parsing clipboard: %s", traceback.format_exc())
        else:
            if battle_info and not any(
                b.get("Duration") == battle_info.get("Duration")
                and b.get("Kills") == battle_info.get("Kills")
                for b in self._battles
            ):
                self._battles.append(battle_info)
                self.ui_manager.update()
                self.start_save_timer()
                logger.info("Battle info added successfully.")

        self.ui_manager.popup_manager.close_popup(popup_id)

    def process_parsing_requests(self):
        while self.running:
            try:
                request = self.parsing_queue.get(timeout=1)
                if request:
                    sleep(0.3)
                    logger.info("Processing parsing request: %s", request)
                    clipboard_text = pyperclip.paste()

                    if not clipboard_text:
                        logger.warning("Clipboard is empty.")
                        continue

                    self.handle_clipboard_parsing(clipboard_text)
                    self.parsing_queue.task_done()
            except queue.Empty:
                continue  # Avoid blocking indefinitely
            except Exception as e:
                logger.error(
                    "Error in parsing queue processing: %s", traceback.format_exc()
                )
            finally:
                sleep(0.1)  # Avoid busy waiting
                if not self.running:
                    logger.info("Stopping parsing request processing.")
                    break

    def trigger_parsing_request(self):
        if not is_war_thunder_in_focus():
            logger.info("Skipping parsing: War Thunder not in focus.")
            return

        logger.info("Adding parsing request to queue.")
        self.parsing_queue.put("parse_clipboard")

    def start_save_timer(self):
        if self._save_timer:
            self._save_timer.cancel()
        self._save_timer = Timer(10, self.save_battles)
        self._save_timer.start()
        logger.info("Save timer started.")

    def save_battles(self):
        FileManager.auto_save(self._battles)
        self._save_timer = None
        self.ui_manager.popup_manager.show_popup("Battles saved", 2)

    def run(self):
        logger.info("Starting application...")
        self.ui_manager.start()
        sleep(1)

        def log_and_execute(action_name, action):
            def wrapper():
                logger.info("Hotkey pressed: %s", action_name)
                action()

            return wrapper

        hotkey_actions = {
            "<ctrl>+c": log_and_execute(
                "Copy (trigger parsing request)", self.trigger_parsing_request
            ),
            "<end>": log_and_execute("End (stop application)", self.stop),
        }

        self.hotkeys = keyboard.GlobalHotKeys(hotkey_actions)
        sleep(0.2)
        self.hotkeys.start()
        sleep(1)
        self.hotkeys.join()
        sleep(1)
        logger.info("Hotkeys registered.")

        self._battles = FileManager.auto_load()
        sleep(0.5)
        self.ui_manager.update()
        sleep(0.1)

        self.queue_thread.start()
        logger.info("Parsing queue thread started.")
        logger.info("Application started.")

    def stop(self):
        logger.info("Stopping application.")
        self.running = False
        if self.hotkeys:
            self.hotkeys.stop()
        sleep(1)
        logger.info("Application stopped.")
        self.executor.shutdown(wait=False)
        os._exit(0)
