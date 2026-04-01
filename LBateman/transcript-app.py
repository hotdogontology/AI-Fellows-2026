#!/usr/bin/env python3
"""Desktop GUI for transcript bookmark generation."""

from __future__ import annotations

import re
import subprocess
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:  # pragma: no cover - depends on local environment
    PdfReader = None
    PdfWriter = None

PDFTOTEXT_PATH = Path(r"C:\texlive\2025\bin\windows\pdftotext.exe")
TRANSCRIPT_PAGE_PATTERN = r"Student Name|Transcript|Academic Record|GPA Summary"
DEFAULT_NAME_PATTERNS = [
    r"Student\s+Name\s*\n\s*(?P<name>[A-Z][A-Za-z'., -]+)",
    r"Student\s+Name\s+(?P<name>[A-Z][A-Za-z'., -]+)",
    r"Name\s*:\s*(?P<name>[A-Z][A-Za-z'., -]+)",
]
REJECT_NAME_PATTERNS = (
    r"\b(?:GPA|Credit|Credits|Record|Graduation|Class Of|School|Address|Date|Gender|Grade|Student|ID|Parent|Guardian)\b",
    r"\d",
)


@dataclass(frozen=True)
class BookmarkEntry:
    name: str
    page_index: int


def compile_pattern(pattern: str, label: str) -> re.Pattern[str]:
    try:
        return re.compile(pattern, re.IGNORECASE | re.MULTILINE)
    except re.error as exc:
        raise ValueError(f"Invalid {label}: {pattern}\n{exc}") from exc


def normalize_name(raw_name: str) -> str:
    left_column = re.split(r"\s{2,}", raw_name, maxsplit=1)[0]
    cleaned = re.sub(r"\s+", " ", left_column).strip(" ,.;:-")
    cleaned = cleaned.replace(" ,", ",")
    return cleaned


def is_likely_name(candidate: str) -> bool:
    if not candidate:
        return False
    if len(candidate.split()) < 2:
        return False
    return not any(re.search(pattern, candidate, re.IGNORECASE) for pattern in REJECT_NAME_PATTERNS)


def extract_names_from_text(
    page_text: str,
    patterns: list[re.Pattern[str]],
) -> list[str]:
    candidates: list[str] = []

    for pattern in patterns:
        for match in pattern.finditer(page_text):
            raw = match.groupdict().get("name") or match.group(1)
            name = normalize_name(raw)
            if is_likely_name(name) and name not in candidates:
                candidates.append(name)

    lines = [line.strip() for line in page_text.splitlines()]
    for index, line in enumerate(lines):
        if line.lower() != "student name":
            continue
        for next_line in lines[index + 1 : index + 4]:
            candidate = normalize_name(next_line)
            if is_likely_name(candidate) and candidate not in candidates:
                candidates.append(candidate)
                break

    return candidates


def extract_text_with_pdftotext(input_path: Path) -> list[str]:
    if not PDFTOTEXT_PATH.exists():
        raise RuntimeError(
            "Text extraction requires either the 'pypdf' package or pdftotext.exe. "
            f"Expected pdftotext at {PDFTOTEXT_PATH}."
        )

    command = [str(PDFTOTEXT_PATH), "-layout", str(input_path), "-"]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    raw_text = result.stdout.replace("\r\n", "\n")
    pages = [page.strip() for page in raw_text.split("\f") if page.strip()]
    if not pages:
        raise RuntimeError("No text could be extracted from the PDF. The file may need OCR.")
    return pages


def read_pdf_pages(input_path: Path) -> tuple[object | None, list[str]]:
    if PdfReader is not None:
        reader = PdfReader(str(input_path))
        pages = [(page.extract_text() or "").strip() for page in reader.pages]
        return reader, pages

    return None, extract_text_with_pdftotext(input_path)


def extract_student_bookmarks(
    page_texts: list[str],
    patterns: list[re.Pattern[str]],
    required_pattern: re.Pattern[str] | None,
) -> list[BookmarkEntry]:
    found: dict[str, int] = {}

    for page_index, page_text in enumerate(page_texts):
        if required_pattern and not required_pattern.search(page_text):
            continue

        for name in extract_names_from_text(page_text, patterns):
            found.setdefault(name, page_index)

    return [BookmarkEntry(name=name, page_index=page_index) for name, page_index in sorted(found.items())]


