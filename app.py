import os
import tkinter as tk
from tkinter import ttk

from storage import BookStorage
from pages.book_list_page import BookListPage
from pages.book_edit_page import BookEditPage
from pages.book_sort_page import BookSortPage


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # =========================
        # App Title / Window
        # =========================
        self.title("Library Manager")
        self.geometry("1100x700")
        self.minsize(1000, 650)

        # =========================
        # Colors (IMPORTANT: BG + FG exist)
        # =========================
        self.BG = "#F4F4F4"
        self.FG = "#111111"          # ✅ this fixes your error (app.FG exists)

        # logo colour (blue text)
        self.LOGO_FG = "#0000FF"

        # optional aliases (so old/new pages both work)
        self.TEXT = self.FG

        self.PANEL_BG = "#FFFFFF"
        self.BORDER = "#D0D0D0"

        # Sidebar
        self.SIDEBAR_BG = "#FFFFFF"
        self.SIDEBAR_FG = self.FG
        self.SIDEBAR_HOVER_BG = "#E9E9E9"
        self.SIDEBAR_ACTIVE_BG = "#111111"
        self.SIDEBAR_ACTIVE_FG = "#FFFFFF"

        # Buttons (for tk.Button pages if you still use them)
        self.BTN_BG = "#111111"
        self.BTN_FG = "#FFFFFF"
        self.BTN_ACTIVE_BG = "#2A2A2A"
        self.BTN_ACTIVE_FG = "#FFFFFF"

        # For ttk buttons style
        self.BUTTON_BG = self.BTN_BG
        self.BUTTON_FG = self.BTN_FG
        self.BUTTON_HOVER_BG = self.BTN_ACTIVE_BG

        self.configure(bg=self.BG)

        # =========================
        # Storage
        # =========================
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, "data", "books.json")

        self.storage = BookStorage(data_path)
        self.books = self.storage.load_books()

        # =========================
        # ttk Theme (macOS)
        # =========================
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        self._configure_styles()

        # =========================
        # Layout
        # =========================
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = tk.Frame(
            self,
            bg=self.SIDEBAR_BG,
            highlightthickness=1,
            highlightbackground=self.BORDER
        )
        self.sidebar.grid(row=0, column=0, sticky="ns")

        self.container = tk.Frame(self, bg=self.BG)
        self.container.grid(row=0, column=1, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # =========================
        # Pages
        # =========================
        self.pages = {}
        self._build_pages()

        # =========================
        # Sidebar Nav
        # =========================
        self.active_page = None
        self._build_sidebar()

        # default
        self.show_page("book_list")

    # -------------------------
    # Styles
    # -------------------------
    def _configure_styles(self):
        # Treeview
        self.style.configure(
            "Treeview",
            font=("Arial", 12),
            rowheight=28,
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
            foreground=self.FG,
            bordercolor=self.BORDER,
            lightcolor=self.BORDER,
            darkcolor=self.BORDER
        )
        self.style.configure(
            "Treeview.Heading",
            font=("Arial", 12, "bold"),
            background="#111111",
            foreground="#FFFFFF",
            relief="flat"
        )
        self.style.map("Treeview.Heading", background=[("active", "#222222")])

        # App buttons (ttk)
        self.style.configure(
            "App.TButton",
            font=("Arial", 12, "bold"),
            padding=(12, 10),
            background=self.BTN_BG,
            foreground=self.BTN_FG,
            borderwidth=1,
            focusthickness=0
        )
        self.style.map(
            "App.TButton",
            background=[
                ("active", self.BTN_ACTIVE_BG),
                ("pressed", "#000000"),
                ("disabled", "#BDBDBD"),
            ],
            foreground=[
                ("disabled", "#666666"),
            ]
        )

        self.style.configure("TEntry", padding=6)
        self.style.configure("TCombobox", padding=6)

    # -------------------------
    # Pages
    # -------------------------
    def _build_pages(self):
        self.pages["book_list"] = BookListPage(self.container, self)
        self.pages["edit_books"] = BookEditPage(self.container, self)
        self.pages["sort_books"] = BookSortPage(self.container, self)

        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

    # -------------------------
    # Sidebar
    # -------------------------
    def _build_sidebar(self):
        # Static book drawing on canvas (no animation)
        class BookCanvas(tk.Canvas):
            def __init__(self, parent, **kw):
                super().__init__(parent, width=80, height=80, bg=parent['bg'], highlightthickness=0, **kw)
                self._draw_book()

            def _draw_book(self):
                # simple closed book with spine and minor shading
                # outer cover
                self.create_rectangle(15, 20, 65, 60, fill='white', outline='black')
                # spine shading
                self.create_polygon(15,20, 13,22, 13,58, 15,60, fill='#ccc', outline='#ccc')
                # cover texture lines
                for x in range(20, 60, 8):
                    self.create_line(x, 24, x, 56, fill='#888')
                # a small book icon or text in centre
                self.create_text(40, 40, text='📚', font=('Arial', 24))

        book_widget = BookCanvas(self.sidebar)
        book_widget.pack(padx=18, pady=20, fill='x')

        self.nav_labels = {}

        items = [
            ("Book List", "book_list"),
            ("Edit Book List", "edit_books"),
            ("Sort Book List", "sort_books"),
        ]

        for text, key in items:
            lbl = tk.Label(
                self.sidebar,
                text=text,
                bg=self.SIDEBAR_BG,
                fg=self.SIDEBAR_FG,
                font=("Arial", 13),
                padx=18,
                pady=12,
                anchor="w",
                cursor="hand2"
            )
            lbl.pack(fill="x")
            lbl.bind("<Enter>", lambda e, k=key: self._nav_hover(k, True))
            lbl.bind("<Leave>", lambda e, k=key: self._nav_hover(k, False))
            lbl.bind("<Button-1>", lambda e, k=key: self.show_page(k))
            self.nav_labels[key] = lbl

        # Spacer
        tk.Frame(self.sidebar, bg=self.SIDEBAR_BG, height=20).pack(fill="x", expand=True)

        exit_lbl = tk.Label(
            self.sidebar,
            text="Exit",
            bg=self.SIDEBAR_BG,
            fg=self.SIDEBAR_FG,
            font=("Arial", 13),
            padx=18,
            pady=12,
            anchor="w",
            cursor="hand2"
        )
        exit_lbl.pack(fill="x")
        exit_lbl.bind("<Enter>", lambda e: exit_lbl.config(bg=self.SIDEBAR_HOVER_BG))
        exit_lbl.bind("<Leave>", lambda e: exit_lbl.config(bg=self.SIDEBAR_BG))
        exit_lbl.bind("<Button-1>", lambda e: self.destroy())

    def _nav_hover(self, key: str, enter: bool):
        if key == self.active_page:
            return
        lbl = self.nav_labels.get(key)
        if not lbl:
            return
        lbl.config(bg=self.SIDEBAR_HOVER_BG if enter else self.SIDEBAR_BG)

    def _set_active_nav(self, key: str):
        self.active_page = key
        for k, lbl in self.nav_labels.items():
            if k == key:
                lbl.config(bg=self.SIDEBAR_ACTIVE_BG, fg=self.SIDEBAR_ACTIVE_FG)
            else:
                lbl.config(bg=self.SIDEBAR_BG, fg=self.SIDEBAR_FG)

    # -------------------------
    # Navigation
    # -------------------------
    def show_page(self, key: str):
        page = self.pages.get(key)
        if not page:
            return

        self._set_active_nav(key)
        page.tkraise()

        # Always refresh when showing a page
        if hasattr(page, "refresh") and callable(getattr(page, "refresh")):
            page.refresh()

    # -------------------------
    # Data Helpers
    # -------------------------
    def reload_books(self):
        self.books = self.storage.load_books()

    def save_books(self):
        self.storage.save_books(self.books)