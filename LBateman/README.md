# Transcript PDF Bookmarker (Acrobat-friendly workflow)

This utility is a lightweight alternative to writing a full Adobe Acrobat plugin.
It creates bookmarks that Acrobat displays in the left navigation pane.

## Non-technical friendly workflow (no terminal)

You now have a desktop app (`bookmark_transcripts_app.py`) with file pickers and buttons:

- **Preview Names**: detect likely student names and show pages.
- **Create Bookmarked PDF**: generate the Acrobat-friendly bookmarked output PDF.

This means the end user does not need to run bash commands.

## Build a shareable executable (.exe)

On Windows (one-time build machine setup):

```bash
pip install pypdf pyinstaller
pyinstaller --onefile --windowed --name TranscriptBookmarker transcript_bookmarker/bookmark_transcripts_app.py
```

After build, share:

- `dist/TranscriptBookmarker.exe`

The recipient can double-click the executable and use the GUI.

## Concern addressed: false matches from transcript content

Yes—overly broad regex can accidentally match non-name content.
This version adds safeguards:

- Default extraction patterns are label-based (`Student Name: ...`) instead of broad free-text matching.
- Candidates are filtered to reject digits and transcript vocabulary like `GPA`, `Credits`, `Course`, etc.
- Optional `Required page regex` gate can restrict extraction to transcript pages only.

## GUI usage

1. Open `TranscriptBookmarker.exe` (or run `python transcript_bookmarker/bookmark_transcripts_app.py`).
2. Select input transcript PDF.
3. Select output PDF path.
4. (Optional) adjust required-page regex.
5. Click **Preview Names** and verify detection quality.
6. Click **Create Bookmarked PDF**.

## CLI usage (still available)

```bash
python transcript_bookmarker/bookmark_transcripts.py \
  --input class_transcripts.pdf \
  --output class_transcripts_bookmarked.pdf \
  --required-page-pattern "Transcript|Academic Record"
```

## Notes and limitations

- If pages are scanned images (no embedded text), run OCR first.
- For district-specific formatting, customize name patterns and keep them label-based when possible.
- Current logic keeps the first page for each student and alphabetizes bookmarks by student name.

