import threading

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

