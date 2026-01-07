from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QProgressDialog, QComboBox, QLineEdit
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
from . import logic_netzwerkscanner
import os

class NetworkScanThread(QThread):
    result = pyqtSignal(list)
    current_ip = pyqtSignal(str)
    def __init__(self, interface=None, parent=None):
        super().__init__(parent)
        self.interface = interface
    def run(self):
        ips = []
        for ip in logic_netzwerkscanner.scan_network_iter(self.interface):
            self.current_ip.emit(ip["current"])
            if ip["active"]:
                ips.append(ip["current"])
        self.result.emit(ips)

def get_widget(translation, *args, **kwargs):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    # QSS laden
    qss_path = os.path.join(os.path.dirname(__file__), 'netzwerkscanner.qss')
    if os.path.exists(qss_path):
        with open(qss_path, 'r') as f:
            widget.setStyleSheet(f.read())

    label = QLabel(logic_netzwerkscanner.get_text())
    label.setStyleSheet('color: white; font-size: 18px;')
    layout.addWidget(label)

    # Dropdown für Netzwerk-Interface
    net_combo = QComboBox()
    interfaces = logic_netzwerkscanner.get_networks()
    for name, net in interfaces.items():
        net_combo.addItem(f"{name}: {net}", userData=net)
    layout.addWidget(net_combo)

    scan_btn = QPushButton('Netzwerk scannen')
    layout.addWidget(scan_btn)

    from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
    import subprocess
    ip_table = QTableWidget()
    ip_table.setColumnCount(4)
    ip_table.setHorizontalHeaderLabels(["IP", "Hostname", "MAC", "Online"])
    ip_table.setStyleSheet('color: white; background: #222; font-size: 12px;')
    ip_table.horizontalHeader().setStretchLastSection(False)
    ip_table.horizontalHeader().setSectionResizeMode(0, ip_table.horizontalHeader().ResizeMode.Fixed)
    ip_table.horizontalHeader().setSectionResizeMode(1, ip_table.horizontalHeader().ResizeMode.Fixed)
    ip_table.horizontalHeader().setSectionResizeMode(2, ip_table.horizontalHeader().ResizeMode.Fixed)
    ip_table.horizontalHeader().setSectionResizeMode(3, ip_table.horizontalHeader().ResizeMode.Fixed)
    ip_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    layout.addWidget(ip_table)
    # Spaltenbreiten anpassen
    ip_table.setColumnWidth(0, 160)  # IP
    ip_table.setColumnWidth(1, 200)  # Hostname
    ip_table.setColumnWidth(2, 180)  # MAC
    ip_table.setColumnWidth(3, 50)   # Online

    current_ip_label = QLabel('Aktuelle IP:')
    current_ip_label.setStyleSheet('color: white; font-size: 14px;')
    layout.addWidget(current_ip_label)
    current_ip_field = QLineEdit()
    current_ip_field.setReadOnly(True)
    current_ip_field.setStyleSheet('color: white; background: #222; font-size: 14px;')
    layout.addWidget(current_ip_field)

    progress = QProgressDialog('Netzwerk wird gescannt...', None, 0, 0, widget)
    progress.setWindowTitle('Bitte warten')
    progress.setCancelButton(None)
    progress.setModal(True)
    progress.close()

    timer = QTimer(widget)
    timer.setInterval(60000)  # 60 Sekunden
    timer.timeout.connect(lambda: update_online_status())

    def start_scan():
        scan_btn.setEnabled(False)
        ip_table.setRowCount(0)
        current_ip_field.setText('')
        progress.show()
        net = net_combo.currentData()
        thread = NetworkScanThread(interface=net)
        thread.result.connect(lambda ips: on_scan_finished(ips, thread))
        thread.current_ip.connect(lambda ip: current_ip_field.setText(ip))
        thread.start()

    def on_scan_finished(ips, thread):
        progress.close()
        import socket
        import re
        ip_table.setRowCount(len(ips))
        # ARP-Cache auslesen (macOS/Linux)
        try:
            arp_out = subprocess.check_output(['arp', '-a'], text=True)
        except Exception:
            arp_out = ''
        arp_map = {}
        for line in arp_out.splitlines():
            match = re.search(r'\((\d+\.\d+\.\d+\.\d+)\) at ([0-9a-fA-F:]{11,})', line)
            if match:
                arp_map[match.group(1)] = match.group(2)
        for row, ip in enumerate(ips):
            # Hostname
            try:
                hostname = socket.gethostbyaddr(ip)[0]
            except Exception:
                hostname = 'unbekannt'
            # MAC-Adresse
            mac = arp_map.get(ip, 'unbekannt')
            # Online-Status
            online_icon = '✔️' if ip else '❌'
            ip_table.setItem(row, 0, QTableWidgetItem(ip))
            ip_table.setItem(row, 1, QTableWidgetItem(hostname))
            ip_table.setItem(row, 2, QTableWidgetItem(mac))
            ip_table.setItem(row, 3, QTableWidgetItem(online_icon))
        scan_btn.setEnabled(True)
        current_ip_field.setText('')
        thread.deleteLater()
        # Starte/Resette den Timer für Online-Status-Update
        timer.stop()
        if ips:
            timer.start()
        widget._last_ips = ips

    def update_online_status():
        import subprocess
        for row, ip in enumerate(getattr(widget, '_last_ips', [])):
            try:
                result = subprocess.run(['ping', '-c', '1', '-W', '0.1', ip], stdout=subprocess.DEVNULL)
                online = result.returncode == 0
            except Exception:
                online = False
            online_icon = '✔️' if online else '❌'
            ip_table.setItem(row, 3, QTableWidgetItem(online_icon))

    scan_btn.clicked.connect(start_scan)
    return widget
