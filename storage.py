# storage.py
from __future__ import annotations

import csv
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional


class BookStorage:
    """
    Handles reading/writing books from/to data/books.json
    Also supports importing from CSV with safe backup behavior
    and restoring 4 default SAMPLE books only when user clicks.
    """

    def __init__(self, data_path: str | Path):
        self.data_path = Path(data_path)

    # ---------- core json I/O ----------
    def load_books(self) -> List[Dict[str, Any]]:
        if not self.data_path.exists():
            # if file missing -> create empty structure (NO auto defaults)
            self.save_books([])
            return []

        try:
            with self.data_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            # broken json -> backup to temp then reset empty
            self._backup_to_temp(reason="broken_json")
            self.save_books([])
            return []

        books = data.get("books", [])
        if not isinstance(books, list):
            return []

        # normalize
        fixed = []
        for b in books:
            fixed.append({
                "no": str(b.get("no", "")).strip(),
                "title": str(b.get("title", "")).strip(),
                "genre": str(b.get("genre", "")).strip(),
                "author": str(b.get("author", "")).strip(),
                "price": str(b.get("price", "")).strip(),
                "year": str(b.get("year", "")).strip(),
            })
        return fixed

    def save_books(self, books: List[Dict[str, Any]]) -> None:
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"books": books}
        with self.data_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    # ---------- backups ----------
    def backup_to_path(self, backup_path: str | Path) -> str:
        """Copy current books.json to a user-selected path."""
        backup_path = Path(backup_path)
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        if self.data_path.exists():
            shutil.copy2(self.data_path, backup_path)
        else:
            self.save_books([])
            shutil.copy2(self.data_path, backup_path)

        return str(backup_path)

    def _backup_to_temp(self, reason: str = "import_csv") -> str:
        """Copy current books.json to a temp file and return its path."""
        tmp_dir = Path(tempfile.gettempdir())
        tmp_name = f"books_backup_{reason}_{os.getpid()}.json"
        tmp_path = tmp_dir / tmp_name

        if self.data_path.exists():
            shutil.copy2(self.data_path, tmp_path)
        else:
            self.save_books([])
            shutil.copy2(self.data_path, tmp_path)

        return str(tmp_path)

    # ---------- import from csv ----------
    def import_from_csv(self, csv_path: str | Path) -> List[Dict[str, Any]]:
        """
        Reads CSV and returns list of book dicts.
        Required headers: no,title,genre,author,price,year
        """
        csv_path = Path(csv_path)
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                raise ValueError("CSV has no header row.")

            fieldnames = [h.strip().lower() for h in reader.fieldnames]
            required = ["no", "title", "genre", "author", "price", "year"]
            for r in required:
                if r not in fieldnames:
                    raise ValueError(f"Missing required column '{r}'. Found: {fieldnames}")

            header_map = {h.strip().lower(): h for h in reader.fieldnames}

            books: List[Dict[str, Any]] = []
            for row in reader:
                book = {
                    "no": str(row.get(header_map["no"], "")).strip(),
                    "title": str(row.get(header_map["title"], "")).strip(),
                    "genre": str(row.get(header_map["genre"], "")).strip(),
                    "author": str(row.get(header_map["author"], "")).strip(),
                    "price": str(row.get(header_map["price"], "")).strip(),
                    "year": str(row.get(header_map["year"], "")).strip(),
                }

                if not any(book.values()):
                    continue

                if not book["no"] or not book["title"]:
                    raise ValueError("Each row must have at least 'no' and 'title'.")

                books.append(book)

        return books

    def import_csv_with_backup(
        self,
        csv_path: str | Path,
        backup_path: Optional[str | Path] = None,
    ) -> str:
        """
        Import CSV and overwrite books.json.
        If backup_path provided -> backup there.
        Else -> backup to temp.
        Returns backup file path used.
        """
        if backup_path:
            backup_used = self.backup_to_path(backup_path)
        else:
            backup_used = self._backup_to_temp(reason="import_csv")

        books = self.import_from_csv(csv_path)
        self.save_books(books)

        return backup_used

    # ---------- defaults (ONLY by button click) ----------
    def default_books(self) -> List[Dict[str, Any]]:
        # 4 obvious DEFAULT/SAMPLE placeholders
        return [
            {"no": "D01", "title": "DEFAULT_SAMPLE_TITLE_1", "genre": "SAMPLE_GENRE", "author": "DEFAULT_AUTHOR_A", "price": "0.00", "year": "0000"},
            {"no": "D02", "title": "DEFAULT_SAMPLE_TITLE_2", "genre": "SAMPLE_GENRE", "author": "DEFAULT_AUTHOR_B", "price": "0.00", "year": "0000"},
            {"no": "D03", "title": "DEFAULT_SAMPLE_TITLE_3", "genre": "SAMPLE_GENRE", "author": "DEFAULT_AUTHOR_C", "price": "0.00", "year": "0000"},
            {"no": "D04", "title": "DEFAULT_SAMPLE_TITLE_4", "genre": "SAMPLE_GENRE", "author": "DEFAULT_AUTHOR_D", "price": "0.00", "year": "0000"},
        ]

    def restore_defaults(self) -> None:
        self.save_books(self.default_books())