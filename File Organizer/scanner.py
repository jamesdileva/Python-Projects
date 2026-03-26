# scanner.py
# Handles scanning folders and the undo feature

import os
import shutil
import tkinter as tk
from tkinter import filedialog
from logger import view_log, log_error

CATEGORY_FOLDERS = [
    "Images", "Videos", "Audio",
    "Documents", "Code", "Archives", "Other"
]

def get_folder_path():
    while True:
        print("\nHow would you like to select a folder?")
        print("1. Browse for folder (recommended)")
        print("2. Type the path manually")
        print("q. Cancel")

        choice = input("\nEnter choice: ").strip().lower()

        if choice == "q":
            return None

        elif choice == "1":
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            path = filedialog.askdirectory(title="Select a folder to organize")
            root.destroy()

            if not path:
                print("\nNo folder selected.")
                continue
            return path

        elif choice == "2":
            path = input("\nEnter the full folder path (or 'q' to cancel): ").strip()
            if path.lower() == "q":
                return None
            if not path:
                print("Please enter a path.")
                continue
            if not os.path.exists(path):
                print(f"⚠ Folder not found: {path}")
                continue
            if not os.path.isdir(path):
                print(f"⚠ That path is a file not a folder: {path}")
                continue
            return path

        else:
            print("\nInvalid choice.")
            
def scan_summary(folder_path):
    total_files = 0
    total_size = 0

    files = [f for f in os.listdir(folder_path)
             if os.path.isfile(os.path.join(folder_path, f))]

    for filename in files:
        filepath = os.path.join(folder_path, filename)
        total_files += 1
        total_size += os.path.getsize(filepath)

    size_mb = total_size / (1024 * 1024)

    print(f"\n--- Folder Summary ---")
    print(f"Location:    {folder_path}")
    print(f"Total files: {total_files}")
    print(f"Total size:  {size_mb:.2f} MB")

    return total_files

def undo_organization(folder_path):
    moved_back = 0
    skipped = 0

    for category in CATEGORY_FOLDERS:
        category_path = os.path.join(folder_path, category)

        if not os.path.exists(category_path):
            continue

        files = [f for f in os.listdir(category_path)
                 if os.path.isfile(os.path.join(category_path, f))]

        for filename in files:
            src = os.path.join(category_path, filename)
            dest = os.path.join(folder_path, filename)

            if os.path.exists(dest):
                print(f"  ⚠ Skipped (already exists): {filename}")
                skipped += 1
                continue

            try:
                shutil.move(src, dest)
                moved_back += 1
            except Exception as e:
                log_error(filename, str(e))
                print(f"  ⚠ Error moving {filename}: {e}")

        try:
            os.rmdir(category_path)
        except OSError:
            print(f"  ⚠ Could not remove {category} folder — may not be empty")

    print(f"\n✓ Undo complete — {moved_back} files restored, {skipped} skipped")