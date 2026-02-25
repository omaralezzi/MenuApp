import tkinter as tk
from tkinter import ttk


class BookListPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=app.BG)
        self.app = app

        self._build_ui()

    def _build_ui(self):
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        header = tk.Label(
            self,
            text="Book List",
            bg=self.app.BG,
            fg=self.app.TEXT,
            font=("Arial", 22, "bold"),
            padx=18,
            pady=18,
            anchor="w",
        )
        header.grid(row=0, column=0, sticky="ew")

        # Search
        search_bar = tk.Frame(self, bg=self.app.BG)
        search_bar.grid(row=1, column=0, sticky="ew", padx=18)
        search_bar.grid_columnconfigure(1, weight=1)

        tk.Label(search_bar, text="Search:", bg=self.app.BG, fg=self.app.TEXT, font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_bar, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=10)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh())

        # Table
        wrap = tk.Frame(self, bg=self.app.PANEL_BG, highlightthickness=1, highlightbackground=self.app.BORDER)
        wrap.grid(row=2, column=0, sticky="nsew", padx=18, pady=18)
        wrap.grid_rowconfigure(0, weight=1)
        wrap.grid_columnconfigure(0, weight=1)

        cols = ("no", "title", "genre", "author", "price", "year")
        self.tree = ttk.Treeview(wrap, columns=cols, show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        headings = {
            "no": "No.",
            "title": "Title",
            "genre": "Genre",
            "author": "Author",
            "price": "Price",
            "year": "Year",
        }
        widths = {"no": 70, "title": 320, "genre": 140, "author": 220, "price": 90, "year": 90}
        for c in cols:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=widths[c], anchor="w")

        scroll = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.grid(row=0, column=1, sticky="ns", pady=10)

    def refresh(self):
        # Always reload from JSON to show latest data
        self.app.reload_books()

        query = self.search_var.get().strip().lower()
        self.tree.delete(*self.tree.get_children())

        for b in self.app.books:
            s = f'{b["no"]} {b["title"]} {b["genre"]} {b["author"]} {b["price"]} {b["year"]}'.lower()
            if query and query not in s:
                continue
            self.tree.insert("", "end", values=(b["no"], b["title"], b["genre"], b["author"], b["price"], b["year"]))