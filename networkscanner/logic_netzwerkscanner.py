import socket
import ipaddress
import subprocess
import psutil
import scapy.all as scapy
import concurrent.futures

# Logik für netzwerkscanner

def get_text():
    return 'Netzwerk-Scan'

def scan_network():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    net = ipaddress.ip_network(local_ip + '/24', strict=False)
    clients = arp_scan(str(net))
    if clients:
        ips = [client["ip"] for client in clients if client["ip"] != local_ip]
    else:
        # Fallback to ping scan
        ip_list = [str(ip) for ip in net.hosts() if str(ip) != local_ip]
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            results = list(executor.map(ping_ip, ip_list))
        ips = [result["current"] for result in results if result["active"]]
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

def arp_scan(network):
    try:
        print(f"Starte ARP-Scan für {network}")
        arp_request = scapy.ARP(pdst=network)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast / arp_request
        answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]
        clients_list = []
        for element in answered_list:
            client_dict = {"ip": element[1].psrc, "mac": element[1].hwsrc}
            clients_list.append(client_dict)
            print(f"ARP gefunden: {client_dict}")
        print(f"ARP-Scan beendet, {len(clients_list)} Geräte gefunden")
        return clients_list
    except RuntimeError as e:
        if "winpcap is not installed" in str(e):
            print("ARP-Scan nicht verfügbar (Npcap nicht installiert). Falle auf Ping-Scan zurück.")
            return []
        else:
            raise

def ping_ip(ip_str):
    try:
        result = subprocess.run(['ping', '-n', '1', '-w', '500', ip_str], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        active = result.returncode == 0
        print(f"Ping {ip_str}: {'aktiv' if active else 'inaktiv'}")
    except Exception as e:
        print(f"Fehler bei Ping {ip_str}: {e}")
        active = False
    return {"current": ip_str, "active": active}

def scan_network_iter(network_cidr=None):
    if not network_cidr:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        net = ipaddress.ip_network(local_ip + '/24', strict=False)
    else:
        net = ipaddress.ip_network(network_cidr, strict=False)
    clients = arp_scan(str(net))
    if clients:
        for client in clients:
            ip_str = client["ip"]
            if ip_str != socket.gethostbyname(socket.gethostname()):  # exclude local IP
                yield {"current": ip_str, "active": True}
    else:
        # Fallback to ping scan
        ip_list = [str(ip) for ip in net.hosts()]
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            future_to_ip = {executor.submit(ping_ip, ip): ip for ip in ip_list}
            for future in concurrent.futures.as_completed(future_to_ip):
                result = future.result()
                if result["current"] != socket.gethostbyname(socket.gethostname()):  # exclude local
                    yield result
