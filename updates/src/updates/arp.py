def process_arp_result(arp_data: str) -> dict:
    result = dict()
    for line in arp_data.splitlines():
        ip, mac = extract_ip_and_mac(line)
        result[mac] = ip
    return result


def extract_ip_and_mac(line: str) -> tuple[str, str]:
    parts = line.split(" ")
    return parts[1], parts[3]
