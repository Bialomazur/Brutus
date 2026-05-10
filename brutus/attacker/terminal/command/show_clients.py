from brutus.attacker.util import CLIENT_HEADER, CLIENT_ROW_TEMPLATE, NO_CLIENTS_TEMPLATE


class ShowClientsCommand:
    def execute(self, window, command: str, context: dict) -> None:
        connections = context.get("connections", {})
        locator = context.get("locator")
        if not connections:
            window.Output.addItem(NO_CLIENTS_TEMPLATE)
            window.Input.clear()
            return

        rows = "\n".join(
            CLIENT_ROW_TEMPLATE.format(
                id=cid,
                addr=conn.addr,
                location=locator.get_location(conn.addr[0]) if locator else "",
            )
            for cid, conn in connections.items()
        )
        window.Output.addItem(f"{CLIENT_HEADER}{rows}")
        window.Input.clear()
