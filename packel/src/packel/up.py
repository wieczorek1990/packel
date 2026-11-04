import logging
from pathlib import Path

import fabric
import invoke.exceptions
import paramiko.ssh_exception

from packel import constants

logger = logging.getLogger(__name__)


def get_connection(host: str, key_passphrase: str, sudo_password: str) -> fabric.Connection:
    """Create a Fabric Connection to the given host using SSH key authentication.

    Args:
        host: The target host IP or hostname.
        key_passphrase: Passphrase to decrypt the local SSH private key.
        sudo_password: Password for sudo commands on the remote host.
    """
    key_path = Path.home() / ".ssh" / "id_ed25519"
    conn = fabric.Connection(
        host,
        user=constants.USERNAME,
        connect_kwargs={
            "key_filename": str(key_path),
            "passphrase": key_passphrase,
        },
    )
    conn.config.update({"sudo": {"password": sudo_password}})
    return conn


def remote_sudo(host: str, key_passphrase: str, sudo_password: str, command: str) -> fabric.Result | None:
    """Run a command with sudo on a remote host, without exposing the password on the command line."""
    connection = get_connection(host, key_passphrase, sudo_password)
    try:
        result = connection.sudo(command)
        return result
    except (
        invoke.exceptions.AuthFailure,
        invoke.exceptions.UnexpectedExit,
        paramiko.ssh_exception.SSHException,
    ) as e:
        logger.error("Error connecting to %s: %s", host, e)
        return None


class Update:
    def __init__(self, host: str, key_passphrase: str, sudo_password: str, os: str) -> None:
        self.host = host
        self.key_passphrase = key_passphrase
        self.sudo_password = sudo_password
        self.os = os

    def core(self) -> None:
        raise NotImplementedError

    def needs_restarting(self) -> None:
        raise NotImplementedError

    def proceed(self) -> None:
        logger.info("Updating...")
        self.core()
        self.needs_restarting()
        logger.info("Done updating.")


class FedoraUpdate(Update):
    def core(self) -> None:
        remote_sudo(
            self.host,
            self.key_passphrase,
            self.sudo_password,
            "dnf upgrade --assumeyes --refresh",
        )

    def needs_restarting(self) -> None:
        remote_sudo(
            self.host,
            self.key_passphrase,
            self.sudo_password,
            "dnf needs-restarting",
        )


class MacOSUpdate(Update):
    def core(self) -> None:
        remote_sudo(
            self.host,
            self.key_passphrase,
            self.sudo_password,
            "softwareupdate --background",
        )

    def needs_restarting(self) -> None:
        pass


class NotSupportedUpdate(Update):
    def core(self) -> None:
        pass

    def needs_restarting(self) -> None:
        pass

    def proceed(self) -> None:
        logger.warning("OS '%s' is not supported — skipping.", self.os)


def get_update_for_os(
    os: str,
) -> type[FedoraUpdate | MacOSUpdate | NotSupportedUpdate]:
    if os == "Fedora":
        update = FedoraUpdate
    elif os == "macOS":
        update = MacOSUpdate
    else:
        update = NotSupportedUpdate
    return update
