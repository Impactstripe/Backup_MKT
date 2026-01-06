
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
import logic_button5

def get_widget(translation, *args, **kwargs):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    label = QLabel(logic_button5.get_text())
    label.setStyleSheet('color: white; font-size: 18px;')
    layout.addWidget(label)
    return widget
