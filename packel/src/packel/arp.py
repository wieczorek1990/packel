import os
import re


def trim_ip(ip: str) -> str:
    """Strip surrounding parentheses from an IP address (deprecated, kept for backward compatibility)."""
    return ip.strip("()")


def extract_ip_and_mac(line: str) -> tuple[str, str] | None:
    """Extract IP and MAC from an ARP output line using regex.

    Returns None if the line doesn't match the expected format.
    """
    match = re.search(r"\(([^)]+)\)\s+at\s+([0-9a-fA-F:]+)", line)
    if match:
        return match.group(1), match.group(2)
    return None


def process_arp_data(arp_data: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in arp_data.splitlines():
        parsed = extract_ip_and_mac(line)
        if parsed is None:
            continue
        ip, mac = parsed
        result[mac] = ip
    return result


def get_arp_data() -> str:
    arp_data = os.popen("arp -an").read()
    return arp_data
