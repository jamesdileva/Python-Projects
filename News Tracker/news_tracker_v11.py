# news_tracker_v11.py
# News Tracker v1.1 — CustomTkinter modern UI
# Dark Charcoal and Electric Blue — editorial feed layout

import os
import threading
import webbrowser
import customtkinter as ctk
from tkinter import messagebox, filedialog
from tkinter import ttk
from datetime import datetime
import requests
from dotenv import load_dotenv, set_key

load_dotenv()

BASE_URL  = "https://newsapi.org/v2"
ENV_FILE  = ".env"
CATEGORIES = ["general", "business", "entertainment",
               "health", "science", "sports", "technology"]

# ── CustomTkinter Setup ──────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Color Palette ────────────────────────────────────────────
COLORS = {
    "charcoal":     "#1C1C2E",
    "steel":        "#2A2A3E",
    "steel_light":  "#3A3A52",
    "electric":     "#0066FF",
    "electric_light":"#4D94FF",
    "electric_dark": "#0052CC",
    "white":        "#F0F0F0",
    "muted":        "#888899",
    "green":        "#2ECC71",
    "red":          "#E74C3C",
    "amber":        "#F39C12",
    "marquee_bg":   "#0A0A1A",
    "marquee_fg":   "#00FF88",
    "dark_bg":      "#0F0F1A",
    "dark_steel":   "#1C1C2E",
    "light_bg":     "#F0F2F5",
    "light_steel":  "#FFFFFF",
    "light_muted":  "#6C757D",
    "light_text":   "#1A1A2E",
}

# ── API Layer ────────────────────────────────────────────────
def get_api_key():
    return os.environ.get("NEWS_API_KEY", "")

def fetch_headlines(category="general", api_key=None):
    params = {
        "apiKey": api_key or get_api_key(),
        "country": "us",
        "category": category,
        "pageSize": 20
    }
    response = requests.get(
        f"{BASE_URL}/top-headlines", params=params)
    return response.json()

def fetch_keyword(keyword, api_key=None):
    params = {
        "apiKey": api_key or get_api_key(),
        "q": keyword,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 20
    }
    response = requests.get(
        f"{BASE_URL}/everything", params=params)
    return response.json()

def parse_articles(data):
    if data.get("status") != "ok":
        return None, data.get("message", "Unknown error")
    return data.get("articles", []), None

