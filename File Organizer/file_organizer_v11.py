# file_organizer_v11.py
# File Organizer v1.1 — CustomTkinter modern UI
# Forest Green and Coral color scheme — sidebar layout

import os
import threading
import customtkinter as ctk
from tkinter import messagebox, filedialog
from tkinter import ttk
from organizer import (get_category, organize_folder,
                        find_and_move_duplicates,
                        FILE_CATEGORIES)
from scanner import scan_summary, undo_organization
from logger import (log_session_start, log_session_end,
                    LOG_FILE)

# ── CustomTkinter Setup ──────────────────────────────────────
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

# ── Color Palette ────────────────────────────────────────────
COLORS = {
    "forest":       "#1B4332",
    "forest_light": "#2D6A4F",
    "forest_mid":   "#40916C",
    "sage":         "#52B788",
    "coral":        "#FF6B6B",
    "coral_dark":   "#E05555",
    "amber":        "#F4A261",
    "amber_dark":   "#E76F51",
    "white":        "#FFFFFF",
    "off_white":    "#F8F9FA",
    "grey_light":   "#E9ECEF",
    "text_dark":    "#1A1A2E",
    "text_light":   "#F0F0F0",
    "muted":        "#6C757D",
    "success":      "#52B788",
    "warning":      "#F4A261",
    "error":        "#FF6B6B",
    "dark_bg":      "#0D2818",
    "dark_panel":   "#1B4332",
    "dark_surface": "#2D6A4F",
    "dark_muted":   "#8BAF99",
    "log_bg":       "#0A1F0F",
    "log_fg":       "#52B788",
}

