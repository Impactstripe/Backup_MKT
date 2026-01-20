import sys
import os
import json
from PyQt6.QtWidgets import (
	QApplication, QLabel, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QScrollArea, QSizePolicy
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import importlib

# --- begin utils merged from package_one.utils ---
_settings_path = os.path.join(os.path.dirname(__file__), 'Data', 'settings.json')

def _settings_read():
	try:
		with open(_settings_path, 'r', encoding='utf-8') as f:
			return json.load(f)
	except Exception:
		return {}

def _settings_write(data):
	try:
		with open(_settings_path, 'w', encoding='utf-8') as f:
			json.dump(data, f, ensure_ascii=False, indent=4)
	except Exception:
		pass

def get_language(default='de'):
	d = _settings_read()
	return d.get('language', default)


def get_settings_default_language():
	d = _settings_read()
	return d.get('default_language')


def get_available_languages():
	names_path = os.path.join(os.path.dirname(__file__), 'Data', 'names.json')
	try:
		with open(names_path, 'r', encoding='utf-8') as f:
			names = json.load(f)
	except Exception:
		names = {}

	codes = []
	wt = names.get('window_title')
	if isinstance(wt, dict):
		for k in wt.keys():
			if k not in codes:
				codes.append(k)

	def _looks_like_lang_map(d):
		if not isinstance(d, dict) or not d:
			return False
		for k, v in d.items():
			if not (isinstance(k, str) and 1 <= len(k) <= 3):
				return False
			if not isinstance(v, str):
				return False
		return True

	for key, val in names.items():
		if key == 'window_title':
			continue
		if isinstance(val, dict) and _looks_like_lang_map(val):
			for k in val.keys():
				if k not in codes:
					codes.append(k)

	settings_default = get_settings_default_language()
	if settings_default and settings_default in codes:
		codes = [settings_default] + [c for c in codes if c != settings_default]

	if not codes:
		codes = ['de']
	return codes

def set_language(lang_code):
	d = _settings_read()
	d['language'] = lang_code
	_settings_write(d)

def clear_content(content_layout):
	while content_layout.count():
		item = content_layout.takeAt(0)
		widget = item.widget()
		if widget is not None:
			widget.deleteLater()


def update_content(idx, content_layout, *args, **kwargs):
	settings_path = kwargs.get('settings_path', None)
	button_refs = kwargs.get('button_refs', None)
	button5 = kwargs.get('button5', None)
	if len(args) >= 1 and settings_path is None:
		if len(args) >= 2:
			settings_path = args[1]
		if len(args) >= 3:
			button_refs = args[2]
		if len(args) >= 4:
			button5 = args[3]

	clear_content(content_layout)
	module_map = {
		0: 'package_one.extensions.einstellung.ui_einstellung',
		1: 'package_one.extensions.modbus_template_konfigurator.ui_modbus_template',
		2: 'package_one.extensions.search_utility.ui_search',
	}
	module_name = module_map.get(idx)
	if module_name:
		ui_module = None
		try:
			ui_module = importlib.import_module(module_name)
		except ModuleNotFoundError:
			prefixes = []
			if __package__:
				prefixes.append(__package__ + '.')
			prefixes.extend(['src.package_one.', 'package_one.'])
			for p in prefixes:
				try:
					ui_module = importlib.import_module(p + module_name)
					break
				except Exception:
					continue
			if ui_module is None:
				raise
		top_widgets = kwargs.get('top_widgets', None)
		try:
			if top_widgets is not None:
				widget = ui_module.get_widget(None, top_widgets=top_widgets)
			else:
				widget = ui_module.get_widget(None)
		except TypeError:
			if top_widgets is not None:
				widget = ui_module.get_widget(top_widgets=top_widgets)
			else:
				widget = ui_module.get_widget()
		content_layout.addWidget(widget)
	else:
		label = QLabel('Kein UI-Modul gefunden!')
		content_layout.addWidget(label)

# --- end utils merged ---

def main():
	settings_path = os.path.join(os.path.dirname(__file__), 'Data', 'settings.json')

	project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
	if project_root not in sys.path:
		sys.path.insert(0, project_root)
	src_path = os.path.join(project_root, 'src')
	if src_path not in sys.path and os.path.exists(src_path):
		sys.path.insert(0, src_path)
	print('sys.path[0:5]=', sys.path[0:5])

	# preload names.json so labels are available before widgets
	_names = {}
	try:
		with open(os.path.join(os.path.dirname(__file__), 'Data', 'names.json'), 'r', encoding='utf-8') as f:
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
	button_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
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
		if v is None:
			# also support labels grouped under 'main_menu_page' (e.g. choose_prompt)
			v = _names.get('main_menu_page', {}).get(key)
		if v is None:
			# also support menu labels grouped under 'menu_punkte'
			v = _names.get('menu_punkte', {}).get(key)
		if isinstance(v, dict):
			return v.get(lang_local) or next(iter(v.values()))
		return v or key
	# logo above main menu (if available) - scale to fit sidebar width and height, keep aspect ratio
	try:
		logo_label = None
		logo_path = os.path.join(os.path.dirname(__file__), 'assets', 'MC_LOGO.jpg')
		if os.path.exists(logo_path):
			pix = QPixmap(logo_path)
			if not pix.isNull():
				# determine available width in sidebar (use 90% of configured max)
				try:
					avail_w = max(64, int(button_widget.maximumWidth() * 0.9))
				except Exception:
					avail_w = 140
				# limit height to a reasonable maximum so the logo is visible
				avail_h = 120
				# scale pixmap keeping aspect ratio and using smooth transform
				scaled = pix.scaled(avail_w, avail_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
				if not scaled.isNull():
					logo_label = QLabel()
					logo_label.setPixmap(scaled)
					logo_label.setMaximumSize(avail_w, avail_h)
					logo_label.setContentsMargins(0, 6, 0, 6)
					logo_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
		# only add the label if it was successfully created and contains a pixmap
		if logo_label is not None:
			button_layout.addWidget(logo_label)
		else:
			# ensure layout spacing stays consistent even without logo
			button_layout.addSpacing(6)
	except Exception:
		pass

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

	# Modbus Extension Button
	modbus_btn = QPushButton(_lbl('modbus_template'))
	modbus_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
	modbus_btn.setObjectName('modbus_btn')
	button_layout.addWidget(modbus_btn)

	# Search Extension Button
	search_btn = QPushButton(_lbl('search'))
	search_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
	search_btn.setObjectName('search_btn')
	button_layout.addWidget(search_btn)
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

	# Initialer Inhalt: zeige das Hauptmenü beim Start
	# central mapping of important top-level widgets passed to extensions
	top_widgets = {
		'mainmenu_btn': mainmenu_btn,
		'modbus_btn': modbus_btn,
		'search_btn': search_btn,
		'settings_btn': button5,
		# placeholder for dynamic prompt label (will be set later)
		'prompt_label': None,
	}

	# show main menu by default
	show_mainmenu()

	for idx, btn in enumerate(button_refs):
		btn.clicked.connect(lambda checked, i=idx: update_content(i, content_layout, None, settings_path, button_refs, button5, top_widgets=top_widgets))
	button5.clicked.connect(lambda checked: update_content(0, content_layout, None , settings_path, button_refs, button5, top_widgets=top_widgets))
	# connect Modbus button to the new extension (index 1)
	try:
		modbus_btn.clicked.connect(lambda checked: update_content(1, content_layout, None , settings_path, button_refs, button5, top_widgets=top_widgets))
		search_btn.clicked.connect(lambda checked: update_content(2, content_layout, None , settings_path, button_refs, button5, top_widgets=top_widgets))
	except NameError:
		# modbus_btn may not exist in older checkouts
		pass

	main_layout.addWidget(flickable_widget)
	main_layout.addWidget(content_widget, stretch=1)
	window.setLayout(main_layout)
	window.resize(1200, 800)
	window.setMinimumSize(1200, 800)

	# QSS laden
	qss_path = os.path.join(os.path.dirname(__file__), 'mc_ui', 'mc_styleguide.qss')
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
