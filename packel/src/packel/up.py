import fabric

from packel import constants


def remote_system(host: str, password: str, commands: str) -> fabric.Result | None:
    connection = fabric.Connection(
        host,
        user=constants.USERNAME,
        connect_kwargs={"password": password},
    )
    result = connection.run(commands)
    return result


class Update:
    def __init__(self, host: str, password: str) -> None:
        self.host = host
        self.password = password

    def core(self) -> None:
        raise NotImplementedError

    def needs_restarting(self) -> None:
        raise NotImplementedError

    def proceed(self) -> None:
        print("Updating...")
        self.core()
        self.needs_restarting()
        print("Done updating.")


class FedoraUpdate(Update):
    def core(self) -> None:
        remote_system(self.host, self.password, f"""echo {self.password} | sudo -S dnf upgrade --assumeyes --refresh""")

    def needs_restarting(self) -> None:
        remote_system(self.host, self.password, f"""echo {self.password} | sudo -S dnf needs-restarting""")


class MacOSUpdate(Update):
    def core(self) -> None:
        remote_system(self.host, self.password, f"""echo {self.password} | sudo -S softwareupdate --background""")

    def needs_restarting(self) -> None:
        pass


class NotSupportedUpdate(Update):
    def core(self) -> None:
        pass

    def needs_restarting(self) -> None:
        pass

    def proceed(self) -> None:
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
