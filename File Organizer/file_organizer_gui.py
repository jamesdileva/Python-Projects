# file_organizer_gui.py
# File Organizer GUI — Sidebar layout with Tkinter

import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from organizer import (get_category, preview_organization,
                        organize_folder, find_and_move_duplicates,
                        FILE_CATEGORIES)
from scanner import scan_summary, undo_organization
from logger import (log_session_start, log_session_end,
                    view_log, LOG_FILE)

THEMES = {
    "light": {
        "bg":         "#F4F4F4",
        "fg":         "#1A1A1A",
        "sidebar_bg": "#2C3E50",
        "sidebar_fg": "#ECF0F1",
        "sidebar_sel":"#1A252F",
        "panel_bg":   "#FFFFFF",
        "panel_fg":   "#1A1A1A",
        "accent":     "#2E75B6",
        "success":    "#27AE60",
        "warning":    "#E67E22",
        "error":      "#E74C3C",
        "status_bg":  "#E0E0E0",
        "status_fg":  "#555555",
        "tree_bg":    "#FFFFFF",
        "log_bg":     "#1E1E1E",
        "log_fg":     "#00FF88"
    },
    "dark": {
        "bg":         "#1E1E1E",
        "fg":         "#F0F0F0",
        "sidebar_bg": "#111111",
        "sidebar_fg": "#ECF0F1",
        "sidebar_sel":"#2C3E50",
        "panel_bg":   "#2D2D2D",
        "panel_fg":   "#F0F0F0",
        "accent":     "#1A3A5C",
        "success":    "#1E8449",
        "warning":    "#D35400",
        "error":      "#922B21",
        "status_bg":  "#2D2D2D",
        "status_fg":  "#AAAAAA",
        "tree_bg":    "#2D2D2D",
        "log_bg":     "#0A0A0A",
        "log_fg":     "#00FF88"
    }
}

class FileOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Organizer")
        self.root.geometry("1050x680")
        self.root.resizable(True, True)

        self.folder_path  = None
        self.theme        = "light"
        self.active_btn   = None
        self.operation_running = False

        self._build_ui()

    # ── UI Construction ──────────────────────────────────────
    def _build_ui(self):
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_panel()
        self._build_status_bar()
        self._show_panel("welcome")

    def _build_sidebar(self):
        self.sidebar = tk.Frame(self.root, bg="#2C3E50", width=180)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        tk.Label(self.sidebar,
                 text="FILE\nORGANIZER",
                 font=("Arial", 13, "bold"),
                 bg="#2C3E50", fg="#ECF0F1",
                 pady=20).pack(fill="x")

        tk.Frame(self.sidebar, bg="#3D5166",
                 height=1).pack(fill="x", padx=16, pady=(0,12))

        self.sidebar_buttons = {}
        actions = [
            ("📂", "Load Folder",    "load"),
            ("👁", "Preview",        "preview"),
            ("⚙", "Organize",       "organize"),
            ("🔍", "Find Duplicates","duplicates"),
            ("↩", "Undo",           "undo"),
            ("📋", "View Log",       "log"),
        ]

        for icon, label, key in actions:
            btn = tk.Button(self.sidebar,
                            text=f"  {icon}  {label}",
                            font=("Arial", 10),
                            bg="#2C3E50", fg="#ECF0F1",
                            activebackground="#1A252F",
                            activeforeground="white",
                            anchor="w", padx=16, pady=10,
                            relief="flat", cursor="hand2",
                            command=lambda k=key: self._sidebar_action(k))
            btn.pack(fill="x")
            self.sidebar_buttons[key] = btn

        tk.Frame(self.sidebar, bg="#3D5166",
                 height=1).pack(fill="x", padx=16, pady=12)

        self.btn_theme = tk.Button(self.sidebar,
                                    text="  🌙  Dark Mode",
                                    font=("Arial", 10),
                                    bg="#2C3E50", fg="#ECF0F1",
                                    activebackground="#1A252F",
                                    activeforeground="white",
                                    anchor="w", padx=16, pady=10,
                                    relief="flat", cursor="hand2",
                                    command=self._toggle_theme)
        self.btn_theme.pack(fill="x")

    def _build_main_panel(self):
        self.main_panel = tk.Frame(self.root, bg="#FFFFFF")
        self.main_panel.grid(row=0, column=1, sticky="nsew")
        self.main_panel.columnconfigure(0, weight=1)
        self.main_panel.rowconfigure(0, weight=1)

        self.panels = {}
        self._build_welcome_panel()
        self._build_preview_panel()
        self._build_organize_panel()
        self._build_duplicates_panel()
        self._build_undo_panel()
        self._build_log_panel()

    def _build_welcome_panel(self):
        panel = tk.Frame(self.main_panel, bg="#FFFFFF")
        self.panels["welcome"] = panel

        tk.Label(panel,
                 text="📂",
                 font=("Arial", 64),
                 bg="#FFFFFF").pack(pady=(80, 16))

        tk.Label(panel,
                 text="File Organizer",
                 font=("Arial", 28, "bold"),
                 bg="#FFFFFF", fg="#2C3E50").pack()

        tk.Label(panel,
                 text="Click 'Load Folder' in the sidebar to get started",
                 font=("Arial", 12, "italic"),
                 bg="#FFFFFF", fg="#888888").pack(pady=12)

        tk.Label(panel,
                 text="Organizes files into: " +
                      ", ".join(FILE_CATEGORIES.keys()),
                 font=("Arial", 10),
                 bg="#FFFFFF", fg="#AAAAAA").pack(pady=4)

    def _build_preview_panel(self):
        panel = tk.Frame(self.main_panel, bg="#FFFFFF")
        self.panels["preview"] = panel
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(1, weight=1)

        tk.Label(panel, text="Preview",
                 font=("Arial", 16, "bold"),
                 bg="#FFFFFF", fg="#2C3E50",
                 anchor="w", padx=20, pady=16).grid(
                 row=0, column=0, sticky="ew")

        cols = ("category", "count", "extensions")
        self.tree_preview = ttk.Treeview(panel, columns=cols,
                                          show="headings", height=20)
        self.tree_preview.heading("category",   text="Category")
        self.tree_preview.heading("count",      text="Files")
        self.tree_preview.heading("extensions", text="Extensions Found")

        self.tree_preview.column("category",   width=160, anchor="center")
        self.tree_preview.column("count",      width=80,  anchor="center")
        self.tree_preview.column("extensions", width=500, anchor="w")

        sb = ttk.Scrollbar(panel, orient="vertical",
                           command=self.tree_preview.yview)
        self.tree_preview.configure(yscrollcommand=sb.set)
        self.tree_preview.grid(row=1, column=0, sticky="nsew", padx=(16,0), pady=8)
        sb.grid(row=1, column=1, sticky="ns", pady=8)

    def _build_organize_panel(self):
        panel = tk.Frame(self.main_panel, bg="#FFFFFF")
        self.panels["organize"] = panel
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(2, weight=1)

        tk.Label(panel, text="Organize",
                 font=("Arial", 16, "bold"),
                 bg="#FFFFFF", fg="#2C3E50",
                 anchor="w", padx=20, pady=16).grid(
                 row=0, column=0, columnspan=2, sticky="ew")

        prog_frame = tk.Frame(panel, bg="#FFFFFF")
        prog_frame.grid(row=1, column=0, sticky="ew",
                        padx=20, pady=(0,8))
        prog_frame.columnconfigure(0, weight=1)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(prog_frame,
                                             variable=self.progress_var,
                                             maximum=100, length=400)
        self.progress_bar.grid(row=0, column=0, sticky="ew")

        self.lbl_progress = tk.Label(prog_frame, text="",
                                      font=("Arial", 9, "italic"),
                                      bg="#FFFFFF", fg="#555555")
        self.lbl_progress.grid(row=1, column=0, sticky="w", pady=(4,0))

        self.tree_organize = ttk.Treeview(panel,
                                           columns=("status", "file", "dest"),
                                           show="headings", height=18)
        self.tree_organize.heading("status", text="Status")
        self.tree_organize.heading("file",   text="File")
        self.tree_organize.heading("dest",   text="Destination")

        self.tree_organize.column("status", width=90,  anchor="center")
        self.tree_organize.column("file",   width=280, anchor="w")
        self.tree_organize.column("dest",   width=160, anchor="center")

        sb2 = ttk.Scrollbar(panel, orient="vertical",
                             command=self.tree_organize.yview)
        self.tree_organize.configure(yscrollcommand=sb2.set)
        self.tree_organize.grid(row=2, column=0, sticky="nsew",
                                 padx=(16,0), pady=8)
        sb2.grid(row=2, column=1, sticky="ns", pady=8)

        self.tree_organize.tag_configure("moved",   background="#EAFAF1")
        self.tree_organize.tag_configure("skipped", background="#FEF9E7")
        self.tree_organize.tag_configure("error",   background="#FDEDEC")

    def _build_duplicates_panel(self):
        panel = tk.Frame(self.main_panel, bg="#FFFFFF")
        self.panels["duplicates"] = panel
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(2, weight=1)

        tk.Label(panel, text="Find Duplicates",
                 font=("Arial", 16, "bold"),
                 bg="#FFFFFF", fg="#2C3E50",
                 anchor="w", padx=20, pady=16).grid(
                 row=0, column=0, columnspan=2, sticky="ew")

        prog_frame2 = tk.Frame(panel, bg="#FFFFFF")
        prog_frame2.grid(row=1, column=0, sticky="ew",
                         padx=20, pady=(0,8))
        prog_frame2.columnconfigure(0, weight=1)

        self.dup_progress_var = tk.DoubleVar()
        self.dup_progress_bar = ttk.Progressbar(prog_frame2,
                                                  variable=self.dup_progress_var,
                                                  maximum=100, length=400)
        self.dup_progress_bar.grid(row=0, column=0, sticky="ew")

        self.lbl_dup_progress = tk.Label(prog_frame2, text="",
                                          font=("Arial", 9, "italic"),
                                          bg="#FFFFFF", fg="#555555")
        self.lbl_dup_progress.grid(row=1, column=0, sticky="w", pady=(4,0))

        self.tree_dupes = ttk.Treeview(panel,
                                        columns=("file", "status"),
                                        show="headings", height=18)
        self.tree_dupes.heading("file",   text="File")
        self.tree_dupes.heading("status", text="Status")

        self.tree_dupes.column("file",   width=500, anchor="w")
        self.tree_dupes.column("status", width=160, anchor="center")

        sb3 = ttk.Scrollbar(panel, orient="vertical",
                             command=self.tree_dupes.yview)
        self.tree_dupes.configure(yscrollcommand=sb3.set)
        self.tree_dupes.grid(row=2, column=0, sticky="nsew",
                              padx=(16,0), pady=8)
        sb3.grid(row=2, column=1, sticky="ns", pady=8)

        self.tree_dupes.tag_configure("duplicate", background="#FDEDEC")
        self.tree_dupes.tag_configure("scanning",  background="#EBF3FB")

    def _build_undo_panel(self):
        panel = tk.Frame(self.main_panel, bg="#FFFFFF")
        self.panels["undo"] = panel
        panel.columnconfigure(0, weight=1)

        tk.Label(panel, text="Undo Organization",
                 font=("Arial", 16, "bold"),
                 bg="#FFFFFF", fg="#2C3E50",
                 anchor="w", padx=20, pady=16).pack(fill="x")

        tk.Label(panel,
                 text="This will move all organized files back\n"
                      "to the root folder.",
                 font=("Arial", 11),
                 bg="#FFFFFF", fg="#555555",
                 justify="center").pack(pady=(40,20))

        self.lbl_undo_folder = tk.Label(panel, text="No folder selected",
                                         font=("Arial", 10, "italic"),
                                         bg="#FFFFFF", fg="#888888")
        self.lbl_undo_folder.pack(pady=(0,30))

        tk.Button(panel, text="↩  Undo Organization",
                  command=self._run_undo,
                  font=("Arial", 12, "bold"),
                  bg="#E74C3C", fg="white",
                  padx=24, pady=10,
                  cursor="hand2", relief="flat").pack()

    def _build_log_panel(self):
        panel = tk.Frame(self.main_panel, bg="#FFFFFF")
        self.panels["log"] = panel
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(1, weight=1)

        header = tk.Frame(panel, bg="#FFFFFF")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(16,8))

        tk.Label(header, text="Session Log",
                 font=("Arial", 16, "bold"),
                 bg="#FFFFFF", fg="#2C3E50").pack(side="left")

        tk.Button(header, text="🔄 Refresh",
                  command=self._refresh_log,
                  font=("Arial", 9), pady=2,
                  cursor="hand2").pack(side="right")

        self.log_text = tk.Text(panel,
                                 font=("Courier New", 10),
                                 bg="#1E1E1E", fg="#00FF88",
                                 state="disabled",
                                 wrap="word",
                                 padx=12, pady=12,
                                 relief="flat")
        self.log_text.grid(row=1, column=0, sticky="nsew",
                            padx=16, pady=(0,16))

    def _build_status_bar(self):
        self.status_bar = tk.Frame(self.root, bg="#E0E0E0", pady=4)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.status_bar.columnconfigure(0, weight=1)

        self.lbl_status = tk.Label(self.status_bar,
                                    text="Ready — load a folder to get started",
                                    font=("Arial", 9),
                                    bg="#E0E0E0", fg="#555555",
                                    anchor="w", padx=12)
        self.lbl_status.grid(row=0, column=0, sticky="w")

        self.lbl_folder = tk.Label(self.status_bar,
                                    text="No folder loaded",
                                    font=("Arial", 9, "italic"),
                                    bg="#E0E0E0", fg="#888888",
                                    anchor="e", padx=12)
        self.lbl_folder.grid(row=0, column=1, sticky="e")

    # ── Panel Management ─────────────────────────────────────
    def _show_panel(self, key):
        for panel in self.panels.values():
            panel.grid_forget()
        self.panels[key].grid(row=0, column=0, sticky="nsew")

        if self.active_btn and self.active_btn in self.sidebar_buttons:
            self.sidebar_buttons[self.active_btn].config(
                bg="#2C3E50")
        if key in self.sidebar_buttons:
            self.sidebar_buttons[key].config(bg="#1A252F")
            self.active_btn = key
            
        # Apply current theme to newly shown panel
        t = THEMES[self.theme]
        self._theme_panel(self.panels[key], t)

    def _set_status(self, message, color="#555555"):
        self.lbl_status.config(text=message, fg=color)
        self.root.update_idletasks()

    # ── Sidebar Actions ──────────────────────────────────────
    def _sidebar_action(self, key):
        if self.operation_running:
            messagebox.showwarning("Busy",
                "An operation is already running. Please wait.")
            return

        if key == "load":
            self._load_folder()
        elif key == "preview":
            self._run_preview()
        elif key == "organize":
            self._run_organize()
        elif key == "duplicates":
            self._run_duplicates()
        elif key == "undo":
            self._show_undo()
        elif key == "log":
            self._show_log()

    # ── Load Folder ──────────────────────────────────────────
    def _load_folder(self):
        from tkinter import filedialog
        path = filedialog.askdirectory(
            title="Select a folder to organize"
        )
        if not path:
            return
        self.folder_path = path
        folder_name = os.path.basename(path)
        self.lbl_folder.config(
            text=f"📂 {folder_name}")
        self.lbl_undo_folder.config(
            text=f"Folder: {folder_name}")

        files = [f for f in os.listdir(path)
                 if os.path.isfile(os.path.join(path, f))]
        total_size = sum(
            os.path.getsize(os.path.join(path, f))
            for f in files
        ) / (1024 * 1024)

        self._set_status(
            f"✓ Loaded: {folder_name} — "
            f"{len(files)} files, {total_size:.1f} MB",
            "#27AE60")
        self._show_panel("preview")
        self._run_preview()

    # ── Preview ──────────────────────────────────────────────
    def _run_preview(self):
        if not self.folder_path:
            messagebox.showwarning("No Folder",
                "Please load a folder first.")
            return

        self._show_panel("preview")

        for row in self.tree_preview.get_children():
            self.tree_preview.delete(row)

        files = [f for f in os.listdir(self.folder_path)
                 if os.path.isfile(
                     os.path.join(self.folder_path, f))]

        category_data = {}
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            category = get_category(ext)
            if category not in category_data:
                category_data[category] = {
                    "count": 0, "extensions": set()}
            category_data[category]["count"] += 1
            if ext:
                category_data[category]["extensions"].add(ext)

        for category, data in sorted(
                category_data.items(),
                key=lambda x: x[1]["count"],
                reverse=True):
            exts = ", ".join(sorted(data["extensions"]))
            self.tree_preview.insert("", "end", values=(
                category,
                data["count"],
                exts if exts else "various"
            ))

        self._set_status(
            f"Preview ready — {len(files)} files in "
            f"{len(category_data)} categories", "#2E75B6")

    # ── Organize ─────────────────────────────────────────────
    def _run_organize(self):
        if not self.folder_path:
            messagebox.showwarning("No Folder",
                "Please load a folder first.")
            return

        files = [f for f in os.listdir(self.folder_path)
                 if os.path.isfile(
                     os.path.join(self.folder_path, f))]
        if not files:
            messagebox.showinfo("Empty Folder",
                "No files found to organize.")
            return

        if not messagebox.askyesno("Confirm",
                f"Organize {len(files)} files in:\n"
                f"{self.folder_path}?"):
            return

        self._show_panel("organize")
        for row in self.tree_organize.get_children():
            self.tree_organize.delete(row)
        self.progress_var.set(0)
        self.lbl_progress.config(text="Starting...")
        self.operation_running = True

        log_session_start(self.folder_path)
        threading.Thread(
            target=self._organize_thread,
            daemon=True).start()

    def _organize_thread(self):
        def callback(current, total, message,
                     skipped=False, error=False):
            pct = (current / total) * 100
            self.root.after(0, self._on_organize_progress,
                            pct, message, skipped, error)

        moved, skipped = organize_folder(
            self.folder_path, progress_callback=callback)
        self.root.after(0, self._on_organize_complete,
                        moved, skipped)

    def _on_organize_progress(self, pct, message,
                               skipped, error):
        self.progress_var.set(pct)
        self.lbl_progress.config(text=message)

        parts = message.split("→")
        filename = parts[0].replace(
            "Moved: ", "").replace(
            "Skipped (exists): ", "").replace(
            "Error: ", "").strip()
        dest = parts[1].strip() if len(parts) > 1 else "—"

        if error:
            status = "❌ Error"
            tag = "error"
        elif skipped:
            status = "⏭ Skipped"
            tag = "skipped"
        else:
            status = "✓ Moved"
            tag = "moved"

        self.tree_organize.insert("", "end",
            values=(status, filename, dest), tags=(tag,))
        self.tree_organize.yview_moveto(1)

    def _on_organize_complete(self, moved, skipped):
        self.progress_var.set(100)
        self.operation_running = False
        log_session_end(moved, skipped)
        self._set_status(
            f"✓ Complete — {moved} files organized, "
            f"{skipped} skipped", "#27AE60")
        messagebox.showinfo("Done",
            f"Organization complete!\n\n"
            f"Files moved:   {moved}\n"
            f"Files skipped: {skipped}")

    # ── Duplicates ───────────────────────────────────────────
    def _run_duplicates(self):
        if not self.folder_path:
            messagebox.showwarning("No Folder",
                "Please load a folder first.")
            return

        if not messagebox.askyesno("Confirm",
                "Scan for duplicates and move them to a\n"
                "Duplicates folder for review?"):
            return

        self._show_panel("duplicates")
        for row in self.tree_dupes.get_children():
            self.tree_dupes.delete(row)
        self.dup_progress_var.set(0)
        self.lbl_dup_progress.config(text="Starting scan...")
        self.operation_running = True

        threading.Thread(
            target=self._duplicates_thread,
            daemon=True).start()

    def _duplicates_thread(self):
        def callback(current, total, message,
                     duplicate=False, **kwargs):
            pct = (current / total) * 100
            self.root.after(0, self._on_dup_progress,
                            pct, message, duplicate)

        count = find_and_move_duplicates(
            self.folder_path, progress_callback=callback)
        self.root.after(0, self._on_duplicates_complete, count)

    def _on_dup_progress(self, pct, message, duplicate):
        self.dup_progress_var.set(pct)
        self.lbl_dup_progress.config(text=message)
        tag = "duplicate" if duplicate else "scanning"
        status = "🔴 Duplicate" if duplicate else "🔍 Scanning"
        filename = message.replace(
            "Duplicate found: ", "").replace(
            "Scanning: ", "").strip()
        self.tree_dupes.insert("", "end",
            values=(filename, status), tags=(tag,))
        self.tree_dupes.yview_moveto(1)

    def _on_duplicates_complete(self, count):
        self.dup_progress_var.set(100)
        self.operation_running = False
        if count == 0:
            self._set_status(
                "✓ Scan complete — no duplicates found",
                "#27AE60")
            messagebox.showinfo("No Duplicates",
                "No duplicate files were found.")
        else:
            self._set_status(
                f"✓ Found {count} duplicate(s) — "
                f"moved to Duplicates folder", "#E67E22")
            messagebox.showinfo("Duplicates Found",
                f"{count} duplicate file(s) moved to\n"
                f"the Duplicates folder for review.")

    # ── Undo ─────────────────────────────────────────────────
    def _show_undo(self):
        self._show_panel("undo")

    def _run_undo(self):
        if not self.folder_path:
            messagebox.showwarning("No Folder",
                "Please load a folder first.")
            return
        if not messagebox.askyesno("Confirm Undo",
                "Move all organized files back to\n"
                "the root folder?"):
            return
        self.operation_running = True
        threading.Thread(
            target=self._undo_thread,
            daemon=True).start()

    def _undo_thread(self):
        undo_organization(self.folder_path)
        self.root.after(0, self._on_undo_complete)

    def _on_undo_complete(self):
        self.operation_running = False
        self._set_status("✓ Undo complete — files restored",
                          "#27AE60")
        messagebox.showinfo("Undo Complete",
            "All files have been moved back\n"
            "to the original folder.")

    # ── Log ──────────────────────────────────────────────────
    def _show_log(self):
        self._show_panel("log")
        self._refresh_log()

    def _refresh_log(self):
        import os
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r",
                      encoding="utf-8") as f:
                content = f.read()
            self.log_text.insert("end",
                content if content else "Log is empty.")
        else:
            self.log_text.insert("end",
                "No log file found yet.\n"
                "Run an organization to create one.")
        self.log_text.config(state="disabled")
        self.log_text.yview_moveto(1)

    # ── Dark Mode ────────────────────────────────────────────
    def _toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        t = THEMES[self.theme]

        self.sidebar.configure(bg=t["sidebar_bg"])
        self.btn_theme.configure(
            bg=t["sidebar_bg"], fg=t["sidebar_fg"],
            activebackground=t["sidebar_sel"])

        for key, btn in self.sidebar_buttons.items():
            bg = t["sidebar_sel"] if key == self.active_btn \
                 else t["sidebar_bg"]
            btn.configure(bg=bg, fg=t["sidebar_fg"],
                          activebackground=t["sidebar_sel"])

        self.main_panel.configure(bg=t["panel_bg"])
        self.status_bar.configure(bg=t["status_bg"])
        self.lbl_status.configure(
            bg=t["status_bg"], fg=t["status_fg"])
        self.lbl_folder.configure(
            bg=t["status_bg"], fg=t["status_fg"])

        self.log_text.configure(
            bg=t["log_bg"], fg=t["log_fg"])

        self.panels["log"].configure(bg=t["panel_bg"])
        for panel in self.panels.values():
            self._theme_panel(panel, t)

        self.btn_theme.configure(
            text="  ☀  Light Mode" if self.theme == "dark"
                 else "  🌙  Dark Mode")

    def _theme_panel(self, widget, t):
        try:
            wc = widget.winfo_class()
            if wc in ("Frame",):
                widget.configure(bg=t["panel_bg"])
            elif wc == "Label":
                widget.configure(
                    bg=t["panel_bg"], fg=t["panel_fg"])
            elif wc == "Button":
                pass
        except tk.TclError:
            pass
        for child in widget.winfo_children():
            self._theme_panel(child, t)

# ── Entry Point ──────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = FileOrganizerApp(root)
    root.mainloop()
