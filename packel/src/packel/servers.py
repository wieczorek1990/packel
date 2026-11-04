import getpass
import logging
import subprocess
from typing import Any

import tomllib

from packel import arp, up

logger = logging.getLogger(__name__)


def process(data: dict) -> None:
    password = getpass.getpass("Enter password to the SSH key: ")

    logger.info("Processing servers...")
    for workshop, workshop_data in data["rooms"].items():
        logger.info(f"Processing workshop: {workshop}")

        try:
            broadcast = workshop_data["broadcast"]
        except KeyError:
            logger.warning("No broadcast found.")
            continue

        logger.info("Broadcasting: %s", broadcast)
        subprocess.run(["ping", "-c", "1", broadcast], stdout=subprocess.DEVNULL)

        try:
            servers = workshop_data["servers"]
        except KeyError:
            logger.warning("No servers found.")
            continue

        for server, server_data in servers.items():
            logger.info(f"Processing server: {server}")

            arp_data = arp.get_arp_data()
            arp_result = arp.process_arp_data(arp_data)

            mac = server_data["mac"]
            try:
                host = arp_result[mac]
            except KeyError:
                logger.warning(f"No MAC found: {mac}")
                continue

            os = server_data["os"]
            update_class = up.get_update_for_os(os)

            update = update_class(host, password, os)
            update.proceed()
    logger.info("Finished processing servers...")


def validate_config(data: dict[str, Any]) -> None:
    """Validate the TOML config structure.

    Checks that required keys exist and have the correct types.
    Raises ValueError with a descriptive message on invalid config.
    """
    if "rooms" not in data:
        raise ValueError("Config missing required key: 'rooms'")
    if not isinstance(data["rooms"], dict):
        raise ValueError("'rooms' must be a dictionary")

    for room_name, room_data in data["rooms"].items():
        if not isinstance(room_data, dict):
            raise ValueError(f"Room '{room_name}' must be a dictionary")
        if "broadcast" not in room_data:
            raise ValueError(f"Room '{room_name}' missing required key: 'broadcast'")
        if not isinstance(room_data["broadcast"], str):
            raise ValueError(f"Room '{room_name}' 'broadcast' must be a string")
        if "servers" not in room_data:
            raise ValueError(f"Room '{room_name}' missing required key: 'servers'")
        if not isinstance(room_data["servers"], dict):
            raise ValueError(f"Room '{room_name}' 'servers' must be a dictionary")

        for server_name, server_data in room_data["servers"].items():
            if not isinstance(server_data, dict):
                raise ValueError(f"Server '{server_name}' in room '{room_name}' must be a dictionary")
            if "mac" not in server_data:
                raise ValueError(f"Server '{server_name}' in room '{room_name}' missing required key: 'mac'")
            if not isinstance(server_data["mac"], str):
                raise ValueError(f"Server '{server_name}' in room '{room_name}' 'mac' must be a string")
            if "os" not in server_data:
                raise ValueError(f"Server '{server_name}' in room '{room_name}' missing required key: 'os'")
            if not isinstance(server_data["os"], str):
                raise ValueError(f"Server '{server_name}' in room '{room_name}' 'os' must be a string")


def init(filename: str) -> dict[str, Any]:
    with open(filename, "rb") as file_descriptor:
        data = tomllib.load(file_descriptor)
    validate_config(data)
    return data
