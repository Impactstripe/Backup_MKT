import sys
import os
import json
from PyQt6.QtWidgets import (
	QApplication, QLabel, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt
from .main_funktions import clear_content, update_content, get_language, get_settings_default_language, get_available_languages

def main():
	# settings path retained for potential future use
	settings_path = os.path.join(os.path.dirname(__file__), 'settings.json')

	# Ensure project root is on sys.path so packages at repo root (e.g. `extensions`) are importable
	project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
	if project_root not in sys.path:
		sys.path.insert(0, project_root)
	# Also ensure `src` folder is on sys.path so `package_one` can be imported directly
	src_path = os.path.join(project_root, 'src')
	if src_path not in sys.path and os.path.exists(src_path):
		sys.path.insert(0, src_path)
	print('sys.path[0:5]=', sys.path[0:5])

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
			# prefer a default set in settings.json, otherwise fall back to derived languages
			settings_default = get_settings_default_language()
			languages = get_available_languages()
			fallback = _names.get('default_language') or (languages[0] if languages else 'de')
			lang = get_language(default=(settings_default or fallback))
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
		settings_default = get_settings_default_language()
		languages = get_available_languages()
		fallback = _names.get('default_language') or (languages[0] if languages else 'de')
		lang_local = get_language(default=(settings_default or fallback))
		# labels may be stored directly at root (e.g. "menu_main": {..}) or under "labels"
		v = _names.get(key)
		if v is None:
			v = _names.get('labels', {}).get(key)
		if isinstance(v, dict):
			return v.get(lang_local) or next(iter(v.values()))
		return v or key
	mainmenu_btn = QPushButton(_lbl('menu_main'))
	mainmenu_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
	# styling moved to main.qss
	mainmenu_btn.setObjectName('mainmenu_btn')
	button_layout.addWidget(mainmenu_btn)
	def show_mainmenu():
		clear_content(content_layout)
		prompt = QLabel(_lbl('choose_prompt'))
		prompt.setObjectName('prompt_label')
		content_layout.addWidget(prompt)
		# update reference to current prompt label for other modules
		top_widgets['prompt_label'] = prompt
	mainmenu_btn.clicked.connect(lambda: show_mainmenu())
	# Nur Einstellungen-Button
	button_layout.addStretch()
	button5 = QPushButton(_lbl('settings'))
	button5.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
	# styling moved to main.qss
	button5.setObjectName('settings_btn')
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
	# central mapping of important top-level widgets passed to extensions
	top_widgets = {
		'mainmenu_btn': mainmenu_btn,
		'settings_btn': button5,
		'prompt_label': label,
	}

	for idx, btn in enumerate(button_refs):
		btn.clicked.connect(lambda checked, i=idx: update_content(i, content_layout, None, settings_path, button_refs, button5, top_widgets=top_widgets))
	button5.clicked.connect(lambda checked: update_content(0, content_layout, None , settings_path, button_refs, button5, top_widgets=top_widgets))

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
				# Apply stylesheet to the whole application to ensure consistent styling
				try:
					app.setStyleSheet(qss)
				except Exception:
					# fallback to setting on window and flickable_widget
					window.setStyleSheet(qss)
					try:
						flickable_widget.setStyleSheet(qss)
					except Exception:
						pass
				print(f"Loaded QSS: {qss_path}")
		except Exception as e:
			print(f"Failed to load QSS {qss_path}: {e}")
	else:
		print(f"QSS file not found at {qss_path}")

	window.show()
	sys.exit(app.exec())

if __name__ == "__main__":
	main()
