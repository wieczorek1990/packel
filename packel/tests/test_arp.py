import unittest
from unittest.mock import patch

from packel.arp import (
    extract_ip_and_mac,
    extract_ip_and_mac_linux,
    get_arp_data,
    is_multicast_mac,
    normalize_mac,
    process_arp_data,
    trim_ip,
)

SAMPLE_ONE = """? (172.20.10.1) at 82:4:5f:a3:bd:64 on en1 ifscope [ethernet]"""
SAMPLE_FOUR = """? (172.20.10.1) at 82:4:5f:a3:bd:64 on en1 ifscope [ethernet]
? (172.20.10.10) at 5c:84:3c:51:25:84 on en1 ifscope [ethernet]
mdns.mcast.net (224.0.0.251) at 1:0:5e:0:0:fb on en1 ifscope permanent [ethernet]
? (239.255.255.250) at 1:0:5e:7f:ff:fa on en1 ifscope permanent [ethernet]"""

LINUX_SAMPLE_ONE = """172.20.10.1 dev enp0s25 lladdr 82:04:5f:a3:bd:64 REACHABLE"""
LINUX_SAMPLE_FOUR = """172.20.10.1 dev enp0s25 lladdr 82:04:5f:a3:bd:64 REACHABLE
172.20.10.10 dev enp0s25 lladdr 5c:84:3c:51:25:84 STALE
172.20.10.251 dev enp0s25 lladdr 01:00:5e:00:00:fb FAILED"""


class TestArp(unittest.TestCase):
    def assertIsARPLine(self, ip: str, mac: str) -> None:
        self.assertIsNotNone(ip)
        self.assertIsInstance(ip, str)

        self.assertIsNotNone(mac)
        self.assertIsInstance(mac, str)

    def test_extract_ip_and_mac(self):
        result = extract_ip_and_mac(SAMPLE_ONE)

        self.assertIsNotNone(result)
        ip, mac = result
        self.assertIsARPLine(ip, mac)

    def test_extract_ip_and_mac_malformed_line_returns_none(self):
        """extract_ip_and_mac should return None for malformed lines."""
        result = extract_ip_and_mac("this is not an ARP line")
        self.assertIsNone(result)

    def test_extract_ip_and_mac_empty_line_returns_none(self):
        """extract_ip_and_mac should return None for empty lines."""
        result = extract_ip_and_mac("")
        self.assertIsNone(result)

    def test_process_arp_result(self):
        result = process_arp_data(SAMPLE_FOUR)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

        # SAMPLE_FOUR has 4 lines: 2 unicast + 2 multicast
        # Multicast entries are filtered out, so only 2 remain
        self.assertEqual(len(result), 2)

    def test_process_arp_result_normalizes_mac(self):
        """process_arp_data should normalize MACs to 2-digit format."""
        result = process_arp_data(SAMPLE_ONE)

        # '82:4:5f:a3:bd:64' should be normalized to '82:04:5f:a3:bd:64'
        self.assertIn("82:04:5f:a3:bd:64", result)
        self.assertEqual(result["82:04:5f:a3:bd:64"], "172.20.10.1")


    def test_process_arp_result_skips_malformed_lines(self):
        """process_arp_data should skip lines that don't match the ARP format."""
        mixed = """? (172.20.10.1) at 82:4:5f:a3:bd:64 on en1 ifscope [ethernet]
this is garbage
? (172.20.10.10) at 5c:84:3c:51:25:84 on en1 ifscope [ethernet]"""
        result = process_arp_data(mixed)

        self.assertEqual(len(result), 2)
        # MACs are normalized to 2-digit format
        self.assertEqual(result["82:04:5f:a3:bd:64"], "172.20.10.1")
        self.assertEqual(result["5c:84:3c:51:25:84"], "172.20.10.10")

    def test_process_arp_result_empty_input(self):
        """process_arp_data should return an empty dict for empty input."""
        result = process_arp_data("")
        self.assertEqual(result, {})


class TestTrimIp(unittest.TestCase):
    """Tests for the trim_ip() function."""

    def test_trim_ip_removes_parens(self):
        """trim_ip should remove leading and trailing parentheses."""
        result = trim_ip("(172.20.10.1)")
        self.assertEqual(result, "172.20.10.1")

    def test_trim_ip_no_change_without_parens(self):
        """trim_ip should leave strings without parentheses unchanged."""
        result = trim_ip("172.20.10.1")
        self.assertEqual(result, "172.20.10.1")


class TestNormalizeMac(unittest.TestCase):
    """Tests for the normalize_mac() function."""

    def test_normalize_mac_pads_single_digits(self):
        """normalize_mac should pad single-digit groups to 2 digits."""
        result = normalize_mac("82:4:5f:a3:bd:64")
        self.assertEqual(result, "82:04:5f:a3:bd:64")

    def test_normalize_mac_lowercases(self):
        """normalize_mac should convert to lowercase."""
        result = normalize_mac("82:04:5F:A3:BD:64")
        self.assertEqual(result, "82:04:5f:a3:bd:64")

    def test_normalize_mac_already_normalized(self):
        """normalize_mac should leave already-normalized MACs unchanged."""
        result = normalize_mac("66:d5:31:63:5c:78")
        self.assertEqual(result, "66:d5:31:63:5c:78")


