import sys
import json
import os
from PyQt6.QtWidgets import (
	QApplication, QLabel, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QScrollArea, QSizePolicy
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
	window.setWindowTitle('Toolbox')
	window.setStyleSheet('background-color: white;')
	main_layout = QHBoxLayout()

	# Flickable Bereich (QScrollArea) mit 2 Buttons
	button_widget = QWidget()
	button_widget.setMaximumWidth(150)
	button_widget.setFixedWidth(150)
	button_layout = QVBoxLayout()
	button_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
	button_layout.setSpacing(2)
	button_refs = []
	# Hauptmenü-Button oben
	mainmenu_btn = QPushButton('Hauptmenü')
	mainmenu_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
	mainmenu_btn.setStyleSheet('font-size: 12px;')
	button_layout.addWidget(mainmenu_btn)
	def show_mainmenu():
		clear_content()
		label = QLabel('Bitte wähle einen Button links!')
		label.setStyleSheet('color: white; font-size: 18px;')
		content_layout.addWidget(label)
	mainmenu_btn.clicked.connect(lambda: show_mainmenu())
	# Nur Button 1 und 2
	button = QPushButton('config_tool')
	button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
	button.setStyleSheet('font-size: 12px;')
	button_layout.addWidget(button)
	button_refs.append(button)
	button2 = QPushButton('netzwerkscanner')
	button2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
	button2.setStyleSheet('font-size: 12px;')
	button_layout.addWidget(button2)
	button_refs.append(button2)
	button_layout.addStretch()
	button5 = QPushButton('Einstellungen')
	button5.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
	button5.setStyleSheet('font-size: 12px;')
	button_layout.addWidget(button5)
	button_widget.setLayout(button_layout)
	button_widget.setStyleSheet('background-color: black;')

	scroll_area = QScrollArea()
	scroll_area.setWidgetResizable(True)
	scroll_area.setWidget(button_widget)
	scroll_area.setMinimumWidth(150)
	scroll_area.setMaximumWidth(150)
	scroll_area.setFixedWidth(150)
	scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

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
		# Mapping Button-Index zu Modulnamen (neue Struktur)
		module_map = {
			0: 'config_tool.ui_config_tool',
			1: 'netzwerkscanner.ui_netzwerkscanner',
			2: 'einstellung.ui_einstellung',  # Button 5 zeigt das Einstellungsmenü
		}
		module_name = module_map.get(idx)
		if module_name:
			ui_module = importlib.import_module(module_name)
			# Für das Einstellungsmenü: Callback für Sprachwechsel übergeben
			if module_name == 'einstellung.ui_einstellung':
				def on_language_change(new_lang):
					translation.set_language(new_lang)
					# Speichere Spracheinstellung
					with open(settings_path, 'w') as f:
						json.dump({'language': new_lang}, f)
					button_refs[0].setText('config_tool')
					button_refs[1].setText('netzwerkscanner')
					button5.setText('Einstellungen')
					update_content(2)
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
	button5.clicked.connect(lambda checked: update_content(2))

	main_layout.addWidget(flickable_widget)
	main_layout.addWidget(content_widget, stretch=1)
	window.setLayout(main_layout)
	window.resize(1200, 800)
	window.setMinimumSize(1200, 800)

	# QSS laden
	qss_path = os.path.join(os.path.dirname(__file__), 'main.qss')
	if os.path.exists(qss_path):
		with open(qss_path, 'r') as f:
			window.setStyleSheet(f.read())
			flickable_widget.setStyleSheet(f.read())

	window.show()
	sys.exit(app.exec())

if __name__ == "__main__":
	main()
