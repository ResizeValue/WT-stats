from tkinter import Tk, ttk, StringVar, Label, Button, Frame, Toplevel
from typing import TYPE_CHECKING

from src.settings import CURRENT_VERSION

if TYPE_CHECKING:
    from WTStatTracker import WTStatTracker


class UIWindow:
    """UI window for displaying battles and filters."""

    def __init__(self, tracker: "WTStatTracker"):
        """
        Initialize the UI window.

        Args:
            tracker (WTStatTracker): Reference to the WTStatTracker instance.
        """
        self.tracker = tracker
        self.window = None
        self.battle_table = None
        self.summary_label = None
        self.sort_column = None
        self.sort_reverse = False

        # NEW OR MODIFIED CODE
        # Predefined list of Nations & Battle Types for editing
        self.available_nations = [
            "USA",
            "Germany",
            "USSR",
            "France",
            "UK",
            "Japan",
            "Italy",
            "China",
            "Sweden",
            "Israel",
        ]
        self.available_battle_types = ["Ground", "Air"]

    def show(self):
        """Show the UI window."""
        if self.window is not None:
            self.window.lift()
            return

        self.window = Tk()
        self.window.title("WTStatTracker v" + CURRENT_VERSION + " - Battles")
        self.window.geometry("1200x600")  # Adjust width for longer headers

        self.nation_filter_var = StringVar(value="All")
        self.battle_type_filter_var = StringVar(value="All")

        # Filters and actions section
        filter_frame = Frame(self.window)
        filter_frame.pack(fill="x", padx=10, pady=5)

        Label(filter_frame, text="Nation Filter:").pack(side="left", padx=5)
        self.nation_filter_dropdown = ttk.Combobox(
            filter_frame,
            textvariable=self.nation_filter_var,
            values=["All"] + self.available_nations,
        )
        self.nation_filter_dropdown.pack(side="left", padx=5)
        self.nation_filter_dropdown.bind("<<ComboboxSelected>>", self.apply_filters)
        self.nation_filter_dropdown.current(0)

        Label(filter_frame, text="Battle Type Filter:").pack(side="left", padx=5)
        self.battle_type_dropdown = ttk.Combobox(
            filter_frame,
            textvariable=self.battle_type_filter_var,
            values=["All"] + self.available_battle_types,
        )
        self.battle_type_dropdown.pack(side="left", padx=5)
        self.battle_type_dropdown.bind("<<ComboboxSelected>>", self.apply_filters)
        self.battle_type_dropdown.current(0)

        Button(filter_frame, text="Clear Filters", command=self.clear_filters).pack(
            side="left", padx=10
        )
        Button(filter_frame, text="Open JSON", command=self.open_json).pack(
            side="left", padx=10
        )
        Button(filter_frame, text="Save JSON", command=self.save_json).pack(
            side="left", padx=10
        )
        Button(filter_frame, text="New Session", command=self.tracker.new_session).pack(
            side="left", padx=10
        )
        Button(
            filter_frame,
            text="Toggle Live Stat",
            command=self.tracker.ui_manager.live_stats.toggle,
        ).pack(side="left", padx=10)

        # Battle table
        self.battle_table = ttk.Treeview(
            self.window,
            columns=(
                "Win/Lose",
                "Map",
                "Nation",
                "Battle Type",
                "Duration (min)",
                "Kills",
                "Silver Lions",
                "Experience",
                "Silver/Min",
                "Exp/Min",
            ),
            show="headings",
        )
        self.battle_table.pack(fill="both", expand=True, padx=10, pady=10)

        headers = [
            "Win/Lose",
            "Map",
            "Nation",
            "Battle Type",
            "Duration (min)",
            "Kills",
            "Silver Lions",
            "Experience",
            "Silver/Min",
            "Exp/Min",
        ]
        for header in headers:
            self.battle_table.heading(
                header, text=header, command=lambda h=header: self.sort_by(h)
            )

        self.battle_table.column("Win/Lose", width=100, anchor="center")
        self.battle_table.column("Map", width=200, anchor="w")
        self.battle_table.column("Nation", width=100, anchor="center")
        self.battle_table.column("Battle Type", width=100, anchor="center")
        self.battle_table.column("Duration (min)", width=120, anchor="center")
        self.battle_table.column("Kills", width=80, anchor="center")
        self.battle_table.column("Silver Lions", width=120, anchor="e")
        self.battle_table.column("Experience", width=120, anchor="e")
        self.battle_table.column("Silver/Min", width=100, anchor="e")
        self.battle_table.column("Exp/Min", width=100, anchor="e")

        # NEW OR MODIFIED CODE
        # Bind a double-click event on the table
        self.battle_table.bind("<Double-1>", self.on_row_double_click)

        # Summary section
        summary_frame = Frame(self.window, bg="#f0f0f0", relief="sunken", height=30)
        summary_frame.pack(fill="x", padx=10, pady=5)

        self.summary_label = Label(
            summary_frame,
            text="Summary: Total Games: 0 | Wins: 0 | Losses: 0 | Silver Earned: 0 | Exp Earned: 0",
            anchor="w",
        )
        self.summary_label.pack(fill="x", padx=5)

        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.mainloop()

    def update(self):
        filtered_battles = self.tracker.get_battles()
        self.populate_table(filtered_battles)

    def close(self):
        """Close the UI window and terminate the application."""
        if self.window:
            self.window.destroy()
            self.tracker.stop()

    def populate_table(self, battles):
        """Populate the table with battles."""
        for row in self.battle_table.get_children():
            try:
                self.battle_table.delete(row)
            except:
                pass

        # NEW OR MODIFIED CODE
        # Insert battles with an 'iid' that matches their index in the list.
        for i, battle in enumerate(battles):
            duration = battle.get("Duration", "0:0")
            minutes, seconds = map(int, duration.split(":"))
            total_minutes = minutes + seconds / 60

            silver_per_min = (
                battle.get("Silver Lions", 0) / total_minutes
                if total_minutes > 0
                else 0
            )
            exp_per_min = (
                battle.get("Experience", 0) / total_minutes if total_minutes > 0 else 0
            )

            self.battle_table.insert(
                "",
                "end",
                iid=str(i),  # store index as string ID
                values=(
                    battle.get("Win/Lose"),
                    battle.get("Map", "Unknown"),
                    battle.get("Nation"),
                    battle.get("Battle Type"),
                    duration,
                    battle.get("Kills"),
                    battle.get("Silver Lions"),
                    battle.get("Experience"),
                    f"{silver_per_min:.1f}",
                    f"{exp_per_min:.1f}",
                ),
            )

        self.update_summary(battles)

    def open_json(self):
        from src.file_manager import FileManager

        battles = FileManager.read_result_dialog()
        self.tracker.set_battles(battles)

    def save_json(self):
        from src.file_manager import FileManager

        FileManager.save_result_dialog(self.tracker._battles)

    def sort_by(self, column):
        if column == self.sort_column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        battles = self.tracker.get_battles()
        if column in ["Silver Lions", "Experience", "Kills"]:
            sorted_battles = sorted(
                battles,
                key=lambda b: b.get(column.replace(" ", "_"), 0),
                reverse=self.sort_reverse,
            )
        elif column == "Duration (min)":
            sorted_battles = sorted(
                battles,
                key=lambda b: sum(
                    int(x) * 60**i
                    for i, x in enumerate(
                        reversed(b.get("Duration", "0:00").split(":"))
                    )
                ),
                reverse=self.sort_reverse,
            )
        else:
            sorted_battles = sorted(
                battles,
                key=lambda b: b.get(column, "").lower(),
                reverse=self.sort_reverse,
            )

        self.populate_table(sorted_battles)

    def apply_filters(self, event=None):
        nation_filter = self.nation_filter_dropdown.get().lower()
        battle_type_filter = self.battle_type_dropdown.get().lower()

        self.tracker.filter_manager.set_nation_filter(nation_filter)
        self.tracker.filter_manager.set_battle_type_filter(battle_type_filter)

        self.update()

    def clear_filters(self):
        self.tracker.filter_manager.clear_filters()
        self.nation_filter_var.set("All")
        self.battle_type_filter_var.set("All")
        self.update()

    def update_summary(self, battles):
        if not self.summary_label:
            return

        total_games = len(battles)
        wins = sum(1 for battle in battles if battle.get("Win/Lose") == "Victory")
        losses = total_games - wins
        percentage = f"{(wins / total_games * 100):.1f}%" if total_games > 0 else "0%"
        total_silver = sum(battle.get("Silver Lions", 0) for battle in battles)
        total_exp = sum(battle.get("Experience", 0) for battle in battles)

        total_minutes = 0
        for battle in battles:
            duration = battle.get("Duration", "0:0")
            try:
                minutes, seconds = map(int, duration.split(":"))
                total_minutes += minutes + seconds / 60
            except ValueError:
                continue

        avg_silver_per_min = total_silver / total_minutes if total_minutes > 0 else 0
        avg_exp_per_min = total_exp / total_minutes if total_minutes > 0 else 0

        self.summary_label.config(
            text=(
                f"Summary: Games {wins}-{losses} ({percentage}) | "
                f"Duration: {total_minutes:.1f} min | "
                f"Silver Earned: {total_silver:,} | Exp Earned: {total_exp:,} | "
                f"Avg Silver: {avg_silver_per_min:.1f} | Avg Exp: {avg_exp_per_min:.1f}"
            )
        )

    # NEW OR MODIFIED CODE
    def on_row_double_click(self, event):
        """
        Handle double-click on a table row. Opens a small popup
        to let the user modify Nation or Battle Type.
        """
        selected_item = self.battle_table.selection()
        if not selected_item:
            return

        # The treeview IID is the index of the battle in the underlying list
        battle_index = int(selected_item[0])
        battles = self.tracker.get_battles()
        if battle_index >= len(battles):
            return
        battle = battles[battle_index]

        # Create a top-level window for editing
        edit_window = Toplevel(self.window)
        edit_window.title("Edit Battle")

        Label(edit_window, text="Nation:").grid(row=0, column=0, padx=10, pady=5)
        Label(edit_window, text="Battle Type:").grid(row=1, column=0, padx=10, pady=5)

        print("Battle double click:", battle)

        nation_var = StringVar(value=battle.get("Nation", ""))
        nation_combo = ttk.Combobox(
            edit_window, textvariable=nation_var, values=self.available_nations
        )
        nation_combo.grid(row=0, column=1, padx=10, pady=5)

        battle_type_var = StringVar(value=battle.get("Battle Type", ""))
        battle_type_combo = ttk.Combobox(
            edit_window,
            textvariable=battle_type_var,
            values=self.available_battle_types,
        )
        battle_type_combo.grid(row=1, column=1, padx=10, pady=5)

        def save_changes():
            # Update the selected battle in memory
            battle["Nation"] = nation_var.get()
            battle["Battle Type"] = battle_type_var.get()

            # Refresh table
            self.populate_table(battles)
            edit_window.destroy()

        def cancel_changes():
            edit_window.destroy()

        Button(edit_window, text="Save", command=save_changes).grid(
            row=2, column=0, padx=10, pady=5
        )
        Button(edit_window, text="Cancel", command=cancel_changes).grid(
            row=2, column=1, padx=10, pady=5
        )

        edit_window.grab_set()  # Make this window modal
        edit_window.focus()
