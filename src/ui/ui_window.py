from tkinter import Tk, ttk, StringVar, Label, Button, Frame

from src.file_manager import FileManager

from typing import TYPE_CHECKING

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
        self.summary_label = None  # Initialize summary_label as None
        self.sort_column = None
        self.sort_reverse = False  # Track sorting order

    def show(self):
        """Show the UI window."""
        if self.window is not None:
            self.window.lift()
            return

        self.window = Tk()
        self.window.title("WTStatTracker - Battles")
        self.window.geometry("1200x600")  # Adjust width for longer headers

        # Initialize StringVars after the root window is created
        self.nation_filter_var = StringVar(value="All")
        self.battle_type_filter_var = StringVar(value="All")

        # Filters and actions section
        filter_frame = Frame(self.window)
        filter_frame.pack(fill="x", padx=10, pady=5)

        Label(filter_frame, text="Nation Filter:").pack(side="left", padx=5)
        self.nation_filter_dropdown = ttk.Combobox(
            filter_frame,
            textvariable=self.nation_filter_var,
            values=["All", "USA", "Germany", "USSR", "France", "UK"],
        )
        self.nation_filter_dropdown.pack(side="left", padx=5)
        self.nation_filter_dropdown.bind("<<ComboboxSelected>>", self.apply_filters)
        self.nation_filter_dropdown.current(0)

        Label(filter_frame, text="Battle Type Filter:").pack(side="left", padx=5)
        self.battle_type_dropdown = ttk.Combobox(
            filter_frame,
            textvariable=self.battle_type_filter_var,
            values=["All", "Ground", "Air"],
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

        # Set column headings
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

        # Set column widths
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

        # Summary section
        summary_frame = Frame(self.window, bg="#f0f0f0", relief="sunken", height=30)
        summary_frame.pack(fill="x", padx=10, pady=5)

        self.summary_label = Label(
            summary_frame,
            text="Summary: Total Games: 0 | Wins: 0 | Losses: 0 | Silver Earned: 0 | Exp Earned: 0",
            anchor="w",
        )
        self.summary_label.pack(fill="x", padx=5)

        self.refresh_ui()  # Start the periodic UI refresh

        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.mainloop()

    def update(self):
        filtered_battles = self.tracker.get_battles()
        self.populate_table(filtered_battles)

    def refresh_ui(self):
        """Periodically refresh the table and summary."""
        self.update()
        self.window.after(1000, self.refresh_ui)  # Refresh every second

    def close(self):
        """Close the UI window and terminate the application."""
        if self.window:
            self.window.destroy()
            self.tracker.stop()

    def populate_table(self, battles):
        """Populate the table with battles."""
        for row in self.battle_table.get_children():
            # Check if row is not empty
            try:
                if row:
                    self.battle_table.delete(row)
            except:
                pass

        for battle in battles:
            duration = battle.get(
                "Duration", "0:0"
            )  # Default to "0:0" if Duration is missing
            minutes, seconds = map(
                int, duration.split(":")
            )  # Split and convert to integers
            total_minutes = minutes + seconds / 60  # Convert total time to minutes

            # Calculate silver and experience per minute
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
        battles = FileManager.read_result_dialog()
        self.tracker.set_battles(battles)

    def save_json(self):
        FileManager.save_result_dialog(self.tracker._battles)

    def sort_by(self, column):
        """Sort the table by the given column."""
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
        """Apply filters and update the table."""
        nation_filter = self.nation_filter_dropdown.get().lower()
        battle_type_filter = self.battle_type_dropdown.get().lower()

        self.tracker.filter_manager.set_nation_filter(nation_filter)
        self.tracker.filter_manager.set_battle_type_filter(battle_type_filter)

    def clear_filters(self):
        """Clear all filters and refresh the table."""
        self.tracker.filter_manager.clear_filters()
        self.nation_filter_var.set("All")
        self.battle_type_filter_var.set("All")

    def update_summary(self, battles):
        """Update the summary row based on battles."""
        if not self.summary_label:  # Ensure summary_label is initialized
            return

        total_games = len(battles)
        wins = sum(1 for battle in battles if battle.get("Win/Lose") == "Victory")
        losses = total_games - wins
        percentage = f"{(wins / total_games * 100):.1f}%" if total_games > 0 else "0%"
        total_silver = sum(battle.get("Silver Lions", 0) for battle in battles)
        total_exp = sum(battle.get("Experience", 0) for battle in battles)

        total_minutes = 0
        for battle in battles:
            duration = battle.get("Duration", "0:0")  # Default to "0:0"
            try:
                minutes, seconds = map(int, duration.split(":"))
                total_minutes += minutes + seconds / 60
            except ValueError:
                continue  # Skip invalid duration formats

        # Calculate averages
        avg_silver_per_min = total_silver / total_minutes if total_minutes > 0 else 0
        avg_exp_per_min = total_exp / total_minutes if total_minutes > 0 else 0

        self.summary_label.config(
            text=f"Summary: Games {wins}-{losses} ({ percentage }) | Duration: {total_minutes:.1f} min | "
            f"Silver Earned: {total_silver:,} | Exp Earned: {total_exp:,} | Avg Silver: {avg_silver_per_min:.1f} | Avg Exp: {avg_exp_per_min:.1f}"
        )
