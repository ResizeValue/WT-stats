from WTStatTracker import WTStatTracker
from src.settings import CURRENT_VERSION, REPO_NAME, REPO_OWNER
from src.version_manager import VersionManager


if __name__ == "__main__":
    version_manager = VersionManager(CURRENT_VERSION, REPO_OWNER, REPO_NAME)
    version_manager.check_for_updates()

    tracker = WTStatTracker()

    try:
        tracker.run()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
