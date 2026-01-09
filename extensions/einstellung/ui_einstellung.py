from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from . import logic_einstellung
import os

def get_widget(translation, *args, **kwargs):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    label = QLabel(logic_einstellung.get_text())
    layout.addWidget(label)
    return widget
