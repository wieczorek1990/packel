import sys

from updates.servers import init


def main():
	if len(sys.argv) != 2:
		print("Usage:\tservers.py servers.toml")
		sys.exit(1)

	print("Starting reading requested...")

	filename = sys.argv[1]
	init(filename)

	print("Done.")
