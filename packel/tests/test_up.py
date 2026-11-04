import unittest
from unittest.mock import patch, MagicMock

from packel.up import (
    get_update_for_os,
    Update,
    FedoraUpdate,
    MacOSUpdate,
    NotSupportedUpdate,
    remote_system,
)


class TestGetUpdateForOS(unittest.TestCase):
    """Tests for the get_update_for_os() factory function."""

    def test_fedora_returns_fedora_update(self):
        """Fedora OS should return FedoraUpdate class."""
        result = get_update_for_os("Fedora")
        self.assertEqual(result, FedoraUpdate)

    def test_macos_returns_macos_update(self):
        """macOS should return MacOSUpdate class."""
        result = get_update_for_os("macOS")
        self.assertEqual(result, MacOSUpdate)

    def test_unknown_os_returns_not_supported(self):
        """Unknown OS should return NotSupportedUpdate class."""
        result = get_update_for_os("Ubuntu")
        self.assertEqual(result, NotSupportedUpdate)

    def test_empty_string_returns_not_supported(self):
        """Empty string OS should return NotSupportedUpdate class."""
        result = get_update_for_os("")
        self.assertEqual(result, NotSupportedUpdate)

    def test_case_sensitive_matching(self):
        """OS matching should be case-sensitive."""
        # "fedora" (lowercase) should not match "Fedora"
        result = get_update_for_os("fedora")
        self.assertEqual(result, NotSupportedUpdate)

        # "MACOS" should not match "macOS"
        result = get_update_for_os("MACOS")
        self.assertEqual(result, NotSupportedUpdate)


class TestRemoteSystem(unittest.TestCase):
    """Tests for the remote_system() function."""

    @patch("packel.up.fabric.Connection")
    def test_remote_system_runs_command(self, mock_connection_class):
        """remote_system should run commands via fabric Connection."""
        mock_connection = MagicMock()
        mock_connection_class.return_value = mock_connection
        mock_result = MagicMock()
        mock_connection.run.return_value = mock_result

        result = remote_system("192.168.1.1", "password", "dnf upgrade")

        mock_connection_class.assert_called_once_with(
            "192.168.1.1",
            user="administrator",
            connect_kwargs={"password": "password"},
        )
        mock_connection.run.assert_called_once_with("dnf upgrade")
        self.assertEqual(result, mock_result)

    @patch("packel.up.fabric.Connection")
    def test_remote_system_handles_connection_error(self, mock_connection_class):
        """remote_system should return None on connection errors."""
        mock_connection = MagicMock()
        mock_connection_class.return_value = mock_connection
        mock_connection.run.side_effect = Exception("Connection refused")

        result = remote_system("192.168.1.1", "password", "dnf upgrade")

        self.assertIsNone(result)


class TestFedoraUpdate(unittest.TestCase):
    """Tests for the FedoraUpdate class."""

    @patch("packel.up.remote_system")
    def test_fedora_update_core_runs_dnf(self, mock_remote):
        """FedoraUpdate.core should run dnf upgrade command."""
        update = FedoraUpdate("192.168.1.1", "secret", "Fedora")
        update.core()

        mock_remote.assert_called_once()
        call_args = mock_remote.call_args[0]
        self.assertEqual(call_args[0], "192.168.1.1")
        self.assertEqual(call_args[1], "secret")
        self.assertIn("dnf upgrade", call_args[2])

    @patch("packel.up.remote_system")
    def test_fedora_update_needs_restarting(self, mock_remote):
        """FedoraUpdate.needs_restarting should check for restarts."""
        update = FedoraUpdate("192.168.1.1", "secret", "Fedora")
        update.needs_restarting()

        mock_remote.assert_called_once()
        call_args = mock_remote.call_args[0]
        self.assertIn("needs-restarting", call_args[2])


class TestMacOSUpdate(unittest.TestCase):
    """Tests for the MacOSUpdate class."""

    @patch("packel.up.remote_system")
    def test_macos_update_core_runs_softwareupdate(self, mock_remote):
        """MacOSUpdate.core should run softwareupdate command."""
        update = MacOSUpdate("192.168.1.1", "secret", "macOS")
        update.core()

        mock_remote.assert_called_once()
        call_args = mock_remote.call_args[0]
        self.assertIn("softwareupdate", call_args[2])

    def test_macos_update_needs_restarting_is_noop(self):
        """MacOSUpdate.needs_restarting should do nothing."""
        update = MacOSUpdate("192.168.1.1", "secret", "macOS")
        # Should not raise
        update.needs_restarting()


class TestNotSupportedUpdate(unittest.TestCase):
    """Tests for the NotSupportedUpdate class."""

    def test_not_supported_proceed_prints_warning(self):
        """NotSupportedUpdate.proceed should print a skip message."""
        update = NotSupportedUpdate("192.168.1.1", "secret", "Ubuntu")

        with patch("packel.up.print") as mock_print:
            update.proceed()
            mock_print.assert_called_once_with(
                "OS 'Ubuntu' is not supported — skipping."
            )

    def test_not_supported_core_is_noop(self):
        """NotSupportedUpdate.core should do nothing."""
        update = NotSupportedUpdate("192.168.1.1", "secret", "Ubuntu")
        update.core()  # Should not raise

    def test_not_supported_needs_restarting_is_noop(self):
        """NotSupportedUpdate.needs_restarting should do nothing."""
        update = NotSupportedUpdate("192.168.1.1", "secret", "Ubuntu")
        update.needs_restarting()  # Should not raise


class TestUpdateBase(unittest.TestCase):
    """Tests for the base Update class."""

    def test_update_initialization(self):
        """Update should store host, password, and os."""
        update = Update("192.168.1.1", "secret", "Fedora")
        self.assertEqual(update.host, "192.168.1.1")
        self.assertEqual(update.password, "secret")
        self.assertEqual(update.os, "Fedora")

    def test_update_core_raises_not_implemented(self):
        """Base Update.core should raise NotImplementedError."""
        update = Update("192.168.1.1", "secret", "Fedora")
        with self.assertRaises(NotImplementedError):
            update.core()

    def test_update_needs_restarting_raises_not_implemented(self):
        """Base Update.needs_restarting should raise NotImplementedError."""
        update = Update("192.168.1.1", "secret", "Fedora")
        with self.assertRaises(NotImplementedError):
            update.needs_restarting()


if __name__ == "__main__":
    unittest.main()
