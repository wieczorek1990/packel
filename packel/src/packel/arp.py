import re
import subprocess
import sys


def trim_ip(ip: str) -> str:
    """Strip surrounding parentheses from an IP address (deprecated, kept for backward compatibility)."""
    return ip.strip("()")


def is_linux() -> bool:
    """Return True if running on Linux."""
    return sys.platform == "linux"


def normalize_mac(mac: str) -> str:
    """Normalize a MAC address to lowercase 2-digit colon-separated format.

    E.g., '82:4:5F:A3:BD:64' -> '82:04:5f:a3:bd:64'
    """
    parts = mac.split(":")
    return ":".join(p.lower().zfill(2) for p in parts)


def is_multicast_mac(mac: str) -> bool:
    """Return True if the MAC address is a multicast/broadcast address.

    Checks the least significant bit of the first octet (multicast bit)
    and common multicast OUIs like 01:00:5e (mDNS/SSDP) and 33:33 (IPv6 link-local).
    """
    first_byte = int(mac.split(":")[0], 16)
    # Multicast bit is the LSB of the first octet
    return (first_byte & 0x01) == 0x01


def extract_ip_and_mac(line: str) -> tuple[str, str] | None:
    """Extract IP and MAC from a macOS ARP output line using regex.

    macOS format: ? (192.168.8.101) at 66:d5:31:63:5c:78 on en0 ifscope [ethernet]
    Returns None if the line doesn't match the expected format.
    """
    match = re.search(r"\(([^)]+)\)\s+at\s+([0-9a-fA-F:]+)", line)
    if match:
        return match.group(1), match.group(2)
    return None


def extract_ip_and_mac_linux(line: str) -> tuple[str, str] | None:
    """Extract IP and MAC from a Linux 'ip neigh' output line using regex.

    Linux format: 192.168.8.101 dev enp0s25 lladdr 66:d5:31:63:5c:78 REACHABLE
    Returns None if the line doesn't match the expected format.
    """
    match = re.search(r"(\d+\.\d+\.\d+\.\d+).*?lladdr\s+([0-9a-fA-F:]+)", line)
    if match:
        return match.group(1), match.group(2)
    return None


def process_arp_data(arp_data: str, linux: bool = False) -> dict[str, str]:
    """Parse ARP neighbor data into a MAC-to-IP mapping.

    Args:
        arp_data: Raw output from 'arp -an' (macOS) or 'ip neigh' (Linux).
        linux: If True, parse Linux 'ip neigh' format; otherwise parse macOS format.
    """
    result: dict[str, str] = {}
    extractor = extract_ip_and_mac_linux if linux else extract_ip_and_mac
    for line in arp_data.splitlines():
        parsed = extractor(line)
        if parsed is None:
            continue
        ip, mac = parsed
        # Skip multicast/broadcast MACs (mDNS, SSDP, etc.)
        if is_multicast_mac(mac):
            continue
        # Normalize MAC to 2-digit format for consistent lookups
        mac = normalize_mac(mac)
        result[mac] = ip
    return result


def get_arp_data() -> tuple[str, bool]:
    """Run the platform-appropriate ARP command with sudo and return (output, is_linux).

    On macOS, 'arp -an' requires root privileges to show all entries.
    On Linux, 'sudo ip neigh show' ensures the full neighbor table is visible.

    Returns:
        A tuple of (raw_output, is_linux_flag) so the caller knows which parser to use.
    """
    linux = is_linux()
    if linux:
        cmd = ["sudo", "ip", "neigh", "show"]
    else:
        cmd = ["sudo", "arp", "-an"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return result.stdout, linux
