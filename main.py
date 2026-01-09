import sys
import json
import os
from PyQt6.QtWidgets import (
	QApplication, QLabel, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt
import importlib
from main_funktions import clear_content, update_content

def main():
	# settings path retained for potential future use
	settings_path = os.path.join(os.path.dirname(__file__), 'settings.json')

	app = QApplication(sys.argv)
	window = QWidget()
	# object names sourced from language files
	window.setObjectName(translation.t('object_appWindow'))
	window.setWindowTitle('Toolbox')
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
	mainmenu_btn.setStyleSheet('')
	button_layout.addWidget(mainmenu_btn)
	def show_mainmenu():
		clear_content(content_layout)
		label = QLabel('Bitte wähle einen Button links!')
		label.setStyleSheet('color: white;')
		content_layout.addWidget(label)
	mainmenu_btn.clicked.connect(lambda: show_mainmenu())
	# Nur Einstellungen-Button
	button_layout.addStretch()
	button5 = QPushButton('Einstellungen')
	button5.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
	button5.setStyleSheet('')
	button_layout.addWidget(button5)
	button_widget.setLayout(button_layout)
	button_widget.setObjectName(translation.t('object_sidePanel'))

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
	content_widget.setObjectName(translation.t('object_contentArea'))

	# use clear_content and update_content from main_funktions

	# Initialer Inhalt
	label = QLabel('Bitte wähle einen Button links!')
	content_layout.addWidget(label)

	for idx, btn in enumerate(button_refs):
		btn.clicked.connect(lambda checked, i=idx: update_content(i, content_layout, translation, settings_path, button_refs, button5))
	button5.clicked.connect(lambda checked: update_content(0, content_layout, translation, settings_path, button_refs, button5))

	main_layout.addWidget(flickable_widget)
	main_layout.addWidget(content_widget, stretch=1)
	window.setLayout(main_layout)
	window.resize(1200, 800)
	window.setMinimumSize(1200, 800)

	# QSS laden
	qss_path = os.path.join(os.path.dirname(__file__), 'main.qss')
	if os.path.exists(qss_path):
		with open(qss_path, 'r') as f:
			qss = f.read()
			# apply general QSS, then ensure window background stays white
			window.setStyleSheet(qss)
			flickable_widget.setStyleSheet(qss)
	# QSS from main.qss will style window and widget areas

	window.show()
	sys.exit(app.exec())

if __name__ == "__main__":
	main()
