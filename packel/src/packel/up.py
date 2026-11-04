import logging

import fabric

from packel import constants

logger = logging.getLogger(__name__)


def get_connection(host: str, password: str) -> fabric.Connection:
    """Create a Fabric Connection to the given host."""
    return fabric.Connection(
        host,
        user=constants.USERNAME,
        connect_kwargs={"password": password},
    )


def remote_sudo(host: str, password: str, command: str) -> fabric.Result | None:
    """Run a command with sudo on a remote host, without exposing the password on the command line."""
    connection = get_connection(host, password)
    try:
        result = connection.sudo(command)
        return result
    except Exception as e:
        logger.error("Error connecting to %s: %s", host, e)
        return None


class Update:
    def __init__(self, host: str, password: str, os: str) -> None:
        self.host = host
        self.password = password
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
            self.password,
            "dnf upgrade --assumeyes --refresh",
        )

    def needs_restarting(self) -> None:
        remote_sudo(
            self.host,
            self.password,
            "dnf needs-restarting",
        )


class MacOSUpdate(Update):
    def core(self) -> None:
        remote_sudo(
            self.host,
            self.password,
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
