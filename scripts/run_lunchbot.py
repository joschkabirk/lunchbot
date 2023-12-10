import logging
import os
from subprocess import run  # nosec
from urllib import request  # nosec

import yaml

from lunchbot.alsterfood_scraping import fetch_lunch_menu
from lunchbot.description_generation import get_food_description
from lunchbot.image_generation import generate_hash, generate_image
from lunchbot.mattermost_posting import send_message

DEBUG = True
ALSTERFOOD_WEBSITE_URL = os.getenv("ALSTERFOOD_WEBSITE_URL")
MATTERMOST_WEBHOOK_URL = os.getenv("MATTERMOST_WEBHOOK_URL")
IMAGE_CLOUD_UPLOAD_URL = os.getenv("IMAGE_CLOUD_UPLOAD_URL")
IMAGE_CLOUD_UPLOAD_TOKEN = os.getenv("IMAGE_CLOUD_UPLOAD_TOKEN")
IMAGE_CLOUD_DOWNLOAD_URL = os.getenv("IMAGE_CLOUD_DOWNLOAD_URL")


# TODO: add username as .env variable
# TODO: make logging colored?

debug_variables = yaml.safe_load(open("debug_variables.yml"))

logger = logging.getLogger("lunchbot")

# Create a formatter that includes the time, log level, and message
formatter = logging.Formatter("[%(asctime)s] - %(levelname)s - %(message)s")

# Create a handler that outputs to the console, and set its formatter
handler = logging.StreamHandler()
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

# Set the log level
logger.setLevel(logging.DEBUG)


def main():
    # -------------------------------------------------------------------------
    # Get the list of meals and prices
    # ---
    if DEBUG:
        list_of_meals = debug_variables["debug_list_of_meals"]
    else:
        list_of_meals, list_of_prices = fetch_lunch_menu(ALSTERFOOD_WEBSITE_URL)

    logger.info("The following meals were found:")
    for i, meal in enumerate(list_of_meals):
        logger.info(f"  {i+1})  {meal}")

    # -------------------------------------------------------------------------
    # Generate images for the meals
    # ---
    if DEBUG:
        images = debug_variables["debug_list_of_images"]
    else:
        images = []
        # Generate an image with DALL-E based on the menu entries
        for menu_entry in list_of_meals:
            generated_image_url = generate_image(prompt=menu_entry)
            images.append(generated_image_url)
            # log the URL of the generated image
            logger.debug(f"Generated Image URL: {generated_image_url}")

    images_cloud_urls = []

    for image_url in images:
        # generate a unique hash for the image
        image_hash = generate_hash(image_url)
        # download the image from the openAI url and save in images/image_hash.png
        # (openAI urls are only valid for one hour)
        # command = f"curl --output images/asdf{i}.png {image_url}"
        request.urlretrieve(image_url, f"images/{image_hash}.png")  # nosec
        # upload the image to the cloud (where it will be available for unlimited
        # time / until we delete it, but we don't have to worry about the
        # image expiring after a short time)
        upload_command = [
            "curl",
            "-u",
            f"'{IMAGE_CLOUD_UPLOAD_TOKEN}'",
            "-T",
            f"images/{image_hash}.png",
            f"{IMAGE_CLOUD_UPLOAD_URL}{image_hash}.png",
        ]
        upload_command = " ".join(upload_command)
        run(upload_command, shell=True)  # nosec
        # log the URL of the generated image and its hash
        logger.debug(f"Generated Image URL: {image_url}, Hash: {image_hash}")

        images_cloud_urls.append(f"{IMAGE_CLOUD_DOWNLOAD_URL}{image_hash}.png")

    # -------------------------------------------------------------------------
    # Generate the description for each meal
    # ---
    if DEBUG:
        descriptions = debug_variables["debug_list_of_descriptions"]
    else:
        descriptions = []
        for menu_entry in list_of_meals:
            descriptions.append(get_food_description(menu_entry, verbose=True))

    # -------------------------------------------------------------------------
    # Put the message together and send to Mattermost
    # ---

    prefix = f"For today, we have the following meals ({ALSTERFOOD_WEBSITE_URL}):"

    # Generate markdown table
    table = "| Preview | Meal | Description | \n| --- | --- | --- |\n"
    for meal, desc, img_url in zip(list_of_meals, descriptions, images_cloud_urls):
        table += f"| ![preview]({img_url}) | **{meal}**  | {desc}| \n"

    message = prefix + "\n\n" + table

    logger.info("Posting the following message on Mattermost:")
    logger.info(message)

    send_message(
        url=MATTERMOST_WEBHOOK_URL,
        message=message,
        username="Lunchbot (always hungry)",
    )


if __name__ == "__main__":
    main()
