import csv
import os
import shutil
import tempfile
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


class BookEditPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=app.BG)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        header = tk.Label(
            self,
            text="Edit Book List",
            bg=self.app.BG,
            fg=self.app.FG,
            font=("Arial", 22, "bold"),
            padx=18,
            pady=18,
            anchor="w",
        )
        header.grid(row=0, column=0, columnspan=2, sticky="ew")

        # ---- Left form panel ----
        form_wrap = tk.Frame(self, bg=self.app.PANEL_BG, highlightthickness=1, highlightbackground=self.app.BORDER)
        form_wrap.grid(row=1, column=0, sticky="ns", padx=(18, 10), pady=(0, 18))

        form_title = tk.Label(
            form_wrap,
            text="New / Update",
            bg=self.app.PANEL_BG,
            fg=self.app.FG,
            font=("Arial", 14, "bold"),
            padx=14,
            pady=12,
            anchor="w",
        )
        form_title.pack(fill="x")

        self.vars = {
            "no": tk.StringVar(),
            "title": tk.StringVar(),
            "genre": tk.StringVar(),
            "author": tk.StringVar(),
            "price": tk.StringVar(),
            "year": tk.StringVar(),
        }

        def row(label, key):
            r = tk.Frame(form_wrap, bg=self.app.PANEL_BG)
            r.pack(fill="x", padx=14, pady=6)
            tk.Label(r, text=label, bg=self.app.PANEL_BG, fg=self.app.FG, width=10, anchor="w").pack(side="left")
            ttk.Entry(r, textvariable=self.vars[key], width=24).pack(side="left")

        row("No.", "no")
        row("Title", "title")
        row("Genre", "genre")
        row("Author", "author")
        row("Price", "price")
        row("Year", "year")

        btn_frame = tk.Frame(form_wrap, bg=self.app.PANEL_BG)
        btn_frame.pack(fill="x", padx=14, pady=(12, 14))

        ttk.Button(btn_frame, text="Add / Update", style="App.TButton", command=self.add_update).pack(fill="x", pady=6)
        ttk.Button(btn_frame, text="Delete Selected", style="App.TButton", command=self.delete_selected).pack(fill="x", pady=6)

        # CSV IMPORT (extra option)
        ttk.Button(btn_frame, text="Import from CSV", style="App.TButton", command=self.import_from_csv).pack(fill="x", pady=(16, 6))

        ttk.Button(btn_frame, text="Restore Default Books", style="App.TButton", command=self.restore_defaults).pack(fill="x", pady=(16, 6))
        ttk.Button(btn_frame, text="Save", style="App.TButton", command=self.save).pack(fill="x", pady=6)
        ttk.Button(btn_frame, text="Reload", style="App.TButton", command=self.reload).pack(fill="x", pady=6)
        ttk.Button(btn_frame, text="Export CSV", style="App.TButton", command=self.export_csv).pack(fill="x", pady=6)

        # ---- Right table panel ----
        table_wrap = tk.Frame(self, bg=self.app.PANEL_BG, highlightthickness=1, highlightbackground=self.app.BORDER)
        table_wrap.grid(row=1, column=1, sticky="nsew", padx=(10, 18), pady=(0, 18))
        table_wrap.grid_rowconfigure(1, weight=1)
        table_wrap.grid_columnconfigure(0, weight=1)

        search_bar = tk.Frame(table_wrap, bg=self.app.PANEL_BG)
        search_bar.grid(row=0, column=0, sticky="ew", padx=12, pady=12)
        search_bar.grid_columnconfigure(1, weight=1)

        tk.Label(search_bar, text="Search:", bg=self.app.PANEL_BG, fg=self.app.FG, font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_bar, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky="ew", padx=10)
        search_entry.bind("<KeyRelease>", lambda e: self.refresh())

        cols = ("no", "title", "genre", "author", "price", "year")
        self.tree = ttk.Treeview(table_wrap, columns=cols, show="headings")
        self.tree.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))

        headings = {"no": "No.", "title": "Title", "genre": "Genre", "author": "Author", "price": "Price", "year": "Year"}
        widths = {"no": 70, "title": 260, "genre": 140, "author": 220, "price": 90, "year": 90}
        for c in cols:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=widths[c], anchor="w")

        scroll = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.grid(row=1, column=1, sticky="ns", pady=(0, 12))

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    # ---------------- Core actions ----------------
    def refresh(self):
        self.app.reload_books()

        query = self.search_var.get().strip().lower()
        self.tree.delete(*self.tree.get_children())

        for b in self.app.books:
            s = f'{b.get("no","")} {b.get("title","")} {b.get("genre","")} {b.get("author","")} {b.get("price","")} {b.get("year","")}'.lower()
            if query and query not in s:
                continue
            self.tree.insert("", "end", values=(b.get("no",""), b.get("title",""), b.get("genre",""), b.get("author",""), b.get("price",""), b.get("year","")))

    def on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        no, title, genre, author, price, year = self.tree.item(sel[0], "values")
        self.vars["no"].set(no)
        self.vars["title"].set(title)
        self.vars["genre"].set(genre)
        self.vars["author"].set(author)
        self.vars["price"].set(price)
        self.vars["year"].set(year)

    def add_update(self):
        book = {k: self.vars[k].get().strip() for k in self.vars.keys()}
        if not book["no"] or not book["title"]:
            messagebox.showwarning("Missing Data", "Please enter at least: No. and Title.")
            return

        self.app.reload_books()

        updated = False
        for i, b in enumerate(self.app.books):
            if b.get("no", "") == book["no"]:
                self.app.books[i] = book
                updated = True
                break

        if not updated:
            self.app.books.append(book)

        self.app.save_books()
        self.refresh()

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Delete", "Please select a book first.")
            return

        no = self.tree.item(sel[0], "values")[0]

        self.app.reload_books()
        self.app.books = [b for b in self.app.books if b.get("no", "") != no]
        self.app.save_books()
        self.refresh()

        for v in self.vars.values():
            v.set("")

    def restore_defaults(self):
        ok = messagebox.askyesno(
            "Restore Defaults",
            "This will REPLACE all current books with 4 DEFAULT sample entries.\n\nContinue?"
        )
        if not ok:
            return

        self.app.storage.restore_defaults()
        self.refresh()
        messagebox.showinfo("Done", "Default books restored successfully.")

    def save(self):
        self.app.save_books()
        messagebox.showinfo("Saved", "Saved to data/books.json")

    def reload(self):
        self.refresh()
        messagebox.showinfo("Reloaded", "Reloaded from data/books.json")

    def export_csv(self):
        self.app.reload_books()
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title="Export CSV"
        )
        if not path:
            return

        headers = ["no", "title", "genre", "author", "price", "year"]
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=headers)
                w.writeheader()
                for b in self.app.books:
                    w.writerow({h: b.get(h, "") for h in headers})
        except Exception as e:
            messagebox.showerror("Export Error", str(e))
            return

        messagebox.showinfo("Exported", f"CSV exported:\n{path}")

    # ---------------- CSV Import with Backup ----------------
    def import_from_csv(self):
        csv_file = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not csv_file:
            return

        answer = messagebox.askyesnocancel(
            "Backup current data?",
            "Before importing, do you want to save a backup of the current books.json?\n\n"
            "Yes = choose location\n"
            "No = auto-save to TEMP file\n"
            "Cancel = abort import"
        )
        if answer is None:
            return

        backup_path = None
        if answer is True:
            backup_path = filedialog.asksaveasfilename(
                title="Save backup as...",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if not backup_path:
                backup_path = None  # fallback to temp

        try:
            backup_used = self.app.storage.import_csv_with_backup(csv_file, backup_path=backup_path)
        except Exception as e:
            messagebox.showerror("Import Error", f"Could not import CSV:\n\n{e}")
            return

        if backup_path:
            messagebox.showinfo("Import Completed", f"CSV imported successfully.\n\nBackup saved to:\n{backup_used}")
        else:
            messagebox.showinfo("Import Completed", f"CSV imported successfully.\n\nBackup saved in TEMP:\n{backup_used}")

        self.refresh()
        if hasattr(self.app, "show_page"):
            self.app.show_page("book_list")