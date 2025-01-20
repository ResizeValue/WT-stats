from datetime import datetime
import json
import os
from tkinter import filedialog

class FileManager:
    def __init__(self, directory="results"):
        """Initialize the FileManager with a directory for storing results."""

        self.directory = directory

        if not os.path.exists(directory):
            os.makedirs(directory)
    
    @staticmethod
    def auto_save(data):
        """Save battles to a JSON file."""
        file_path = os.path.join(os.getcwd(), f"autosave.json")

        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)

        print(f"Auto-saved battles to {file_path}")

    @staticmethod
    def auto_load():
        """Load battles from the autosave file."""
        file_path = os.path.join(os.getcwd(), f"autosave.json")

        if not os.path.exists(file_path):
            return []

        with open(file_path, "r") as file:
            return json.load(file)

        print(f"Auto-loaded battles from {file_path}")

    @staticmethod
    def save_result(filename, data):
        """
        Save a result to a file in JSON format.

        Args:
            filename (str): The name of the file (without extension).
            data (dict): The data to save in the file.
        """

        filepath = os.path.join(os.getcwd(), f"results/{filename}.json")

        with open(filepath, "w") as file:
            json.dump(data, file, indent=4)

        print(f"Result saved to {filepath}")

    @staticmethod
    def save_result_dialog(data):
        """Save battles to a JSON file."""
        # Root/results directory
        default_dir = os.path.join(os.getcwd(), "results")

        # If the results directory doesn't exist, create it
        if not os.path.exists(default_dir):
            os.makedirs(default_dir)

        today_date = datetime.now().strftime("%Y-%m-%d")

        file_path = filedialog.asksaveasfilename(
            title="Save JSON File",
            initialdir=default_dir,  # Set default directory
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            initialfile=f"{today_date}.json",
        )

        if not file_path:
            return

        with open(file_path, "w") as file:
            return json.dump(data, file, indent=4)

    @staticmethod
    def read_result(filename):
        """
        Read a result from a file.

        Args:
            filename (str): The name of the file (without extension).

        Returns:
            dict: The data read from the file.
        """

        filepath = os.path.join(os.getcwd(), f"results/{filename}.json")

        if not os.path.exists(filepath):
            return []

        with open(filepath, "r") as file:
            data = json.load(file)

        return data

    @staticmethod
    def read_result_dialog():
        """Open JSON files and load battles."""
        # Root/results directory
        default_dir = os.path.join(os.getcwd(), "results")

        # If the results directory doesn't exist, create it
        if not os.path.exists(default_dir):
            os.makedirs(default_dir)

        # Allow the user to select multiple files
        file_paths = filedialog.askopenfilenames(
            title="Open JSON Files",
            initialdir=default_dir,  # Set default directory
            filetypes=[("JSON Files", "*.json")],
        )

        if not file_paths:
            return

        combined_battles = []

        for file_path in file_paths:
            with open(file_path, "r") as file:
                data = json.load(file)
                if isinstance(data, list):  # Ensure the JSON contains a list
                    combined_battles.extend(data)

        # Remove duplicates (optional, based on battle uniqueness criteria)
        # Assuming a unique battle has a combination of "Map" and "Duration"
        unique_battles = {
            (battle["Map"], battle["Duration"]): battle for battle in combined_battles
        }.values()

        # Update tracker battles and populate the table
        return unique_battles

    @staticmethod
    def list_results():
        """
        List all result files in the directory.

        Returns:
            list: A list of file names (without extensions).
        """

        files = [
            f.replace(".json", "")
            for f in os.listdir("results")
            if f.endswith(".json")
        ]

        return files
