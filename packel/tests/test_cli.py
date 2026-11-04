import unittest
from unittest.mock import patch
import sys

from packel.cli import main


class TestCLIMain(unittest.TestCase):
    """Tests for the CLI main() entry point."""

    def setUp(self) -> None:
        self._original_argv = sys.argv

    def tearDown(self) -> None:
        sys.argv = self._original_argv

    def test_main_exits_with_usage_when_no_args(self):
        """main() should exit with code 1 when no arguments are provided."""
        sys.argv = ["packel"]
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 1)

    def test_main_exits_with_usage_when_too_many_args(self):
        """main() should exit with code 1 when too many arguments are provided."""
        sys.argv = ["packel", "file1.toml", "file2.toml"]
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 1)

    @patch("packel.cli.process")
    @patch("packel.cli.init")
    def test_main_calls_init_and_process(self, mock_init, mock_process):
        """main() should call init() with the filename and then process()."""
        mock_init.return_value = {"rooms": {"room1": {"broadcast": "192.168.1.255"}}}

        sys.argv = ["packel", "data/servers.toml"]
        main()

        mock_init.assert_called_once_with("data/servers.toml")
        mock_process.assert_called_once()

    @patch("packel.cli.process")
    @patch("packel.cli.init")
    def test_main_passes_data_to_process(self, mock_init, mock_process):
        """main() should pass the parsed TOML data to process()."""
        expected_data = {
            "rooms": {
                "room1": {
                    "broadcast": "10.0.0.255",
                    "servers": {"server1": {"os": "Fedora", "mac": "aa:bb:cc"}},
                }
            }
        }
        mock_init.return_value = expected_data

        sys.argv = ["packel", "data/servers.toml"]
        main()

        mock_process.assert_called_once_with(expected_data)


if __name__ == "__main__":
    unittest.main()
