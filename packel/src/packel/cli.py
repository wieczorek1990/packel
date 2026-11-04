import logging
import sys

from packel.servers import init, process

logger = logging.getLogger(__name__)


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage:\tpackel data/servers.toml")
        sys.exit(1)

    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s")
    logger.info("Starting reading requested...")

    filename = sys.argv[1]
    data = init(filename)
    process(data)

    logger.info("Done.")
