"""Send a message to a Mattermost channel via a webhook."""
import requests


def send_message_via_webhook(
    webhook_url: str,
    message: str,
    username: str = "Lunchbot",
    timeout: int = 20,
):
    """Send a message via a webhook.

    Parameters
    ----------
    webhook_url : str
        The URL of the webhook to send the message to.
    message : str
        The message to send.
    username : str, optional
        The username to use for the message, by default "Lunchbot".
    timeout : int, optional
        The timeout in seconds for the request, by default 20.
    """
    r = requests.post(
        webhook_url,
        json={
            "username": username,
            "text": message,
        },
        timeout=timeout,
    )
    assert r.status_code == 200
    return r
