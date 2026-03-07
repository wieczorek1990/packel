import unittest

from updates.arp import extract_ip

SAMPLE = """? (172.20.10.1) at 82:4:5f:a3:bd:64 on en1 ifscope [ethernet]
? (172.20.10.10) at 5c:84:3c:51:25:84 on en1 ifscope [ethernet]
mdns.mcast.net (224.0.0.251) at 1:0:5e:0:0:fb on en1 ifscope permanent [ethernet]
? (239.255.255.250) at 1:0:5e:7f:ff:fa on en1 ifscope permanent [ethernet]"""


class TestArp(unittest.TestCase):
    def test_arp(self):
        for line in SAMPLE.splitlines():
            ip = extract_ip(line)
            print(ip)
