from tabulate import tabulate


class ConsolePrinter:
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
