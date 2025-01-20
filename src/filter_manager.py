# typecheck

import typing

if typing.TYPE_CHECKING:
    from WTStatTracker import WTStatTracker


class FilterManager:
    """Manager to handle filtering of battles."""

    def __init__(self, tracker: "WTStatTracker"):
        self.nation_filter = None  # Filter by nation, e.g., 'usa', 'germany'
        self.battle_type_filter = None  # Filter by battle type, e.g., 'ground', 'air'
        self.tracker = tracker

    def apply_filters(self, battles):
        """Filter battles based on the current filters."""

        filtered_battles = battles
        if self.nation_filter:
            filtered_battles = [
                battle
                for battle in filtered_battles
                if battle.get("Nation").lower() == self.nation_filter.lower()
            ]
        if self.battle_type_filter:
            filtered_battles = [
                battle
                for battle in filtered_battles
                if battle.get("Battle Type").lower() == self.battle_type_filter.lower()
            ]
        return filtered_battles

    def set_nation_filter(self, nation):
        """Set the nation filter."""

        print(f"Nation filter set to: {nation}")

        if nation.lower() == "all":
            self.nation_filter = None
        else:
            self.nation_filter = nation

        print(f"Nation filter set to: {nation}")
        self.tracker.ui_manager.update()

    def set_battle_type_filter(self, battle_type):
        """Set the battle type filter."""

        if battle_type.lower() == "all":
            self.battle_type_filter = None
        else:
            self.battle_type_filter = battle_type

        print(f"Battle type filter set to: {battle_type}")
        self.tracker.ui_manager.update()

    def clear_filters(self):
        """Clear all filters."""

        self.nation_filter = None
        self.battle_type_filter = None
        print("All filters cleared.")
        self.tracker.ui_manager.update()
