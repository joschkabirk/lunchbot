import logging
import os
from subprocess import run  # nosec
from urllib import request  # nosec

from lunchbot.alsterfood_scraping import fetch_lunch_menu
from lunchbot.description_generation import get_food_description
from lunchbot.image_generation import generate_hash, generate_image
from lunchbot.mattermost_posting import send_message

ALSTERFOOD_WEBSITE_URL = os.getenv("ALSTERFOOD_WEBSITE_URL")
MATTERMOST_WEBHOOK_URL = os.getenv("MATTERMOST_WEBHOOK_URL")
IMAGE_CLOUD_UPLOAD_URL = os.getenv("IMAGE_CLOUD_UPLOAD_URL")
IMAGE_CLOUD_UPLOAD_TOKEN = os.getenv("IMAGE_CLOUD_UPLOAD_TOKEN")
IMAGE_CLOUD_DOWNLOAD_URL = os.getenv("IMAGE_CLOUD_DOWNLOAD_URL")


# TODO: add username as .env variable
# TODO: make logging colored?
# TODO: add the context / bot definition to the .env file

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
    # some initial logging
    logger.info(50 * "-")
    logger.info("LUNCHBOT hungry!")
    logger.info("LUNCHBOT will be looking for food now...")
    logger.info(50 * "-")

    # -------------------------------------------------------------------------
    # Get the list of meals and prices
    # ---
    logger.info(
        f"Fetching the lunch menu from Alsterfood... ({ALSTERFOOD_WEBSITE_URL})"
    )
    list_of_meals, list_of_prices = fetch_lunch_menu(ALSTERFOOD_WEBSITE_URL)

    logger.info("The following meals were found:")
    for i, meal in enumerate(list_of_meals):
        logger.info(f"  {i+1})  {meal}")

    # -------------------------------------------------------------------------
    # Generate images for the meals
    # ---
    logger.info(50 * "-")
    logger.info("Generating images for the meals...")

    images = []
    images_cloud_urls = []
    for meal in list_of_meals:
        # generate a unique hash for the image
        image_hash = generate_hash(meal)

        logger.debug(f"Meal: {meal}")
        logger.debug(f"Hash: {image_hash}")

        if os.path.isfile(f"images/{image_hash}.png"):
            # if the image already exists in images/, skip the download
            logger.info(f"Image already exists for meal {meal}")
        else:
            # Generate an image with DALL-E based on the menu entries
            generated_image_url = generate_image(prompt=meal)
            images.append(generated_image_url)
            # log the URL of the generated image
            logger.info(f"Generated Image URL: {generated_image_url}")

            # download the image from the openAI url and save in images/image_hash.png
            # (openAI urls are only valid for one hour)
            # command = f"curl --output images/asdf{i}.png {image_url}"
            request.urlretrieve(
                generated_image_url, f"images/{image_hash}.png"
            )  # nosec

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

        images_cloud_urls.append(f"{IMAGE_CLOUD_DOWNLOAD_URL}{image_hash}.png")

    # -------------------------------------------------------------------------
    # Generate the description for each meal
    # ---
    logger.info(50 * "-")
    logger.info("Generating descriptions for the meals...")

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
