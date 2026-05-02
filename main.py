"""Launcher for the PySide6 text editor.

If the current Python interpreter cannot import PySide6, this file tries to
re-exec itself using the workspace virtual environment so `python main.py`
still opens the PySide UI.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _try_relaunch_with_venv() -> bool:
    workspace_root = Path(__file__).resolve().parent
    venv_python = workspace_root / ".venv" / "Scripts" / "python.exe"

    if not venv_python.exists():
        return False

    if Path(sys.executable).resolve() == venv_python.resolve():
        return False

    env = os.environ.copy()
    env["PYTHONPATH"] = str(workspace_root)
    subprocess.run([str(venv_python), str(Path(__file__).resolve()), *sys.argv[1:]], check=False, env=env)
    return True


try:
    from app.ui import PYSIDE_AVAILABLE, run_pyside_app
except Exception:
    PYSIDE_AVAILABLE = False


if not PYSIDE_AVAILABLE:
    if _try_relaunch_with_venv():
        raise SystemExit(0)

    import tkinter as tk
    from text_editor import TextEditor

    if __name__ == "__main__":
        root = tk.Tk()
        app = TextEditor(root)
        root.geometry("800x600")
        root.mainloop()
else:
    if __name__ == "__main__":
        run_pyside_app()
