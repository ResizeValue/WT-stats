from time import sleep
import requests
import os
import sys
import zipfile
import shutil
import subprocess
from packaging import version


class VersionManager:
    """Manages version checking and updating for the application."""

    def __init__(self, current_version, repo_owner, repo_name):
        """
        Initialize the VersionManager.

        Args:
            current_version (str): The current version of the application.
            repo_owner (str): The owner of the GitHub repository.
            repo_name (str): The name of the GitHub repository.
        """
        self.current_version = current_version
        self.repo_owner = repo_owner
        self.repo_name = repo_name

    def get_latest_release(self):
        """
        Get the latest release information from GitHub.

        Returns:
            dict: A dictionary containing the latest version and download URL for a `.zip` file.
        """
        api_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            release_data = response.json()
            latest_version = release_data.get("tag_name", "").lstrip("v")
            assets = release_data.get("assets", [])
            for asset in assets:
                if asset.get("name", "").endswith(".zip"):  # Look for the .zip file
                    download_url = asset.get("browser_download_url")
                    return {"version": latest_version, "download_url": download_url}
            print("No suitable .zip file found in the latest release.")
            return None
        except requests.RequestException as e:
            print(f"Error checking for updates: {e}")
            return None

    def is_update_available(self, latest_version):
        """
        Check if an update is available.

        Args:
            latest_version (str): The latest version from GitHub.

        Returns:
            bool: True if an update is available, False otherwise.
        """
        return version.parse(latest_version) > version.parse(self.current_version)

    def download_update(self, update_url, target_path):
        """
        Download the update `.zip` file.

        Args:
            update_url (str): The URL of the `.zip` file.
            target_path (str): Path to save the downloaded file.

        Returns:
            str: Path to the downloaded file.
        """
        try:
            with requests.get(update_url, stream=True) as response:
                response.raise_for_status()
                with open(target_path, "wb") as file:
                    shutil.copyfileobj(response.raw, file)
            print(f"Update downloaded to {target_path}")
            return target_path
        except requests.RequestException as e:
            print(f"Error downloading the update: {e}")
            return None

    def apply_update(self, zip_file_path):
        """
        Apply the update by extracting the `.zip` file.

        Args:
            zip_file_path (str): Path to the downloaded `.zip` file.
        """
        extract_dir = os.path.join(os.getcwd(), "update_temp")
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)  # Clean up any previous updates

        os.makedirs(extract_dir, exist_ok=True)
        try:
            # Extract the .zip file
            with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)

            print("Update extracted successfully.")

            # Update the updater first
            updater_path = os.path.join(extract_dir, "Updater.exe")
            if os.path.exists(updater_path):
                shutil.copy(updater_path, os.path.join(os.getcwd(), "Updater.exe"))
                print("Updater updated successfully.")
                sleep(1)  # Wait for the updater to be replaced
                os.remove(updater_path)

            updater_path = os.path.join(os.getcwd(), "Updater.exe")

            print("Launching updated updater to apply the main update...")
            subprocess.Popen(
                [
                    updater_path,
                    zip_file_path,
                    extract_dir,
                    os.getcwd(),
                    "WT Stats Tracker",
                ],
                close_fds=True,
            )
            print("Updated updater launched successfully. Exiting application...")
            sys.exit(0)

        except Exception as e:
            print(f"Error applying the update: {e}")

    def check_for_updates(self):
        """
        Check for updates, download, and apply them if available.
        """
        print("Checking for updates...")
        release_info = self.get_latest_release()

        if not release_info:
            print("Could not fetch release information.")
            return

        latest_version = release_info["version"]
        update_url = release_info["download_url"]

        print(f"Latest version: {release_info}")
        if self.is_update_available(latest_version):
            print("Update available. Downloading...")
            zip_file_path = self.download_update(update_url, "update.zip")
            if zip_file_path:
                print("Applying update...")
                self.apply_update(zip_file_path)
        else:
            print("You are using the latest version.")
