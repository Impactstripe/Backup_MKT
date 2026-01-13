"""UI for Modbus Template Konfigurator."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QMenu, QMessageBox, QFileDialog
import json
import os
import csv
from PyQt6.QtCore import Qt
from .logic_modbus_template import ModbusTemplateManager
from package_one.main_funktions import get_language, get_settings_default_language, get_available_languages


def open_config_window():
    """Placeholder function to open the configuration window."""
    print("Open Modbus Template Konfigurator UI (placeholder)")


def get_widget(translation=None, *args, **kwargs):
    """Return a QWidget for the Modbus Template Konfigurator.

    Provide a horizontal Nav bar with `Datei`, `Import`, `Export` buttons.
    """
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

    title = QLabel("Modbus Template Konfigurator")
    layout.addWidget(title)

    # load names.json and helper to get localized labels
    def _read_names_file():
        path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'Data', 'names.json'))
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    _names_local = _read_names_file()

    def _lbl(key):
        try:
            settings_default = get_settings_default_language()
            languages = get_available_languages()
            fallback = _names_local.get('default_language') or (languages[0] if languages else 'de')
            lang_local = get_language(default=(settings_default or fallback))
        except Exception:
            lang_local = 'de'
        v = _names_local.get(key)
        if v is None:
            # check grouped keys for this page
            v = _names_local.get('modbus_template_page', {}).get(key)
        if v is None:
            # check column names grouped under modbus_template_page
            v = _names_local.get('modbus_template_page', {}).get('column_names', {}).get(key)
        if v is None:
            return key
        if isinstance(v, dict):
            return v.get(lang_local) or next(iter(v.values()))
        return v

    # Nav bar area
    nav = QWidget()
    nav_layout = QHBoxLayout(nav)
    nav_layout.setContentsMargins(0, 0, 0, 0)
    nav_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
    btn_datei = QPushButton(_lbl('nav_file'))
    btn_import = QPushButton(_lbl('nav_import'))
    btn_export = QPushButton(_lbl('nav_export'))
    # prepare File menu actions (will be connected after save/load functions exist)
    file_actions = {}
    file_menu = QMenu()
    file_actions['new'] = file_menu.addAction(_lbl('file_new_table'))
    file_actions['load_template'] = file_menu.addAction(_lbl('file_load_from_template'))
    file_actions['save'] = file_menu.addAction(_lbl('file_save'))
    file_actions['list'] = file_menu.addAction(_lbl('file_saved_tables'))
    file_actions['delete'] = file_menu.addAction(_lbl('file_delete_saved'))
    btn_datei.setMenu(file_menu)
    # Import/Export menus for the Import and Export buttons
    import_menu = QMenu()
    import_actions = {}
    import_actions['csv'] = import_menu.addAction(_lbl('import_csv'))
    import_actions['json'] = import_menu.addAction(_lbl('import_json'))
    btn_import.setMenu(import_menu)

    export_menu = QMenu()
    export_actions = {}
    export_actions['csv'] = export_menu.addAction(_lbl('export_csv'))
    export_actions['json'] = export_menu.addAction(_lbl('export_json'))
    btn_export.setMenu(export_menu)
    for b in (btn_datei, btn_import, btn_export):
        b.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        try:
            b.setFixedWidth(100)
        except Exception:
            pass
        nav_layout.addWidget(b)
    nav.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    # style nav buttons: white border
    try:
        nav.setStyleSheet('''
            QPushButton { border: 1px solid white; background: transparent; }
            QPushButton:hover { background: rgba(255,255,255,0.03); }
        ''')
    except Exception:
        pass

    # menus attached to Import/Export buttons; no click placeholder needed

    layout.addWidget(nav)

    # expose nav buttons for potential external access
    top_widgets = kwargs.get('top_widgets')
    if isinstance(top_widgets, dict):
        top_widgets['nav_buttons'] = {
            'datei': btn_datei,
            'import': btn_import,
            'export': btn_export,
        }

    # Toolbar directly under nav bar with two options
    toolbar = QWidget()
    tb_layout = QHBoxLayout(toolbar)
    tb_layout.setContentsMargins(0, 0, 0, 0)
    tb_layout.setSpacing(6)
    tb_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
    opt1 = QPushButton(_lbl('toolbar_opt1'))
    opt2 = QPushButton(_lbl('toolbar_opt2'))
    for b in (opt1, opt2):
        b.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        try:
            b.setFixedWidth(90)
        except Exception:
            pass
        tb_layout.addWidget(b)
    # style toolbar buttons: white border
    try:
        toolbar.setStyleSheet('''
            QPushButton { border: 1px solid white; background: transparent; }
            QPushButton:hover { background: rgba(255,255,255,0.03); }
        ''')
    except Exception:
        pass
    layout.addWidget(toolbar)

    # expose toolbar buttons as well
    if isinstance(top_widgets, dict):
        top_widgets['toolbar_buttons'] = {
            'opt1': opt1,
            'opt2': opt2,
        }

    # Input field under the toolbar
    input_field = QLineEdit()
    input_field.setPlaceholderText(_lbl('input_placeholder'))
    input_field.setFixedHeight(28)
    input_field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    layout.addWidget(input_field)

    # expose input field to caller
    if isinstance(top_widgets, dict):
        top_widgets['input_field'] = input_field

    # (save connection will be established after save_to_file is defined)

    # Table unter dem Eingabefeld
    table = QTableWidget()
    table.setColumnCount(6)
    # header labels are loaded from names.json via _lbl defined earlier

    headers = [
        _lbl('col_name'),
        _lbl('col_address'),
        _lbl('col_type'),
        _lbl('col_unit'),
        _lbl('col_scale'),
        _lbl('col_comment'),
    ]
    table.setHorizontalHeaderLabels(headers)
    table.setRowCount(0)
    table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    # improve visual differentiation: alternating rows, row selection and grid
    try:
        table.setAlternatingRowColors(True)
    except Exception:
        pass
    try:
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
    except Exception:
        pass
    try:
        table.setShowGrid(True)
    except Exception:
        pass
    # apply QSS to make individual cells visually distinct
    try:
        table.setStyleSheet('''
            QTableWidget { gridline-color: white; background-color: #ffffff; color: #000000; }
            QTableWidget::item { border-bottom: 1px solid white; padding: 6px; color: #000000; }
            QHeaderView::section { background-color: #000000; color: #ffffff; padding: 6px; border: 1px solid white; }
            QTableWidget::item:selected { background: #dcdcdc; color: #000000; }
            QTableWidget::item:selected:!active { background: #dcdcdc; color: #000000; }
        ''')
    except Exception:
        pass
    # stretch columns to fill available width
    try:
        header = table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        else:
            # fallback if header unexpectedly None
            try:
                hh = table.horizontalHeader()
                if hh is not None and hasattr(hh, 'setStretchLastSection'):
                    hh.setStretchLastSection(True)
            except Exception:
                pass
    except Exception:
        try:
            hh = table.horizontalHeader()
            if hh is not None and hasattr(hh, 'setStretchLastSection'):
                hh.setStretchLastSection(True)
        except Exception:
            pass
    layout.addWidget(table, stretch=1)

    # safe text helper available to other nested handlers
    def _safe_text(row_idx, col_idx):
        try:
            it = table.item(row_idx, col_idx)
            return it.text() if it is not None else ''
        except Exception:
            return ''

    # path for last template file in Data
    data_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'Data', 'last_Modbus_Template.json'))

    def save_to_file():
        try:
            rows = []
            for r in range(table.rowCount()):
                # read each cell safely
                def _safe_text(row_idx, col_idx):
                    try:
                        it = table.item(row_idx, col_idx)
                        return it.text() if it is not None else ''
                    except Exception:
                        return ''

                row = {
                    'Name': _safe_text(r, 0),
                    'Address': _safe_text(r, 1),
                    'Type': _safe_text(r, 2),
                    'Unit': _safe_text(r, 3),
                    'Scale': _safe_text(r, 4),
                    'Comment': _safe_text(r, 5),
                }
                rows.append(row)
            # include current input field text
            payload = {'templates': rows, 'last_used': None, 'input_text': input_field.text() if input_field is not None else ''}
            os.makedirs(os.path.dirname(data_path), exist_ok=True)
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def load_from_file():
        if not os.path.exists(data_path):
            return False
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            templates = data.get('templates') or []
            table.blockSignals(True)
            table.setRowCount(0)
            for i, tpl in enumerate(templates):
                table.insertRow(i)
                table.setItem(i, 0, QTableWidgetItem(str(tpl.get('Name', '') or '')))
                table.setItem(i, 1, QTableWidgetItem(str(tpl.get('Address', '') or '')))
                table.setItem(i, 2, QTableWidgetItem(str(tpl.get('Type', '') or '')))
                table.setItem(i, 3, QTableWidgetItem(str(tpl.get('Unit', '') or '')))
                table.setItem(i, 4, QTableWidgetItem(str(tpl.get('Scale', '') or '')))
                table.setItem(i, 5, QTableWidgetItem(str(tpl.get('Comment', '') or '')))
            # restore input field text if present
            try:
                input_field.setText(str(data.get('input_text', '') or ''))
            except Exception:
                pass
            table.blockSignals(False)
            return True
        except Exception:
            try:
                table.blockSignals(False)
            except Exception:
                pass
            return False

    # Connect File menu actions now that save/load are available
    try:
        def _new_table_action():
            try:
                table.setRowCount(0)
                save_to_file()
            except Exception:
                pass

        def _load_from_template_action():
            # load templates from data_path and populate table (if present)
            if not os.path.exists(data_path):
                QMessageBox.information(widget, _lbl('file_load_from_template'), _lbl('file_saved_tables') + ': 0')
                return
            try:
                with open(data_path, 'r', encoding='utf-8') as f:
                    d = json.load(f)
                templates = d.get('templates') or []
                if not templates:
                    QMessageBox.information(widget, _lbl('file_load_from_template'), _lbl('file_saved_tables') + ': 0')
                    return
                # populate table with stored templates
                table.blockSignals(True)
                table.setRowCount(0)
                for i, tpl in enumerate(templates):
                    table.insertRow(i)
                    table.setItem(i, 0, QTableWidgetItem(str(tpl.get('Name', '') or '')))
                    table.setItem(i, 1, QTableWidgetItem(str(tpl.get('Address', '') or '')))
                    table.setItem(i, 2, QTableWidgetItem(str(tpl.get('Type', '') or '')))
                    table.setItem(i, 3, QTableWidgetItem(str(tpl.get('Unit', '') or '')))
                    table.setItem(i, 4, QTableWidgetItem(str(tpl.get('Scale', '') or '')))
                    table.setItem(i, 5, QTableWidgetItem(str(tpl.get('Comment', '') or '')))
                table.blockSignals(False)
            except Exception:
                QMessageBox.warning(widget, _lbl('file_load_from_template'), 'Fehler beim Laden')

        def _save_action():
            try:
                save_to_file()
                QMessageBox.information(widget, _lbl('file_save'), 'OK')
            except Exception:
                QMessageBox.warning(widget, _lbl('file_save'), 'Fehler')

        def _list_saved_tables():
            if not os.path.exists(data_path):
                QMessageBox.information(widget, _lbl('file_saved_tables'), 'Keine')
                return
            try:
                with open(data_path, 'r', encoding='utf-8') as f:
                    d = json.load(f)
                templates = d.get('templates') or []
                if not templates:
                    QMessageBox.information(widget, _lbl('file_saved_tables'), 'Keine')
                    return
                # show simple list with indices and Name
                lines = []
                for i, tpl in enumerate(templates):
                    lines.append(f"{i+1}. {tpl.get('Name','')}")
                QMessageBox.information(widget, _lbl('file_saved_tables'), '\n'.join(lines))
            except Exception:
                QMessageBox.warning(widget, _lbl('file_saved_tables'), 'Fehler')

        def _delete_saved_tables():
            if not os.path.exists(data_path):
                QMessageBox.information(widget, _lbl('file_delete_saved'), 'Keine')
                return
            ok = QMessageBox.question(widget, _lbl('file_delete_saved'), 'Alle gespeicherten Tabellen löschen?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if ok == QMessageBox.StandardButton.Yes:
                try:
                    with open(data_path, 'w', encoding='utf-8') as f:
                        json.dump({'templates': [], 'last_used': None, 'input_text': ''}, f, ensure_ascii=False, indent=2)
                    QMessageBox.information(widget, _lbl('file_delete_saved'), 'OK')
                except Exception:
                    QMessageBox.warning(widget, _lbl('file_delete_saved'), 'Fehler')

        # wire actions (if they exist)
        try:
            a = file_actions.get('new')
            if a is not None and hasattr(a, 'triggered'):
                a.triggered.connect(_new_table_action)
            a = file_actions.get('load_template')
            if a is not None and hasattr(a, 'triggered'):
                a.triggered.connect(_load_from_template_action)
            a = file_actions.get('save')
            if a is not None and hasattr(a, 'triggered'):
                a.triggered.connect(_save_action)
            a = file_actions.get('list')
            if a is not None and hasattr(a, 'triggered'):
                a.triggered.connect(_list_saved_tables)
            a = file_actions.get('delete')
            if a is not None and hasattr(a, 'triggered'):
                a.triggered.connect(_delete_saved_tables)
        except Exception:
            pass
    except Exception:
        pass

    # Import/Export handlers (CSV / JSON)
    try:
        def _export_csv():
            fn, _ = QFileDialog.getSaveFileName(widget, _lbl('export_csv'), os.path.join(os.path.dirname(__file__), '..', '..', 'Data', 'last_Modbus_Template.csv'), 'CSV Files (*.csv)')
            if not fn:
                return
            try:
                with open(fn, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([_lbl('col_name'), _lbl('col_address'), _lbl('col_type'), _lbl('col_unit'), _lbl('col_scale'), _lbl('col_comment')])
                    for r in range(table.rowCount()):
                        writer.writerow([_safe_text(r, c) for c in range(table.columnCount())])
                QMessageBox.information(widget, _lbl('export_csv'), 'OK')
            except Exception:
                QMessageBox.warning(widget, _lbl('export_csv'), 'Fehler')

        def _export_json():
            fn, _ = QFileDialog.getSaveFileName(widget, _lbl('export_json'), os.path.join(os.path.dirname(__file__), '..', '..', 'Data', 'last_Modbus_Template.json'), 'JSON Files (*.json)')
            if not fn:
                return
            try:
                rows = []
                for r in range(table.rowCount()):
                    rows.append({
                        'Name': _safe_text(r, 0),
                        'Address': _safe_text(r, 1),
                        'Type': _safe_text(r, 2),
                        'Unit': _safe_text(r, 3),
                        'Scale': _safe_text(r, 4),
                        'Comment': _safe_text(r, 5),
                    })
                payload = {'templates': rows, 'last_used': None, 'input_text': input_field.text() if input_field is not None else ''}
                with open(fn, 'w', encoding='utf-8') as f:
                    json.dump(payload, f, ensure_ascii=False, indent=2)
                QMessageBox.information(widget, _lbl('export_json'), 'OK')
            except Exception:
                QMessageBox.warning(widget, _lbl('export_json'), 'Fehler')

        def _import_csv():
            fn, _ = QFileDialog.getOpenFileName(widget, _lbl('import_csv'), os.path.join(os.path.dirname(__file__), '..', '..', 'Data'), 'CSV Files (*.csv)')
            if not fn:
                return
            try:
                with open(fn, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                if not rows:
                    QMessageBox.information(widget, _lbl('import_csv'), 'Keine Daten')
                    return
                headers_row = rows[0]
                expected = [_lbl('col_name'), _lbl('col_address'), _lbl('col_type'), _lbl('col_unit'), _lbl('col_scale'), _lbl('col_comment')]
                start_idx = 1 if headers_row == expected else 0
                table.blockSignals(True)
                table.setRowCount(0)
                for i, row in enumerate(rows[start_idx:]):
                    table.insertRow(i)
                    for c in range(min(len(row), table.columnCount())):
                        table.setItem(i, c, QTableWidgetItem(str(row[c] if row[c] is not None else '')))
                table.blockSignals(False)
                save_to_file()
            except Exception:
                QMessageBox.warning(widget, _lbl('import_csv'), 'Fehler')

        def _import_json():
            fn, _ = QFileDialog.getOpenFileName(widget, _lbl('import_json'), os.path.join(os.path.dirname(__file__), '..', '..', 'Data'), 'JSON Files (*.json)')
            if not fn:
                return
            try:
                with open(fn, 'r', encoding='utf-8') as f:
                    d = json.load(f)
                templates = d.get('templates') or []
                table.blockSignals(True)
                table.setRowCount(0)
                for i, tpl in enumerate(templates):
                    table.insertRow(i)
                    table.setItem(i, 0, QTableWidgetItem(str(tpl.get('Name', '') or '')))
                    table.setItem(i, 1, QTableWidgetItem(str(tpl.get('Address', '') or '')))
                    table.setItem(i, 2, QTableWidgetItem(str(tpl.get('Type', '') or '')))
                    table.setItem(i, 3, QTableWidgetItem(str(tpl.get('Unit', '') or '')))
                    table.setItem(i, 4, QTableWidgetItem(str(tpl.get('Scale', '') or '')))
                    table.setItem(i, 5, QTableWidgetItem(str(tpl.get('Comment', '') or '')))
                table.blockSignals(False)
                save_to_file()
            except Exception:
                QMessageBox.warning(widget, _lbl('import_json'), 'Fehler')

        # connect import/export actions
        try:
            a = import_actions.get('csv')
            if a is not None and hasattr(a, 'triggered'):
                a.triggered.connect(_import_csv)
            a = import_actions.get('json')
            if a is not None and hasattr(a, 'triggered'):
                a.triggered.connect(_import_json)
            a = export_actions.get('csv')
            if a is not None and hasattr(a, 'triggered'):
                a.triggered.connect(_export_csv)
            a = export_actions.get('json')
            if a is not None and hasattr(a, 'triggered'):
                a.triggered.connect(_export_json)
        except Exception:
            pass
    except Exception:
        pass

    # expose table to caller
    if isinstance(top_widgets, dict):
        top_widgets['table'] = table

    # Try load saved templates; if none, add a sample row
    loaded = load_from_file()
    if not loaded:
        try:
            table.insertRow(0)
            table.setItem(0, 0, QTableWidgetItem('TempSensor'))
            table.setItem(0, 1, QTableWidgetItem('0x01'))
            table.setItem(0, 2, QTableWidgetItem('uint16'))
            table.setItem(0, 3, QTableWidgetItem('°C'))
            table.setItem(0, 4, QTableWidgetItem('0.1'))
            table.setItem(0, 5, QTableWidgetItem('Room temperature'))
        except Exception:
            pass

    # Funktionen zum Hinzufügen und Entfernen von Zeilen
    def add_row():
        try:
            row = table.rowCount()
            table.insertRow(row)
            name = input_field.text().strip() or f'Item {row+1}'
            table.setItem(row, 0, QTableWidgetItem(name))
            table.setItem(row, 1, QTableWidgetItem('0x00'))
            table.setItem(row, 2, QTableWidgetItem('uint16'))
            table.setItem(row, 3, QTableWidgetItem(''))
            table.setItem(row, 4, QTableWidgetItem('1'))
            table.setItem(row, 5, QTableWidgetItem(''))
            # save current state including input field
            try:
                save_to_file()
            except Exception:
                pass
            # optional: clear input after saving
            try:
                input_field.clear()
            except Exception:
                pass
        except Exception:
            pass
        

    def remove_selected_row():
        try:
            sel_model = table.selectionModel()
            if sel_model is None:
                return
            sel = sel_model.selectedRows()
            if not sel:
                return
            # remove in reverse order to keep indices valid
            rows = sorted((idx.row() for idx in sel), reverse=True)
            for r in rows:
                table.removeRow(r)
        except Exception:
            pass
        finally:
            save_to_file()

    # Verbinde die Toolbar-Buttons mit den Funktionen
    try:
        opt1.clicked.connect(add_row)
    except Exception:
        pass
    try:
        opt2.clicked.connect(remove_selected_row)
    except Exception:
        pass

    # Save on cell edit
    try:
        def on_item_changed(item):
            # called for any edit; save current table
            save_to_file()

        table.itemChanged.connect(on_item_changed)
    except Exception:
        pass

    # connect input_field save triggers now that save_to_file exists
    try:
        input_field.returnPressed.connect(save_to_file)
    except Exception:
        pass
    try:
        input_field.editingFinished.connect(save_to_file)
    except Exception:
        pass

    return widget
