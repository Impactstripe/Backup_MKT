from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from . import logic_einstellung
import os

def get_widget(translation, *args, **kwargs):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    # QSS laden
    qss_path = os.path.join(os.path.dirname(__file__), 'einstellung.qss')
    if os.path.exists(qss_path):
        with open(qss_path, 'r') as f:
            widget.setStyleSheet(f.read())
    label = QLabel(logic_einstellung.get_text())
    label.setStyleSheet('color: white;')
    layout.addWidget(label)
    return widget
