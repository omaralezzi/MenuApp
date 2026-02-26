
# minimal pdf writer without external dependencies

def _pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def create_summary_pdf(output_path: str = "AppSummary.pdf"):
    # page size 612x792 points (letter)
    lines = []
    def add_line(text: str, indent: int = 0):
        lines.append((indent, text))

    add_line("Library Manager - Application Summary")
    add_line("")
    add_line("Overview:")
    add_line("A simple desktop application built using Tkinter for managing a personal library of books.", 20)
    add_line("Users can view, add, edit, sort, import, and export book records stored in a JSON file.", 20)
    add_line("")
    add_line("Core Components:")
    add_line("• app.py: Main application window, styling, and navigation logic.", 20)
    add_line("• models.py: Book dataclass and serialization helpers.", 20)
    add_line("• storage.py: Handles loading/saving JSON, CSV import, backups, and defaults.", 20)
    add_line("• pages/*: GUI pages for listing, editing, and sorting books using Tkinter widgets.", 20)
    add_line("")
    add_line("Data Storage:")
    add_line("Books are persisted in 'data/books.json'. Storage class normalizes and backs up data.", 20)
    add_line("Supports CSV import with safe backup to temp or user-specified location.", 20)
    add_line("")
    add_line("Features:")
    add_line("• Book List page shows all records in a Treeview with search capabilities.", 20)
    add_line("• Edit Books page allows creating, updating, deleting, and restoring default samples.", 20)
    add_line("• Sort Books page can re-order the list and save the new sequence.", 20)
    add_line("• Sidebar navigation for switching pages, with simple book icon graphic.", 20)
    add_line("• Theming and styling tailored for macOS with ttk and custom colors.", 20)
    add_line("")
    add_line("Setup & Run:")
    add_line("Execute 'python app.py' from workspace root. Requires Python 3.x and Tkinter.", 20)
    add_line("")
    add_line("Repository Structure:")
    add_line("- app.py", 20)
    add_line("- main.py (proxy to app)", 20)
    add_line("- models.py, storage.py", 20)
    add_line("- pages/book_list_page.py, book_edit_page.py, book_sort_page.py", 20)
    add_line("- data/books.json (initially may be empty)", 20)
    add_line("")
    add_line("This summary fits on a single page using standard letter size.")

    # build PDF
    width = 612
    height = 792
    font_size = 12
    y_start = height - 72
    y = y_start
    line_height = 14

    content_stream = []
    content_stream.append("BT")
    content_stream.append(f"/F1 {font_size} Tf")
    for indent, text in lines:
        if y < 72:
            break
        # set absolute text matrix: [1 0 0 1 x y] Tm
        x = 72 + indent
        content_stream.append(f"1 0 0 1 {x} {int(y)} Tm")
        escaped = _pdf_escape(text)
        content_stream.append(f"({escaped}) Tj")
        y -= line_height
    content_stream.append("ET")

    stream_data = "\n".join(content_stream)
    stream_len = len(stream_data.encode("utf-8"))

    # objects
    objs = []
    # 1 catalog
    objs.append("1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj")
    # 2 pages
    objs.append("2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj")
    # 3 page
    objs.append(
        "3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        f"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj"
    )
    # 4 contents
    objs.append(f"4 0 obj << /Length {stream_len} >> stream\n{stream_data}\nendstream endobj")
    # 5 font
    objs.append("5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj")

    # write file
    with open(output_path, "wb") as f:
        f.write(b"%PDF-1.1\n")
        xref_positions = []
        for obj in objs:
            xref_positions.append(f.tell())
            f.write(obj.encode("utf-8"))
            f.write(b"\n")
        xref_start = f.tell()
        # write xref
        f.write(b"xref\n")
        f.write(f"0 {len(objs)+1}\n".encode("utf-8"))
        f.write(b"0000000000 65535 f \n")
        for pos in xref_positions:
            f.write(f"{pos:010d} 00000 n \n".encode("utf-8"))
        # trailer
        f.write(b"trailer << /Size ")
        f.write(str(len(objs)+1).encode("utf-8"))
        f.write(b" /Root 1 0 R >>\nstartxref\n")
        f.write(str(xref_start).encode("utf-8"))
        f.write(b"\n%%EOF")


if __name__ == "__main__":
    create_summary_pdf()
    print("PDF generated: AppSummary.pdf")
