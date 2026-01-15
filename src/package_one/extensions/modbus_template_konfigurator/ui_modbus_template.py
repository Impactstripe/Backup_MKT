"""UI for Modbus Template Konfigurator."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QMenu, QMessageBox, QFileDialog
import json
import os
import csv
import datetime
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QStyledItemDelegate, QComboBox
from PyQt6.QtGui import QFont
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
        _lbl('col_register'),    # Register
        _lbl('col_datentyp'),    # Datentyp
        _lbl('col_einheit'),     # Einheit
        _lbl('col_beschreibung'),# Beschreibung
        _lbl('col_faktor'),      # Faktor
        _lbl('col_modbus_funktionen'),  # Modbus Funktionen
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

    # Allowed datatypes and autocomplete delegate for the Datentyp column
    DATATYPES = [
        'INT8', 'UINT8',
        'INT16 HL', 'INT16 LH', 'UINT16 HL', 'UINT16 LH',
        'INT32 HL', 'INT32 LH', 'UINT32 HL', 'UINT32 LH',
        'INT32 B0123', 'UINT32 B0123',
        'INT48 HL', 'INT48 LH', 'UINT48 HL', 'UINT48 LH',
        'INT48 B012345', 'UINT48 B012345',
        'INT64 HL', 'INT64 LH', 'UINT64 HL', 'UINT64 LH',
        'INT64 B01234567', 'UINT64 B01234567',
        'FLOAT32 HL', 'FLOAT32 LH', 'FLOAT32 B0123',
        'FLOAT64 HL', 'FLOAT64 LH', 'FLOAT64 B01234567',
        'HEX8',
        'HEX16 HL', 'HEX16 LH',
        'HEX32 HL', 'HEX32 LH',
        'HEX48 HL', 'HEX48 LH',
        'HEX64 HL', 'HEX64 LH',
    ]

    # allowed Modbus functions (1..4)
    MODBUS_FUNCTIONS = ['1', '2', '3', '4']

    class DatatypeDelegate(QStyledItemDelegate):
        def __init__(self, parent=None, values=None):
            super().__init__(parent)
            self.values = values or []

        def createEditor(self, parent, option, index):
            # only provide editor for the datentyp column (index 1)
            if index.column() == 1:
                cb = QComboBox(parent)
                cb.setEditable(True)
                cb.addItems(self.values)
                try:
                    from PyQt6.QtWidgets import QCompleter
                    completer = QCompleter(self.values, cb)
                    completer.setCaseSensitivity(Qt.CaseInsensitive)
                    cb.setCompleter(completer)
                except Exception:
                    pass
                return cb
            return super().createEditor(parent, option, index)

        def setEditorData(self, editor, index):
            if isinstance(editor, QComboBox):
                val = index.data() or ''
                i = editor.findText(val)
                if i >= 0:
                    editor.setCurrentIndex(i)
                else:
                    editor.setEditText(val)
            else:
                super().setEditorData(editor, index)

        def setModelData(self, editor, model, index):
            if isinstance(editor, QComboBox):
                text = editor.currentText().strip()
                model.setData(index, text)
            else:
                super().setModelData(editor, model, index)

        def updateEditorGeometry(self, editor, option, index):
            editor.setGeometry(option.rect)

    # install delegate for datentyp column and for modbus functions column
    delegate = DatatypeDelegate(widget, DATATYPES)
    table.setItemDelegateForColumn(1, delegate)
    func_delegate = DatatypeDelegate(widget, MODBUS_FUNCTIONS)
    table.setItemDelegateForColumn(5, func_delegate)

    # transient popup in top-right for unsupported datatypes
    def show_top_right_popup(message: str):
        try:
            popup = QLabel(message, widget)
            popup.setObjectName('mc_datatype_popup')
            popup.setStyleSheet('background: #ffcccc; border: 1px solid #990000; padding:6px;')
            popup.setFont(QFont('Segoe UI', 9))
            popup.adjustSize()
            x = max(10, widget.width() - popup.width() - 10)
            popup.move(x, 10)
            popup.show()
            QTimer.singleShot(2500, popup.deleteLater)
        except Exception:
            try:
                QMessageBox.warning(widget, 'Datentyp', message)
            except Exception:
                pass

    # validate entries after edits
    def _validate_cell(item):
        try:
            if item is None:
                return
            col = item.column()
            val = (item.text() or '').strip()
            if not val:
                return
            if col == 1:
                # Datentyp column
                ok = any(val.lower() == t.lower() for t in DATATYPES)
                if not ok:
                    show_top_right_popup(f"Datentyp '{val}' wird nicht unterstützt")
                    try:
                        table.blockSignals(True)
                        item.setText('')
                    finally:
                        try:
                            table.blockSignals(False)
                        except Exception:
                            pass
            elif col == 5:
                # Modbus functions column (must be '1'..'4')
                ok = val in MODBUS_FUNCTIONS
                if not ok:
                    show_top_right_popup("ungültige Modbus Funktion")
                    try:
                        table.blockSignals(True)
                        item.setText('')
                    finally:
                        try:
                            table.blockSignals(False)
                        except Exception:
                            pass
            elif col == 0:
                # Register column: accept decimal integers or hex (0x...) and disallow duplicates
                try:
                    if isinstance(val, str) and val.lower().startswith('0x'):
                        num = int(val, 16)
                    else:
                        num = int(val)
                    # check for duplicates in other rows
                    for rr in range(table.rowCount()):
                        if rr == item.row():
                            continue
                        other_txt = _safe_text(rr, 0)
                        if not other_txt:
                            continue
                        try:
                            if isinstance(other_txt, str) and other_txt.lower().startswith('0x'):
                                other_num = int(other_txt, 16)
                            else:
                                other_num = int(other_txt)
                        except Exception:
                            # ignore unparsable other rows
                            continue
                        if other_num == num:
                            show_top_right_popup('Doppelter Registerwert nicht erlaubt')
                            try:
                                table.blockSignals(True)
                                item.setText('')
                            finally:
                                try:
                                    table.blockSignals(False)
                                except Exception:
                                    pass
                            return
                except Exception:
                    show_top_right_popup("Ungültiger Registerwert")
                    try:
                        table.blockSignals(True)
                        item.setText('')
                    finally:
                        try:
                            table.blockSignals(False)
                        except Exception:
                            pass
                else:
                    # if parsing succeeded and no duplicates, keep table sorted
                    try:
                        sort_table_by_register()
                    except Exception:
                        try:
                            save_to_file()
                        except Exception:
                            pass
            elif col == 4:
                # Faktor column: must be float
                try:
                    float(val)
                except Exception:
                    show_top_right_popup("Ungültiger Faktor")
                    try:
                        table.blockSignals(True)
                        item.setText('')
                    finally:
                        try:
                            table.blockSignals(False)
                        except Exception:
                            pass
        except Exception:
            pass

    table.itemChanged.connect(_validate_cell)

    # safe text helper available to other nested handlers
    def _safe_text(row_idx, col_idx):
        try:
            it = table.item(row_idx, col_idx)
            return it.text() if it is not None else ''
        except Exception:
            return ''


    def _parse_register_value(txt):
        """Parse register text (supports hex 0x.. and decimal). Returns int or None."""
        try:
            if isinstance(txt, str) and txt.lower().startswith('0x'):
                return int(txt, 16)
            return int(str(txt))
        except Exception:
            return None


    def sort_table_by_register():
        """Reorder table rows ascending by numeric register (column 0)."""
        try:
            rows = []
            for r in range(table.rowCount()):
                # capture full row as list of texts
                row_vals = [ _safe_text(r, c) for c in range(table.columnCount()) ]
                reg_num = _parse_register_value(row_vals[0])
                # use large sentinel for unparsable to push to end
                key = reg_num if reg_num is not None else float('inf')
                rows.append((key, row_vals))

            rows.sort(key=lambda x: x[0])

            # repopulate table in sorted order
            table.blockSignals(True)
            table.setRowCount(0)
            for i, (_k, vals) in enumerate(rows):
                table.insertRow(i)
                for c, v in enumerate(vals):
                    table.setItem(i, c, QTableWidgetItem(str(v)))
            table.blockSignals(False)
            try:
                save_to_file()
            except Exception:
                pass
        except Exception:
            try:
                table.blockSignals(False)
            except Exception:
                pass

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
                    'Address': _safe_text(r, 0),
                    'Type': _safe_text(r, 1),
                    'Unit': _safe_text(r, 2),
                    'Comment': _safe_text(r, 3),
                    'Scale': _safe_text(r, 4),
                    'Functions': _safe_text(r, 5),
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
                table.setItem(i, 0, QTableWidgetItem(str(tpl.get('Address', '') or '')))
                table.setItem(i, 1, QTableWidgetItem(str(tpl.get('Type', '') or '')))
                table.setItem(i, 2, QTableWidgetItem(str(tpl.get('Unit', '') or '')))
                # map older 'Name' to Description/Comment if present
                descr = tpl.get('Comment', '') or tpl.get('Name', '')
                table.setItem(i, 3, QTableWidgetItem(str(descr or '')))
                table.setItem(i, 4, QTableWidgetItem(str(tpl.get('Scale', '') or '')))
                table.setItem(i, 5, QTableWidgetItem(str(tpl.get('Functions', '') or tpl.get('select', '') or '')))
            # restore input field text if present
            try:
                input_field.setText(str(data.get('input_text', '') or ''))
            except Exception:
                pass
            table.blockSignals(False)
            try:
                sort_table_by_register()
            except Exception:
                pass
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
                    table.setItem(i, 0, QTableWidgetItem(str(tpl.get('Address', '') or '')))
                    table.setItem(i, 1, QTableWidgetItem(str(tpl.get('Type', '') or '')))
                    table.setItem(i, 2, QTableWidgetItem(str(tpl.get('Unit', '') or '')))
                    descr = tpl.get('Comment', '') or tpl.get('Name', '')
                    table.setItem(i, 3, QTableWidgetItem(str(descr or '')))
                    table.setItem(i, 4, QTableWidgetItem(str(tpl.get('Scale', '') or '')))
                    table.setItem(i, 5, QTableWidgetItem(str(tpl.get('Functions', '') or tpl.get('select', '') or '')))
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
                # export table 1:1 as CSV, with a metadata row documenting the input field
                with open(fn, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    try:
                        input_text = input_field.text() if input_field is not None else ''
                    except Exception:
                        input_text = ''
                    # metadata row (first row) documents input_field above the table
                    writer.writerow(["#input", input_text])
                    writer.writerow([_lbl('col_address'), _lbl('col_type'), _lbl('col_unit'), _lbl('col_comment'), _lbl('col_scale'), _lbl('col_modbus_functions')])
                    for r in range(table.rowCount()):
                        row_vals = [_safe_text(r, c) for c in range(table.columnCount())]
                        writer.writerow(row_vals)
                QMessageBox.information(widget, _lbl('export_csv'), 'OK')
            except Exception:
                QMessageBox.warning(widget, _lbl('export_csv'), 'Fehler')

        def _export_json():
            try:
                # build RX entries from table rows using provided column mapping
                rx_entries = []
                for r in range(table.rowCount()):
                    reg_txt = _safe_text(r, 0)
                    # try parse register as int (support hex 0x...)
                    register = None
                    try:
                        if isinstance(reg_txt, str) and reg_txt.lower().startswith('0x'):
                            register = int(reg_txt, 16)
                        else:
                            register = int(reg_txt)
                    except Exception:
                        # keep original if parsing fails
                        register = reg_txt

                    # factor from scale column
                    factor_txt = _safe_text(r, 4)
                    try:
                        factor = float(factor_txt)
                    except Exception:
                        factor = 1

                    # Always export an empty select for RX entries per requirement
                    rx_entries.append({
                        'register': register,
                        'format': _safe_text(r, 1),
                        'unit': _safe_text(r, 2),
                        'description': _safe_text(r, 3),
                        'factor': factor,
                        'select': ''
                    })

                # Build TX blocks by grouping contiguous register ranges that share the same Modbus function.
                # Each block: {'function': <int>, 'start': <int>, 'length': <int>} where length = last-start+1
                tx_entries = []
                try:
                    # Build regs directly from table so TX derivation uses the Modbus function
                    # column values independent of RX 'select' (which is exported empty).
                    regs = []
                    for row_idx in range(table.rowCount()):
                        reg_txt = _safe_text(row_idx, 0)
                        try:
                            if isinstance(reg_txt, str) and reg_txt.lower().startswith('0x'):
                                reg_num = int(reg_txt, 16)
                            else:
                                reg_num = int(reg_txt)
                        except Exception:
                            # skip unparsable registers
                            continue

                        fc_txt = _safe_text(row_idx, 5) or ''
                        try:
                            fc_str = str(fc_txt).strip()
                        except Exception:
                            fc_str = ''
                        if not fc_str:
                            fc_str = '3'
                        try:
                            fc_int = int(fc_str)
                        except Exception:
                            fc_int = 3

                        regs.append((reg_num, fc_int))

                    regs.sort(key=lambda x: x[0])

                    if regs:
                        # helper to append chunks of max length 50 for a given start..end range
                        def _append_chunks(func_code, s, e):
                            st = s
                            while st <= e:
                                chunk_len = min(50, e - st + 1)
                                tx_entries.append({'function': func_code, 'start': st, 'length': chunk_len})
                                st = st + chunk_len

                        cur_func = regs[0][1]
                        start = regs[0][0]
                        end = regs[0][0]
                        for reg, func in regs[1:]:
                            if func == cur_func:
                                # same function: extend block range to include this register
                                end = reg
                                # if current span exceeds max, emit chunks from the start
                                if (end - start + 1) > 50:
                                    # emit first full chunk(s) up to current end
                                    _append_chunks(cur_func, start, start + ((end - start) // 50) * 50 + 49)
                                    # compute new start as next address after emitted chunks
                                    # find remaining lowest start position
                                    # find smallest st > previous emitted end
                                    # previous emitted end = start + ((end - start) // 50) * 50 + 49
                                    prev_emitted_end = start + ((end - start) // 50) * 50 + 49
                                    start = prev_emitted_end + 1
                            else:
                                # different function: flush existing range (chunked)
                                _append_chunks(cur_func, start, end)
                                start = reg
                                end = reg
                                cur_func = func
                        # finalize last block (may be chunked)
                        _append_chunks(cur_func, start, end)
                except Exception:
                    tx_entries = []

                # build LC entry from first table row: {function: <fc>, start: <register>, length: 1}
                lc_entries = []
                try:
                    if table.rowCount() > 0:
                        first_reg_txt = _safe_text(0, 0)
                        try:
                            if isinstance(first_reg_txt, str) and first_reg_txt.lower().startswith('0x'):
                                first_reg = int(first_reg_txt, 16)
                            else:
                                first_reg = int(first_reg_txt)
                        except Exception:
                            first_reg = first_reg_txt

                        first_fc_txt = _safe_text(0, 5) or ''
                        try:
                            first_fc = int(str(first_fc_txt).strip()) if str(first_fc_txt).strip() else 3
                        except Exception:
                            first_fc = 3

                        lc_entries.append({'function': first_fc, 'start': first_reg, 'length': 1})
                except Exception:
                    lc_entries = []

                device_obj = {
                    'Address': 0,
                    'AddressBase': 0,
                    'Type': (input_field.text().strip() if input_field is not None else ''),
                    'TX': tx_entries,
                    'RX': rx_entries,
                    'LC': lc_entries
                }

                payload = {'device': device_obj}

                # determine Downloads folder (fallback to Data folder)
                home = os.path.expanduser('~') or os.path.dirname(__file__)
                downloads = os.path.join(home, 'Downloads')
                if not os.path.isdir(downloads):
                    downloads = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'Data'))
                    os.makedirs(downloads, exist_ok=True)

                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"modbus_device_export_{timestamp}.json"
                fn = os.path.join(downloads, filename)

                with open(fn, 'w', encoding='utf-8') as f:
                    json.dump(payload, f, ensure_ascii=False, indent=2)

                QMessageBox.information(widget, _lbl('export_json'), f"{_lbl('file_save')}: {fn}")
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

                # detect metadata input row if present (first cell '#input')
                first = rows[0]
                if first and len(first) > 0 and str(first[0]).strip().lower().startswith('#input'):
                    try:
                        val = first[1] if len(first) > 1 else ''
                        input_field.setText(str(val))
                    except Exception:
                        pass
                    # remove metadata row
                    rows = rows[1:]

                # if next row is header labels, skip it
                expected = [_lbl('col_address'), _lbl('col_type'), _lbl('col_unit'), _lbl('col_comment'), _lbl('col_scale'), _lbl('col_modbus_functions')]
                if rows and rows[0] == expected:
                    rows = rows[1:]

                # populate table 1:1 with rows (preserve order); pad missing columns
                table.blockSignals(True)
                table.setRowCount(0)
                for i, row in enumerate(rows):
                    table.insertRow(i)
                    for c in range(table.columnCount()):
                        val = row[c] if c < len(row) else ''
                        table.setItem(i, c, QTableWidgetItem(str(val)))
                table.blockSignals(False)
                save_to_file()
                QMessageBox.information(widget, _lbl('import_csv'), f'Importiert: {len(rows)}')
            except Exception:
                QMessageBox.warning(widget, _lbl('import_csv'), 'Fehler')

        def _import_json():
            fn, _ = QFileDialog.getOpenFileName(widget, _lbl('import_json'), os.path.join(os.path.dirname(__file__), '..', '..', 'Data'), 'JSON Files (*.json)')
            if not fn:
                return
            try:
                # read and validate JSON syntax first
                with open(fn, 'r', encoding='utf-8') as f:
                    d = json.load(f)

                # determine source of rows: older templates format or exported device structure
                rows_source = []
                if isinstance(d, dict) and d.get('templates'):
                    # templates format: list of template dicts
                    rows_source = d.get('templates') or []
                elif isinstance(d, dict) and d.get('device') and isinstance(d.get('device'), dict):
                    # device export: prefer RX list, but derive Modbus function from TX ranges
                    dev = d.get('device')
                    rx = dev.get('RX') or dev.get('rx') or []
                    tx = dev.get('TX') or dev.get('tx') or []

                    # build mapping addr->function from TX blocks
                    tx_map = {}
                    try:
                        for t in tx:
                            if not isinstance(t, dict):
                                continue
                            # function code
                            try:
                                func = int(t.get('function', t.get('Function', 3)))
                            except Exception:
                                func = 3
                            # start and length
                            start = t.get('start')
                            length = t.get('length', 1)
                            try:
                                if isinstance(start, str) and str(start).lower().startswith('0x'):
                                    start_i = int(start, 16)
                                else:
                                    start_i = int(start)
                                length_i = int(length)
                            except Exception:
                                continue
                            for addr in range(start_i, start_i + max(1, length_i)):
                                tx_map[addr] = func
                    except Exception:
                        tx_map = {}

                    # normalize RX entries into template-like dicts and assign Functions from tx_map when possible
                    norm = []
                    for e in rx:
                        try:
                            if not isinstance(e, dict):
                                continue
                            reg = e.get('register', '')
                            reg_int = None
                            try:
                                if isinstance(reg, str) and str(reg).lower().startswith('0x'):
                                    reg_int = int(reg, 16)
                                else:
                                    reg_int = int(reg)
                            except Exception:
                                reg_int = None

                            # determine function: prefer tx_map if register parseable, else fall back to select
                            func_val = ''
                            if reg_int is not None and reg_int in tx_map:
                                func_val = str(tx_map.get(reg_int, ''))
                            else:
                                func_val = str(e.get('select', '') or '')

                            norm.append({
                                'Address': reg,
                                'Type': e.get('format', ''),
                                'Unit': e.get('unit', ''),
                                'Comment': e.get('description', ''),
                                'Scale': e.get('factor', ''),
                                'Functions': func_val,
                            })
                        except Exception:
                            continue
                    rows_source = norm

                # if no usable rows found, inform user
                if not rows_source:
                    QMessageBox.information(widget, _lbl('import_json'), _lbl('import_json') + ': keine Einträge gefunden')
                    return

                # validate rows and only populate valid entries
                valid_rows = []
                errors = []
                seen_regs = set()
                for i, tpl in enumerate(rows_source):
                    # Address/register must be parseable
                    addr_raw = tpl.get('Address', '')
                    reg_num = _parse_register_value(addr_raw)
                    if reg_num is None:
                        errors.append(f"Zeile {i+1}: ungültiger Register '{addr_raw}'")
                        continue

                    # duplicate within import
                    if reg_num in seen_regs:
                        errors.append(f"Zeile {i+1}: doppelter Register '{addr_raw}'")
                        continue

                    # Datentyp must be supported if present
                    dtype = str(tpl.get('Type', '') or '').strip()
                    if dtype:
                        ok_dt = any(dtype.lower() == t.lower() for t in DATATYPES)
                        if not ok_dt:
                            errors.append(f"Zeile {i+1}: ungültiger Datentyp '{dtype}'")
                            continue

                    # Faktor must be numeric if present
                    scale_val = tpl.get('Scale', '')
                    if scale_val is not None and str(scale_val).strip() != '':
                        try:
                            float(scale_val)
                        except Exception:
                            errors.append(f"Zeile {i+1}: ungültiger Faktor '{scale_val}'")
                            continue

                    # Functions must be one of allowed values or empty
                    func_val = str(tpl.get('Functions', '') or '').strip()
                    if func_val and func_val not in MODBUS_FUNCTIONS:
                        errors.append(f"Zeile {i+1}: ungültige Modbus-Funktion '{func_val}'")
                        continue

                    seen_regs.add(reg_num)
                    valid_rows.append(tpl)

                if not valid_rows:
                    QMessageBox.information(widget, _lbl('import_json'), 'Kein gültiger Eintrag zum Importieren.\n' + '\n'.join(errors[:10]))
                    return

                # clear and populate table with validated rows
                table.blockSignals(True)
                table.setRowCount(0)
                for i, tpl in enumerate(valid_rows):
                    table.insertRow(i)
                    table.setItem(i, 0, QTableWidgetItem(str(tpl.get('Address', '') or '')))
                    table.setItem(i, 1, QTableWidgetItem(str(tpl.get('Type', '') or '')))
                    table.setItem(i, 2, QTableWidgetItem(str(tpl.get('Unit', '') or '')))
                    descr = tpl.get('Comment', '') or tpl.get('Name', '')
                    table.setItem(i, 3, QTableWidgetItem(str(descr or '')))
                    table.setItem(i, 4, QTableWidgetItem(str(tpl.get('Scale', '') or '')))
                    table.setItem(i, 5, QTableWidgetItem(str(tpl.get('Functions', '') or tpl.get('select', '') or '')))
                table.blockSignals(False)
                try:
                    sort_table_by_register()
                except Exception:
                    pass
                save_to_file()

                # show brief import summary with up to 10 errors
                summary = f"Importiert: {len(valid_rows)}; Übersprungen: {len(errors)}"
                if errors:
                    summary += '\n' + '\n'.join(errors[:10])
                QMessageBox.information(widget, _lbl('import_json'), summary)
            except json.JSONDecodeError as jde:
                QMessageBox.warning(widget, _lbl('import_json'), f"JSON Syntaxfehler: {str(jde)}")
            except Exception:
                QMessageBox.warning(widget, _lbl('import_json'), 'Fehler beim Import')

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
            # New column order: Register, Datentyp, Einheit, Beschreibung, Faktor, Modbus Funktionen
            table.setItem(0, 0, QTableWidgetItem('0x01'))
            table.setItem(0, 1, QTableWidgetItem('uint16'))
            table.setItem(0, 2, QTableWidgetItem('°C'))
            table.setItem(0, 3, QTableWidgetItem('Room temperature'))
            table.setItem(0, 4, QTableWidgetItem('0.1'))
            table.setItem(0, 5, QTableWidgetItem(''))
        except Exception:
            pass

    # Funktionen zum Hinzufügen und Entfernen von Zeilen
    def add_row():
        try:
            row = table.rowCount()
            table.insertRow(row)
            # default values for new row in the new column order
            table.setItem(row, 0, QTableWidgetItem(''))
            table.setItem(row, 1, QTableWidgetItem(''))
            table.setItem(row, 2, QTableWidgetItem(''))
            # leave Beschreibung (description) empty for new rows
            table.setItem(row, 3, QTableWidgetItem(''))
            table.setItem(row, 4, QTableWidgetItem(''))
            table.setItem(row, 5, QTableWidgetItem(''))
            # save current state including input field (sort will save)
            try:
                try:
                    sort_table_by_register()
                except Exception:
                    try:
                        save_to_file()
                    except Exception:
                        pass
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
            try:
                try:
                    sort_table_by_register()
                except Exception:
                    pass
                save_to_file()
            except Exception:
                pass

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
