# logger.py
# Handles all logging of file moves and errors

import os
from datetime import datetime

LOG_FILE = "organizer_log.txt"

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log_move(filename, category, folder_path):
    timestamp = get_timestamp()
    entry = f"[{timestamp}] MOVED: {filename} → {category} ({folder_path})\n"
    _write_log(entry)

def log_error(filename, error_message):
    timestamp = get_timestamp()
    entry = f"[{timestamp}] ERROR: {filename} — {error_message}\n"
    _write_log(entry)

def log_session_start(folder_path):
    timestamp = get_timestamp()
    entry = (
        f"\n{'='*50}\n"
        f"SESSION STARTED: {timestamp}\n"
        f"TARGET FOLDER:  {folder_path}\n"
        f"{'='*50}\n"
    )
    _write_log(entry)

def log_session_end(moved, skipped):
    timestamp = get_timestamp()
    entry = (
        f"SESSION ENDED:  {timestamp}\n"
        f"FILES MOVED:    {moved}\n"
        f"FILES SKIPPED:  {skipped}\n"
        f"{'='*50}\n"
    )
    _write_log(entry)

def view_log():
    if not os.path.exists(LOG_FILE):
        print("\nNo log file found yet.")
        return
    print(f"\n--- Organizer Log ---")
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        print(f.read())

def _write_log(entry):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)