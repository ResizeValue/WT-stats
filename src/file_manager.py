import json
import os


class FileManager:
    def __init__(self, directory="results"):
        """Initialize the FileManager with a directory for storing results."""
        
        self.directory = directory
        
        if not os.path.exists(directory):
            os.makedirs(directory)

    def save_result(self, filename, data):
        """
        Save a result to a file in JSON format.

        Args:
            filename (str): The name of the file (without extension).
            data (dict): The data to save in the file.
        """
        
        filepath = os.path.join(self.directory, f"{filename}.json")
        
        with open(filepath, "w") as file:
            json.dump(data, file, indent=4)
            
        print(f"Result saved to {filepath}")

    def read_result(self, filename):
        """
        Read a result from a file.

        Args:
            filename (str): The name of the file (without extension).

        Returns:
            dict: The data read from the file.
        """
        
        filepath = os.path.join(self.directory, f"{filename}.json")

        if not os.path.exists(filepath):
            return []

        with open(filepath, "r") as file:
            data = json.load(file)

        return data

    def list_results(self):
        """
        List all result files in the directory.

        Returns:
            list: A list of file names (without extensions).
        """
        
        files = [
            f.replace(".json", "")
            for f in os.listdir(self.directory)
            if f.endswith(".json")
        ]
        
        return files
