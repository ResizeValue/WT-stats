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
        activity_units = BattleParser.parse_time_played_vehicles(text)
        keys = activity_units.keys()

        print("\n\n")
        print("Vehicle keys:", keys)
        print("\n\n")

        if any(unit in keys for unit in vehicles.usa_tanks):
            return "ground ; USA"

        if any(unit in keys for unit in vehicles.usa_aircraft):
            return "air ; USA"

        if any(unit in keys for unit in vehicles.ussr_tanks):
            return "ground ; USSR"

        if any(unit in keys for unit in vehicles.ussr_aircraft):
            return "air ; USSR"

        if any(unit in keys for unit in vehicles.uk_tanks):
            return "ground ; UK"

        if any(unit in keys for unit in vehicles.german_ground_vehicles):
            return "ground ; Germany"

        if any(unit in keys for unit in vehicles.german_aircraft):
            return "air ; Germany"

        if any(unit in keys for unit in vehicles.french_tanks):
            return "ground ; France"

        if any(unit in keys for unit in vehicles.french_aircraft):
            return "air ; France"

        if any(unit in keys for unit in vehicles.japan_tanks):
            return "ground ; Japan"

        # if any(unit in keys for unit in vehicles.japan_aircraft):
        #     return "air ; Japan"

        if any(unit in keys for unit in vehicles.italy_tanks):
            return "ground ; Italy"

        # if any(unit in keys for unit in vehicles.italy_aircraft):
        #     return "air ; Italy"

        if any(unit in keys for unit in vehicles.sweden_tanks):
            return "ground ; Sweden"

        # if any(unit in keys for unit in vehicles.sweden_aircraft):
        #     return "air ; Sweden"

        if any(unit in keys for unit in vehicles.china_tanks):
            return "ground ; China"

        # if any(unit in keys for unit in vehicles.china_aircraft):
        #     return "air ; China"

        if any(unit in keys for unit in vehicles.israel_tanks):
            return "ground ; Israel"

        if any(unit in keys for unit in vehicles_ru.ussr_tanks_ru):
            return "ground ; USSR"

        if any(unit in keys for unit in vehicles_ru.ussr_aircraft_ru):
            return "air ; USSR"

        return "Unknown ; Unknown"

    @staticmethod
    def parse_time_played_vehicles(text):
        """
        Parse vehicles (with their played-time parameters) from the "Time Played" / "Время игры" section.

        For English logs the section header is "Time Played" and the reward is labeled "RP".
        For Russian logs the header is "Время игры" and the reward is labeled "ОИ".

        Example English section:

            Time Played                     11:57                15865 RP
                Mirage F1C-200    86%    11:57    3777 + (PA)7555 + (Booster)756 + (Talismans)3777 = 15865 RP

        Example Russian section:

            Время игры                            4:52                6544 ОИ
                Mirage F1C-200    87%    4:52    1558 + (ПА)3116 + (Усилитель)312 + (Талисманы)1558 = 6544 ОИ

        Returns:
            dict: A dictionary mapping vehicle names to a dict with keys:
                  - For English logs: "RP", "percent", "duration"
                  - For Russian logs: "ОИ", "percent", "duration"
        """
        # Detect language based on the header present
        if "Время игры" in text:
            # Russian log
            block_pattern = r"Время игры\s+[\d:]+\s+[\d,]+\s*ОИ\s*\n((?:\s+.*\n)+)"
            line_pattern = re.compile(
                r"^\s*(?P<vehicle>.+?)\s+(?P<percent>\d+%)\s+(?P<duration>[\d:]+)\s+.*?=\s*(?P<oi_total>\d+)\s*ОИ",
                re.MULTILINE,
            )
            reward_key = "ОИ"
        elif "Time Played" in text:
            # English log
            block_pattern = r"Time Played\s+[\d:]+\s+[\d,]+\s*RP\s*\n((?:\s+.*\n)+)"
            line_pattern = re.compile(
                r"^\s*(?P<vehicle>.+?)\s+(?P<percent>\d+%)\s+(?P<duration>[\d:]+)\s+.*?=\s*(?P<rp_total>\d+)\s*RP",
                re.MULTILINE,
            )
            reward_key = "RP"
        else:
            print("No recognized 'Time Played' or 'Время игры' section found.")
            return {}

        block_match = re.search(block_pattern, text)
        if not block_match:
            print("No time-played block found.")
            return {}

        block = block_match.group(1)
        vehicles_time_played = {}

        for match in line_pattern.finditer(block):
            vehicle = match.group("vehicle").strip()
            percent = match.group("percent").strip()
            duration = match.group("duration").strip()
            # Depending on language, extract the reward using the correct group name.
            if reward_key == "ОИ":
                reward = int(match.group("oi_total"))
            else:
                reward = int(match.group("rp_total"))
            vehicles_time_played[vehicle] = {
                reward_key: reward,
                "percent": percent,
                "duration": duration,
            }

        return vehicles_time_played


# --- Example usage ---
if __name__ == "__main__":
    # Example English log snippet
    english_log = r"""
Victory in the [Operation] Battle for Vietnam mission!

Destruction of aircraft             1     2944 SL      228 RP    
    5:15    Mirage F1C-200    Matra R550 Magic 2    MiG-23MLA()     89 mission points    Own target (the rest of the reward)    1784 + (PA)892 + (Booster)268 = 2944 SL    54 + (PA)109 + (Booster)11 + (Talismans)54 = 228 RP

... (other sections) ...

Time Played                     11:57                15865 RP    
    Mirage F1C-200    86%    11:57    3777 + (PA)7555 + (Booster)756 + (Talismans)3777 = 15865 RP

... (rest of log) ...
    """

    # Example Russian log snippet
    russian_log = r"""
Победа в миссии "[Альтернативная история] Испания"!

Уничтожение авиации                      1     2944 СЛ     228 ОИ    
    3:38    Mirage F1C-200    Matra R550 Magic 2    F-111F     89 очков миссии    Своей цели (остаток награды)    1784 + (ПА)892 + (Усилитель)268 = 2944 СЛ    54 + (ПА)109 + (Усилитель)11 + (Талисманы)54 = 228 ОИ

... (other sections) ...

Время игры                            4:52                6544 ОИ    
    Mirage F1C-200    87%    4:52    1558 + (ПА)3116 + (Усилитель)312 + (Талисманы)1558 = 6544 ОИ

... (rest of log) ...
    """

    print("English Time Played Vehicles:")
    vehicles_played_en = BattleParser.parse_time_played_vehicles(english_log)
    print(vehicles_played_en)

    print("\nRussian Time Played Vehicles:")
    vehicles_played_ru = BattleParser.parse_time_played_vehicles(russian_log)
    print(vehicles_played_ru)
