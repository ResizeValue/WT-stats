from threading import Thread
from src.ui.live_stat_manager import LiveStatManager
from src.ui.popup_manager import PopupManager
from src.ui.ui_window import UIWindow


class UIManager:
    def __init__(self, tracker):
        self.popup_manager = PopupManager()
        self.live_stats = LiveStatManager(tracker)
        self.ui_window = UIWindow(tracker)
        self.tracker = tracker
        self.ui_window_thread = None
        
    def run_ui_window(self):
        """Run the UI window in a separate thread."""
        if self.ui_window_thread and self.ui_window_thread.is_alive():
            print("UI window is already running.")
            return

        self.ui_window_thread = Thread(target=self.ui_window.show, daemon=True)
        self.ui_window_thread.start()
    
    def stop_ui_window(self):
        """Stop the UI window thread."""
        if self.ui_window_thread and self.ui_window_thread.is_alive():
            self.ui_window_thread.join()
            
    def start(self):
        """Start the UI components."""
        self.live_stats.start()
        self.run_ui_window()
    
    def update(self):
        """Update the UI window with the latest stats."""
        thread = Thread(target=self._update, daemon=True)
        thread.start()
    
    def _update(self):
        """Update the UI window with the latest stats."""
        self.live_stats.update()
        self.ui_window.update()