# ── Main Application ─────────────────────────────────────────
class NewsTrackerV11(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("News Tracker")
        self.geometry("1200x740")
        self.minsize(1000, 660)

        self.articles        = []
        self.saved_articles  = []
        self.dark_mode       = True
        self.marquee_active  = False
        self.marquee_text    = ""
        self.marquee_pos     = 0
        self.auto_refresh    = False
        self.refresh_interval = 30
        self.refresh_after_id = None

        self._apply_colors()
        self._build_ui()
        self._check_api_key()

    def _apply_colors(self):
        self.C = COLORS
        if self.dark_mode:
            ctk.set_appearance_mode("dark")
            self.bg         = self.C["charcoal"]
            self.panel_bg   = self.C["steel"]
            self.surface    = self.C["steel_light"]
            self.text_color = self.C["white"]
            self.muted      = self.C["muted"]
            self.toolbar_bg = self.C["dark_bg"]
        else:
            ctk.set_appearance_mode("light")
            self.bg         = self.C["light_bg"]
            self.panel_bg   = self.C["light_steel"]
            self.surface    = "#E9ECEF"
            self.text_color = self.C["light_text"]
            self.muted      = self.C["light_muted"]
            self.toolbar_bg = self.C["steel"]

    # ── UI Construction ──────────────────────────────────────
    def _build_ui(self):
        self.configure(fg_color=self.bg)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_toolbar()
        self._build_main_area()
        self._build_marquee_bar()
        self._build_bottom_buttons()

    def _build_toolbar(self):
        self.toolbar = ctk.CTkFrame(self,
                                     fg_color=self.C["dark_bg"],
                                     corner_radius=0,
                                     height=64)
        self.toolbar.grid(row=0, column=0, sticky="ew")
        self.toolbar.grid_propagate(False)
        self.toolbar.columnconfigure(4, weight=1)

        # Title
        ctk.CTkLabel(self.toolbar,
                      text="📰  News Tracker",
                      font=ctk.CTkFont("Arial", 18, "bold"),
                      text_color=self.C["white"]).grid(
                      row=0, column=0,
                      padx=(20,4), pady=16, sticky="w")

        ctk.CTkLabel(self.toolbar,
                      text="live news feed",
                      font=ctk.CTkFont("Arial", 10),
                      text_color=self.C["muted"]).grid(
                      row=0, column=1,
                      padx=(0,20), pady=16, sticky="w")

        # Category
        self.var_category = ctk.StringVar(value="general")
        ctk.CTkOptionMenu(self.toolbar,
                           variable=self.var_category,
                           values=CATEGORIES,
                           command=lambda v: None,
                           fg_color=self.C["steel"],
                           button_color=self.C["electric"],
                           button_hover_color=self.C["electric_dark"],
                           text_color=self.C["white"],
                           font=ctk.CTkFont("Arial", 11),
                           width=150, height=36).grid(
                           row=0, column=2,
                           padx=(0,8), pady=14)

        # Fetch button
        ctk.CTkButton(self.toolbar,
                       text="🔍  Get Headlines",
                       command=self._fetch_headlines,
                       fg_color=self.C["electric"],
                       hover_color=self.C["electric_dark"],
                       text_color=self.C["white"],
                       font=ctk.CTkFont("Arial", 11, "bold"),
                       height=36, corner_radius=8,
                       width=140).grid(
                       row=0, column=3,
                       padx=(0,8), pady=14)

        # Search entry
        self.var_search = ctk.StringVar()
        search = ctk.CTkEntry(self.toolbar,
                               textvariable=self.var_search,
                               placeholder_text="Search keywords...",
                               fg_color=self.C["steel"],
                               border_color=self.C["electric"],
                               text_color=self.C["white"],
                               placeholder_text_color=self.C["muted"],
                               font=ctk.CTkFont("Arial", 11),
                               width=180, height=36)
        search.grid(row=0, column=5,
                    padx=(0,8), pady=14)
        search.bind("<Return>",
                    lambda e: self._fetch_keyword())

        ctk.CTkButton(self.toolbar,
                       text="🔎",
                       command=self._fetch_keyword,
                       fg_color=self.C["steel_light"],
                       hover_color=self.C["electric_dark"],
                       text_color=self.C["white"],
                       font=ctk.CTkFont("Arial", 14),
                       width=40, height=36,
                       corner_radius=8).grid(
                       row=0, column=6,
                       padx=(0,8), pady=14)

        ctk.CTkButton(self.toolbar,
                       text="⚙",
                       command=self._show_settings,
                       fg_color=self.C["steel_light"],
                       hover_color=self.C["electric_dark"],
                       text_color=self.C["white"],
                       font=ctk.CTkFont("Arial", 14),
                       width=40, height=36,
                       corner_radius=8).grid(
                       row=0, column=7,
                       padx=(0,8), pady=14)

        self.btn_theme = ctk.CTkButton(
            self.toolbar,
            text="☀️",
            command=self._toggle_theme,
            fg_color=self.C["steel_light"],
            hover_color=self.C["electric_dark"],
            text_color=self.C["white"],
            font=ctk.CTkFont("Arial", 14),
            width=40, height=36,
            corner_radius=8)
        self.btn_theme.grid(row=0, column=8,
                             padx=(0,8), pady=14)

        # Status
        self.lbl_status = ctk.CTkLabel(
            self.toolbar,
            text="Enter a category or keyword to begin",
            font=ctk.CTkFont("Arial", 10),
            text_color=self.C["muted"])
        self.lbl_status.grid(row=0, column=9,
                              padx=(0,20), pady=14,
                              sticky="e")

    def _build_main_area(self):
        main = ctk.CTkFrame(self, fg_color=self.bg,
                             corner_radius=0)
        main.grid(row=1, column=0, sticky="nsew",
                  padx=16, pady=(12,8))
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        self._build_headlines_panel(main)
        self._build_saved_panel(main)

    def _build_headlines_panel(self, parent):
        self.headlines_frame = ctk.CTkFrame(
            parent,
            fg_color=self.panel_bg,
            corner_radius=12)
        self.headlines_frame.grid(
            row=0, column=0, sticky="nsew",
            padx=(0,12))
        self.headlines_frame.columnconfigure(0, weight=1)
        self.headlines_frame.rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self.headlines_frame,
                               fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew",
                    padx=16, pady=(14,8))
        header.columnconfigure(1, weight=1)

        ctk.CTkLabel(header,
                      text="HEADLINES",
                      font=ctk.CTkFont("Arial", 11, "bold"),
                      text_color=self.C["electric_light"]).grid(
                      row=0, column=0, sticky="w")

        self.lbl_count = ctk.CTkLabel(
            header, text="",
            font=ctk.CTkFont("Arial", 10),
            text_color=self.C["muted"])
        self.lbl_count.grid(row=0, column=1, sticky="e")

        # Scrollable article list
        self.headlines_scroll = ctk.CTkScrollableFrame(
            self.headlines_frame,
            fg_color="transparent",
            scrollbar_button_color=self.C["steel_light"],
            scrollbar_button_hover_color=self.C["electric"])
        self.headlines_scroll.grid(
            row=1, column=0, sticky="nsew",
            padx=8, pady=(0,8))
        self.headlines_scroll.columnconfigure(0, weight=1)

        ctk.CTkLabel(self.headlines_scroll,
                      text="Fetch headlines to see articles here",
                      font=ctk.CTkFont("Arial", 11),
                      text_color=self.C["muted"]).pack(
                      pady=40)

    def _build_saved_panel(self, parent):
        self.saved_frame = ctk.CTkFrame(
            parent,
            fg_color=self.panel_bg,
            corner_radius=12)
        self.saved_frame.grid(
            row=0, column=1, sticky="nsew")
        self.saved_frame.columnconfigure(0, weight=1)
        self.saved_frame.rowconfigure(1, weight=1)

        ctk.CTkLabel(self.saved_frame,
                      text="SAVED ARTICLES",
                      font=ctk.CTkFont("Arial", 11, "bold"),
                      text_color=self.C["electric_light"]).grid(
                      row=0, column=0, sticky="w",
                      padx=16, pady=(14,8))

        self.saved_scroll = ctk.CTkScrollableFrame(
            self.saved_frame,
            fg_color="transparent",
            scrollbar_button_color=self.C["steel_light"],
            scrollbar_button_hover_color=self.C["electric"])
        self.saved_scroll.grid(
            row=1, column=0, sticky="nsew",
            padx=8, pady=(0,8))
        self.saved_scroll.columnconfigure(0, weight=1)

        ctk.CTkLabel(self.saved_scroll,
                      text="No saved articles yet",
                      font=ctk.CTkFont("Arial", 11),
                      text_color=self.C["muted"]).pack(
                      pady=40)

    def _build_marquee_bar(self):
        self.marquee_frame = ctk.CTkFrame(
            self,
            fg_color=self.C["marquee_bg"],
            corner_radius=0,
            height=32)
        self.marquee_frame.grid(
            row=2, column=0, sticky="ew")
        self.marquee_frame.grid_propagate(False)
        self.marquee_frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(self.marquee_frame,
                      text=" 📰 LIVE ",
                      font=ctk.CTkFont("Arial", 9, "bold"),
                      fg_color=self.C["electric"],
                      text_color=self.C["white"],
                      corner_radius=4).grid(
                      row=0, column=0,
                      padx=(8,6), pady=5)

        self.marquee_label = ctk.CTkLabel(
            self.marquee_frame,
            text="Enable marquee after fetching headlines",
            font=ctk.CTkFont("Courier New", 18, "bold"),
            text_color=self.C["marquee_fg"],
            fg_color="transparent",
            anchor="w")
        self.marquee_label.grid(
            row=0, column=1, sticky="ew", padx=(0,8))

    def _build_bottom_buttons(self):
        btn_frame = ctk.CTkFrame(self,
                                  fg_color="transparent")
        btn_frame.grid(row=3, column=0, sticky="ew",
                        padx=16, pady=(0,16))

        btn_cfg = {
            "font": ctk.CTkFont("Arial", 11),
            "height": 36,
            "corner_radius": 8
        }

        ctk.CTkButton(btn_frame,
                       text="🔖  Save All Articles",
                       command=self._save_all_articles,
                       fg_color=self.C["electric"],
                       hover_color=self.C["electric_dark"],
                       text_color=self.C["white"],
                       **btn_cfg).pack(side="left", padx=(0,8))

        ctk.CTkButton(btn_frame,
                       text="💾  Export Saved",
                       command=self._export_saved,
                       fg_color="#217346",
                       hover_color="#1A5C38",
                       text_color=self.C["white"],
                       **btn_cfg).pack(side="left", padx=(0,8))

        ctk.CTkButton(btn_frame,
                       text="🗑  Clear Saved",
                       command=self._clear_saved,
                       fg_color=self.C["red"],
                       hover_color="#C0392B",
                       text_color=self.C["white"],
                       **btn_cfg).pack(side="left", padx=(0,8))

        self.btn_live = ctk.CTkButton(
            btn_frame,
            text="▶  Start Live Feed",
            command=self._toggle_live_feed,
            fg_color=self.C["green"],
            hover_color="#27AE60",
            text_color=self.C["white"],
            **btn_cfg)
        self.btn_live.pack(side="left", padx=(0,8))

        self.lbl_last_updated = ctk.CTkLabel(
            btn_frame,
            text="",
            font=ctk.CTkFont("Arial", 9),
            text_color=self.C["muted"])
        self.lbl_last_updated.pack(
            side="left", padx=(0,16))

        self.btn_marquee = ctk.CTkButton(
            btn_frame,
            text="📰  Marquee: OFF",
            command=self._toggle_marquee,
            fg_color=self.C["steel_light"],
            hover_color=self.C["electric_dark"],
            text_color=self.C["white"],
            **btn_cfg)
        self.btn_marquee.pack(side="left", padx=(0,8))

        ctk.CTkButton(btn_frame,
                       text="⤢  Pop Out",
                       command=self._popout_marquee,
                       fg_color=self.C["steel_light"],
                       hover_color=self.C["electric_dark"],
                       text_color=self.C["white"],
                       font=ctk.CTkFont("Arial", 11),
                       height=36, corner_radius=8,
                       width=90).pack(side="left")

    # ── Status Helper ────────────────────────────────────────
    def _set_status(self, message, color=None):
        self.lbl_status.configure(
            text=message,
            text_color=color or self.C["muted"])
        self.update_idletasks()

    # ── API Key ──────────────────────────────────────────────
    def _check_api_key(self):
        if not get_api_key():
            self._show_settings(first_run=True)

    def _show_settings(self, first_run=False):
        win = ctk.CTkToplevel(self)
        win.title("Settings — API Key")
        win.geometry("460x220")
        win.resizable(False, False)
        win.grab_set()
        win.configure(fg_color=self.C["steel"])

        msg = ("Welcome! Enter your NewsAPI key to get started.\n"
               "Get a free key at newsapi.org") \
              if first_run else "Update your NewsAPI key below."

        ctk.CTkLabel(win, text=msg,
                      font=ctk.CTkFont("Arial", 11),
                      text_color=self.C["white"],
                      wraplength=400).pack(
                      pady=(20,12), padx=20)

        key_frame = ctk.CTkFrame(win,
                                  fg_color="transparent")
        key_frame.pack(fill="x", padx=20, pady=(0,4))

        ctk.CTkLabel(key_frame, text="API Key:",
                      font=ctk.CTkFont("Arial", 11, "bold"),
                      text_color=self.C["white"]).pack(
                      side="left", padx=(0,8))

        var_key = ctk.StringVar(value=get_api_key())
        entry = ctk.CTkEntry(key_frame,
                              textvariable=var_key,
                              show="*",
                              fg_color=self.C["steel_light"],
                              border_color=self.C["electric"],
                              text_color=self.C["white"],
                              width=250)
        entry.pack(side="left", padx=(0,8))

        self._show_key = False
        def toggle_show():
            self._show_key = not self._show_key
            entry.configure(
                show="" if self._show_key else "*")
            btn_show.configure(
                text="🙈" if self._show_key else "👁")

        btn_show = ctk.CTkButton(key_frame,
                                  text="👁",
                                  command=toggle_show,
                                  fg_color=self.C["steel_light"],
                                  hover_color=self.C["electric_dark"],
                                  text_color=self.C["white"],
                                  width=36, height=32,
                                  corner_radius=6)
        btn_show.pack(side="left")

        def save_key():
            key = var_key.get().strip()
            if not key:
                messagebox.showwarning("Missing Key",
                    "Please enter an API key.", parent=win)
                return
            os.environ["NEWS_API_KEY"] = key
            set_key(ENV_FILE, "NEWS_API_KEY", key)
            self._set_status("✓ API key saved",
                              self.C["green"])
            win.destroy()

        ctk.CTkButton(win, text="Save API Key",
                       command=save_key,
                       fg_color=self.C["electric"],
                       hover_color=self.C["electric_dark"],
                       text_color=self.C["white"],
                       font=ctk.CTkFont("Arial", 12, "bold"),
                       height=38, corner_radius=8).pack(
                       fill="x", padx=20, pady=16)

    # ── Fetch Headlines ──────────────────────────────────────
    def _fetch_headlines(self):
        if not get_api_key():
            self._show_settings(first_run=True)
            return
        category = self.var_category.get()
        self._set_status(
            f"Fetching {category} headlines...",
            self.C["amber"])
        threading.Thread(
            target=self._fetch_thread,
            args=(category, "category"),
            daemon=True).start()

    def _fetch_keyword(self):
        if not get_api_key():
            self._show_settings(first_run=True)
            return
        keyword = self.var_search.get().strip()
        if not keyword:
            messagebox.showwarning("Empty Search",
                "Please enter a keyword.")
            return
        self._set_status(
            f"Searching '{keyword}'...",
            self.C["amber"])
        threading.Thread(
            target=self._fetch_thread,
            args=(keyword, "keyword"),
            daemon=True).start()

    def _fetch_thread(self, query, mode):
        try:
            if mode == "category":
                data = fetch_headlines(query)
            else:
                data = fetch_keyword(query)
            articles, error = parse_articles(data)
            self.after(0, self._on_fetched,
                       articles, error)
        except Exception as e:
            self.after(0, self._on_error, str(e))

    def _on_fetched(self, articles, error):
        if error:
            self._set_status(f"⚠ {error}",
                              self.C["red"])
            return
        self.articles = articles
        self._populate_headlines(articles)
        self._update_marquee_text(articles)
        timestamp = datetime.now().strftime("%I:%M %p")
        self._set_status(
            f"✓ {len(articles)} articles — {timestamp}",
            self.C["green"])
        self.lbl_count.configure(
            text=f"{len(articles)} articles")

    def _on_error(self, message):
        self._set_status(
            f"⚠ Connection error", self.C["red"])
        messagebox.showerror("Error",
            f"Could not fetch news:\n{message}")

    # ── Populate Headlines ───────────────────────────────────
    def _populate_headlines(self, articles):
        for widget in self.headlines_scroll.winfo_children():
            widget.destroy()

        if not articles:
            ctk.CTkLabel(self.headlines_scroll,
                          text="No articles found",
                          text_color=self.C["muted"]).pack(
                          pady=40)
            return

        for i, article in enumerate(articles):
            self._make_article_card(
                self.headlines_scroll, article, i,
                is_saved=False)

    def _make_article_card(self, parent, article,
                            index, is_saved=False):
        card = ctk.CTkFrame(parent,
                             fg_color=self.surface,
                             corner_radius=8)
        card.pack(fill="x", pady=(0,6), padx=4)
        card.columnconfigure(0, weight=1)

        title = article.get("title", "No title") \
                or "No title"
        source = article.get("source", {}) \
                         .get("name", "Unknown")
        date   = article.get("publishedAt", "")[:10]
        url    = article.get("url", "")

        # Title — clickable
        title_lbl = ctk.CTkLabel(card,
                                   text=title,
                                   font=ctk.CTkFont(
                                       "Arial", 11, "bold"),
                                   text_color=self.text_color,
                                   anchor="w",
                                   wraplength=550,
                                   justify="left",
                                   cursor="hand2")
        title_lbl.grid(row=0, column=0, sticky="ew",
                        padx=12, pady=(10,2))

        if url:
            title_lbl.bind("<Button-1>",
                lambda e, u=url: webbrowser.open(u))
            title_lbl.bind("<Enter>",
                lambda e, l=title_lbl: l.configure(
                    text_color=self.C["electric_light"]))
            title_lbl.bind("<Leave>",
                lambda e, l=title_lbl: l.configure(
                    text_color=self.text_color))

        # Source and date
        ctk.CTkLabel(card,
                      text=f"{source}  ·  {date}",
                      font=ctk.CTkFont("Arial", 9),
                      text_color=self.C["muted"],
                      anchor="w").grid(
                      row=1, column=0, sticky="w",
                      padx=12, pady=(0,8))

        # Separator
        if not is_saved:
            ctk.CTkFrame(parent, height=1,
                          fg_color=self.C["steel"]).pack(
                          fill="x", padx=4)

    def _populate_saved(self):
        for widget in self.saved_scroll.winfo_children():
            widget.destroy()

        if not self.saved_articles:
            ctk.CTkLabel(self.saved_scroll,
                          text="No saved articles yet",
                          text_color=self.C["muted"]).pack(
                          pady=40)
            return

        for i, article in enumerate(self.saved_articles):
            self._make_saved_card(article, i)

    def _make_saved_card(self, article, index):
        card = ctk.CTkFrame(self.saved_scroll,
                             fg_color=self.surface,
                             corner_radius=8)
        card.pack(fill="x", pady=(0,6), padx=4)

        title  = article.get("title", "No title") \
                 or "No title"
        source = article.get("source", {}) \
                         .get("name", "Unknown")
        url    = article.get("url", "")

        title_lbl = ctk.CTkLabel(card,
                                   text=title,
                                   font=ctk.CTkFont(
                                       "Arial", 10, "bold"),
                                   text_color=self.text_color,
                                   anchor="w",
                                   wraplength=220,
                                   justify="left",
                                   cursor="hand2")
        title_lbl.pack(fill="x", padx=10,
                        pady=(8,2))

        if url:
            title_lbl.bind("<Button-1>",
                lambda e, u=url: webbrowser.open(u))
            title_lbl.bind("<Enter>",
                lambda e, l=title_lbl: l.configure(
                    text_color=self.C["electric_light"]))
            title_lbl.bind("<Leave>",
                lambda e, l=title_lbl: l.configure(
                    text_color=self.text_color))

        ctk.CTkLabel(card,
                      text=source,
                      font=ctk.CTkFont("Arial", 9),
                      text_color=self.C["muted"],
                      anchor="w").pack(
                      fill="x", padx=10,
                      pady=(0,8))

    # ── Save Articles ────────────────────────────────────────
    def _save_article(self):
        if not self.articles:
            messagebox.showwarning("No Articles",
                "Fetch some headlines first.")
            return

        saved = 0
        for widget in \
                self.headlines_scroll.winfo_children():
            if hasattr(widget, "_article_index"):
                idx = widget._article_index
                if idx < len(self.articles):
                    article = self.articles[idx]
                    if article not in self.saved_articles:
                        self.saved_articles.append(article)
                        saved += 1

        if not self.articles:
            return

        # Save most recent fetch article at top
        article = self.articles[0] \
                  if self.articles else None
        if article and article not in self.saved_articles:
            self.saved_articles.append(article)
            self._populate_saved()
            self._set_status(
                f"✓ Article saved — "
                f"{len(self.saved_articles)} total",
                self.C["green"])
        else:
            self._set_status(
                "Select an article to save — "
                "click the title to open, "
                "or use keyboard shortcut",
                self.C["muted"])

    def _save_specific(self, article):
        if article not in self.saved_articles:
            self.saved_articles.append(article)
            self._populate_saved()
            self._set_status(
                f"✓ Saved — "
                f"{len(self.saved_articles)} articles",
                self.C["green"])
        else:
            self._set_status(
                "Already saved", self.C["amber"])

    def _export_saved(self):
        if not self.saved_articles:
            messagebox.showinfo("No Saved Articles",
                "Save some articles first.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            title="Export Saved Articles"
        )
        if not filepath:
            return

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M")
        with open(filepath, "w",
                  encoding="utf-8") as f:
            f.write(f"Saved Articles — {timestamp}\n")
            f.write("=" * 50 + "\n\n")
            for i, article in enumerate(
                    self.saved_articles, 1):
                title  = article.get("title", "No title")
                source = article.get(
                    "source", {}).get("name", "Unknown")
                date   = article.get(
                    "publishedAt", "")[:10]
                url    = article.get("url", "")
                desc   = article.get(
                    "description", "") or ""
                f.write(f"{i}. {title}\n")
                f.write(
                    f"   Source: {source} | {date}\n")
                f.write(f"   {desc}\n")
                f.write(f"   {url}\n\n")

        messagebox.showinfo("Exported",
            f"Articles saved to:\n{filepath}")
        self._set_status(
            "✓ Articles exported", self.C["green"])

    def _clear_saved(self):
        if not self.saved_articles:
            return
        if messagebox.askyesno("Confirm",
                "Clear all saved articles?"):
            self.saved_articles = []
            self._populate_saved()
            self._set_status(
                "Saved articles cleared",
                self.C["muted"])
            
    def _save_all_articles(self):
        if not self.articles:
            messagebox.showwarning("No Articles",
                "Fetch some headlines first.")
            return
        saved_count = 0
        for article in self.articles:
            if article not in self.saved_articles:
                self.saved_articles.append(article)
                saved_count += 1
        if saved_count > 0:
            self._populate_saved()
            self._set_status(
                f"✓ {saved_count} articles saved — "
                f"{len(self.saved_articles)} total",
                self.C["green"])
        else:
            self._set_status(
                "All articles already saved",
                self.C["amber"])

    # ── Live Feed ────────────────────────────────────────────
    def _toggle_live_feed(self):
        if self.auto_refresh:
            self.auto_refresh = False
            self.btn_live.configure(
                text="▶  Start Live Feed",
                fg_color=self.C["green"])
            if self.refresh_after_id:
                self.after_cancel(self.refresh_after_id)
            self.lbl_last_updated.configure(text="")
            self._set_status(
                "Live feed stopped", self.C["muted"])
        else:
            if not get_api_key():
                self._show_settings(first_run=True)
                return
            self.auto_refresh = True
            self.btn_live.configure(
                text="⏹  Stop Live Feed",
                fg_color=self.C["red"])
            self._set_status(
                "🔴 Live feed active",
                self.C["red"])
            self._run_live_fetch()

    def _run_live_fetch(self):
        if not self.auto_refresh:
            return
        category = self.var_category.get()
        threading.Thread(
            target=self._live_fetch_thread,
            args=(category,),
            daemon=True).start()

    def _live_fetch_thread(self, category):
        try:
            data = fetch_headlines(category)
            articles, error = parse_articles(data)
            self.after(0, self._on_live_fetched,
                       articles, error)
        except Exception as e:
            self.after(0, self._on_error, str(e))

    def _on_live_fetched(self, articles, error):
        if error:
            self._set_status(
                f"⚠ Live feed error: {error}",
                self.C["red"])
        else:
            self.articles = articles
            self._populate_headlines(articles)
            self._update_marquee_text(articles)
            timestamp = datetime.now().strftime(
                "%I:%M %p")
            self.lbl_last_updated.configure(
                text=f"Updated {timestamp}")
            self._set_status(
                f"🔴 Live — {len(articles)} articles"
                f" — {timestamp}",
                self.C["red"])

        if self.auto_refresh:
            ms = self.refresh_interval * 60 * 1000
            self.refresh_after_id = self.after(
                ms, self._run_live_fetch)
    # ── Marquee ──────────────────────────────────────────────
    def _toggle_marquee(self):
        if self.marquee_active:
            self.marquee_active = False
            self.btn_marquee.configure(
                text="📰  Marquee: OFF",
                fg_color=self.C["steel_light"])
            self.marquee_label.configure(
                text="Enable marquee after fetching headlines")
        else:
            if not self.marquee_text:
                messagebox.showinfo("No Headlines",
                    "Fetch headlines first.")
                return
            self.marquee_active = True
            self.btn_marquee.configure(
                text="📰  Marquee: ON",
                fg_color=self.C["electric"])
            self._scroll_marquee()

    def _update_marquee_text(self, articles):
        titles = [a.get("title", "") or ""
                  for a in articles if a.get("title")]
        self.marquee_text = \
            "    ●    ".join(titles) + "    ●    "
        self.marquee_pos = 0

    def _scroll_marquee(self):
        if not self.marquee_active or \
           not self.marquee_text:
            return
        try:
            win_width = self.marquee_label.winfo_width()
            char_width = 7
            display_width = max(
                80, win_width // char_width)
            text   = self.marquee_text
            double = text + text
            snippet = double[
                self.marquee_pos:
                self.marquee_pos + display_width]
            self.marquee_label.configure(text=snippet)
            self.marquee_pos = \
                (self.marquee_pos + 1) % len(text)
        except Exception:
            return
        self.after(120, self._scroll_marquee)

    def _popout_marquee(self):
        if not self.marquee_text:
            messagebox.showinfo("No Headlines",
                "Fetch headlines first.")
            return

        # If popout already open — close it and return
        if hasattr(self, "_popout_win") and \
           self._popout_win.winfo_exists():
            self._close_popout()
            return

        # Open the floating window
        self._popout_win = ctk.CTkToplevel(self)
        self._popout_win.title("📰 News Ticker")
        self._popout_win.geometry("1400x52+0+0")
        self._popout_win.resizable(True, False)
        self._popout_win.attributes("-topmost", True)
        self._popout_win.configure(
            fg_color=self.C["marquee_bg"])

        self._popout_win.columnconfigure(1, weight=1)

        ctk.CTkLabel(self._popout_win,
                      text=" 📰 ",
                      font=ctk.CTkFont("Arial", 11, "bold"),
                      fg_color=self.C["electric"],
                      text_color=self.C["white"],
                      corner_radius=4).grid(
                      row=0, column=0,
                      padx=(8,6), pady=8)

        self._popout_label = ctk.CTkLabel(
            self._popout_win,
            text="",
            font=ctk.CTkFont("Courier New", 18, "bold"),
            text_color=self.C["marquee_fg"],
            fg_color="transparent",
            anchor="w")
        self._popout_label.grid(
            row=0, column=1, sticky="ew", padx=(0,8))

        self._popout_win.protocol(
            "WM_DELETE_WINDOW",
            self._close_popout)

        self._scroll_popout()

    def _close_popout(self):
        if hasattr(self, "_popout_win") and \
           self._popout_win.winfo_exists():
            self._popout_win.destroy()

    def _scroll_popout(self):
        if not hasattr(self, "_popout_win") or \
           not self._popout_win.winfo_exists():
            return
        if not self.marquee_text:
            return
        try:
            win_width = self._popout_label.winfo_width()
            char_width = 7
            display_width = max(
                120, win_width // char_width)
            text   = self.marquee_text
            double = text + text
            snippet = double[
                self.marquee_pos:
                self.marquee_pos + display_width]
            self._popout_label.configure(text=snippet)
        except Exception:
            return
        self.after(120, self._scroll_popout)

    # ── Dark Mode ────────────────────────────────────────────
    def _toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self._apply_colors()

        self.configure(fg_color=self.bg)
        self.toolbar.configure(
            fg_color=self.C["dark_bg"]
            if self.dark_mode else self.C["steel"])
        self.btn_theme.configure(
            text="☀️" if self.dark_mode else "🌙")

        self.headlines_frame.configure(
            fg_color=self.panel_bg)
        self.saved_frame.configure(
            fg_color=self.panel_bg)
        self.headlines_scroll.configure(
            fg_color="transparent")
        self.saved_scroll.configure(
            fg_color="transparent")

        self._populate_headlines(self.articles)
        self._populate_saved()

        self.update_idletasks()
        self.update()

    # ── Article Card Save Button ─────────────────────────────
    def _make_article_card(self, parent, article,
                            index, is_saved=False):
        card = ctk.CTkFrame(parent,
                             fg_color=self.surface,
                             corner_radius=8)
        card.pack(fill="x", pady=(0,6), padx=4)
        card.columnconfigure(0, weight=1)

        title  = article.get("title", "No title") \
                 or "No title"
        source = article.get("source", {}) \
                         .get("name", "Unknown")
        date   = article.get("publishedAt", "")[:10]
        url    = article.get("url", "")

        title_lbl = ctk.CTkLabel(card,
                                   text=title,
                                   font=ctk.CTkFont(
                                       "Arial", 11, "bold"),
                                   text_color=self.text_color,
                                   anchor="w",
                                   wraplength=550,
                                   justify="left",
                                   cursor="hand2")
        title_lbl.grid(row=0, column=0, sticky="ew",
                        padx=12, pady=(10,2))

        if url:
            title_lbl.bind("<Button-1>",
                lambda e, u=url: webbrowser.open(u))
            title_lbl.bind("<Enter>",
                lambda e, l=title_lbl: l.configure(
                    text_color=self.C["electric_light"]))
            title_lbl.bind("<Leave>",
                lambda e, l=title_lbl: l.configure(
                    text_color=self.text_color))

        meta_frame = ctk.CTkFrame(card,
                                   fg_color="transparent")
        meta_frame.grid(row=1, column=0, sticky="ew",
                         padx=12, pady=(0,8))
        meta_frame.columnconfigure(0, weight=1)

        ctk.CTkLabel(meta_frame,
                      text=f"{source}  ·  {date}",
                      font=ctk.CTkFont("Arial", 9),
                      text_color=self.C["muted"],
                      anchor="w").grid(
                      row=0, column=0, sticky="w")

        if not is_saved:
            save_btn = ctk.CTkButton(
                meta_frame,
                text="+ Save",
                command=lambda a=article:
                    self._save_specific(a),
                fg_color=self.C["electric"],
                hover_color=self.C["electric_dark"],
                text_color=self.C["white"],
                font=ctk.CTkFont("Arial", 9),
                height=22, width=60,
                corner_radius=4)
            save_btn.grid(row=0, column=1,
                           sticky="e")

# ── Entry Point ──────────────────────────────────────────────
if __name__ == "__main__":
    app = NewsTrackerV11()
    app.mainloop()
