from threading import Thread, Event
import tkinter as tk
import ctypes

class LiveStatManager:
    """Manager to display game stats in the bottom-left corner as a single-row text."""

    def __init__(self, tracker):
        self.stats_window = None
        self.running = False
        self.tracker = tracker
        self.stop_event = Event()  # Event to signal the thread to stop
        self.frame = None

    def start(self):
        """Start the stats display."""
        if not self.running:
            self.running = True
            self.stop_event.clear()
            Thread(target=self._run_display, daemon=True).start()

    def stop(self):
        """Stop the stats display."""
        if self.running:
            self.running = False
            self.stop_event.set()  # Signal the thread to stop
            if self.stats_window:
                self.stats_window.quit()  # Safely end the mainloop
                self.stats_window = None

    def toggle(self):
        """Toggle the stats display."""
        if self.running:
            self.running = False
            self.frame.pack_forget()  # Hide the frame
        else:
            self.running = True
            self.frame.pack(expand=True, fill="both")

    def update(self):
        battles = self.tracker.get_battles()
        self._update_stats(battles)
    
    def _update_stats(self, battles):
        """
        Update the stats displayed in the window.

        Args:
            battles (list): List of battle information dictionaries.
        """
        if battles:
            # Calculate stats
            total_games = len(battles)
            wins = sum(1 for battle in battles if battle.get("Win/Lose") == "Victory")
            losses = total_games - wins
            total_silver = sum(battle.get("Silver Lions", 0) for battle in battles)
            total_exp = sum(battle.get("Experience", 0) for battle in battles)

            # Calculate total time in minutes
            total_minutes = sum(
                int(duration.split(":")[0]) * 60 + int(duration.split(":")[1])
                for battle in battles
                if (duration := battle.get("Duration", "0:00")).count(":") == 1
            )

            # Convert total minutes back to HH:MM format
            total_time = f"{total_minutes // 60}:{total_minutes % 60:02}"

            # Calculate average XP per game and win rate
            avg_exp_per_min = total_exp / total_minutes * 60 if total_minutes > 0 else 0
            win_rate = (wins / total_games * 100) if total_games > 0 else 0

            # Format stats as a single row
            stats_text = (
                f"WT Stats | {total_games} ; {wins}-{losses} ({win_rate:.1f}%) ; "
                f"{total_time} min ; {total_silver:,} sl ; {total_exp:,} exp ; {avg_exp_per_min:.1f} exp/min"
            )
        else:
            # Default message if no battles are found
            stats_text = "WT Stats | No battles found."

        # Update the label text
        if self.stats_window and self.stats_label:
            self.stats_label.config(text=stats_text)
            
    def _run_display(self):
        """Run the tkinter window to display stats."""
        # Enable DPI awareness for sharp rendering
        ctypes.windll.shcore.SetProcessDpiAwareness(1)

        self.stats_window = tk.Tk()
        self.stats_window.overrideredirect(True)  # Remove window borders
        self.stats_window.geometry(
            "450x20+0+0"
        )  # Position at bottom-left
        self.stats_window.attributes("-topmost", True)  # Keep it on top
        self.stats_window.configure(bg="#282C34")  # Semi-transparent dark background

        # Apply rounded corners (Windows only)
        self.stats_window.attributes("-transparentcolor", "#282C34")
        self.stats_window.wm_attributes("-alpha", 0.9)

        # Create a modern frame with padding
        self.frame = tk.Frame(
            self.stats_window,
            bg="#1E222A",
            relief="flat",
            border=1,
            padx=2,
            pady=2,
        )
        self.frame.pack(expand=True, fill="both")

        # Add a stylish label for stats
        self.stats_label = tk.Label(
            self.frame,
            text="",
            fg="white",
            bg="#1E222A",
            font=("Segoe UI", 8, "bold"),
            justify="left",
            anchor="w",
        )
        self.stats_label.pack(expand=True, fill="both")

        # Periodically check if stop_event is set
        self._periodic_check()

        self.stats_window.mainloop()

    def _periodic_check(self):
        """Check periodically if the stop event is set."""
        if self.stop_event.is_set():
            if self.stats_window:  # Ensure the stats_window is not None
                self.stats_window.quit()
        else:
            if self.stats_window:  # Ensure the stats_window is not None
                self.stats_window.after(100, self._periodic_check)

