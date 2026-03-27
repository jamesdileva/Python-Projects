# File Organizer

A desktop file organization tool with a modern sidebar interface.
Point it at any folder and it automatically sorts files into
subfolders by type, detects duplicates, and keeps a full session log.

## How to Run

**download the executable** from the
[Releases](https://github.com/jamesdileva/python-projects/releases/tag/file-organizer-v1.0)
page — no Python installation required. Windows only.

**GUI version (recommended):**
```
python file_organizer_gui.py
```

**Command line version:**
```
python main.py
```

## Features

### GUI Version
- **Sidebar navigation** — always visible action panel with
  one click access to every feature
- **Native folder picker** — browse for any folder, no typing
  required
- **Live preview** — see exactly which files go where before
  organizing, grouped by category with extension breakdown
- **One click organize** — moves files into subfolders by type
  with a live progress bar and real time log table
- **Duplicate detection** — scans files using MD5 hashing,
  moves true duplicates to a Duplicates folder for review
- **Undo** — move all organized files back to the root folder
- **Session log viewer** — every move and error recorded with
  timestamps, viewable inside the app
- **Dark mode** — full dark theme with explicit sidebar theming
- **Status bar** — shows current folder and operation state
- **Background threading** — UI stays responsive during all
  file operations
- **Operation guard** — prevents running multiple operations
  simultaneously

### Command Line Version
- Select folder via browse dialog or manual path entry
- Preview organization before committing
- Organize files into category subfolders
- Find and move duplicate files
- Undo organization
- View session log

## File Categories
```
Images     — jpg, jpeg, png, gif, bmp, svg, webp
Videos     — mp4, mov, avi, mkv, wmv, flv
Audio      — mp3, wav, aac, flac, ogg, m4a
Documents  — pdf, doc, docx, txt, xls, xlsx, csv
Code       — py, js, html, css, cpp, h, java, json
Archives   — zip, rar, tar, gz, 7z
Other      — anything not matched above
```

## Project Structure
```
FileOrganizer/
├── file_organizer_gui.py  # GUI entry point
├── main.py                # Command line entry point
├── organizer.py           # File category rules and logic
├── scanner.py             # Folder scanning and undo logic
└── logger.py              # Session and move logging
```

## How Duplicate Detection Works
Each file is read in 8KB chunks and passed through an MD5
hashing algorithm to generate a unique fingerprint. If two
files share the same fingerprint they are identical regardless
of filename. Duplicates are moved to a Duplicates folder for
manual review — nothing is deleted automatically.

## Roadmap

### Completed
- ✅ GUI — sidebar layout with Tkinter
- ✅ Native folder picker dialog
- ✅ Live preview with category and extension breakdown
- ✅ One click organize with progress bar
- ✅ Real time operation log table
- ✅ Duplicate detection using MD5 hashing
- ✅ Undo organization
- ✅ Session log viewer
- ✅ Dark mode
- ✅ Background threading
- ✅ Operation guard — prevents simultaneous operations

### Planned
- **Dark mode polish** — full theme coverage when switching
  panels after load
- **Custom category rules** — user defines their own file types
- **Scheduled runs** — auto organize on a timer
- **Recursive organization** — organize files inside subfolders
- **Duplicate preview** — show duplicates before moving them
- **Statistics report** — space saved after organizing
- **CustomTkinter modernization** — modern rounded UI styling
