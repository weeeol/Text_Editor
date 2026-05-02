from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat


class SimplePythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent):
        super().__init__(parent.document())
        self._highlighting_rules = []

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            "def", "class", "import", "from", "as", "if", "elif", "else",
            "for", "while", "return", "with", "try", "except", "finally",
        ]
        for word in keywords:
            pattern = QRegularExpression(r"\b" + word + r"\b")
            self._highlighting_rules.append((pattern, keyword_format))

        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))
        self._highlighting_rules.append((QRegularExpression(r'".*"'), string_format))
        self._highlighting_rules.append((QRegularExpression(r"'.*'"), string_format))

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        self._highlighting_rules.append((QRegularExpression(r"#.*"), comment_format))

    def highlightBlock(self, text: str):
        for pattern, fmt in self._highlighting_rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                match = it.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)