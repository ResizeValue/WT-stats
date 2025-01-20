import threading

from tabulate import tabulate

class ConsoleManager:
    """Manager to handle console input and commands."""

    def __init__(self, tracker):
        self.tracker = tracker
        self.console_thread = None
        self.running = False

    def run_console(self):
        """Start the console in a separate thread."""
        if not self.running:
            self.running = True
            self.console_thread = threading.Thread(target=self._console_loop, daemon=True)
            self.console_thread.start()

    def _console_loop(self):
        """Continuously read and process console commands."""
        print("Console started. Type 'help' for available commands.")
        while self.running:
            try:
                command = input("> ").strip()
                if command == "exit":
                    print("Exiting console mode...")
                    self.running = False
                elif command.startswith("filter nat"):
                    _, _, nation = command.split(maxsplit=2)
                    self.tracker.filter_manager.set_nation_filter(nation)
                    self.tracker.apply_filters_and_update()
                elif command.startswith("filter bt"):
                    _, _, battle_type = command.split(maxsplit=2)
                    self.tracker.filter_manager.set_battle_type_filter(battle_type)
                    self.tracker.apply_filters_and_update()
                elif command == "clear filters":
                    self.tracker.filter_manager.clear_filters()
                    self.tracker.apply_filters_and_update()
                elif command == "help":
                    print("Available commands:")
                    print("  filter nat <nation>    - Filter by nation (e.g., usa, germany)")
                    print("  filter bt <type>       - Filter by battle type (e.g., ground, air)")
                    print("  clear filters          - Clear all filters")
                    print("  exit                   - Exit console mode")
                else:
                    print("Unknown command. Type 'help' for available commands.")
            except Exception as e:
                print(f"Error processing command: {e}")

    def stop_console(self):
        """Stop the console thread."""
        self.running = False
        if self.console_thread:
            self.console_thread.join()

    @staticmethod
    def print_battle_list(battles):
        """
        Prints a formatted table of battles.

        Args:
            battles (list): A list of dictionaries, where each dictionary represents a battle.
        """
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

        table = [
            [
                battle["Win/Lose"],
                battle["Map"],
                battle["Nation"],
                battle["Battle Type"],
                battle["Duration"],
                battle["Kills"],
                battle["Silver Lions"],
                battle["Experience"],
                f"{battle['Silver/Min']:.2f}",
                f"{battle['Exp/Min']:.2f}",
            ]
            for battle in battles
        ]

        print("=== Battles List ===")
        print(tabulate(table, headers=headers, tablefmt="grid"))

    @staticmethod
    def print_summary(battles):
        """
        Prints a summary table of the battles.

        Args:
            battles (list): A list of dictionaries, where each dictionary represents a battle.
        """
        
        total_wins = sum(1 for b in battles if b["Win/Lose"] == "Victory")
        total_battles = len(battles)
        winrate = (total_wins / total_battles) * 100 if total_battles > 0 else 0
        total_battles_str = f"{total_battles} ({winrate:.2f}%)"
        total_loses = total_battles - total_wins
        total_kills = sum(b["Kills"] for b in battles)
        total_silver = sum(b["Silver Lions"] for b in battles)
        total_exp = sum(b["Experience"] for b in battles)
        avg_silver_per_min = (
            sum(b["Silver/Min"] for b in battles) / total_battles
            if total_battles > 0
            else 0
        )
        avg_exp_per_min = (
            sum(b["Exp/Min"] for b in battles) / total_battles
            if total_battles > 0
            else 0
        )

        summary_table = [
            ["Total Battles", total_battles_str],
            ["Wins", total_wins],
            ["Losses", total_loses],
            ["Total Kills", total_kills],
            ["Total Silver", total_silver],
            ["Total Experience", total_exp],
            ["Avg Silver/Min", f"{avg_silver_per_min:.2f}"],
            ["Avg Exp/Min", f"{avg_exp_per_min:.2f}"],
        ]

        print("=== Summary ===")
        print(tabulate(summary_table, tablefmt="grid"))
