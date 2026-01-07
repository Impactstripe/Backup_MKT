import socket
import ipaddress
import subprocess
import platform
import psutil

# Logik für netzwerkscanner

def get_text():
    return 'Netzwerk-Scan'

def scan_network():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    net = ipaddress.ip_network(local_ip + '/24', strict=False)
    ips = []
    is_mac = platform.system() == 'Darwin'
    for ip in net.hosts():
        ip_str = str(ip)
        if ip_str == local_ip:
            continue
        try:
            if is_mac:
                result = subprocess.run(['ping', '-c', '1', '-t', '1', ip_str], stdout=subprocess.DEVNULL)
            else:
                result = subprocess.run(['ping', '-c', '1', '-W', '1', ip_str], stdout=subprocess.DEVNULL)
            if result.returncode == 0:
                ips.append(ip_str)
        except Exception:
            pass
    return ips

def get_networks():
    nets = {}
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and not addr.address.startswith('127.'):
                ip = addr.address
                net = ipaddress.ip_network(ip + '/24', strict=False)
                nets[iface] = str(net)
    return nets

def scan_network_iter(network_cidr=None):
    if not network_cidr:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        net = ipaddress.ip_network(local_ip + '/24', strict=False)
    else:
        net = ipaddress.ip_network(network_cidr, strict=False)
    is_mac = platform.system() == 'Darwin'
    for ip in net.hosts():
        ip_str = str(ip)
        try:
            if is_mac:
                result = subprocess.run(['ping', '-c', '1', '-t', '1', '-W', '100', ip_str], stdout=subprocess.DEVNULL)
            else:
                result = subprocess.run(['ping', '-c', '1', '-W', '0.1', ip_str], stdout=subprocess.DEVNULL)
            active = result.returncode == 0
        except Exception:
            active = False
        yield {"current": ip_str, "active": active}
