from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem

def add_row(table: QTableWidget):
    row_count = table.rowCount()
    table.insertRow(row_count)
    for col in range(table.columnCount()):
        table.setItem(row_count, col, QTableWidgetItem(''))

def remove_row(table: QTableWidget):
    row_count = table.rowCount()
    if row_count > 1:
        table.removeRow(row_count - 1)