class TestIsMulticastMac(unittest.TestCase):
    """Tests for the is_multicast_mac() function."""

    def test_multicast_mdns(self):
        """mDNS multicast MAC 01:00:5e should be detected."""
        self.assertTrue(is_multicast_mac("01:00:5e:00:00:fb"))

    def test_multicast_ssdp(self):
        """SSDP multicast MAC should be detected."""
        self.assertTrue(is_multicast_mac("01:00:5e:7f:ff:fa"))

    def test_unicast_mac(self):
        """Unicast MACs should not be detected as multicast."""
        self.assertFalse(is_multicast_mac("82:04:5f:a3:bd:64"))
        self.assertFalse(is_multicast_mac("66:d5:31:63:5c:78"))

    def test_multicast_bit_check(self):
        """Any MAC with LSB of first octet set should be multicast."""
        # First byte 0x83 (10000011) has LSB set -> multicast
        self.assertTrue(is_multicast_mac("83:00:00:00:00:00"))
        # First byte 0x82 (10000010) has LSB clear -> unicast
        self.assertFalse(is_multicast_mac("82:00:00:00:00:00"))


class TestGetArpData(unittest.TestCase):
    """Tests for the get_arp_data() function."""

    @patch("packel.arp.subprocess.run")
    @patch("packel.arp.is_linux")
    def test_get_arp_data_macos(self, mock_is_linux, mock_run):
        """get_arp_data should run 'sudo arp -an' on macOS and return tuple."""
        mock_is_linux.return_value = False
        mock_run.return_value.stdout = "? (192.168.1.1) at aa:bb:cc on en0"

        result = get_arp_data()

        mock_run.assert_called_once_with(["sudo", "arp", "-an"], capture_output=True, text=True, check=False)
        self.assertEqual(result, ("? (192.168.1.1) at aa:bb:cc on en0", False))

    @patch("packel.arp.subprocess.run")
    @patch("packel.arp.is_linux")
    def test_get_arp_data_linux(self, mock_is_linux, mock_run):
        """get_arp_data should run 'sudo ip neigh show' on Linux and return tuple."""
        mock_is_linux.return_value = True
        mock_run.return_value.stdout = "192.168.1.1 dev eth0 lladdr aa:bb:cc REACHABLE"

        result = get_arp_data()

        mock_run.assert_called_once_with(["sudo", "ip", "neigh", "show"], capture_output=True, text=True, check=False)
        self.assertEqual(result, ("192.168.1.1 dev eth0 lladdr aa:bb:cc REACHABLE", True))


class TestExtractIpAndMacLinux(unittest.TestCase):
    """Tests for the extract_ip_and_mac_linux() function."""

    def test_extract_linux_ip_and_mac(self):
        """extract_ip_and_mac_linux should parse Linux ip neigh format."""
        result = extract_ip_and_mac_linux(LINUX_SAMPLE_ONE)

        self.assertIsNotNone(result)
        ip, mac = result
        self.assertEqual(ip, "172.20.10.1")
        self.assertEqual(mac, "82:04:5f:a3:bd:64")

    def test_extract_linux_malformed_line_returns_none(self):
        """extract_ip_and_mac_linux should return None for malformed lines."""
        result = extract_ip_and_mac_linux("this is not an ip neigh line")
        self.assertIsNone(result)

    def test_extract_linux_empty_line_returns_none(self):
        """extract_ip_and_mac_linux should return None for empty lines."""
        result = extract_ip_and_mac_linux("")
        self.assertIsNone(result)


class TestProcessLinuxArpData(unittest.TestCase):
    """Tests for process_arp_data() with Linux format."""

    def test_process_linux_arp_data(self):
        """process_arp_data with linux=True should parse ip neigh output."""
        result = process_arp_data(LINUX_SAMPLE_FOUR, linux=True)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        # LINUX_SAMPLE_FOUR has 3 lines: 2 unicast + 1 multicast
        # Multicast entries are filtered out, so only 2 remain
        self.assertEqual(len(result), 2)
        self.assertEqual(result["82:04:5f:a3:bd:64"], "172.20.10.1")
        self.assertEqual(result["5c:84:3c:51:25:84"], "172.20.10.10")

    def test_process_linux_arp_data_normalizes_mac(self):
        """process_arp_data with linux=True should normalize MACs."""
        sample = "172.20.10.1 dev enp0s25 lladdr 82:4:5f:a3:bd:64 REACHABLE"
        result = process_arp_data(sample, linux=True)

        self.assertIn("82:04:5f:a3:bd:64", result)
        self.assertEqual(result["82:04:5f:a3:bd:64"], "172.20.10.1")

    def test_process_linux_arp_data_empty_input(self):
        """process_arp_data with linux=True should return empty dict for empty input."""
        result = process_arp_data("", linux=True)
        self.assertEqual(result, {})


if __name__ == "__main__":
    unittest.main()
