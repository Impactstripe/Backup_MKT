from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, QComboBox
import importlib

def get_widget(translation, on_language_change=None, *args, **kwargs):
    t = translation.translations

    widget = QWidget()
    layout = QVBoxLayout(widget)
    label = QLabel(t['settings'])
    label.setStyleSheet('color: white; font-size: 20px; font-weight: bold;')
    layout.addWidget(label)

    # Sprachwahl
    lang_select = QComboBox()
    lang_select.addItem(t['german'], 'de')
    lang_select.addItem(t['english'], 'en')
    layout.addWidget(QLabel(t['language']))
    layout.addWidget(lang_select)

    form = QFormLayout()
    eintrag1 = QLineEdit()
    eintrag2 = QLineEdit()
    form.addRow(t['username'], eintrag1)
    form.addRow(t['password'], eintrag2)
    layout.addLayout(form)

    speichern_btn = QPushButton(t['save'])
    layout.addWidget(speichern_btn)

    def change_language(idx):
        lang_code = lang_select.currentData()
        if on_language_change:
            on_language_change(lang_code)

    lang_select.currentIndexChanged.connect(change_language)

    return widget
