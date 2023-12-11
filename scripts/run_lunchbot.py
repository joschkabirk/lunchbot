import os
from subprocess import run  # nosec
from urllib import request  # nosec

from dotenv import load_dotenv

from lunchbot.alsterfood_scraping import fetch_todays_lunch_menu
from lunchbot.description_generation import get_food_description
from lunchbot.image_generation import generate_hash, generate_image
from lunchbot.mattermost_posting import send_message
from lunchbot.utils import get_logger

load_dotenv()  # take environment variables from .env

ALSTERFOOD_WEBSITE_URL = os.getenv("ALSTERFOOD_WEBSITE_URL")
MATTERMOST_WEBHOOK_URL = os.getenv("MATTERMOST_WEBHOOK_URL")
IMAGE_CLOUD_UPLOAD_URL = os.getenv("IMAGE_CLOUD_UPLOAD_URL")
IMAGE_CLOUD_UPLOAD_TOKEN = os.getenv("IMAGE_CLOUD_UPLOAD_TOKEN")
IMAGE_CLOUD_DOWNLOAD_URL = os.getenv("IMAGE_CLOUD_DOWNLOAD_URL")
MESSAGE_PREFIX = os.getenv("MESSAGE_PREFIX")
MESSAGE_SUFFIX = os.getenv("MESSAGE_SUFFIX")
MATTERMOST_USERNAME = os.getenv("MATTERMOST_USERNAME")
SYSTEM_CONTENT = os.getenv("SYSTEM_CONTENT")
DESCRIPTION_SUFFIX = os.getenv("DESCRIPTION_SUFFIX")

if DESCRIPTION_SUFFIX is None:
    DESCRIPTION_SUFFIX = ""


logger = get_logger("lunchbot")


def main():
    # some initial logging
    logger.info(50 * "-")
    logger.info("LUNCHBOT hungry!")
    logger.info("LUNCHBOT will be looking for food now...")
    logger.info(50 * "-")

    # create the images/ directory if it doesn't exist
    os.makedirs("images", exist_ok=True)

    # -------------------------------------------------------------------------
    # Get the list of meals and prices
    # ---
    logger.info(
        f"Fetching the lunch menu from Alsterfood... ({ALSTERFOOD_WEBSITE_URL})"
    )
    list_of_dishes = fetch_todays_lunch_menu(ALSTERFOOD_WEBSITE_URL)

    logger.info("The following dishes were found:")
    for i, dish_name in enumerate(list_of_dishes):
        logger.info(f"  {i+1})  {dish_name}")

    # -------------------------------------------------------------------------
    # Generate images and descriptions for the meals
    # ---
    logger.info(50 * "-")
    logger.info("Generating images for the meals...")

    for dish in list_of_dishes:
        dish_name = dish["name"]
        # generate a unique hash for the image
        meal_hash = generate_hash(dish_name)

        logger.debug(f"Meal: {dish_name}")
        logger.debug(f"Hash: {meal_hash}")

        # --------------------------------------------------------------------
        # Generate the image for the meal

        if os.path.isfile(f"images/{meal_hash}.png"):
            # if the image already exists in images/, skip the download
            logger.info(f"Image already exists for meal '{dish_name}'")
        else:
            # Generate an image with DALL-E based on the menu entries
            generated_image_url = generate_image(prompt=dish_name)
            # log the URL of the generated image
            logger.info(f"Generated Image URL: {generated_image_url}")

            # download the image from the openAI url and save in images/image_hash.png
            # (openAI urls are only valid for one hour)
            # command = f"curl --output images/asdf{i}.png {image_url}"
            request.urlretrieve(generated_image_url, f"images/{meal_hash}.png")  # nosec

        # upload the image to the cloud (where it will be available for unlimited
        # time / until we delete it, but we don't have to worry about the
        # image expiring after a short time)
        upload_command = [
            "curl",
            "-u",
            f"'{IMAGE_CLOUD_UPLOAD_TOKEN}'",
            "-T",
            f"images/{meal_hash}.png",
            f"{IMAGE_CLOUD_UPLOAD_URL}{meal_hash}.png",
        ]
        upload_command = " ".join(upload_command)
        run(upload_command, shell=True)  # nosec

        dish["image_url"] = f"{IMAGE_CLOUD_DOWNLOAD_URL}{meal_hash}.png"

        # -------------------------------------------------------------------------
        # Generate the description
        # ---
        # check if images/<hash>.txt exists, if yes, skip the description generation
        # and just read the description from the file
        if os.path.isfile(f"images/{meal_hash}.txt"):
            logger.info(f"Description already exists for meal '{dish_name}'")
            with open(f"images/{meal_hash}.txt") as f:
                description = f.read()
        else:
            logger.info(f"Generating description for meal {dish_name}")
            description = get_food_description(
                meal_name=dish_name,
                system_content=SYSTEM_CONTENT,
            )
            with open(f"images/{meal_hash}.txt", "w") as f:
                f.write(description)
        dish["description"] = description

    # -------------------------------------------------------------------------
    # Put the message together and send to Mattermost
    # ---

    # Generate markdown table
    table = (
        f"| Preview | Price | Info | Meal | Description {DESCRIPTION_SUFFIX}| "
        "\n| --- | --- | --- | --- | --- |\n"
    )
    for dish in list_of_dishes:
        table += (
            f"| ![preview]({dish['image_url']}) "
            f"| {dish['price']} "
            f"| {dish['info']} "
            f"| **{dish['name']}**  "
            f"| {dish['description']}| \n"
        )

    message = MESSAGE_PREFIX + "\n" + table + "\n" + MESSAGE_SUFFIX

    logger.info("Posting the following message on Mattermost:")
    logger.info(message)

    send_message(
        url=MATTERMOST_WEBHOOK_URL,
        message=message,
        username=MATTERMOST_USERNAME,
    )
    logger.info("Message posted successfully!")


if __name__ == "__main__":
    main()
