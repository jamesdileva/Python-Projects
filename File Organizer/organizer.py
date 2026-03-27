# organizer.py
# Defines file type categories and organizer logic

import os
import shutil
import hashlib
from logger import log_move, log_error

FILE_CATEGORIES = {
    "Images":     [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
    "Videos":     [".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv"],
    "Audio":      [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"],
    "Documents":  [".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx",
                   ".ppt", ".pptx", ".csv"],
    "Code":       [".py", ".js", ".html", ".css", ".cpp", ".h",
                   ".java", ".ts", ".json", ".xml"],
    "Archives":   [".zip", ".rar", ".tar", ".gz", ".7z"],
    "Other":      []
}

def get_category(extension):
    for category, extensions in FILE_CATEGORIES.items():
        if extension.lower() in extensions:
            return category
    return "Other"

def preview_organization(folder_path):
    if not os.path.exists(folder_path):
        print(f"\n⚠ Folder not found: {folder_path}")
        return False

    files = [f for f in os.listdir(folder_path)
             if os.path.isfile(os.path.join(folder_path, f))]

    if not files:
        print("\nNo files found in that folder.")
        return False

    print(f"\n--- Preview: {len(files)} files found ---")
    category_counts = {}
    for filename in files:
        ext = os.path.splitext(filename)[1]
        category = get_category(ext)
        category_counts[category] = category_counts.get(category, 0) + 1

    for category, count in sorted(category_counts.items()):
        print(f"  {category:<12} {count} file(s)")

    return True

def organize_folder(folder_path, progress_callback=None):
    files = [f for f in os.listdir(folder_path)
             if os.path.isfile(os.path.join(folder_path, f))]

    moved = 0
    skipped = 0
    total = len(files)

    for i, filename in enumerate(files):
        ext = os.path.splitext(filename)[1]
        category = get_category(ext)

        dest_folder = os.path.join(folder_path, category)
        os.makedirs(dest_folder, exist_ok=True)

        src = os.path.join(folder_path, filename)
        dest = os.path.join(dest_folder, filename)

        if os.path.exists(dest):
            skipped += 1
            if progress_callback:
                progress_callback(i + 1, total,
                    f"Skipped (exists): {filename}", skipped=True)
            continue

        try:
            shutil.move(src, dest)
            log_move(filename, category, folder_path)
            moved += 1
            if progress_callback:
                progress_callback(i + 1, total,
                    f"Moved: {filename} → {category}")
        except Exception as e:
            log_error(filename, str(e))
            if progress_callback:
                progress_callback(i + 1, total,
                    f"Error: {filename}", error=True)

    return moved, skipped
    
def get_file_hash(filepath):
    hasher = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        log_error(filepath, str(e))
        return None

def find_and_move_duplicates(folder_path, progress_callback=None):
    files = [f for f in os.listdir(folder_path)
             if os.path.isfile(os.path.join(folder_path, f))]

    if not files:
        return 0

    total = len(files)
    seen_hashes = {}
    duplicates_found = 0
    duplicates_folder = os.path.join(folder_path, "Duplicates")

    for i, filename in enumerate(files):
        filepath = os.path.join(folder_path, filename)
        file_hash = get_file_hash(filepath)

        if progress_callback:
            progress_callback(i + 1, total,
                f"Scanning: {filename}")

        if file_hash is None:
            continue

        if file_hash in seen_hashes:
            os.makedirs(duplicates_folder, exist_ok=True)
            dest = os.path.join(duplicates_folder, filename)

            if os.path.exists(dest):
                base, ext = os.path.splitext(filename)
                dest = os.path.join(duplicates_folder,
                    f"{base}_dup{duplicates_found}{ext}")

            try:
                shutil.move(filepath, dest)
                log_move(filename, "Duplicates", folder_path)
                duplicates_found += 1
                if progress_callback:
                    progress_callback(i + 1, total,
                        f"Duplicate found: {filename}",
                        duplicate=True)
            except Exception as e:
                log_error(filename, str(e))
        else:
            seen_hashes[file_hash] = filename

    return duplicates_found