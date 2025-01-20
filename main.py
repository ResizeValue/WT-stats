import os
from time import sleep
from WTStatTracker import WTStatTracker
from src.version_manager import VersionManager

CURRENT_VERSION = "0.0.0"
REPO_OWNER = "ResizeValue"
REPO_NAME = "WT-stats"

if __name__ == "__main__":
    version_manager = VersionManager(CURRENT_VERSION, REPO_OWNER, REPO_NAME)
    version_manager.check_for_updates()

    tracker = WTStatTracker()

    try:
        # Run the application
        tracker.run()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        tracker.stop()
