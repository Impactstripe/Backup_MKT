from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, QComboBox
import importlib
import os

def get_widget(translation, on_language_change=None, *args, **kwargs):
    t = translation.translations

    widget = QWidget()
    layout = QVBoxLayout(widget)
    label = QLabel(t['settings'])
    label.setStyleSheet('color: white; font-weight: bold;')
    layout.addWidget(label)

    # Sprachwahl automatisch aus lang-Dateien
    lang_select = QComboBox()
    lang_dir = os.path.join(os.path.dirname(__file__), 'lang')
    for fname in os.listdir(lang_dir):
        if fname.endswith('.py'):
            code = fname[:-3]
            # Zeige Sprachcode als Auswahl, z.B. 'de' oder 'en'
            lang_label = code.upper() if code not in t else t[code]
            lang_select.addItem(lang_label, code)
    layout.addWidget(QLabel(t['language']))
    layout.addWidget(lang_select)

    speichern_btn = QPushButton(t['save'])
    layout.addWidget(speichern_btn)

    def change_language(idx):
        lang_code = lang_select.currentData()
        if on_language_change:
            on_language_change(lang_code)

    lang_select.currentIndexChanged.connect(change_language)

    # QSS laden
    qss_path = os.path.join(os.path.dirname(__file__), 'einstellung/einstellung.qss')
    if os.path.exists(qss_path):
        with open(qss_path, 'r') as f:
            widget.setStyleSheet(f.read())

    return widget
