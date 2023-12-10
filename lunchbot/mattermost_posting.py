import requests


def send_message(
    url: str,
    message: str,
    username: str = "Lunchbot (always hungry)",
):
    """Send a message via a webhook."""
    r = requests.post(
        url,
        json={
            "username": username,
            "text": message,
        },
    )
    assert r.status_code == 200
    return r
