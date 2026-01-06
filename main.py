import sys
import json
import os
from PyQt6.QtWidgets import (
	QApplication, QLabel, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QScrollArea
)
from PyQt6.QtCore import Qt
import importlib
from translation_manager import TranslationManager

def main():
	# Lade Spracheinstellung
	settings_path = os.path.join(os.path.dirname(__file__), 'settings.json')
	if os.path.exists(settings_path):
		with open(settings_path, 'r') as f:
			settings = json.load(f)
		lang_code = settings.get('language', 'de')
	else:
		lang_code = 'de'
	translation = TranslationManager(lang_code)

	app = QApplication(sys.argv)
	window = QWidget()
	window.setWindowTitle('PyQt6 Row Layout App')
	window.setStyleSheet('background-color: white;')
	main_layout = QHBoxLayout()

	# Flickable Bereich (QScrollArea) mit 4 Buttons
	button_widget = QWidget()
	button_layout = QVBoxLayout()
	button_refs = []
	for i in range(1, 5):
		button = QPushButton(f'Button {i}')
		button_layout.addWidget(button)
		button_refs.append(button)
	button_layout.addStretch()
	button5 = QPushButton('Button 5')
	button_layout.addWidget(button5)
	button_widget.setLayout(button_layout)
	button_widget.setStyleSheet('background-color: black;')

	scroll_area = QScrollArea()
	scroll_area.setWidgetResizable(True)
	scroll_area.setWidget(button_widget)
	scroll_area.setMinimumWidth(80)
	scroll_area.setMaximumWidth(150)
	scroll_area.setFixedWidth(120)

	# Nur Flickable-Bereich (ohne Ein-/Ausklapp-Button)
	flickable_widget = QWidget()
	flickable_layout = QHBoxLayout()
	flickable_layout.setContentsMargins(0, 0, 0, 0)
	flickable_layout.setSpacing(0)
	flickable_layout.addWidget(scroll_area, alignment=Qt.AlignmentFlag.AlignLeft)
	flickable_widget.setLayout(flickable_layout)

	# Hauptinhalt rechts (dynamisch)
	content_layout = QVBoxLayout()
	content_widget = QWidget()
	content_widget.setLayout(content_layout)
	content_widget.setStyleSheet('background-color: black;')

	def clear_content():
		while content_layout.count():
			item = content_layout.takeAt(0)
			widget = item.widget()
			if widget is not None:
				widget.deleteLater()

	def update_content(idx):
		clear_content()
		# Mapping Button-Index zu Modulnamen
		module_map = {
			0: 'ui_button1',
			1: 'ui_button2',
			2: 'ui_button3',
			3: 'ui_button4',
			4: 'ui_settings',  # Button 5 zeigt das Einstellungsmenü
		}
		module_name = module_map.get(idx)
		if module_name:
			ui_module = importlib.import_module(module_name)
			# Für das Einstellungsmenü: Callback für Sprachwechsel übergeben
			if module_name == 'ui_settings':
				def on_language_change(new_lang):
					translation.set_language(new_lang)
					# Speichere Spracheinstellung
					with open(settings_path, 'w') as f:
						json.dump({'language': new_lang}, f)
					# UI neu laden
					update_content(4)
				widget = ui_module.get_widget(translation, on_language_change)
			else:
				widget = ui_module.get_widget(translation)
			content_layout.addWidget(widget)
		else:
			label = QLabel('Kein UI-Modul gefunden!')
			label.setStyleSheet('color: white; font-size: 18px;')
			content_layout.addWidget(label)

	# Initialer Inhalt
	label = QLabel('Bitte wähle einen Button links!')
	label.setStyleSheet('color: white; font-size: 18px;')
	content_layout.addWidget(label)

	for idx, btn in enumerate(button_refs):
		btn.clicked.connect(lambda checked, i=idx: update_content(i))
	button5.clicked.connect(lambda checked: update_content(4))

	main_layout.addWidget(flickable_widget)
	main_layout.addWidget(content_widget, stretch=1)
	window.setLayout(main_layout)
	window.resize(400, 150)
	window.show()
	sys.exit(app.exec())

if __name__ == "__main__":
	main()
