import os


def process_arp_data(arp_data: str) -> dict:
    result = dict()
    for line in arp_data.splitlines():
        ip, mac = extract_ip_and_mac(line)

        # Trimming "(" and ")"
        ip = ip[1:-1]

        result[mac] = ip
    return result


def extract_ip_and_mac(line: str) -> tuple[str, str]:
    parts = line.split(" ")
    return parts[1], parts[3]


def get_arp_data() -> str:
    arp_data = os.popen("arp -a").read()
    return arp_data
