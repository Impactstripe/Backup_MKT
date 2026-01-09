from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QProgressDialog, QComboBox, QLineEdit, QCheckBox, QSpinBox
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
            print(f"UI: IP {ip['current']}, active: {ip['active']}")
            self.current_ip.emit(ip["current"])
            if ip["active"]:
                ips.append(ip["current"])
        print(f"UI: Finale Liste: {ips}")
        self.result.emit(ips)

class HostnameLookupThread(QThread):
    hostname_ready = pyqtSignal(int, str)  # row, hostname
    def __init__(self, ips, parent=None):
        super().__init__(parent)
        self.ips = ips
    def run(self):
        import socket
        for row, ip in enumerate(self.ips):
            if self.isInterruptionRequested():
                break
            try:
                hostname = socket.gethostbyaddr(ip)[0]
            except Exception:
                hostname = 'unbekannt'
            self.hostname_ready.emit(row, hostname)

def get_widget(translation, *args, **kwargs):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    # QSS laden
    qss_path = os.path.join(os.path.dirname(__file__), 'netzwerkscanner.qss')
    if os.path.exists(qss_path):
        with open(qss_path, 'r') as f:
            widget.setStyleSheet(f.read())

    label = QLabel(logic_netzwerkscanner.get_text())
    label.setStyleSheet('color: white;')
    layout.addWidget(label)

    # Dropdown für Netzwerk-Interface
    net_combo = QComboBox()
    interfaces = logic_netzwerkscanner.get_networks()
    for name, net in interfaces.items():
        net_combo.addItem(f"{name}: {net}", userData=net)
    layout.addWidget(net_combo)

    scan_btn = QPushButton('Netzwerk scannen')
    layout.addWidget(scan_btn)

    # Auto-Update Schalter
    auto_update_layout = QHBoxLayout()
    auto_checkbox = QCheckBox('Automatisches Aktualisieren')
    auto_checkbox.setChecked(False)  # Standard: aus
    auto_update_layout.addWidget(auto_checkbox)
    interval_label = QLabel('Intervall (Sekunden):')
    auto_update_layout.addWidget(interval_label)
    interval_spin = QSpinBox()
    interval_spin.setRange(10, 3600)  # 10 Sek bis 1 Stunde
    interval_spin.setValue(60)  # Standard: 60 Sek
    interval_spin.setSuffix(' s')
    auto_update_layout.addWidget(interval_spin)
    auto_update_layout.addStretch()
    layout.addLayout(auto_update_layout)

    from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
    import subprocess
    ip_table = QTableWidget()
    ip_table.setColumnCount(4)
    ip_table.setHorizontalHeaderLabels(["IP", "Hostname", "MAC", "Online"])
    ip_table.setStyleSheet('color: white; background: #222;')
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
    current_ip_label.setStyleSheet('color: white;')
    layout.addWidget(current_ip_label)
    current_ip_field = QLineEdit()
    current_ip_field.setReadOnly(True)
    current_ip_field.setStyleSheet('color: white; background: #222;')
    layout.addWidget(current_ip_field)

    progress = QProgressDialog('Netzwerk wird gescannt...', None, 0, 0, widget)
    progress.setWindowTitle('Bitte warten')
    progress.setCancelButton(None)
    progress.setModal(True)
    progress.close()

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

    timer = QTimer(widget)
    timer.setInterval(60000)  # 60 Sekunden
    timer.timeout.connect(start_scan)  # Automatische Aktualisierung der Liste

    def on_scan_finished(ips, thread):
        progress.close()
        import socket
        import re
        import platform
        is_windows = platform.system() == 'Windows'
        ip_table.setRowCount(len(ips))
        # ARP-Cache auslesen
        try:
            if is_windows:
                arp_out = subprocess.check_output(['arp', '-a'], text=True, encoding='cp1252')  # Windows encoding
            else:
                arp_out = subprocess.check_output(['arp', '-a'], text=True)
        except Exception:
            arp_out = ''
        arp_map = {}
        for line in arp_out.splitlines():
            if is_windows:
                match = re.search(r'(\d+\.\d+\.\d+\.\d+)\s+([0-9a-f\-]{17})', line)
            else:
                match = re.search(r'\((\d+\.\d+\.\d+\.\d+)\) at ([0-9a-f:]{17})', line)
            if match:
                arp_map[match.group(1)] = match.group(2).replace('-', ':')
        for row, ip in enumerate(ips):
            # Hostname wird asynchron geladen
            hostname = 'lädt...'  # Platzhalter
            # MAC-Adresse
            mac = arp_map.get(ip, 'unbekannt')
            # Online-Status
            online_icon = '✔️'
            ip_table.setItem(row, 0, QTableWidgetItem(ip))
            ip_table.setItem(row, 1, QTableWidgetItem(hostname))
            ip_table.setItem(row, 2, QTableWidgetItem(mac))
            ip_table.setItem(row, 3, QTableWidgetItem(online_icon))
        # Starte Hostname-Lookup im Hintergrund
        hostname_thread = HostnameLookupThread(ips)
        hostname_thread.hostname_ready.connect(lambda row, hostname: ip_table.setItem(row, 1, QTableWidgetItem(hostname)))
        hostname_thread.start()
        # Speichere Thread-Referenz, um ihn zu stoppen, wenn Widget zerstört wird
        widget._hostname_thread = hostname_thread
        scan_btn.setEnabled(True)
        current_ip_field.setText('')
        thread.deleteLater()
        # Starte/Resette den Timer für Online-Status-Update
        timer.stop()
        if ips and auto_checkbox.isChecked():
            timer.start()
        widget._last_ips = ips

    def update_online_status():
        import subprocess
        import platform
        is_windows = platform.system() == 'Windows'
        for row, ip in enumerate(getattr(widget, '_last_ips', [])):
            try:
                if is_windows:
                    result = subprocess.run(['ping', '-n', '1', '-w', '100', ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    result = subprocess.run(['ping', '-c', '1', '-W', '0.1', ip], stdout=subprocess.DEVNULL)
                online = result.returncode == 0
            except Exception:
                online = False
            online_icon = '✔️' if online else '❌'
            ip_table.setItem(row, 3, QTableWidgetItem(online_icon))

    def cleanup():
        try:
            if hasattr(widget, '_hostname_thread') and widget._hostname_thread.isRunning():
                widget._hostname_thread.requestInterruption()
                widget._hostname_thread.wait()
        except RuntimeError:
            pass  # Thread already deleted

    widget.destroyed.connect(cleanup)
    scan_btn.clicked.connect(start_scan)
    auto_checkbox.stateChanged.connect(lambda: timer.start() if auto_checkbox.isChecked() else timer.stop())
    interval_spin.valueChanged.connect(lambda value: timer.setInterval(value * 1000))
    return widget
