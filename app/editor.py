"""Reusable document editor widget and file helpers."""

from __future__ import annotations

import os
from pathlib import Path

PYSIDE_AVAILABLE = False

try:
    from PySide6.QtCore import QRect, QSize, Qt, Signal
    from PySide6.QtGui import QColor, QFont, QPainter, QTextCharFormat, QTextCursor, QTextDocument, QTextFormat
    from PySide6.QtWidgets import QPlainTextEdit, QTextEdit, QWidget
    PYSIDE_AVAILABLE = True
except Exception:
    PYSIDE_AVAILABLE = False


if PYSIDE_AVAILABLE:
    try:
        from syntax_highlighter import SimplePythonHighlighter
    except Exception:
        SimplePythonHighlighter = None

    from .theme import THEME_DATA

    class LineNumberArea(QWidget):
        def __init__(self, editor: "DocumentEditor"):
            super().__init__(editor)
            self._editor = editor

        def sizeHint(self):
            return QSize(self._editor.line_number_area_width(), 0)

        def paintEvent(self, event):
            self._editor.paint_line_number_area(event)


    class DocumentEditor(QPlainTextEdit):
        cursorInfoChanged = Signal()
        modeChanged = Signal()
        documentStateChanged = Signal()
        zoomChanged = Signal()

        def __init__(self, parent: QWidget | None = None):
            super().__init__(parent)
            self.file_path: str | None = None
            self.encoding = "UTF-8"
            self.line_ending = "LF"
            self.base_title = "Untitled"
            self._theme_name = "dark"
            self._theme = THEME_DATA[self._theme_name]
            self._highlighter = None
            self.zoom_percent = 100

            self.line_number_area = LineNumberArea(self)

            self.setFont(QFont("Consolas", 11))
            self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(" "))
            self.setOverwriteMode(False)

            self.blockCountChanged.connect(self.update_line_number_area_width)
            self.updateRequest.connect(self.update_line_number_area)
            self.cursorPositionChanged.connect(self._on_cursor_position_changed)
            self.modificationChanged.connect(lambda _modified: self.documentStateChanged.emit())

            self.update_line_number_area_width(0)
            self.highlight_current_line()
            self.apply_theme(self._theme_name)

        def sizeHint(self):
            return QSize(640, 480)

        def line_number_area_width(self) -> int:
            digits = 1
            maximum = max(1, self.blockCount())
            while maximum >= 10:
                maximum //= 10
                digits += 1
            return 8 + self.fontMetrics().horizontalAdvance("9") * digits

        def update_line_number_area_width(self, _block_count: int):
            self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

        def update_line_number_area(self, rect, dy):
            if dy:
                self.line_number_area.scroll(0, dy)
            else:
                self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

            if rect.contains(self.viewport().rect()):
                self.update_line_number_area_width(0)

        def resizeEvent(self, event):
            super().resizeEvent(event)
            cr = self.contentsRect()
            self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

        def paint_line_number_area(self, event):
            painter = QPainter(self.line_number_area)
            painter.fillRect(event.rect(), QColor(self._theme["line_bg"]))

            block = self.firstVisibleBlock()
            block_number = block.blockNumber()
            top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
            bottom = top + round(self.blockBoundingRect(block).height())

            while block.isValid() and top <= event.rect().bottom():
                if block.isVisible() and bottom >= event.rect().top():
                    number = str(block_number + 1)
                    painter.setPen(QColor(self._theme["line_fg"]))
                    painter.drawText(
                        0,
                        top,
                        self.line_number_area.width() - 4,
                        self.fontMetrics().height(),
                        Qt.AlignRight,
                        number,
                    )

                block = block.next()
                top = bottom
                bottom = top + round(self.blockBoundingRect(block).height())
                block_number += 1

        def _on_cursor_position_changed(self):
            self.highlight_current_line()
            self.cursorInfoChanged.emit()

        def cursor_line_column(self) -> tuple[int, int]:
            cursor = self.textCursor()
            return cursor.blockNumber() + 1, cursor.positionInBlock() + 1

        def is_overwrite(self) -> bool:
            return self.overwriteMode()

        def zoom_in(self):
            self.zoomIn(1)
            self.zoom_percent += 10
            self.zoomChanged.emit()

        def zoom_out(self):
            self.zoomOut(1)
            self.zoom_percent = max(10, self.zoom_percent - 10)
            self.zoomChanged.emit()

        def reset_zoom(self):
            while self.zoom_percent > 100:
                self.zoomOut(1)
                self.zoom_percent -= 10
            while self.zoom_percent < 100:
                self.zoomIn(1)
                self.zoom_percent += 10
            self.zoomChanged.emit()

        def keyPressEvent(self, event):
            if event.key() == Qt.Key_Insert:
                self.setOverwriteMode(not self.overwriteMode())
                self.modeChanged.emit()
                return
            super().keyPressEvent(event)

        def highlight_current_line(self):
            selections = []
            if not self.isReadOnly():
                selection = QTextEdit.ExtraSelection()
                line_color = QColor(self._theme["line_current"])
                line_color.setAlpha(255)
                selection.format.setBackground(line_color)
                selection.format.setProperty(QTextFormat.FullWidthSelection, True)
                selection.cursor = self.textCursor()
                selection.cursor.clearSelection()
                selections.append(selection)
            self.setExtraSelections(selections)

        def apply_theme(self, theme_name: str):
            self._theme_name = theme_name
            self._theme = THEME_DATA[theme_name]

            self.setStyleSheet(
                "QPlainTextEdit {"
                f" background: {self._theme['editor_bg']};"
                f" color: {self._theme['editor_fg']};"
                f" selection-background-color: {self._theme['selection_bg']};"
                f" selection-color: {self._theme['selection_fg']};"
                "}"
            )
            self.highlight_current_line()

            if SimplePythonHighlighter is not None:
                try:
                    if self.file_path and str(self.file_path).lower().endswith(".py"):
                        self._highlighter = SimplePythonHighlighter(self)
                    else:
                        self._highlighter = None
                except Exception:
                    self._highlighter = None

        def load_text(self, text: str, file_path: str | None = None, encoding: str = "UTF-8"):
            self.file_path = file_path
            self.encoding = encoding
            self.line_ending = "CRLF" if "\r\n" in text else "LF"
            self.setPlainText(text)
            self.document().setModified(False)
            self.highlight_current_line()
            self.documentStateChanged.emit()
            self.zoomChanged.emit()


    def read_text_file(path: str) -> tuple[str, str]:
        encodings = ("utf-8-sig", "utf-16", "cp1252")
        for encoding in encodings:
            try:
                with open(path, "r", encoding=encoding) as handle:
                    return handle.read(), encoding.upper()
            except Exception:
                pass
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            return handle.read(), "UTF-8"


    def write_text_file(path: str, text: str, encoding: str):
        with open(path, "w", encoding=encoding.lower().replace("UTF-8", "utf-8"), newline="\n") as handle:
            handle.write(text)


    def file_type_for_path(path: str | None) -> str:
        if not path:
            return "Plain Text"
        suffix = Path(path).suffix.lower()
        return {
            ".py": "Python",
            ".md": "Markdown",
            ".json": "JSON",
            ".toml": "TOML",
            ".yaml": "YAML",
            ".yml": "YAML",
            ".txt": "Plain Text",
        }.get(suffix, suffix[1:].upper() if suffix else "Plain Text")


    def detect_line_ending(text: str) -> str:
        return "CRLF" if "\r\n" in text else "LF"
