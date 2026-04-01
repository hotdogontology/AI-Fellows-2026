#!/usr/bin/env python3
"""Desktop GUI for transcript bookmark generation (no terminal required)."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from pypdf import PdfReader

from bookmark_transcripts import (
    DEFAULT_NAME_PATTERNS,
    compile_pattern,
    extract_student_bookmarks,
    write_bookmarked_pdf,
)


class TranscriptBookmarkerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Transcript Bookmarker")
        self.root.geometry("760x620")

        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.required_page_var = tk.StringVar(value="Transcript|Academic Record")

        self._build_ui()

    def _build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=14)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Input PDF").grid(row=0, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.input_var, width=72).grid(row=1, column=0, sticky="ew", padx=(0, 8))
        ttk.Button(frame, text="Browse…", command=self.pick_input).grid(row=1, column=1, sticky="e")

        ttk.Label(frame, text="Output PDF").grid(row=2, column=0, sticky="w", pady=(10, 0))
        ttk.Entry(frame, textvariable=self.output_var, width=72).grid(row=3, column=0, sticky="ew", padx=(0, 8))
        ttk.Button(frame, text="Browse…", command=self.pick_output).grid(row=3, column=1, sticky="e")

        ttk.Label(frame, text="Required page regex (optional, recommended)").grid(row=4, column=0, sticky="w", pady=(10, 0))
        ttk.Entry(frame, textvariable=self.required_page_var, width=72).grid(row=5, column=0, columnspan=2, sticky="ew")

        ttk.Label(frame, text="Name regex patterns (one per line; blank = safe defaults)").grid(
            row=6, column=0, sticky="w", pady=(10, 0)
        )
        self.pattern_text = tk.Text(frame, height=8, wrap="word")
        self.pattern_text.grid(row=7, column=0, columnspan=2, sticky="nsew")
        self.pattern_text.insert("1.0", "\n".join(DEFAULT_NAME_PATTERNS))

        ttk.Label(frame, text="Detected students preview").grid(row=8, column=0, sticky="w", pady=(10, 0))
        self.preview_text = tk.Text(frame, height=12, wrap="word")
        self.preview_text.grid(row=9, column=0, columnspan=2, sticky="nsew")

        button_row = ttk.Frame(frame)
        button_row.grid(row=10, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(button_row, text="Preview Names", command=self.preview).pack(side="left", padx=6)
        ttk.Button(button_row, text="Create Bookmarked PDF", command=self.generate).pack(side="left", padx=6)

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(7, weight=1)
        frame.rowconfigure(9, weight=1)

    def pick_input(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if path:
            self.input_var.set(path)
            if not self.output_var.get():
                output = str(Path(path).with_name(Path(path).stem + "_bookmarked.pdf"))
                self.output_var.set(output)

    def pick_output(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if path:
            self.output_var.set(path)

    def _collect_patterns(self) -> list[str]:
        raw = self.pattern_text.get("1.0", "end").strip()
        if not raw:
            return list(DEFAULT_NAME_PATTERNS)
        return [line.strip() for line in raw.splitlines() if line.strip()]

    def _run_detection(self):
        input_path = Path(self.input_var.get().strip())
        if not input_path.exists():
            raise ValueError("Please choose a valid input PDF.")

        patterns = [compile_pattern(p, "pattern") for p in self._collect_patterns()]
        required_pattern_raw = self.required_page_var.get().strip()
        required_pattern = compile_pattern(required_pattern_raw, "required pattern") if required_pattern_raw else None

        reader = PdfReader(str(input_path))
        bookmarks = extract_student_bookmarks(reader, patterns, required_pattern)
        return reader, bookmarks

    def preview(self) -> None:
        try:
            _, bookmarks = self._run_detection()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Preview failed", str(exc))
            return

        self.preview_text.delete("1.0", "end")
        if not bookmarks:
            self.preview_text.insert("end", "No student names found. Try adjusting patterns.\n")
            return

        self.preview_text.insert("end", f"Found {len(bookmarks)} students:\n\n")
        for item in bookmarks:
            self.preview_text.insert("end", f"- {item.name} (page {item.page_index + 1})\n")

    def generate(self) -> None:
        output_path = Path(self.output_var.get().strip())
        if not output_path:
            messagebox.showerror("Missing output", "Please choose an output PDF path.")
            return

        try:
            reader, bookmarks = self._run_detection()
            if not bookmarks:
                messagebox.showwarning("No names found", "No students found. Run Preview and adjust patterns.")
                return
            write_bookmarked_pdf(reader, output_path, bookmarks)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Generation failed", str(exc))
            return

        self.preview()
        messagebox.showinfo("Success", f"Created bookmarked PDF:\n{output_path}")


def main() -> None:
    root = tk.Tk()
    TranscriptBookmarkerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
