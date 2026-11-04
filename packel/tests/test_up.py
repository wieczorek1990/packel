import unittest
from unittest.mock import MagicMock, patch

from packel.up import (
    FedoraUpdate,
    MacOSUpdate,
    NotSupportedUpdate,
    Update,
    get_connection,
    get_update_for_os,
    remote_sudo,
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


class TestGetConnection(unittest.TestCase):
    """Tests for the get_connection() function."""

    @patch("packel.up.fabric.Connection")
    def test_get_connection_creates_connection(self, mock_connection_class):
        """get_connection should create a fabric Connection with SSH key auth and sudo password."""
        with patch("packel.up.Path.home") as mock_home:
            from pathlib import Path as RealPath

            mock_home.return_value = RealPath("/home/user")

            get_connection("192.168.1.1", "key_pass", "sudo_pass")

            mock_connection_class.assert_called_once_with(
                "192.168.1.1",
                user="administrator",
                connect_kwargs={
                    "key_filename": "/home/user/.ssh/id_ed25519",
                    "passphrase": "key_pass",
                },
            )


class TestRemoteSudo(unittest.TestCase):
    """Tests for the remote_sudo() function."""

    @patch("packel.up.get_connection")
    def test_remote_sudo_runs_sudo_command(self, mock_get_connection):
        """remote_sudo should run commands via connection.sudo()."""
        mock_connection = MagicMock()
        mock_get_connection.return_value = mock_connection
        mock_result = MagicMock()
        mock_connection.sudo.return_value = mock_result

        result = remote_sudo("192.168.1.1", "key_pass", "sudo_pass", "dnf upgrade")

        mock_get_connection.assert_called_once_with(
            "192.168.1.1", "key_pass", "sudo_pass"
        )
        mock_connection.sudo.assert_called_once_with("dnf upgrade")
        self.assertEqual(result, mock_result)

    @patch("packel.up.get_connection")
    def test_remote_sudo_handles_connection_error(self, mock_get_connection):
        """remote_sudo should return None on connection errors."""
        import paramiko.ssh_exception

        mock_connection = MagicMock()
        mock_get_connection.return_value = mock_connection
        mock_connection.sudo.side_effect = paramiko.ssh_exception.SSHException(
            "Connection refused"
        )

        result = remote_sudo("192.168.1.1", "key_pass", "sudo_pass", "dnf upgrade")

        self.assertIsNone(result)

    @patch("packel.up.get_connection")
    def test_remote_sudo_command_no_password_injection(self, mock_get_connection):
        """remote_sudo should not embed the password in the command string."""
        mock_connection = MagicMock()
        mock_get_connection.return_value = mock_connection
        mock_connection.sudo.return_value = MagicMock()

        # Even if the command contains special characters, it should be passed as-is
        remote_sudo("192.168.1.1", "key_pass", "p@$$w0rd!", "dnf upgrade")

        mock_connection.sudo.assert_called_once_with("dnf upgrade")


class TestFedoraUpdate(unittest.TestCase):
    """Tests for the FedoraUpdate class."""

    @patch("packel.up.remote_sudo")
    def test_fedora_update_core_runs_dnf(self, mock_remote):
        """FedoraUpdate.core should run dnf upgrade command via sudo."""
        update = FedoraUpdate("192.168.1.1", "key_pass", "sudo_pass", "Fedora")
        update.core()

        mock_remote.assert_called_once()
        call_args = mock_remote.call_args[0]
        self.assertEqual(call_args[0], "192.168.1.1")
        self.assertEqual(call_args[1], "key_pass")
        self.assertEqual(call_args[2], "sudo_pass")
        # Command should NOT contain the password
        self.assertEqual(call_args[3], "dnf upgrade --assumeyes --refresh")
        self.assertNotIn("key_pass", call_args[3])

    @patch("packel.up.remote_sudo")
    def test_fedora_update_needs_restarting(self, mock_remote):
        """FedoraUpdate.needs_restarting should check for restarts via sudo."""
        update = FedoraUpdate("192.168.1.1", "key_pass", "sudo_pass", "Fedora")
        update.needs_restarting()

        mock_remote.assert_called_once()
        call_args = mock_remote.call_args[0]
        self.assertEqual(call_args[3], "dnf needs-restarting")


class TestMacOSUpdate(unittest.TestCase):
    """Tests for the MacOSUpdate class."""

    @patch("packel.up.remote_sudo")
    def test_macos_update_core_runs_softwareupdate(self, mock_remote):
        """MacOSUpdate.core should run softwareupdate command via sudo."""
        update = MacOSUpdate("192.168.1.1", "key_pass", "sudo_pass", "macOS")
        update.core()

        mock_remote.assert_called_once()
        call_args = mock_remote.call_args[0]
        self.assertEqual(call_args[3], "softwareupdate --background")

    def test_macos_update_needs_restarting_is_noop(self):
        """MacOSUpdate.needs_restarting should do nothing."""
        update = MacOSUpdate("192.168.1.1", "key_pass", "sudo_pass", "macOS")
        # Should not raise
        update.needs_restarting()


class TestNotSupportedUpdate(unittest.TestCase):
    """Tests for the NotSupportedUpdate class."""

    @patch("packel.up.logger")
    def test_not_supported_proceed_logs_warning(self, mock_logger):
        """NotSupportedUpdate.proceed should log a skip warning."""
        update = NotSupportedUpdate("192.168.1.1", "key_pass", "sudo_pass", "Ubuntu")

        update.proceed()
        mock_logger.warning.assert_called_once_with(
            "OS '%s' is not supported — skipping.", "Ubuntu"
        )

    def test_not_supported_core_is_noop(self):
        """NotSupportedUpdate.core should do nothing."""
        update = NotSupportedUpdate("192.168.1.1", "key_pass", "sudo_pass", "Ubuntu")
        update.core()  # Should not raise

    def test_not_supported_needs_restarting_is_noop(self):
        """NotSupportedUpdate.needs_restarting should do nothing."""
        update = NotSupportedUpdate("192.168.1.1", "key_pass", "sudo_pass", "Ubuntu")
        update.needs_restarting()  # Should not raise


class TestUpdateBase(unittest.TestCase):
    """Tests for the base Update class."""

    def test_update_initialization(self):
        """Update should store host, key_passphrase, sudo_password, and os."""
        update = Update("192.168.1.1", "key_pass", "sudo_pass", "Fedora")
        self.assertEqual(update.host, "192.168.1.1")
        self.assertEqual(update.key_passphrase, "key_pass")
        self.assertEqual(update.sudo_password, "sudo_pass")
        self.assertEqual(update.os, "Fedora")

    def test_update_core_raises_not_implemented(self):
        """Base Update.core should raise NotImplementedError."""
        update = Update("192.168.1.1", "key_pass", "sudo_pass", "Fedora")
        with self.assertRaises(NotImplementedError):
            update.core()

    def test_update_needs_restarting_raises_not_implemented(self):
        """Base Update.needs_restarting should raise NotImplementedError."""
        update = Update("192.168.1.1", "key_pass", "sudo_pass", "Fedora")
        with self.assertRaises(NotImplementedError):
            update.needs_restarting()


if __name__ == "__main__":
    unittest.main()
