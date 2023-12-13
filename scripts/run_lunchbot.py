import logging
import os
from subprocess import run  # nosec
from urllib import request  # nosec

from dotenv import load_dotenv

from lunchbot.alsterfood_scraping import fetch_todays_lunch_menu
from lunchbot.description_generation import get_food_description
from lunchbot.image_generation import generate_hash, generate_image
from lunchbot.mattermost_posting import send_message_via_webhook


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    load_dotenv()  # take environment variables from .env

    ALSTERFOOD_WEBSITE_URL = os.getenv("ALSTERFOOD_WEBSITE_URL")
    MATTERMOST_WEBHOOK_URL = os.getenv("MATTERMOST_WEBHOOK_URL")
    USE_OPENAI_IMAGE_URL = os.getenv("USE_OPENAI_IMAGE_URL")
    IMAGE_CLOUD_UPLOAD_URL = os.getenv("IMAGE_CLOUD_UPLOAD_URL")
    IMAGE_CLOUD_UPLOAD_TOKEN = os.getenv("IMAGE_CLOUD_UPLOAD_TOKEN")
    IMAGE_CLOUD_DOWNLOAD_URL = os.getenv("IMAGE_CLOUD_DOWNLOAD_URL")
    MESSAGE_PREFIX = os.getenv("MESSAGE_PREFIX")
    MESSAGE_SUFFIX = os.getenv("MESSAGE_SUFFIX")
    MATTERMOST_USERNAME = os.getenv("MATTERMOST_USERNAME")
    SYSTEM_CONTENT = os.getenv("SYSTEM_CONTENT")
    DESCRIPTION_SUFFIX = os.getenv("DESCRIPTION_SUFFIX")

    logger = logging.getLogger("lunchbot")

    # some initial logging
    logger.info(50 * "-")
    logger.info("LUNCHBOT hungry!")
    logger.info("LUNCHBOT will be looking for food now...")
    logger.info(50 * "-")

    # -------------------------------------------------------------------------
    # input validation
    if ALSTERFOOD_WEBSITE_URL is None:
        raise ValueError("ALSTERFOOD_WEBSITE_URL is not set")
    if MATTERMOST_WEBHOOK_URL is None:
        raise ValueError("MATTERMOST_WEBHOOK_URL is not set")
    if USE_OPENAI_IMAGE_URL == "true":
        logger.warning("Using OpenAI image URL (will expire after 1 hour)")
        logger.info("IMAGE_CLOUD_UPLOAD_URL will be ignored")
        logger.info("IMAGE_CLOUD_UPLOAD_TOKEN will be ignored")
        logger.info("IMAGE_CLOUD_DOWNLOAD_URL will be ignored")
    else:
        if IMAGE_CLOUD_UPLOAD_URL is None:
            raise ValueError("IMAGE_CLOUD_UPLOAD_URL is not set")
        if IMAGE_CLOUD_UPLOAD_TOKEN is None:
            raise ValueError("IMAGE_CLOUD_UPLOAD_TOKEN is not set")
        if IMAGE_CLOUD_DOWNLOAD_URL is None:
            raise ValueError("IMAGE_CLOUD_DOWNLOAD_URL is not set")
    if MESSAGE_PREFIX is None:
        MESSAGE_PREFIX = ""
    if MESSAGE_SUFFIX is None:
        MESSAGE_SUFFIX = ""
    if MATTERMOST_USERNAME is None:
        MATTERMOST_USERNAME = "Lunchbot"
    if SYSTEM_CONTENT is None:
        SYSTEM_CONTENT = "You are a 5-star restaurant critic. You are writing a review of the following dish:"
        logger.warning(
            f"SYSTEM_CONTENT is not set, using default value: {SYSTEM_CONTENT}"
        )
    if DESCRIPTION_SUFFIX is None:
        DESCRIPTION_SUFFIX = ""

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

    description = None

    for dish in list_of_dishes:
        dish_name = dish["name"]
        # generate a unique hash for the image
        meal_hash = generate_hash(dish_name)

        logger.debug(f"Meal: {dish_name}")
        logger.debug(f"Hash: {meal_hash}")

        # --------------------------------------------------------------------
        # Generate the image for the meal
        if USE_OPENAI_IMAGE_URL == "true":
            logger.warning("Using OpenAI image URL (will expire after 1 hour)")
            # Generate an image with DALL-E based on the menu entries
            generated_image_url = generate_image(prompt=dish_name)
            dish["image_url"] = generated_image_url

        else:
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
                request.urlretrieve(
                    generated_image_url, f"images/{meal_hash}.png"
                )  # nosec

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
            logger.info(f"Generating description for meal '{dish_name}'")

            if description is None:
                prompt_system_content = SYSTEM_CONTENT
            else:
                prompt_system_content = f"{SYSTEM_CONTENT} But please don't start the sentence with '{description[:50]}...'"

            description = get_food_description(
                meal_name=dish_name,
                system_content=prompt_system_content,
            )
            with open(f"images/{meal_hash}.txt", "w") as f:
                f.write(description)
        dish["description"] = description

    # -------------------------------------------------------------------------
    # Put the message together and send to Mattermost
    # ---

    # Generate markdown table
    table = (
        f"| Preview | Price | Info | Dish | Description {DESCRIPTION_SUFFIX}| "
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

    send_message_via_webhook(
        webhook_url=MATTERMOST_WEBHOOK_URL,
        message=message,
        username=MATTERMOST_USERNAME,
    )
    logger.info("Message posted successfully!")


if __name__ == "__main__":
    main()
