import unittest
import tempfile
import os
from unittest.mock import patch, mock_open

from packel.servers import init, validate_config


class TestServersInit(unittest.TestCase):
    """Tests for the init() function that loads TOML config files."""

    def _write_toml(self, content: str) -> str:
        """Helper to write TOML content to a temp file and return the path."""
        fd, path = tempfile.mkstemp(suffix=".toml")
        with os.fdopen(fd, "w") as f:
            f.write(content)
        return path

    def test_init_loads_valid_toml(self):
        """init() should parse a valid TOML file and return a dict."""
        toml_content = """
[rooms.room1]
broadcast = "192.168.1.255"

[rooms.room1.servers.server1]
os = "Fedora"
mac = "aa:bb:cc:dd:ee:ff"
"""
        path = self._write_toml(toml_content)
        try:
            result = init(path)
        finally:
            os.unlink(path)

        self.assertIsInstance(result, dict)
        self.assertIn("rooms", result)
        self.assertIn("room1", result["rooms"])
        self.assertEqual(result["rooms"]["room1"]["broadcast"], "192.168.1.255")

    def test_init_returns_nested_structure(self):
        """init() should preserve the nested structure of the TOML file."""
        toml_content = """
[rooms.workshop]
broadcast = "192.168.1.255"

[rooms.workshop.servers.laptop]
os = "macOS"
mac = "11:22:33:44:55:66"
"""
        path = self._write_toml(toml_content)
        try:
            result = init(path)
        finally:
            os.unlink(path)

        self.assertEqual(
            result["rooms"]["workshop"]["servers"]["laptop"]["os"], "macOS"
        )
        self.assertEqual(
            result["rooms"]["workshop"]["servers"]["laptop"]["mac"],
            "11:22:33:44:55:66",
        )

    def test_init_with_multiple_rooms(self):
        """init() should handle TOML with multiple rooms."""
        toml_content = """
[rooms.room1]
broadcast = "10.0.0.255"

[rooms.room1.servers.server1]
mac = "aa:bb:cc:dd:ee:ff"
os = "Fedora"

[rooms.room2]
broadcast = "10.0.1.255"

[rooms.room2.servers.server2]
mac = "11:22:33:44:55:66"
os = "macOS"
"""
        path = self._write_toml(toml_content)
        try:
            result = init(path)
        finally:
            os.unlink(path)

        self.assertIn("room1", result["rooms"])
        self.assertIn("room2", result["rooms"])
        self.assertEqual(result["rooms"]["room1"]["broadcast"], "10.0.0.255")
        self.assertEqual(result["rooms"]["room2"]["broadcast"], "10.0.1.255")


class TestValidateConfig(unittest.TestCase):
    """Tests for the validate_config() function."""

    def test_valid_config_passes(self):
        """validate_config should not raise for a valid config."""
        config = {
            "rooms": {
                "room1": {
                    "broadcast": "192.168.1.255",
                    "servers": {
                        "server1": {"mac": "aa:bb:cc:dd:ee:ff", "os": "Fedora"}
                    },
                }
            }
        }
        # Should not raise
        validate_config(config)

    def test_missing_rooms_raises(self):
        """validate_config should raise ValueError when 'rooms' is missing."""
        config = {"other": "data"}
        with self.assertRaises(ValueError) as context:
            validate_config(config)
        self.assertIn("rooms", str(context.exception))

    def test_missing_broadcast_raises(self):
        """validate_config should raise ValueError when 'broadcast' is missing."""
        config = {
            "rooms": {
                "room1": {
                    "servers": {
                        "server1": {"mac": "aa:bb:cc:dd:ee:ff", "os": "Fedora"}
                    },
                }
            }
        }
        with self.assertRaises(ValueError) as context:
            validate_config(config)
        self.assertIn("broadcast", str(context.exception))

    def test_missing_servers_raises(self):
        """validate_config should raise ValueError when 'servers' is missing."""
        config = {
            "rooms": {
                "room1": {
                    "broadcast": "192.168.1.255",
                }
            }
        }
        with self.assertRaises(ValueError) as context:
            validate_config(config)
        self.assertIn("servers", str(context.exception))

    def test_missing_server_mac_raises(self):
        """validate_config should raise ValueError when server 'mac' is missing."""
        config = {
            "rooms": {
                "room1": {
                    "broadcast": "192.168.1.255",
                    "servers": {
                        "server1": {"os": "Fedora"}
                    },
                }
            }
        }
        with self.assertRaises(ValueError) as context:
            validate_config(config)
        self.assertIn("mac", str(context.exception))

    def test_missing_server_os_raises(self):
        """validate_config should raise ValueError when server 'os' is missing."""
        config = {
            "rooms": {
                "room1": {
                    "broadcast": "192.168.1.255",
                    "servers": {
                        "server1": {"mac": "aa:bb:cc:dd:ee:ff"}
                    },
                }
            }
        }
        with self.assertRaises(ValueError) as context:
            validate_config(config)
        self.assertIn("os", str(context.exception))

    def test_init_validates_config_on_load(self):
        """init() should call validate_config and raise on invalid TOML."""
        toml_content = """
[rooms.room1]
broadcast = "192.168.1.255"
"""
        # Missing 'servers' key — should raise ValueError
        fd, path = tempfile.mkstemp(suffix=".toml")
        with os.fdopen(fd, "w") as f:
            f.write(toml_content)
        try:
            with self.assertRaises(ValueError):
                init(path)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
