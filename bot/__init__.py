from pyrogram import Client

app: Client | None = None


def get_app() -> Client:
    global app
    if app is None:
        raise RuntimeError("Bot client not initialized")
    return app


def set_app(client: Client) -> None:
    global app
    app = client
