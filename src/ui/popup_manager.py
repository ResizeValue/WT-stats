from threading import Thread, Lock
import tkinter as tk
import random


class PopupManager:
    def __init__(self):
        self.popups = {}  # Store references to popups by their IDs
        self.lock = Lock()  # Lock for thread-safe access to popups

    def show_popup(self, message, duration=0):
        """
        Display a popup notification in the top-right corner and return a reference to the popup.
        The popup can be manually closed using the popup ID.

        Args:
            message (str): The message to display in the popup.
        """

        popup_id = f"popup_{random.randint(1000, 9999)}"

        def popup():
            popup_window = tk.Tk()
            popup_window.overrideredirect(True)  # Remove the window border
            popup_window.geometry(
                f"250x50+{popup_window.winfo_screenwidth() - 260}+10"
            )  # Position at the top-right
            popup_window.attributes("-topmost", True)  # Keep it on top

            # Create a label for the message
            label = tk.Label(
                popup_window,
                text=message,
                bg="black",
                fg="white",
                font=("Helvetica", 10),
            )
            label.pack(expand=True, fill="both")

            # Store the popup reference in a thread-safe manner
            if popup_id:
                with self.lock:
                    self.popups[popup_id] = popup_window

            if duration > 0:
                # Schedule the popup to close after the specified duration
                popup_window.after(duration * 1000, popup_window.destroy)

            popup_window.mainloop()

        popup_thread = Thread(target=popup, daemon=True)
        popup_thread.start()
        return popup_id

    def close_popup(self, popup_id):
        """
        Close the popup by its ID.

        Args:
            popup_id (str): The ID of the popup to close.
        """
        with self.lock:
            if popup_id in self.popups:
                popup = self.popups.pop(popup_id)

                # Use after() to safely destroy the popup
                def destroy():
                    popup.destroy()

                popup.after(100, destroy)
