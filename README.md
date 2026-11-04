packel
======

Generic packages updater for modern operating systems.
Given a TOML config of servers grouped by rooms, `packel` resolves their IPs via ARP and SSHes in to run OS-specific update commands.

## Simple validation

```
./bin/validate.py data/servers.toml | less -R
```

## Installation

Install the package in editable mode from the project root:

    pip install -e .

This makes the `packel` command available on your `PATH`.

## Usage

Run `packel` with a path to a TOML configuration file:

    packel data/servers.toml

You will be prompted for the SSH password. The tool will then:

1. Ping each room's broadcast address to populate the ARP cache.
2. Look up each server's IP from its MAC address.
3. SSH into each server and run the appropriate update command.

## Configuration Format

The config file is a TOML document with rooms, each containing a broadcast address and a list of servers:

```toml
[rooms.office]
broadcast = "192.168.1.255"

[rooms.office.servers.desktop1]
mac = "aa:bb:cc:dd:ee:ff"
os = "Fedora"

[rooms.office.servers.laptop1]
mac = "11:22:33:44:55:66"
os = "macOS"
```

Each server requires:
- **`mac`** — the MAC address used to look up the IP via ARP.
- **`os`** — the operating system (`Fedora` or `macOS`).

## Supported OS

| OS | Update Command | Restart Check |
|---|---|---|
| Fedora | `dnf upgrade --assumeyes --refresh` | `dnf needs-restarting` |
| macOS | `softwareupdate --background` | (none) |

Servers with an unrecognized `os` value are skipped with a warning.

## Testing

Run the full test suite from the project root:

    bin/test.sh
