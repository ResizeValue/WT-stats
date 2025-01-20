import os
import sys
import time
import shutil


def replace_file(old_file, new_file):
    try:
        if os.path.exists(old_file):
            os.remove(old_file)
        shutil.move(new_file, old_file)
        print(f"Replaced {old_file} with {new_file}")
    except Exception as e:
        print(f"Error replacing file: {e}")
        sys.exit(1)


def restart_application(executable_path):
    try:
        print("Restarting application...")
        os.startfile(executable_path)
    except Exception as e:
        print(f"Error restarting application: {e}")
        sys.exit(1)


def copy_all_from_dir(src_dir, dest_dir):
    try:
        for file_name in os.listdir(src_dir):
            src_file = os.path.join(src_dir, file_name)
            dest_file = os.path.join(dest_dir, file_name)
            shutil.copy(src_file, dest_file)
            print(f"Copied {src_file} to {dest_file}")
    except Exception as e:
        print(f"Error copying files: {e}")
        sys.exit(1)


def remove_dir(directory):
    try:
        shutil.rmtree(directory)
        print(f"Removed directory: {directory}")
    except Exception as e:
        print(f"Error removing directory: {e}")
        sys.exit(1)


def remove_file(file_path):
    try:
        os.remove(file_path)
        print(f"Removed file: {file_path}")
    except Exception as e:
        print(f"Error removing file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(
            "Usage: python updater.py <archive_path> <unpacked_path> <app_directory> <app_name>"
        )
        print("Entered arguments:", sys.argv)
        time.sleep(3)
        sys.exit(1)

    archive_path = sys.argv[1]
    unpacked_path = sys.argv[2]
    app_directory = sys.argv[3]
    app_name = sys.argv[4]

    print("Starting update process...")
    time.sleep(3)

    copy_all_from_dir(unpacked_path, app_directory)

    remove_dir(unpacked_path)
    remove_file(archive_path)

    restart_application(os.path.join(app_directory, app_name))
    print("Update complete.")
