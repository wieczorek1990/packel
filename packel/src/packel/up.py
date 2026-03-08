class Update:
    def __init__(self, arp_result: dict) -> None:
        pass

    @staticmethod
    def core() -> None:
        pass

    @classmethod
    def proceed(cls) -> None:
        print("Updating...")
        cls.core()
        print("Done updating.")


class FedoraUpdate(Update):
    pass


class MacOSUpdate(Update):
    pass


class NotSupportedUpdate(Update):
    pass


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
