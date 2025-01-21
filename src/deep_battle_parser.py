import re

import src.data.vehicles as vehicles
import src.data.vehicles_ru as vehicles_ru


class BattleParser:
    @staticmethod
    def parse_researched_units(text):
        """
        Parse all researched units from the battle text for multiple languages.

        Args:
            text (str): The full battle log or text.

        Returns:
            list: A list of researched unit names.
        """
        # Detect the language and parse accordingly
        if "Researched unit:" in text:  # English
            return BattleParser._parse_researched_units(text, "en")
        elif "Исследуемая техника:" in text:  # Russian
            return BattleParser._parse_researched_units(text, "ru")
        else:
            print("Unknown language for researched units.")
            return []

    @staticmethod
    def _parse_researched_units(text, lang):
        """
        Parse all researched units from the battle text based on language.

        Args:
            text (str): The full battle log or text.
            lang (str): The language of the log ('en' for English, 'ru' for Russian).

        Returns:
            list: A list of researched unit names.
        """
        if lang == "en":
            pattern = r"Researched unit:\s+([\s\S]+?)(?:\n\n|Researching progress|Session|Total)"
        elif lang == "ru":
            pattern = (
                r"Исследуемая техника:\s+([\s\S]+?)(?:\n\n|Сессия|Итого|Весь прогресс)"
            )
        else:
            print("Unsupported language for parsing researched units.")
            return []

        match = re.search(pattern, text)
        if match:
            unit_section = match.group(1).strip()
            return [
                line.split(":")[0].strip()
                for line in unit_section.splitlines()
                if ":" in line
            ]

        return []

    @staticmethod
    def parse_battle_info(text):
        """
        Extract battle information from the given text, supporting multiple languages.

        Args:
            text (str): The full battle log or text.

        Returns:
            dict: Extracted battle information.
        """

        if "Поражение" in text or "Победа" in text:
            print("Parsing battle info for Russian logs.")
            return BattleParser._parse_battle_info(text, "ru")
        elif "Victory" in text or "Defeat" in text:
            print("Parsing battle info for English logs.")
            return BattleParser._parse_battle_info(text, "en")
        else:
            print("Unknown language or unsupported format.")
            return None

    @staticmethod
    def _parse_battle_info(text, lang):
        """Parse battle information based on language.

        Args:
            text (str): The full battle log or text.
            lang (str): The language of the log ('en' for English, 'ru' for Russian).

        Returns:
            dict: Extracted battle information.
        """
        if lang == "en":
            result = "Victory" if "Victory" in text else "Defeat"
            map_pattern = r"(Victory|Defeat) in the \[.*?\]\s+(.*?)\s+mission"
            duration_pattern = r"Time Played\s+([\d:]+)"
            aircraft_kills_pattern = r"Destruction of aircraft\s+(\d+)"
            ground_kills_pattern = r"Destruction of ground vehicles\s+(\d+)"
            silver_pattern = r"Earned:\s([\d,]+) SL"
            exp_pattern = r"Earned:\s[\d,]+ SL,\s([\d,]+) CRP"
        elif lang == "ru":
            result = "Victory" if "Победа" in text else "Defeat"
            map_pattern = r"(Поражение|Победа) в миссии \"\[(.*?)\]\s+(.*?)\"."
            duration_pattern = r"Время игры\s+([\d:]+)"
            aircraft_kills_pattern = r"Уничтожение авиации\s+(\d+)"
            ground_kills_pattern = r"Уничтожение наземной техники\s+(\d+)"
            silver_pattern = r"Заработано:\s([\d,]+)\sСЛ"
            exp_pattern = r"Заработано:\s[\d,]+\sСЛ,\s([\d,]+)\sСОИ"
        else:
            print("Unsupported language.")
            return None

        # Extract map name
        map_match = re.search(map_pattern, text)
        map_name = (
            map_match.group(2)
            if lang == "en"
            else map_match.group(3) if map_match else "Unknown"
        )

        # Extract duration
        duration_match = re.search(duration_pattern, text)
        duration = duration_match.group(1) if duration_match else "Unknown"

        # Extract kills
        aircraft_kills = (
            int(re.search(aircraft_kills_pattern, text).group(1))
            if re.search(aircraft_kills_pattern, text)
            else 0
        )
        ground_kills = (
            int(re.search(ground_kills_pattern, text).group(1))
            if re.search(ground_kills_pattern, text)
            else 0
        )
        total_kills = aircraft_kills + ground_kills

        # Extract Silver Lions and Experience
        silver_match = re.search(silver_pattern, text)
        silver = int(silver_match.group(1).replace(",", "")) if silver_match else 0

        exp_match = re.search(exp_pattern, text)
        exp = int(exp_match.group(1).replace(",", "")) if exp_match else 0

        # Extract Battle Type and Nation
        additional_info = BattleParser.findout_battle_type(text).split(" ; ")
        battle_type = additional_info[0]
        nation = additional_info[1]

        # Calculate per-minute stats
        if ":" in duration:
            minutes = int(duration.split(":")[0]) + int(duration.split(":")[1]) / 60
            silver_per_min = silver / minutes if minutes > 0 else 0
            exp_per_min = exp / minutes if minutes > 0 else 0
        else:
            print("Invalid duration format.")
            return None

        return {
            "Win/Lose": result,
            "Map": map_name,
            "Nation": nation,
            "Battle Type": battle_type,
            "Duration": duration,
            "Kills": total_kills,
            "Silver Lions": silver,
            "Experience": exp,
            "Silver/Min": silver_per_min,
            "Exp/Min": exp_per_min,
        }

    @staticmethod
    def findout_battle_type(text):
        """
        Determine the battle type and nation based on researched units.

        Args:
            text (str): The full battle log or text.

        Returns:
            str: The battle type and nation in the format "type ; nation".
        """
        researched_units = BattleParser.parse_researched_units(text)

        if any(unit in researched_units for unit in vehicles.usa_tanks):
            return "ground ; USA"

        if any(unit in researched_units for unit in vehicles.usa_aircraft):
            return "air ; USA"

        if any(unit in researched_units for unit in vehicles.ussr_tanks):
            return "ground ; USSR"

        if any(unit in researched_units for unit in vehicles.ussr_aircraft):
            return "air ; USSR"

        if any(unit in researched_units for unit in vehicles.uk_tanks):
            return "ground ; UK"

        if any(unit in researched_units for unit in vehicles.german_ground_vehicles):
            return "ground ; Germany"

        if any(unit in researched_units for unit in vehicles.french_tanks):
            return "ground ; France"

        if any(unit in researched_units for unit in vehicles.french_aircraft):
            return "air ; France"

        if any(unit in researched_units for unit in vehicles_ru.ussr_tanks_ru):
            return "ground ; USSR"

        if any(unit in researched_units for unit in vehicles_ru.ussr_aircraft_ru):
            return "air ; USSR"

        return "Unknown ; Unknown"