class FileOrganizerV11(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("File Organizer")
        self.geometry("1100x700")
        self.minsize(960, 620)

        self.folder_path      = None
        self.dark_mode        = False
        self.operation_running = False
        self.active_section   = "welcome"

        self._apply_colors()
        self._build_ui()

    def _apply_colors(self):
        self.C = COLORS
        if self.dark_mode:
            ctk.set_appearance_mode("dark")
            self.bg          = self.C["dark_bg"]
            self.panel_bg    = self.C["dark_panel"]
            self.surface     = self.C["dark_surface"]
            self.text_color  = self.C["text_light"]
            self.muted       = self.C["dark_muted"]
            self.sidebar_bg  = self.C["dark_bg"]
            self.log_bg      = self.C["log_bg"]
            self.log_fg      = self.C["log_fg"]
        else:
            ctk.set_appearance_mode("light")
            self.bg          = self.C["off_white"]
            self.panel_bg    = self.C["white"]
            self.surface     = self.C["grey_light"]
            self.text_color  = self.C["text_dark"]
            self.muted       = self.C["muted"]
            self.sidebar_bg  = self.C["forest"]
            self.log_bg      = self.C["log_bg"]
            self.log_fg      = self.C["log_fg"]

    # ── UI Construction ──────────────────────────────────────
    def _build_ui(self):
        self.configure(fg_color=self.bg)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_panel()
        self._build_status_bar()
        self._show_section("welcome")

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self,
                                     fg_color=self.C["forest"],
                                     corner_radius=0,
                                     width=200)
        self.sidebar.grid(row=0, column=0,
                           rowspan=2, sticky="ns")
        self.sidebar.grid_propagate(False)
        self.sidebar.columnconfigure(0, weight=1)

        # Logo area
        logo_frame = ctk.CTkFrame(self.sidebar,
                                   fg_color=self.C["dark_bg"],
                                   corner_radius=0,
                                   height=80)
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)

        ctk.CTkLabel(logo_frame,
                      text="🗂",
                      font=ctk.CTkFont("Arial", 28),
                      text_color=self.C["sage"]).pack(
                      pady=(16,2))

        ctk.CTkLabel(logo_frame,
                      text="FILE ORGANIZER",
                      font=ctk.CTkFont("Arial", 9, "bold"),
                      text_color=self.C["sage"]).pack()

        # Navigation buttons
        nav_items = [
            ("📂", "Load Folder",     "load"),
            ("👁", "Preview",         "preview"),
            ("⚙", "Organize",        "organize"),
            ("🔍", "Find Duplicates", "duplicates"),
            ("↩", "Undo",            "undo"),
            ("📋", "View Log",        "log"),
        ]

        self.nav_buttons = {}
        nav_scroll = ctk.CTkScrollableFrame(
            self.sidebar,
            fg_color="transparent",
            scrollbar_button_color=self.C["forest_light"],
            scrollbar_button_hover_color=self.C["sage"])
        nav_scroll.pack(fill="both", expand=True,
                         pady=(8,0))

        for icon, label, key in nav_items:
            btn = ctk.CTkButton(
                nav_scroll,
                text=f"{icon}  {label}",
                command=lambda k=key: self._nav_action(k),
                fg_color="transparent",
                hover_color=self.C["forest_light"],
                text_color=self.C["text_light"],
                font=ctk.CTkFont("Arial", 12),
                height=44,
                corner_radius=8,
                anchor="w")
            btn.pack(fill="x", padx=8, pady=(0,2))
            self.nav_buttons[key] = btn

        # Divider
        ctk.CTkFrame(self.sidebar,
                      fg_color=self.C["forest_light"],
                      height=1).pack(
                      fill="x", padx=12, pady=8)

        # Theme toggle
        self.btn_theme = ctk.CTkButton(
            self.sidebar,
            text="🌙  Dark Mode",
            command=self._toggle_theme,
            fg_color="transparent",
            hover_color=self.C["forest_light"],
            text_color=self.C["text_light"],
            font=ctk.CTkFont("Arial", 11),
            height=38,
            corner_radius=8,
            anchor="w")
        self.btn_theme.pack(fill="x", padx=8,
                             pady=(0,16))

    def _build_main_panel(self):
        self.main = ctk.CTkFrame(self,
                                  fg_color=self.bg,
                                  corner_radius=0)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.columnconfigure(0, weight=1)
        self.main.rowconfigure(0, weight=1)

        self.sections = {}
        self._build_welcome_section()
        self._build_preview_section()
        self._build_organize_section()
        self._build_duplicates_section()
        self._build_undo_section()
        self._build_log_section()

    def _build_welcome_section(self):
        panel = ctk.CTkFrame(self.main,
                              fg_color=self.bg,
                              corner_radius=0)
        self.sections["welcome"] = panel
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(0, weight=1)

        center = ctk.CTkFrame(panel,
                               fg_color="transparent")
        center.grid(row=0, column=0)

        ctk.CTkLabel(center, text="🗂",
                      font=ctk.CTkFont("Arial", 72),
                      text_color=self.C["forest_mid"]).pack(
                      pady=(0,16))

        self.lbl_welcome_title = ctk.CTkLabel(center,
                      text="File Organizer",
                      font=ctk.CTkFont("Arial", 32, "bold"),
                      text_color=self.C["forest"])
        self.lbl_welcome_title.pack()

        ctk.CTkLabel(center,
                      text="Click 'Load Folder' to get started",
                      font=ctk.CTkFont("Arial", 13),
                      text_color=self.muted).pack(pady=8)

        cats = ", ".join(list(FILE_CATEGORIES.keys())[:-1])
        ctk.CTkLabel(center,
                      text=f"Organizes into: {cats}",
                      font=ctk.CTkFont("Arial", 11),
                      text_color=self.muted).pack(pady=4)

        ctk.CTkButton(center,
                       text="📂  Load Folder",
                       command=self._load_folder,
                       fg_color=self.C["forest"],
                       hover_color=self.C["forest_light"],
                       text_color=self.C["white"],
                       font=ctk.CTkFont("Arial", 13, "bold"),
                       height=44,
                       corner_radius=10,
                       width=200).pack(pady=24)

    def _build_preview_section(self):
        panel = ctk.CTkFrame(self.main,
                              fg_color=self.bg,
                              corner_radius=0)
        self.sections["preview"] = panel
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(1, weight=1)

        self._section_header(panel, "👁  Preview",
                              "See what will be organized")

        table_frame = ctk.CTkFrame(panel,
                                    fg_color=self.panel_bg,
                                    corner_radius=12)
        table_frame.grid(row=1, column=0,
                          sticky="nsew",
                          padx=20, pady=(0,20))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Org.Treeview",
                         background=self.panel_bg,
                         foreground=self.text_color,
                         fieldbackground=self.panel_bg,
                         rowheight=32,
                         font=("Arial", 10))
        style.configure("Org.Treeview.Heading",
                         background=self.C["forest"],
                         foreground=self.C["white"],
                         font=("Arial", 10, "bold"),
                         relief="flat")
        style.map("Org.Treeview",
                   background=[("selected",
                                 self.C["forest_light"])])

        cols = ("category", "count", "extensions")
        self.tree_preview = ttk.Treeview(
            table_frame, columns=cols,
            show="headings",
            style="Org.Treeview", height=18)

        self.tree_preview.heading("category",
                                   text="Category")
        self.tree_preview.heading("count",
                                   text="Files")
        self.tree_preview.heading("extensions",
                                   text="Extensions")

        self.tree_preview.column("category",
                                  width=160,
                                  anchor="center")
        self.tree_preview.column("count",
                                  width=80,
                                  anchor="center")
        self.tree_preview.column("extensions",
                                  width=500,
                                  anchor="w")

        sb = ttk.Scrollbar(table_frame,
                            orient="vertical",
                            command=self.tree_preview.yview)
        self.tree_preview.configure(
            yscrollcommand=sb.set)
        self.tree_preview.grid(row=0, column=0,
                                sticky="nsew",
                                padx=(12,0), pady=12)
        sb.grid(row=0, column=1, sticky="ns",
                pady=12)

    def _build_organize_section(self):
        panel = ctk.CTkFrame(self.main,
                              fg_color=self.bg,
                              corner_radius=0)
        self.sections["organize"] = panel
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(2, weight=1)

        self._section_header(panel, "⚙  Organize",
                              "Move files into category folders")

        # Progress area
        prog_frame = ctk.CTkFrame(panel,
                                   fg_color=self.panel_bg,
                                   corner_radius=12)
        prog_frame.grid(row=1, column=0, sticky="ew",
                         padx=20, pady=(0,12))
        prog_frame.columnconfigure(0, weight=1)

        self.progress_var = ctk.DoubleVar()
        self.progress_bar = ctk.CTkProgressBar(
            prog_frame,
            variable=self.progress_var,
            fg_color=self.surface,
            progress_color=self.C["forest_mid"],
            height=16,
            corner_radius=8)
        self.progress_bar.grid(row=0, column=0,
                                sticky="ew",
                                padx=16, pady=(14,6))
        self.progress_bar.set(0)

        self.lbl_progress = ctk.CTkLabel(
            prog_frame, text="Ready to organize",
            font=ctk.CTkFont("Arial", 10),
            text_color=self.muted)
        self.lbl_progress.grid(row=1, column=0,
                                sticky="w",
                                padx=16, pady=(0,12))

        # Results table
        table_frame = ctk.CTkFrame(panel,
                                    fg_color=self.panel_bg,
                                    corner_radius=12)
        table_frame.grid(row=2, column=0,
                          sticky="nsew",
                          padx=20, pady=(0,20))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        cols = ("status", "file", "destination")
        self.tree_organize = ttk.Treeview(
            table_frame, columns=cols,
            show="headings",
            style="Org.Treeview", height=14)

        self.tree_organize.heading("status",
                                    text="Status")
        self.tree_organize.heading("file",
                                    text="File")
        self.tree_organize.heading("destination",
                                    text="Destination")

        self.tree_organize.column("status",
                                   width=100,
                                   anchor="center")
        self.tree_organize.column("file",
                                   width=300,
                                   anchor="w")
        self.tree_organize.column("destination",
                                   width=160,
                                   anchor="center")

        self.tree_organize.tag_configure(
            "moved",   background="#EAFAF1")
        self.tree_organize.tag_configure(
            "skipped", background="#FEF9E7")
        self.tree_organize.tag_configure(
            "error",   background="#FDEDEC")

        sb2 = ttk.Scrollbar(table_frame,
                             orient="vertical",
                             command=self.tree_organize.yview)
        self.tree_organize.configure(
            yscrollcommand=sb2.set)
        self.tree_organize.grid(row=0, column=0,
                                 sticky="nsew",
                                 padx=(12,0), pady=12)
        sb2.grid(row=0, column=1, sticky="ns",
                 pady=12)

    def _build_duplicates_section(self):
        panel = ctk.CTkFrame(self.main,
                              fg_color=self.bg,
                              corner_radius=0)
        self.sections["duplicates"] = panel
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(2, weight=1)

        self._section_header(
            panel, "🔍  Find Duplicates",
            "Scan and move duplicate files for review")

        prog_frame2 = ctk.CTkFrame(panel,
                                    fg_color=self.panel_bg,
                                    corner_radius=12)
        prog_frame2.grid(row=1, column=0,
                          sticky="ew",
                          padx=20, pady=(0,12))
        prog_frame2.columnconfigure(0, weight=1)

        self.dup_progress_var = ctk.DoubleVar()
        self.dup_progress_bar = ctk.CTkProgressBar(
            prog_frame2,
            variable=self.dup_progress_var,
            fg_color=self.surface,
            progress_color=self.C["coral"],
            height=16,
            corner_radius=8)
        self.dup_progress_bar.grid(
            row=0, column=0, sticky="ew",
            padx=16, pady=(14,6))
        self.dup_progress_bar.set(0)

        self.lbl_dup_progress = ctk.CTkLabel(
            prog_frame2,
            text="Ready to scan",
            font=ctk.CTkFont("Arial", 10),
            text_color=self.muted)
        self.lbl_dup_progress.grid(
            row=1, column=0, sticky="w",
            padx=16, pady=(0,12))

        table_frame2 = ctk.CTkFrame(
            panel,
            fg_color=self.panel_bg,
            corner_radius=12)
        table_frame2.grid(row=2, column=0,
                           sticky="nsew",
                           padx=20, pady=(0,20))
        table_frame2.columnconfigure(0, weight=1)
        table_frame2.rowconfigure(0, weight=1)

        cols = ("file", "status")
        self.tree_dupes = ttk.Treeview(
            table_frame2, columns=cols,
            show="headings",
            style="Org.Treeview", height=14)

        self.tree_dupes.heading("file", text="File")
        self.tree_dupes.heading("status",
                                 text="Status")

        self.tree_dupes.column("file", width=500,
                                anchor="w")
        self.tree_dupes.column("status", width=160,
                                anchor="center")

        self.tree_dupes.tag_configure(
            "duplicate", background="#FDEDEC")
        self.tree_dupes.tag_configure(
            "scanning",  background="#EBF3FB")

        sb3 = ttk.Scrollbar(table_frame2,
                             orient="vertical",
                             command=self.tree_dupes.yview)
        self.tree_dupes.configure(
            yscrollcommand=sb3.set)
        self.tree_dupes.grid(row=0, column=0,
                              sticky="nsew",
                              padx=(12,0), pady=12)
        sb3.grid(row=0, column=1, sticky="ns",
                 pady=12)

    def _build_undo_section(self):
        panel = ctk.CTkFrame(self.main,
                              fg_color=self.bg,
                              corner_radius=0)
        self.sections["undo"] = panel
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(0, weight=1)

        center = ctk.CTkFrame(panel,
                               fg_color="transparent")
        center.grid(row=0, column=0)

        ctk.CTkLabel(center, text="↩",
                      font=ctk.CTkFont("Arial", 64),
                      text_color=self.C["coral"]).pack(
                      pady=(0,16))

        self.lbl_undo_title = ctk.CTkLabel(center,
                      text="Undo Organization",
                      font=ctk.CTkFont("Arial", 24, "bold"),
                      text_color=self.text_color)
        self.lbl_undo_title.pack()

        ctk.CTkLabel(center,
                      text="Moves all organized files back\n"
                           "to the root folder",
                      font=ctk.CTkFont("Arial", 12),
                      text_color=self.muted,
                      justify="center").pack(pady=12)

        self.lbl_undo_folder = ctk.CTkLabel(
            center,
            text="No folder selected",
            font=ctk.CTkFont("Arial", 11),
            text_color=self.C["forest_mid"])
        self.lbl_undo_folder.pack(pady=(0,24))

        ctk.CTkButton(center,
                       text="↩  Undo Organization",
                       command=self._run_undo,
                       fg_color=self.C["coral"],
                       hover_color=self.C["coral_dark"],
                       text_color=self.C["white"],
                       font=ctk.CTkFont("Arial", 13, "bold"),
                       height=44,
                       corner_radius=10,
                       width=220).pack()

    def _build_log_section(self):
        panel = ctk.CTkFrame(self.main,
                              fg_color=self.bg,
                              corner_radius=0)
        self.sections["log"] = panel
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(1, weight=1)

        header = ctk.CTkFrame(panel,
                               fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew",
                    padx=20, pady=(20,8))
        header.columnconfigure(0, weight=1)

        ctk.CTkLabel(header,
                      text="📋  Session Log",
                      font=ctk.CTkFont("Arial", 18, "bold"),
                      text_color=self.text_color).grid(
                      row=0, column=0, sticky="w")

        ctk.CTkButton(header,
                       text="🔄 Refresh",
                       command=self._refresh_log,
                       fg_color=self.C["forest_light"],
                       hover_color=self.C["forest_mid"],
                       text_color=self.C["white"],
                       font=ctk.CTkFont("Arial", 10),
                       height=30,
                       corner_radius=6,
                       width=90).grid(
                       row=0, column=1, sticky="e")

        self.log_text = ctk.CTkTextbox(
            panel,
            font=ctk.CTkFont("Courier New", 11),
            fg_color=self.C["log_bg"],
            text_color=self.C["log_fg"],
            corner_radius=12,
            state="disabled")
        self.log_text.grid(row=1, column=0,
                            sticky="nsew",
                            padx=20, pady=(0,20))

    def _build_status_bar(self):
        self.status_bar = ctk.CTkFrame(
            self,
            fg_color=self.C["forest"],
            corner_radius=0,
            height=32)
        self.status_bar.grid(row=1, column=1,
                              sticky="ew")
        self.status_bar.grid_propagate(False)
        self.status_bar.columnconfigure(0, weight=1)

        self.lbl_status = ctk.CTkLabel(
            self.status_bar,
            text="Ready — load a folder to get started",
            font=ctk.CTkFont("Arial", 10),
            text_color=self.C["sage"],
            anchor="w")
        self.lbl_status.grid(row=0, column=0,
                              sticky="w", padx=16,
                              pady=6)

        self.lbl_folder = ctk.CTkLabel(
            self.status_bar,
            text="No folder loaded",
            font=ctk.CTkFont("Arial", 10),
            text_color=self.C["forest_mid"],
            anchor="e")
        self.lbl_folder.grid(row=0, column=1,
                              sticky="e", padx=16,
                              pady=6)

    # ── Helper Widgets ───────────────────────────────────────
    def _section_header(self, parent, title, subtitle):
        header = ctk.CTkFrame(parent,
                               fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew",
                    padx=20, pady=(20,12))

        ctk.CTkLabel(header, text=title,
                      font=ctk.CTkFont("Arial", 20, "bold"),
                      text_color=self.text_color).pack(
                      anchor="w")

        ctk.CTkLabel(header, text=subtitle,
                      font=ctk.CTkFont("Arial", 11),
                      text_color=self.muted).pack(
                      anchor="w")

    # ── Section Management ───────────────────────────────────
    def _show_section(self, key):
        for section in self.sections.values():
            section.grid_forget()
        self.sections[key].grid(row=0, column=0,
                                  sticky="nsew")

        for k, btn in self.nav_buttons.items():
            btn.configure(
                fg_color=self.C["forest_light"]
                if k == key else "transparent")
        self.active_section = key

    def _set_status(self, message, color=None):
        self.lbl_status.configure(
            text=message,
            text_color=color or self.C["sage"])
        self.update_idletasks()

    # ── Navigation Actions ───────────────────────────────────
    def _nav_action(self, key):
        if self.operation_running:
            messagebox.showwarning("Busy",
                "An operation is running. Please wait.")
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
            self._show_section("undo")
        elif key == "log":
            self._show_section("log")
            self._refresh_log()

    # ── Load Folder ──────────────────────────────────────────
    def _load_folder(self):
        path = filedialog.askdirectory(
            title="Select a folder to organize")
        if not path:
            return

        self.folder_path = path
        folder_name = os.path.basename(path)

        files = [f for f in os.listdir(path)
                 if os.path.isfile(
                     os.path.join(path, f))]
        total_size = sum(
            os.path.getsize(os.path.join(path, f))
            for f in files
        ) / (1024 * 1024)

        self.lbl_folder.configure(
            text=f"📂  {folder_name}")
        self.lbl_undo_folder.configure(
            text=f"Folder: {folder_name}")

        self._set_status(
            f"✓ Loaded: {folder_name} — "
            f"{len(files)} files, "
            f"{total_size:.1f} MB",
            self.C["sage"])

        self._show_section("preview")
        self._run_preview()

    # ── Preview ──────────────────────────────────────────────
    def _run_preview(self):
        if not self.folder_path:
            messagebox.showwarning("No Folder",
                "Please load a folder first.")
            return

        self._show_section("preview")

        for row in self.tree_preview.get_children():
            self.tree_preview.delete(row)

        files = [f for f in os.listdir(
                     self.folder_path)
                 if os.path.isfile(os.path.join(
                     self.folder_path, f))]

        category_data = {}
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            category = get_category(ext)
            if category not in category_data:
                category_data[category] = {
                    "count": 0, "extensions": set()}
            category_data[category]["count"] += 1
            if ext:
                category_data[category][
                    "extensions"].add(ext)

        for category, data in sorted(
                category_data.items(),
                key=lambda x: x[1]["count"],
                reverse=True):
            exts = ", ".join(
                sorted(data["extensions"]))
            self.tree_preview.insert("", "end",
                values=(
                    category,
                    data["count"],
                    exts if exts else "various"
                ))

        self._set_status(
            f"Preview — {len(files)} files in "
            f"{len(category_data)} categories",
            self.C["sage"])

    # ── Organize ─────────────────────────────────────────────
    def _run_organize(self):
        if not self.folder_path:
            messagebox.showwarning("No Folder",
                "Please load a folder first.")
            return

        files = [f for f in os.listdir(
                     self.folder_path)
                 if os.path.isfile(os.path.join(
                     self.folder_path, f))]
        if not files:
            messagebox.showinfo("Empty",
                "No files found to organize.")
            return

        if not messagebox.askyesno("Confirm",
                f"Organize {len(files)} files in:\n"
                f"{self.folder_path}?"):
            return

        self._show_section("organize")
        for row in self.tree_organize.get_children():
            self.tree_organize.delete(row)
        self.progress_bar.set(0)
        self.lbl_progress.configure(
            text="Starting...")
        self.operation_running = True
        log_session_start(self.folder_path)

        threading.Thread(
            target=self._organize_thread,
            daemon=True).start()

    def _organize_thread(self):
        def callback(current, total, message,
                     skipped=False, error=False):
            pct = current / total
            self.after(0,
                self._on_organize_progress,
                pct, message, skipped, error)

        moved, skipped = organize_folder(
            self.folder_path,
            progress_callback=callback)
        self.after(0, self._on_organize_complete,
                   moved, skipped)

    def _on_organize_progress(self, pct, message,
                               skipped, error):
        self.progress_bar.set(pct)
        self.lbl_progress.configure(text=message)

        parts = message.split("→")
        filename = parts[0].replace(
            "Moved: ", "").replace(
            "Skipped (exists): ", "").replace(
            "Error: ", "").strip()
        dest = parts[1].strip() \
               if len(parts) > 1 else "—"

        if error:
            status = "❌ Error"
            tag    = "error"
        elif skipped:
            status = "⏭ Skipped"
            tag    = "skipped"
        else:
            status = "✓ Moved"
            tag    = "moved"

        self.tree_organize.insert("", "end",
            values=(status, filename, dest),
            tags=(tag,))
        self.tree_organize.yview_moveto(1)

    def _on_organize_complete(self, moved, skipped):
        self.progress_bar.set(1)
        self.operation_running = False
        log_session_end(moved, skipped)
        self._set_status(
            f"✓ Complete — {moved} moved, "
            f"{skipped} skipped",
            self.C["sage"])
        messagebox.showinfo("Done",
            f"Complete!\n\n"
            f"Files moved:   {moved}\n"
            f"Files skipped: {skipped}")

    # ── Duplicates ───────────────────────────────────────────
    def _run_duplicates(self):
        if not self.folder_path:
            messagebox.showwarning("No Folder",
                "Please load a folder first.")
            return

        if not messagebox.askyesno("Confirm",
                "Scan for duplicates and move them\n"
                "to a Duplicates folder?"):
            return

        self._show_section("duplicates")
        for row in self.tree_dupes.get_children():
            self.tree_dupes.delete(row)
        self.dup_progress_bar.set(0)
        self.lbl_dup_progress.configure(
            text="Starting scan...")
        self.operation_running = True

        threading.Thread(
            target=self._duplicates_thread,
            daemon=True).start()

    def _duplicates_thread(self):
        def callback(current, total, message,
                     duplicate=False, **kwargs):
            pct = current / total
            self.after(0, self._on_dup_progress,
                       pct, message, duplicate)

        count = find_and_move_duplicates(
            self.folder_path,
            progress_callback=callback)
        self.after(0,
            self._on_duplicates_complete, count)

    def _on_dup_progress(self, pct, message,
                          duplicate):
        self.dup_progress_bar.set(pct)
        self.lbl_dup_progress.configure(
            text=message)
        tag    = "duplicate" if duplicate \
                 else "scanning"
        status = "🔴 Duplicate" if duplicate \
                 else "🔍 Scanning"
        filename = message.replace(
            "Duplicate found: ", "").replace(
            "Scanning: ", "").strip()
        self.tree_dupes.insert("", "end",
            values=(filename, status),
            tags=(tag,))
        self.tree_dupes.yview_moveto(1)

    def _on_duplicates_complete(self, count):
        self.dup_progress_bar.set(1)
        self.operation_running = False
        if count == 0:
            self._set_status(
                "✓ No duplicates found",
                self.C["sage"])
            messagebox.showinfo("Clean",
                "No duplicate files found.")
        else:
            self._set_status(
                f"✓ {count} duplicate(s) moved "
                f"to Duplicates folder",
                self.C["amber"])
            messagebox.showinfo("Duplicates Found",
                f"{count} duplicate(s) moved\n"
                f"to Duplicates folder for review.")

    # ── Undo ─────────────────────────────────────────────────
    def _run_undo(self):
        if not self.folder_path:
            messagebox.showwarning("No Folder",
                "Please load a folder first.")
            return
        if not messagebox.askyesno("Confirm",
                "Move all organized files back\n"
                "to the root folder?"):
            return
        self.operation_running = True
        threading.Thread(
            target=self._undo_thread,
            daemon=True).start()

    def _undo_thread(self):
        undo_organization(self.folder_path)
        self.after(0, self._on_undo_complete)

    def _on_undo_complete(self):
        self.operation_running = False
        self._set_status(
            "✓ Undo complete — files restored",
            self.C["sage"])
        messagebox.showinfo("Done",
            "Files restored to original folder.")

    # ── Log ──────────────────────────────────────────────────
    def _refresh_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("0.0", "end")
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r",
                      encoding="utf-8") as f:
                content = f.read()
            self.log_text.insert("end",
                content if content
                else "Log is empty.")
        else:
            self.log_text.insert("end",
                "No log file yet.\n"
                "Run an organization to create one.")
        self.log_text.configure(state="disabled")
        self.log_text.see("end")

    # ── Dark Mode ────────────────────────────────────────────
    def _toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self._apply_colors()

        self.configure(fg_color=self.bg)
        self.sidebar.configure(
            fg_color=self.sidebar_bg)
        self.main.configure(fg_color=self.bg)
        self.status_bar.configure(
            fg_color=self.C["forest"]
            if not self.dark_mode
            else self.C["dark_bg"])

        self.btn_theme.configure(
            text="☀️  Light Mode"
            if self.dark_mode else "🌙  Dark Mode")

        self.log_text.configure(
            fg_color=self.log_bg,
            text_color=self.log_fg)

        style = ttk.Style()
        style.configure("Org.Treeview",
                         background=self.panel_bg,
                         foreground=self.text_color,
                         fieldbackground=self.panel_bg)

        self._theme_panels()
        # Explicitly update welcome and undo sections
        self.sections["welcome"].configure(
            fg_color=self.bg)
        self.sections["undo"].configure(
            fg_color=self.bg)
        self.lbl_undo_title.configure(
            text_color=self.text_color)
        self.lbl_welcome_title.configure(
            text_color=self.C["sage"]
            if self.dark_mode else self.C["forest"])
        self.update_idletasks()
        self.update()

    def _theme_panels(self):
        for key, panel in self.sections.items():
            self._theme_recursive(panel)

    def _theme_recursive(self, widget):
        try:
            wc = widget.winfo_class()
            if wc == "CTkFrame":
                # Check if it looks like a surface card
                current = widget.cget("fg_color")
                if current not in (
                        "transparent", self.C["forest"],
                        self.C["dark_bg"],
                        self.C["log_bg"]):
                    widget.configure(
                        fg_color=self.panel_bg)
            elif wc == "CTkLabel":
                current_color = widget.cget(
                    "text_color")
                if current_color not in (
                        self.C["coral"],
                        self.C["sage"],
                        self.C["forest_mid"],
                        self.C["amber"],
                        self.C["muted"],
                        self.C["dark_muted"]):
                    widget.configure(
                        text_color=self.text_color)
        except Exception:
            pass
        for child in widget.winfo_children():
            self._theme_recursive(child)

# ── Entry Point ──────────────────────────────────────────────
if __name__ == "__main__":
    app = FileOrganizerV11()
    app.mainloop()
