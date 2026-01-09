import sys
import os
import json
from PyQt6.QtWidgets import (
	QApplication, QLabel, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt
from main_funktions import clear_content, update_content
import app_registry
from main_funktions import get_language, set_language

def main():
	# settings path retained for potential future use
	settings_path = os.path.join(os.path.dirname(__file__), 'settings.json')

	# preload names.json so labels are available before widgets
	_names = {}
	try:
		with open(os.path.join(os.path.dirname(__file__), 'names.json'), 'r', encoding='utf-8') as f:
			_names = json.load(f)
	except Exception:
		_names = {}

	# QSS will be loaded after widgets are created so window exists

	app = QApplication(sys.argv)
	window = QWidget()
	# object names for QSS
	window.setObjectName('appWindow')
	# determine window title using settings language (fallback to names.json default)
	try:
		wt = _names.get('window_title')
		if isinstance(wt, dict):
			lang = get_language(default=_names.get('default_language') or (_names.get('language_order') or ['de'])[0])
			window_title = wt.get(lang) or next(iter(wt.values()))
		else:
			window_title = wt or 'Toolbox'
	except Exception:
		window_title = 'Toolbox'
	window.setWindowTitle(window_title)
	main_layout = QHBoxLayout()

	# Flickable Bereich (QScrollArea) mit 2 Buttons
	button_widget = QWidget()
	button_widget.setMaximumWidth(150)
	button_widget.setFixedWidth(150)
	button_layout = QVBoxLayout()
	button_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
	button_layout.setSpacing(2)
	button_refs = []
	# Hauptmenü-Button oben (label from names.json)
	def _lbl(key):
		# use preloaded names and persisted language setting
		labels_local = _names.get('labels', {})
		lang_local = get_language(default=_names.get('default_language') or (_names.get('language_order') or ['de'])[0])
		v = labels_local.get(key)
		if isinstance(v, dict):
			return v.get(lang_local) or next(iter(v.values()))
		return v or key
	mainmenu_btn = QPushButton(_lbl('menu_main'))
	mainmenu_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
	mainmenu_btn.setStyleSheet('')
	mainmenu_btn.setObjectName('mainmenu_btn')
	app_registry.register_widget('mainmenu_btn', mainmenu_btn)
	button_layout.addWidget(mainmenu_btn)
	def show_mainmenu():
		clear_content(content_layout)
		prompt = QLabel(_lbl('choose_prompt'))
		prompt.setObjectName('prompt_label')
		content_layout.addWidget(prompt)
		app_registry.register_widget('prompt_label', prompt)
	mainmenu_btn.clicked.connect(lambda: show_mainmenu())
	# Nur Einstellungen-Button
	button_layout.addStretch()
	button5 = QPushButton(_lbl('settings'))
	button5.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
	button5.setStyleSheet('')
	button5.setObjectName('settings_btn')
	app_registry.register_widget('settings_btn', button5)
	button_layout.addWidget(button5)
	button_widget.setLayout(button_layout)
	button_widget.setObjectName('sidePanel')

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
	content_widget.setObjectName('contentArea')

	# use clear_content and update_content from main_funktions

	# Initialer Inhalt
	label = QLabel(_lbl('choose_prompt'))
	label.setObjectName('prompt_label')
	content_layout.addWidget(label)
	app_registry.register_widget('prompt_label', label)

	for idx, btn in enumerate(button_refs):
		btn.clicked.connect(lambda checked, i=idx: update_content(i, content_layout,None, settings_path, button_refs, button5))
	button5.clicked.connect(lambda checked: update_content(0, content_layout, None , settings_path, button_refs, button5))

	main_layout.addWidget(flickable_widget)
	main_layout.addWidget(content_widget, stretch=1)
	window.setLayout(main_layout)
	window.resize(1200, 800)
	window.setMinimumSize(1200, 800)

	# QSS laden
	qss_path = os.path.join(os.path.dirname(__file__), 'main.qss')
	if os.path.exists(qss_path):
		try:
			with open(qss_path, 'r', encoding='utf-8') as f:
				qss = f.read()
				window.setStyleSheet(qss)
				try:
					flickable_widget.setStyleSheet(qss)
				except Exception:
					pass
		except Exception:
			pass

	window.show()
	sys.exit(app.exec())

if __name__ == "__main__":
	main()
