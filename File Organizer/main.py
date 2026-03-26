# main.py
# Entry point — runs the File Organizer menu

from scanner import get_folder_path, scan_summary, undo_organization
from organizer import preview_organization, organize_folder, find_and_move_duplicates
from logger import log_session_start, log_session_end, view_log

def main():
    print("Welcome to File Organizer")
    folder_path = None

    while True:
        print("\nWhat would you like to do?")
        print("1. Select a Folder")
        print("2. Preview Organization")
        print("3. Organize Folder")
        print("4. Find and Move Duplicates")
        print("5. Undo Organization")
        print("6. View Log")
        print("7. Exit")

        choice = input("\nEnter choice (1-7): ")

        if choice == "1":
            result = get_folder_path()
            if result is None:
                print("\nFolder selection cancelled.")
            else:
                folder_path = result
                scan_summary(folder_path)

        elif choice == "2":
            if not folder_path:
                print("\n⚠ Please select a folder first (option 1).")
                continue
            preview_organization(folder_path)

        elif choice == "3":
            if not folder_path:
                print("\n⚠ Please select a folder first (option 1).")
                continue
            print(f"\nThis will organize all files in:")
            print(f"  {folder_path}")
            confirm = input("\nAre you sure? (yes/no): ").strip().lower()
            if confirm == "yes":
                log_session_start(folder_path)
                moved, skipped = organize_folder(folder_path)
                log_session_end(moved, skipped)
            else:
                print("\nOrganization cancelled.")

        elif choice == "4":
            if not folder_path:
                print("\n⚠ Please select a folder first (option 1).")
                continue
            confirm = input("\nThis will move duplicates to a Duplicates folder. Are you sure? (yes/no): ").strip().lower()
            if confirm == "yes":
                find_and_move_duplicates(folder_path)
            else:
                print("\nDuplicate scan cancelled.")

        elif choice == "5":
            if not folder_path:
                print("\n⚠ Please select a folder first (option 1).")
                continue
            confirm = input("\nThis will move all files back. Are you sure? (yes/no): ").strip().lower()
            if confirm == "yes":
                undo_organization(folder_path)
            else:
                print("\nUndo cancelled.")

        elif choice == "6":
            view_log()

        elif choice == "7":
            print("\nGoodbye!")
            break

        else:
            print("\nInvalid choice. Please enter 1-7.")
main()