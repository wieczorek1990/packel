import os


def trim_ip(ip: str) -> str:
    # Trimming "(" and ")"
    ip = ip[1:-1]
    return ip


def process_arp_data(arp_data: str) -> dict:
    result = dict()
    for line in arp_data.splitlines():
        ip, mac = extract_ip_and_mac(line)
        ip = trim_ip(ip)
        result[mac] = ip
    return result


def extract_ip_and_mac(line: str) -> tuple[str, str]:
    parts = line.split(" ")
    return parts[1], parts[3]


def get_arp_data() -> str:
    arp_data = os.popen("arp -an").read()
    return arp_data
