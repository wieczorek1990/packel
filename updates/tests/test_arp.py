import unittest

from updates.arp import extract_ip_and_mac, process_arp_result

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
        result = process_arp_result(SAMPLE_FOUR)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

        result_length = len(result)
        lines = SAMPLE_FOUR.splitlines()
        sample_length = len(lines)
        self.assertEqual(result_length, sample_length)

