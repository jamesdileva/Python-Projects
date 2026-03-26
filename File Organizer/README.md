# File Organizer

A command line tool that automatically organizes files in any folder 
into subfolders by type, with duplicate detection and full undo support.

## Features
- Browse for folder using a native folder picker dialog
- Preview organization before making any changes
- Organize files into subfolders — Images, Videos, Audio, Documents, 
  Code, Archives, Other
- Detect and move duplicate files using MD5 hash comparison
- Full undo — move everything back to the original folder
- Session logging — every move and error recorded with timestamps

## How to Run
```
python main.py
```
No external libraries required — uses Python standard library only.

## Project Structure
```
FileOrganizer/
├── main.py        # Entry point and menu
├── organizer.py   # File category rules and organization logic
├── scanner.py     # Folder scanning, folder picker, undo logic
└── logger.py      # Session and move logging
```

## How Duplicate Detection Works
Each file is read in chunks and passed through an MD5 hashing algorithm
to generate a unique fingerprint. If two files share the same fingerprint
they are identical regardless of filename. Duplicates are moved to a
Duplicates folder for manual review — nothing is deleted automatically.

## Roadmap
- **Custom category rules** — let the user define their own file types
- **Scheduled runs** — automatically organize on a timer
- **GUI interface** — full desktop window using Tkinter
- **Recursive organization** — organize files inside subfolders too
- **Duplicate preview** — show duplicates before moving them
- **Statistics report** — summary of space saved after organizing
