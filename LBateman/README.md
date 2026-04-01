# Transcript PDF Bookmarker (Acrobat-friendly workflow)

This utility is a lightweight alternative to building a full Adobe Acrobat plugin.
It creates a new PDF with standard bookmarks that Adobe Acrobat can display in the left navigation pane.

## What the app does

The desktop app in `LBateman/transcript-app.py` gives a non-technical user two main actions:

- **Preview Names**: detect likely student names and show which page each one starts on.
- **Create Bookmarked PDF**: generate a new PDF with Acrobat-compatible bookmarks.

The end user does not need to use the terminal once the app or `.exe` is built.

## Adobe Acrobat compatibility

This is not an Acrobat plugin. Instead, it writes standard PDF outline entries into a new output PDF.
When that output file is opened in Adobe Acrobat, the bookmarks should appear in Acrobat's bookmarks pane.

## Build a shareable executable (.exe)

Yes, Lisa can run this as a normal Windows executable once it has been built on a setup machine.

On Windows:

```bash
py -m pip install pypdf pyinstaller
py -m PyInstaller --onefile --windowed --name TranscriptBookmarker LBateman/transcript-app.py
```

After the build finishes, share:

- `dist/TranscriptBookmarker.exe`

Lisa should be able to double-click `TranscriptBookmarker.exe` and use the GUI on her machine.

Important:

- `pypdf` must be installed before building if you want the app to create Acrobat-compatible bookmarked PDFs.
- The app can still preview names without `pypdf` when text extraction is available, but PDF bookmark writing depends on `pypdf`.

## Detection safeguards

Transcript content can accidentally look like a student name, so this version uses safer defaults:

- Default extraction is based on transcript labels such as `Student Name`.
- Candidate names are filtered to reject digits and common transcript field words.
- An optional required-page regex can limit detection to transcript pages only.
- The current sample transcript format is supported where `Student Name` appears on one line and the student name is on the next line.

## GUI usage

1. Open `TranscriptBookmarker.exe`, or run `py LBateman/transcript-app.py`.
2. Select the input transcript PDF.
3. Select the output PDF path.
4. Optionally adjust the required-page regex.
5. Click **Preview Names** and verify the detected names.
6. Click **Create Bookmarked PDF**.
7. Open the generated PDF in Adobe Acrobat to confirm the bookmarks appear correctly.

## Notes and limitations

- If pages are scanned images with no embedded text, OCR is required first.
- For district-specific transcript layouts, the regex patterns may need to be customized.
- Current logic keeps the first page for each student and alphabetizes bookmarks by student name.
