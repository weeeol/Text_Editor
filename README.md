# Text Editor

PySide6 prototype added. To run the improved UI (preferred):

```bash
python main.py
```

To build a Windows executable (requires PyInstaller):

```powershell
./scripts/build.ps1
```

Project layout:

- `app/` contains the structured PySide launcher package.
- `scripts/` contains build and helper scripts.
- `pyside_ui.py` remains as the implementation for compatibility during the transition.

A simple, lightweight text editor written in Python.

Prerequisites

- Python 3.8 or newer

Quick start

1. Open a terminal in the project root.
2. Run:

   python main.py

Features

- New file: create a blank document.
- Save/Open: save the current document to disk and open existing files.
- Undo/Redo: multiple levels of undo and redo.
- Formatting: bold and italic text styling.
- Appearance: toggle light/dark themes.

Usage

- Create a new file from the File menu or the toolbar.
- Type or paste text into the main editing area.
- Use the toolbar or Edit menu to apply formatting and to undo/redo changes.
- Save via the File menu or the toolbar; choose a file name and location when prompted.
- Toggle dark mode from the Appearance menu.

Developer notes

- Main entry: `main.py`
- Core modules: `text_editor.py`, `text_operations.py`, `text_formatting.py`, `file_operations.py`
- Run locally with `python main.py`. No external dependencies required for the basic editor.

Roadmap / Future enhancements

- Find & replace
- Spell check
- Syntax highlighting for code
- Multiple document tabs
- Print support

Contributing
Contributions are welcome — open an issue or submit a pull request.

License
This project is provided under the MIT License.
