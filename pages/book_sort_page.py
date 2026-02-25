import tkinter as tk
from tkinter import ttk, messagebox


class BookSortPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=app.BG)
        self.app = app

        self.all_cols = ("no", "title", "genre", "author", "price", "year")
        self.col_visible = {c: tk.BooleanVar(value=True) for c in self.all_cols}

        self.sort_col_var = tk.StringVar(value="title")
        self.order_var = tk.StringVar(value="asc")
        self.search_var = tk.StringVar(value="")

        self._build_ui()

    def _build_ui(self):
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header
        header = tk.Label(
            self,
            text="Sort Book List",
            bg=self.app.BG,
            fg=self.app.FG,
            font=("Arial", 22, "bold"),
            padx=18,
            pady=18,
            anchor="w",
        )
        header.grid(row=0, column=0, sticky="ew")

        # Controls panel
        panel = tk.Frame(self, bg=self.app.PANEL_BG, highlightthickness=1, highlightbackground=self.app.BORDER)
        panel.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 10))
        panel.grid_columnconfigure(1, weight=1)

        # Sort controls row
        tk.Label(panel, text="Column:", bg=self.app.PANEL_BG, fg=self.app.FG, font=("Arial", 12, "bold")).grid(
            row=0, column=0, padx=12, pady=12, sticky="w"
        )

        sort_combo = ttk.Combobox(
            panel,
            textvariable=self.sort_col_var,
            state="readonly",
            values=list(self.all_cols),
            width=16,
        )
        sort_combo.grid(row=0, column=1, padx=12, pady=12, sticky="w")

        tk.Label(panel, text="Order:", bg=self.app.PANEL_BG, fg=self.app.FG, font=("Arial", 12, "bold")).grid(
            row=0, column=2, padx=(24, 12), pady=12, sticky="w"
        )

        rb1 = tk.Radiobutton(panel, text="Ascending", variable=self.order_var, value="asc",
                             bg=self.app.PANEL_BG, fg=self.app.FG, selectcolor=self.app.PANEL_BG)
        rb2 = tk.Radiobutton(panel, text="Descending", variable=self.order_var, value="desc",
                             bg=self.app.PANEL_BG, fg=self.app.FG, selectcolor=self.app.PANEL_BG)
        rb1.grid(row=0, column=3, sticky="w", padx=(0, 12))
        rb2.grid(row=0, column=4, sticky="w", padx=(0, 12))

        # Search row (NEW)
        tk.Label(panel, text="Search:", bg=self.app.PANEL_BG, fg=self.app.FG, font=("Arial", 12, "bold")).grid(
            row=1, column=0, padx=12, pady=(0, 12), sticky="w"
        )
        search_entry = ttk.Entry(panel, textvariable=self.search_var)
        search_entry.grid(row=1, column=1, columnspan=4, padx=12, pady=(0, 12), sticky="ew")
        search_entry.bind("<KeyRelease>", lambda e: self._apply_filter_to_table())

        # Columns selection block
        tk.Label(panel, text="Show Columns:", bg=self.app.PANEL_BG, fg=self.app.FG, font=("Arial", 12, "bold")).grid(
            row=2, column=0, padx=12, pady=(0, 12), sticky="nw"
        )

        checks = tk.Frame(panel, bg=self.app.PANEL_BG)
        checks.grid(row=2, column=1, columnspan=4, sticky="w", padx=12, pady=(0, 12))

        positions = [
            ("no", 0, 0),
            ("title", 0, 1),
            ("genre", 0, 2),
            ("author", 1, 0),
            ("price", 1, 1),
            ("year", 1, 2),
        ]
        for col, r, c in positions:
            cb = tk.Checkbutton(
                checks,
                text=col.upper(),
                variable=self.col_visible[col],
                bg=self.app.PANEL_BG,
                fg=self.app.FG,
                selectcolor=self.app.PANEL_BG,
                activebackground=self.app.PANEL_BG,
                activeforeground=self.app.FG
            )
            cb.grid(row=r, column=c, sticky="w", padx=(0, 18), pady=3)

        # Select all / deselect all (NEW)
        quick = tk.Frame(panel, bg=self.app.PANEL_BG)
        quick.grid(row=3, column=0, columnspan=5, sticky="ew", padx=12, pady=(0, 12))
        quick.grid_columnconfigure(0, weight=1)
        quick.grid_columnconfigure(1, weight=1)
        quick.grid_columnconfigure(2, weight=1)
        quick.grid_columnconfigure(3, weight=1)
        quick.grid_columnconfigure(4, weight=1)

        ttk.Button(quick, text="Select All", style="App.TButton", command=self.select_all_columns).grid(
            row=0, column=0, sticky="ew", padx=(0, 6)
        )
        ttk.Button(quick, text="Deselect All", style="App.TButton", command=self.deselect_all_columns).grid(
            row=0, column=1, sticky="ew", padx=6
        )
        ttk.Button(quick, text="Apply Columns", style="App.TButton", command=self.apply_columns).grid(
            row=0, column=2, sticky="ew", padx=6
        )
        ttk.Button(quick, text="Sort", style="App.TButton", command=self.sort_books).grid(
            row=0, column=3, sticky="ew", padx=6
        )
        ttk.Button(quick, text="Reset (Reload)", style="App.TButton", command=self.reset).grid(
            row=0, column=4, sticky="ew", padx=(6, 0)
        )

        # Table area
        table_wrap = tk.Frame(self, bg=self.app.PANEL_BG, highlightthickness=1, highlightbackground=self.app.BORDER)
        table_wrap.grid(row=3, column=0, sticky="nsew", padx=18, pady=(0, 18))
        table_wrap.grid_rowconfigure(0, weight=1)
        table_wrap.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(table_wrap, columns=self.all_cols, show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

        headings = {
            "no": "No.",
            "title": "Title",
            "genre": "Genre",
            "author": "Author",
            "price": "Price",
            "year": "Year",
        }
        widths = {"no": 70, "title": 320, "genre": 140, "author": 220, "price": 90, "year": 90}
        for c in self.all_cols:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=widths[c], anchor="w")

        scroll = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.grid(row=0, column=1, sticky="ns", pady=12)

    # called automatically by app.show_page()
    def refresh(self):
        self.app.reload_books()
        self._fill_table(self.app.books)
        self.apply_columns(show_message=False)
        self._apply_filter_to_table()

    def _fill_table(self, books):
        self.tree.delete(*self.tree.get_children())
        for b in books:
            self.tree.insert(
                "",
                "end",
                values=(b.get("no", ""), b.get("title", ""), b.get("genre", ""), b.get("author", ""),
                        b.get("price", ""), b.get("year", ""))
            )

    # ---------- NEW: search filter ----------
    def _apply_filter_to_table(self):
        query = self.search_var.get().strip().lower()

        # always start from current saved list order
        books = self.app.storage.load_books()

        if query:
            filtered = []
            for b in books:
                s = f'{b.get("no","")} {b.get("title","")} {b.get("genre","")} {b.get("author","")} {b.get("price","")} {b.get("year","")}'.lower()
                if query in s:
                    filtered.append(b)
            books = filtered

        self._fill_table(books)
        self.apply_columns(show_message=False)

    # ---------- NEW: select/deselect all ----------
    def select_all_columns(self):
        for c in self.all_cols:
            self.col_visible[c].set(True)
        self.apply_columns()

    def deselect_all_columns(self):
        for c in self.all_cols:
            self.col_visible[c].set(False)
        # keep at least one column visible to avoid empty table
        self.col_visible["title"].set(True)
        self.apply_columns()

    # ---------- column visibility ----------
    def apply_columns(self, show_message=True):
        visible_cols = [c for c in self.all_cols if self.col_visible[c].get()]

        if not visible_cols:
            # should never happen because we force Title on deselect, but keep safe
            self.col_visible["title"].set(True)
            visible_cols = ["title"]

        self.tree["displaycolumns"] = visible_cols

        if show_message:
            messagebox.showinfo("Columns Updated", f"Visible columns:\n{', '.join([c.upper() for c in visible_cols])}")

    # ---------- sorting ----------
    def sort_books(self):
        self.app.reload_books()

        col = self.sort_col_var.get()
        reverse = (self.order_var.get() == "desc")

        def key_func(x):
            v = x.get(col, "")
            if col in ("no", "year"):
                try:
                    return int(v)
                except Exception:
                    return 0
            if col == "price":
                try:
                    return float(v)
                except Exception:
                    return 0.0
            return str(v).lower()

        self.app.books.sort(key=key_func, reverse=reverse)
        self.app.save_books()

        # refresh view respecting search + visible columns
        self._apply_filter_to_table()

    def reset(self):
        self.search_var.set("")
        self.refresh()