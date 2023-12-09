import os

import requests

MATTERMOST_WEBHOOK_URL = os.getenv("MATTERMOST_WEBHOOK_URL")
ALSTERFOOD_WEBSITE_URL = os.getenv("ALSTERFOOD_WEBSITE_URL")
IMAGE_URL = "https://oaidalleapiprodscus.blob.core.windows.net/private/org-Q9Rj5vhxAlToLRKA1ArxsFPb/user-3wIkLqTRO6pY44iwB89vGS34/img-5Z3RFrZgJwdENFP2Za33DoAl.png?st=2023-12-09T15%3A41%3A53Z&se=2023-12-09T17%3A41%3A53Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-12-08T23%3A13%3A02Z&ske=2023-12-09T23%3A13%3A02Z&sks=b&skv=2021-08-06&sig=bqSjVm52XHAoMzcDEbiqvjd1enrdVSzJewY/Iz6vSE4%3D"


def send_message(
    url: str,
    message: str,
    username: str = "Lunchbot (always hungry)",
):
    """Send a message to a Mattermost channel via a webhook."""
    r = requests.post(
        url,
        json={
            "username": username,
            "text": message,
        },
    )
    assert r.status_code == 200
    return r
