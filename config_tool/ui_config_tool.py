from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHBoxLayout, QPushButton, QHeaderView, QToolBar, QToolButton, QMenu
from PyQt6.QtGui import QAction
from . import logic_config_tool
import os

def get_widget(translation, *args, **kwargs):
    widget = QWidget()
    layout = QVBoxLayout(widget)

    # QSS laden
    qss_path = os.path.join(os.path.dirname(__file__), 'config_tool.qss')
    if os.path.exists(qss_path):
        with open(qss_path, 'r') as f:
            widget.setStyleSheet(f.read())

    # Menü-Ersatz als QToolBar mit QToolButton + QMenu
    menutoolbar = QToolBar()
    menutoolbar.setMovable(False)
    menutoolbar.setStyleSheet('QToolBar { spacing: 16px; background: #f5f5f5; border: none; padding: 4px 8px; }')

    def styled_toolbutton(text, icon=None):
        btn = QToolButton()
        btn.setText(text)
        btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        btn.setStyleSheet('''
            QToolButton {
                font-size: 12px;
                padding: 2px 8px;
                border-radius: 4px;
                background: #e0e0e0;
                color: #222;
                min-width: 48px;
                min-height: 22px;
            }
            QToolButton::menu-indicator { image: none; }
            QToolButton:hover {
                background: #d0d0d0;
            }
        ''')
        if icon:
            btn.setIcon(icon)
        return btn

    from PyQt6.QtGui import QIcon
    file_btn = styled_toolbutton('File', QIcon.fromTheme('document-open'))
    file_menu = QMenu()
    file_menu.addAction('Neu')
    file_menu.addAction('Öffnen')
    file_menu.addAction('Speichern')
    export_menu = QMenu('Exportieren')
    export_menu.addAction('Als CSV')
    export_menu.addAction('Als Excel')
    file_menu.addMenu(export_menu)
    file_menu.addSeparator()
    file_menu.addAction('Beenden')
    file_btn.setMenu(file_menu)
    menutoolbar.addWidget(file_btn)

    edit_btn = styled_toolbutton('Bearbeiten', QIcon.fromTheme('edit-copy'))
    edit_menu = QMenu()
    edit_menu.addAction('Kopieren')
    edit_menu.addAction('Einfügen')
    suchen_menu = QMenu('Suchen')
    suchen_menu.addAction('In Tabelle')
    suchen_menu.addAction('Im Projekt')
    edit_menu.addMenu(suchen_menu)
    edit_btn.setMenu(edit_menu)
    menutoolbar.addWidget(edit_btn)

    help_btn = styled_toolbutton('Hilfe', QIcon.fromTheme('help-about'))
    help_menu = QMenu()
    help_menu.addAction('Über')
    faq_menu = QMenu('FAQ')
    faq_menu.addAction('Allgemein')
    faq_menu.addAction('Bedienung')
    help_menu.addMenu(faq_menu)
    help_btn.setMenu(help_menu)
    menutoolbar.addWidget(help_btn)

    layout.insertWidget(0, menutoolbar)

    # Toolbar als QToolBar
    toolbar = QToolBar()
    action_add = QAction(translation.t('add') if hasattr(translation, 't') else 'Hinzufügen', widget)
    action_remove = QAction(translation.t('remove') if hasattr(translation, 't') else 'Entfernen', widget)
    action_refresh = QAction(translation.t('refresh') if hasattr(translation, 't') else 'Aktualisieren', widget)
    toolbar.addAction(action_add)
    toolbar.addAction(action_remove)
    toolbar.addAction(action_refresh)
    layout.addWidget(toolbar)

    # Tabelle
    table = QTableWidget(3, 6)
    table.setHorizontalHeaderLabels([
        translation.t('col1') if hasattr(translation, 't') else 'Spalte 1',
        translation.t('col2') if hasattr(translation, 't') else 'Spalte 2',
        translation.t('col3') if hasattr(translation, 't') else 'Spalte 3',
        translation.t('col4') if hasattr(translation, 't') else 'Spalte 4',
        translation.t('col5') if hasattr(translation, 't') else 'Spalte 5',
        translation.t('col6') if hasattr(translation, 't') else 'Spalte 6',
    ])
    for row, row_data in enumerate([
        ['A', '1', 'X', 'Alpha', 'Rot', '100'],
        ['B', '2', 'Y', 'Beta', 'Blau', '200'],
        ['C', '3', 'Z', 'Gamma', 'Grün', '300']
    ]):
        for col, value in enumerate(row_data):
            table.setItem(row, col, QTableWidgetItem(value))
    table.setStyleSheet('color: black; background: white;')
    table.horizontalHeader().setStretchLastSection(True)
    for col in range(table.columnCount()):
        table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
    layout.addWidget(table)

    widget.setLayout(layout)

    action_add.triggered.connect(lambda: logic_config_tool.add_row(table))
    action_remove.triggered.connect(lambda: logic_config_tool.remove_row(table))
    action_refresh.triggered.connect(lambda: print('Refresh clicked'))

    return widget
