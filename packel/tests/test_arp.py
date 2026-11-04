import unittest
from unittest.mock import patch, MagicMock

from packel.arp import extract_ip_and_mac, process_arp_data, trim_ip, get_arp_data

SAMPLE_ONE = """? (172.20.10.1) at 82:4:5f:a3:bd:64 on en1 ifscope [ethernet]"""
SAMPLE_FOUR = """? (172.20.10.1) at 82:4:5f:a3:bd:64 on en1 ifscope [ethernet]
? (172.20.10.10) at 5c:84:3c:51:25:84 on en1 ifscope [ethernet]
mdns.mcast.net (224.0.0.251) at 1:0:5e:0:0:fb on en1 ifscope permanent [ethernet]
? (239.255.255.250) at 1:0:5e:7f:ff:fa on en1 ifscope permanent [ethernet]"""


class TestArp(unittest.TestCase):
    def assertIsARPLine(self, ip: str, mac: str) -> None:
        self.assertIsNotNone(ip)
        self.assertIsInstance(ip, str)

        self.assertIsNotNone(mac)
        self.assertIsInstance(mac, str)

    def test_extract_ip_and_mac(self):
        ip, mac = extract_ip_and_mac(SAMPLE_ONE)

        self.assertIsARPLine(ip, mac)

    def test_process_arp_result(self):
        result = process_arp_data(SAMPLE_FOUR)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

        result_length = len(result)
        lines = SAMPLE_FOUR.splitlines()
        sample_length = len(lines)
        self.assertEqual(result_length, sample_length)

    def test_process_arp_result_maps_mac_to_ip(self):
        """process_arp_data should map MAC addresses to their IPs."""
        result = process_arp_data(SAMPLE_ONE)

        self.assertIn("82:4:5f:a3:bd:64", result)
        self.assertEqual(result["82:4:5f:a3:bd:64"], "172.20.10.1")


class TestTrimIp(unittest.TestCase):
    """Tests for the trim_ip() function."""

    def test_trim_ip_removes_parens(self):
        """trim_ip should remove leading and trailing parentheses."""
        result = trim_ip("(172.20.10.1)")
        self.assertEqual(result, "172.20.10.1")

    def test_trim_ip_removes_first_and_last_char(self):
        """trim_ip should strip the first and last character of any string."""
        result = trim_ip("[10.0.0.1]")
        self.assertEqual(result, "10.0.0.1")


class TestGetArpData(unittest.TestCase):
    """Tests for the get_arp_data() function."""

    @patch("packel.arp.os.popen")
    def test_get_arp_data_reads_from_os_popen(self, mock_popen):
        """get_arp_data should read ARP output from os.popen."""
        mock_popen.return_value.read.return_value = "? (192.168.1.1) at aa:bb:cc on en0"

        result = get_arp_data()

        mock_popen.assert_called_once_with("arp -an")
        self.assertEqual(result, "? (192.168.1.1) at aa:bb:cc on en0")


if __name__ == "__main__":
    unittest.main()

