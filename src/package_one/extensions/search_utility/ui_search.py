from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt
from .logic_search import search_in_files
import os


class SearchWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.input = QLineEdit()
        self.input.setPlaceholderText('Search query (regex)')
        self.btn = QPushButton('Search')
        self.results = QListWidget()
        self.layout.addWidget(self.input)
        self.layout.addWidget(self.btn)
        self.layout.addWidget(self.results)
        self.btn.clicked.connect(self.on_search)

    def on_search(self):
        q = self.input.text().strip()
        self.results.clear()
        if not q:
            return
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        matches = search_in_files(q, root)
        for path, line_no, text in matches:
            item = QListWidgetItem(f"{os.path.relpath(path, root)}:{line_no} — {text}")
            item.setData(Qt.ItemDataRole.UserRole, (path, line_no))
            self.results.addItem(item)


def get_widget(*args, **kwargs):
    return SearchWidget()
