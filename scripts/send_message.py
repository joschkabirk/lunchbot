import logging
import os
from subprocess import run  # nosec
from urllib import request  # nosec

from dotenv import load_dotenv

from lunchbot.mattermost_posting import send_message_via_webhook

message = "test message"


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger("lunchbot")

    load_dotenv()  # take environment variables from .env

    MATTERMOST_WEBHOOK_URL = os.getenv("MATTERMOST_WEBHOOK_URL")
    MATTERMOST_USERNAME = os.getenv("MATTERMOST_USERNAME")

    logger.info(MATTERMOST_USERNAME)
    logger.info(MATTERMOST_WEBHOOK_URL)

    logger.info("Posting the following message on Mattermost:")
    logger.info(message)

    send_message_via_webhook(
        webhook_url=MATTERMOST_WEBHOOK_URL,
        message=message,
        username=MATTERMOST_USERNAME,
    )
    logger.info("Message posted successfully!")


if __name__ == "__main__":
    main()