import re
from src.vehicles import german_ground_vehicles, french_tanks, french_aircraft, usa_tanks, usa_aircraft, ussr_tanks, ussr_aircraft, uk_tanks
from src.vehicles_ru import ussr_aircraft_ru, ussr_tanks_ru


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
            return BattleParser._parse_researched_units_en(text)
        elif "Исследуемая техника:" in text:  # Russian
            return BattleParser._parse_researched_units_ru(text)
        else:
            print("Unknown language for researched units.")
            return []

    @staticmethod
    def _parse_researched_units_en(text):
        """
        Parse researched units from English logs.

        Args:
            text (str): The full battle log or text.

        Returns:
            list: A list of researched unit names.
        """
        
        print("Parsing researched units for English logs.")
        
        match = re.search(
            r"Researched unit:\s+([\s\S]+?)(?:\n\n|Researching progress|Session|Total)",
            text,
        )
        if match:
            unit_section = match.group(1).strip()
            return [
                line.split(":")[0].strip()
                for line in unit_section.splitlines()
                if ":" in line
            ]
        return []

    @staticmethod
    def _parse_researched_units_ru(text):
        """
        Parse researched units from Russian logs.

        Args:
            text (str): The full battle log or text.

        Returns:
            list: A list of researched unit names.
        """
        
        print("Parsing researched units for Russian logs.")
        
        match = re.search(
            r"Исследуемая техника:\s+([\s\S]+?)(?:\n\n|Сессия|Итого|Всего)",
            text,
        )
        if match:
            unit_section = match.group(1).strip()
            return [
                line.split(":")[0].strip()
                for line in unit_section.splitlines()
                if ":" in line or "x" in line
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
            return BattleParser.parse_battle_info_ru(text)
        elif "Victory" in text or "Defeat" in text:
            print("Parsing battle info for English logs.")
            return BattleParser.parse_battle_info_en(text)
        else:
            print("Unknown language or unsupported format.")
            return None
        
    @staticmethod
    def parse_battle_info_ru(text):
        """Parse battle information for Russian logs."""
        result = "Victory" if "Победа" in text else "Defeat"

        # Extract map name
        # Поражение в миссии "[Операция] Голанские высоты".
        map_match = re.search(r"Поражение в миссии \"\[(.*?)\]\s+(.*?)\".", text) or re.search(r"Победа в миссии \"\[(.*?)\]\s+(.*?)\".", text)
        map_name = map_match.group(2) if map_match else "Unknown"

        # Extract duration
        duration_match = re.search(r"Время игры\s+([\d:]+)", text)
        duration = duration_match.group(1) if duration_match else "Unknown"

        # Extract kills
        aircraft_kills = (
            int(re.search(r"Уничтожение авиации\s+(\d+)", text).group(1))
            if "Уничтожение авиации" in text
            else 0
        )
        ground_kills = (
            int(re.search(r"Уничтожение наземной техники\s+(\d+)", text).group(1))
            if "Уничтожение наземной техники" in text
            else 0
        )
        total_kills = aircraft_kills + ground_kills

        # Extract Silver Lions and Experience
        silver_match = re.search(r"Заработано:\s([\d,]+)\sСЛ", text)
        silver = int(silver_match.group(1).replace(",", "")) if silver_match else 0

        exp_match = re.search(r"Заработано:\s[\d,]+\sСЛ,\s([\d,]+)\sСОИ", text)
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
    def parse_battle_info_en(text):
        """Parse battle information for English logs."""
        result = "Victory" if "Victory" in text else "Defeat"

        # Extract map name
        map_match = re.search(
            r"Victory in the \[.*?\]\s+(.*?)\s+mission", text
        ) or re.search(r"Defeat in the \[.*?\]\s+(.*?)\s+mission", text)
        map_name = map_match.group(1) if map_match else "Unknown"

        # Extract duration
        duration_match = re.search(r"Time Played\s+([\d:]+)", text)
        duration = duration_match.group(1) if duration_match else "Unknown"

        # Extract kills
        aircraft_kills = (
            int(re.search(r"Destruction of aircraft\s+(\d+)", text).group(1))
            if "Destruction of aircraft" in text
            else 0
        )
        ground_kills = (
            int(re.search(r"Destruction of ground vehicles\s+(\d+)", text).group(1))
            if "Destruction of ground vehicles" in text
            else 0
        )
        total_kills = aircraft_kills + ground_kills

        # Extract Silver Lions and Experience
        silver_match = re.search(r"Earned:\s([\d,]+) SL", text)
        silver = int(silver_match.group(1).replace(",", "")) if silver_match else 0

        exp_match = re.search(r"Earned:\s[\d,]+ SL,\s([\d,]+) CRP", text)
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
        
        if any(unit in researched_units for unit in usa_tanks):
            return "ground ; USA"
        
        if any(unit in researched_units for unit in usa_aircraft):
            return "air ; USA"
        
        if any(unit in researched_units for unit in ussr_aircraft):
            return "air ; USSR"
            
        if any(unit in researched_units for unit in ussr_tanks):
            return "ground ; USSR"
        
        if any(unit in researched_units for unit in uk_tanks):
            return "ground ; UK"

        if any(unit in researched_units for unit in german_ground_vehicles):
            return "ground ; Germany"

        if any(unit in researched_units for unit in french_tanks):
            return "ground ; France"

        if any(unit in researched_units for unit in french_aircraft):
            return "air ; France"
        
        if any(unit in researched_units for unit in ussr_tanks_ru):
            return "ground ; USSR"

        if any(unit in researched_units for unit in ussr_aircraft_ru):
            return "air ; USSR"

        return "Unknown ; Unknown"
