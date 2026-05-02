"""Dockable panels for search/replace and file tree navigation."""

from __future__ import annotations

import os
from pathlib import Path

PYSIDE_AVAILABLE = False

try:
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QTextCursor, QTextDocument
    from PySide6.QtWidgets import (
        QCheckBox,
        QDockWidget,
        QFileSystemModel,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPushButton,
        QTreeView,
        QVBoxLayout,
        QWidget,
    )
    PYSIDE_AVAILABLE = True
except Exception:
    PYSIDE_AVAILABLE = False


if PYSIDE_AVAILABLE:
    class SearchReplaceWidget(QWidget):
        def __init__(self, window):
            super().__init__(window)
            self.window = window
            self._build()

        def _build(self):
            layout = QVBoxLayout(self)
            row1 = QHBoxLayout()
            row2 = QHBoxLayout()
            row3 = QHBoxLayout()

            self.find_edit = QLineEdit()
            self.find_edit.setPlaceholderText("Find")
            self.replace_edit = QLineEdit()
            self.replace_edit.setPlaceholderText("Replace")
            self.case_sensitive = QCheckBox("Case sensitive")

            self.find_next_button = QPushButton("Find Next")
            self.find_prev_button = QPushButton("Find Previous")
            self.replace_button = QPushButton("Replace")
            self.replace_all_button = QPushButton("Replace All")

            self.find_next_button.clicked.connect(self.find_next)
            self.find_prev_button.clicked.connect(self.find_previous)
            self.replace_button.clicked.connect(self.replace_one)
            self.replace_all_button.clicked.connect(self.replace_all)

            row1.addWidget(self.find_edit)
            row1.addWidget(self.case_sensitive)
            row2.addWidget(self.replace_edit)
            row3.addWidget(self.find_prev_button)
            row3.addWidget(self.find_next_button)
            row3.addWidget(self.replace_button)
            row3.addWidget(self.replace_all_button)

            layout.addLayout(row1)
            layout.addLayout(row2)
            layout.addLayout(row3)

        def _current_editor(self):
            return self.window.current_editor()

        def _find_flags(self):
            flags = QTextDocument.FindFlag(0)
            if self.case_sensitive.isChecked():
                flags |= QTextDocument.FindFlag.FindCaseSensitively
            return flags

        def find_next(self):
            editor = self._current_editor()
            if editor is None:
                return
            text = self.find_edit.text()
            if not text:
                return
            if not editor.find(text, self._find_flags()):
                cursor = editor.textCursor()
                cursor.movePosition(QTextCursor.Start)
                editor.setTextCursor(cursor)
                editor.find(text, self._find_flags())

        def find_previous(self):
            editor = self._current_editor()
            if editor is None:
                return
            text = self.find_edit.text()
            if not text:
                return
            flags = self._find_flags() | QTextDocument.FindFlag.FindBackward
            if not editor.find(text, flags):
                cursor = editor.textCursor()
                cursor.movePosition(QTextCursor.End)
                editor.setTextCursor(cursor)
                editor.find(text, flags)

        def replace_one(self):
            editor = self._current_editor()
            if editor is None:
                return
            cursor = editor.textCursor()
            if cursor.hasSelection() and cursor.selectedText() == self.find_edit.text():
                cursor.insertText(self.replace_edit.text())
                editor.setTextCursor(cursor)
            self.find_next()

        def replace_all(self):
            editor = self._current_editor()
            if editor is None:
                return
            find_text = self.find_edit.text()
            if not find_text:
                return
            original = editor.toPlainText()
            if self.case_sensitive.isChecked():
                updated = original.replace(find_text, self.replace_edit.text())
            else:
                import re

                updated = re.sub(re.escape(find_text), self.replace_edit.text(), original, flags=re.IGNORECASE)
            if updated != original:
                editor.setPlainText(updated)
                editor.document().setModified(True)


    class FileTreePanel(QWidget):
        def __init__(self, window):
            super().__init__(window)
            self.window = window
            layout = QVBoxLayout(self)
            self.model = QFileSystemModel(self)
            self.model.setRootPath(str(Path.cwd()))
            self.view = QTreeView()
            self.view.setModel(self.model)
            self.view.setRootIndex(self.model.index(str(Path.cwd())))
            self.view.doubleClicked.connect(self.open_index)
            self.view.setHeaderHidden(False)
            self.view.setAnimated(True)
            for column in range(1, 4):
                self.view.hideColumn(column)
            layout.addWidget(self.view)

        def open_index(self, index):
            path = self.model.filePath(index)
            if os.path.isfile(path):
                self.window.open_file(path)