def write_bookmarked_pdf(reader: object | None, output_path: Path, bookmarks: list[BookmarkEntry]) -> None:
    if reader is None or PdfWriter is None:
        raise RuntimeError(
            "Creating a bookmarked PDF requires the 'pypdf' package.\n"
            "Install it with: pip install pypdf"
        )

    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    for bookmark in bookmarks:
        writer.add_outline_item(bookmark.name, bookmark.page_index)

    with output_path.open("wb") as handle:
        writer.write(handle)


class TranscriptBookmarkerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Transcript Bookmarker")
        self.root.geometry("760x620")

        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.required_page_var = tk.StringVar(value=TRANSCRIPT_PAGE_PATTERN)
        self.status_var = tk.StringVar(value=self._build_status_message())

        self._build_ui()

    def _build_status_message(self) -> str:
        if PdfWriter is not None:
            return "Ready: preview and Acrobat-compatible bookmarked PDF creation are available."
        return "Preview is available. Install 'pypdf' to create Acrobat-compatible bookmarked PDFs."

    def _build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=14)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Input PDF").grid(row=0, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.input_var, width=72).grid(row=1, column=0, sticky="ew", padx=(0, 8))
        ttk.Button(frame, text="Browse...", command=self.pick_input).grid(row=1, column=1, sticky="e")

        ttk.Label(frame, text="Output PDF").grid(row=2, column=0, sticky="w", pady=(10, 0))
        ttk.Entry(frame, textvariable=self.output_var, width=72).grid(row=3, column=0, sticky="ew", padx=(0, 8))
        ttk.Button(frame, text="Browse...", command=self.pick_output).grid(row=3, column=1, sticky="e")

        ttk.Label(frame, text="Required page regex (optional, recommended)").grid(row=4, column=0, sticky="w", pady=(10, 0))
        ttk.Entry(frame, textvariable=self.required_page_var, width=72).grid(row=5, column=0, columnspan=2, sticky="ew")

        ttk.Label(frame, textvariable=self.status_var, foreground="#555").grid(
            row=6, column=0, columnspan=2, sticky="w", pady=(10, 0)
        )

        ttk.Label(frame, text="Name regex patterns (one per line; blank = transcript-safe defaults)").grid(
            row=7, column=0, sticky="w", pady=(10, 0)
        )
        self.pattern_text = tk.Text(frame, height=8, wrap="word")
        self.pattern_text.grid(row=8, column=0, columnspan=2, sticky="nsew")
        self.pattern_text.insert("1.0", "\n".join(DEFAULT_NAME_PATTERNS))

        ttk.Label(frame, text="Detected students preview").grid(row=9, column=0, sticky="w", pady=(10, 0))
        self.preview_text = tk.Text(frame, height=12, wrap="word")
        self.preview_text.grid(row=10, column=0, columnspan=2, sticky="nsew")

        button_row = ttk.Frame(frame)
        button_row.grid(row=11, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(button_row, text="Preview Names", command=self.preview).pack(side="left", padx=6)
        ttk.Button(button_row, text="Create Bookmarked PDF", command=self.generate).pack(side="left", padx=6)

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(8, weight=1)
        frame.rowconfigure(10, weight=1)

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

    def _run_detection(self) -> tuple[object | None, list[BookmarkEntry]]:
        input_path = Path(self.input_var.get().strip())
        if not input_path.exists():
            raise ValueError("Please choose a valid input PDF.")

        patterns = [compile_pattern(pattern, "name pattern") for pattern in self._collect_patterns()]
        required_pattern_raw = self.required_page_var.get().strip()
        required_pattern = compile_pattern(required_pattern_raw, "required page pattern") if required_pattern_raw else None

        reader, page_texts = read_pdf_pages(input_path)
        bookmarks = extract_student_bookmarks(page_texts, patterns, required_pattern)
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
