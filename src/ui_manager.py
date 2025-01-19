from threading import Thread, Lock
import tkinter as tk


class UIManager:
    def __init__(self):
        self.popups = {}  # Store references to popups by their IDs
        self.lock = Lock()  # Lock for thread-safe access to popups

    def show_popup(self, message, popup_id=None, duration=0):
        """
        Display a popup notification in the top-right corner and return a reference to the popup.
        The popup can be manually closed using the popup ID.

        Args:
            message (str): The message to display in the popup.
            popup_id (str): An optional ID for the popup to manage it.
        """
        def popup():
            popup_window = tk.Tk()
            popup_window.overrideredirect(True)  # Remove the window border
            popup_window.geometry(
                f"250x50+{popup_window.winfo_screenwidth() - 260}+10"
            )  # Position at the top-right
            popup_window.attributes("-topmost", True)  # Keep it on top

            # Create a label for the message
            label = tk.Label(
                popup_window, text=message, bg="black", fg="white", font=("Helvetica", 10)
            )
            label.pack(expand=True, fill="both")

            # Store the popup reference in a thread-safe manner
            if popup_id:
                with self.lock:
                    self.popups[popup_id] = popup_window

            if duration > 0:
                popup_window.after(duration * 1000, lambda: self.close_popup(popup_id))
                
            popup_window.mainloop()

        popup_thread = Thread(target=popup, daemon=True)
        popup_thread.start()

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

    def show_running_indicator(self):
        """
        Display a small stylish indicator with 'WT Stats' text in the top-left corner.
        """
        def indicator():
            root = tk.Tk()
            root.overrideredirect(True)  # Remove window borders
            root.geometry("100x30+10+10")  # Small rectangle at top-left corner
            root.attributes("-topmost", True)  # Keep it on top

            # Set modern styling
            frame = tk.Frame(root, bg="#282C34", bd=0)  # Dark background
            frame.pack(fill="both", expand=True)

            # Add the text
            label = tk.Label(
                frame,
                text="WT Stats",
                font=("Helvetica", 10, "bold"),
                fg="white",
                bg="#282C34",
            )
            label.pack(expand=True)

            root.mainloop()

        # Run the indicator in a separate thread to avoid blocking the main program
        Thread(target=indicator, daemon=True).start()
