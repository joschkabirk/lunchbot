import datetime
import requests
import logging
import os
from subprocess import run  # nosec
from urllib import request  # nosec

from dotenv import load_dotenv

import lunchbot.alsterfood_scraping as alsterfood_scraping
import lunchbot.cfel_scraping as cfel_scraping
from lunchbot.image_generation import generate_image_openai, generate_image_huggingface
from lunchbot.mattermost_posting import send_message_via_webhook
from lunchbot.utils import color_text

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    load_dotenv()  # take environment variables from .env

    ALSTERFOOD_WEBSITE_URL = os.getenv("ALSTERFOOD_WEBSITE_URL")
    CFEL_WEBSITE_URL = os.getenv("CFEL_WEBSITE_URL")
    MATTERMOST_WEBHOOK_URL = os.getenv("MATTERMOST_WEBHOOK_URL")
    USE_OPENAI_IMAGE_URL = os.getenv("USE_OPENAI_IMAGE_URL")
    IMAGE_CLOUD_UPLOAD_URL = os.getenv("IMAGE_CLOUD_UPLOAD_URL")
    IMAGE_CLOUD_UPLOAD_TOKEN = os.getenv("IMAGE_CLOUD_UPLOAD_TOKEN")
    IMAGE_CLOUD_DOWNLOAD_URL = os.getenv("IMAGE_CLOUD_DOWNLOAD_URL")
    MESSAGE_PREFIX = os.getenv("MESSAGE_PREFIX")
    HUGGINGFACE_API_URL = os.getenv("HUGGINGFACE_API_URL")
    HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
    API_TO_USE = os.getenv("API_TO_USE").lower()  # huggingface or openai

    if API_TO_USE != "huggingface" and API_TO_USE != "openai":
        raise ValueError("API_TO_USE must be either 'huggingface' or 'openai'")

    # check which day it is and set the MESSAGE_SUFFIX accordingly
    today = datetime.datetime.today().weekday()
    even = datetime.datetime.today().isocalendar()[1] % 2
    if today == 0:
        MESSAGE_SUFFIX = os.getenv("MESSAGE_SUFFIX_MON")
        if even == 0 and os.getenv("MESSAGE_SUFFIX_MON_EVEN") is not None:
            MESSAGE_SUFFIX = os.getenv("MESSAGE_SUFFIX_MON_EVEN")
        elif even == 1 and os.getenv("MESSAGE_SUFFIX_MON_ODD") is not None:
            MESSAGE_SUFFIX = os.getenv("MESSAGE_SUFFIX_MON_ODD")
    elif today == 1:
        MESSAGE_SUFFIX = os.getenv("MESSAGE_SUFFIX_TUE")
        if even == 0 and os.getenv("MESSAGE_SUFFIX_TUE_EVEN") is not None:
            MESSAGE_SUFFIX = os.getenv("MESSAGE_SUFFIX_TUE_EVEN")
        elif even == 1 and os.getenv("MESSAGE_SUFFIX_TUE_ODD") is not None:
            MESSAGE_SUFFIX = os.getenv("MESSAGE_SUFFIX_TUE_ODD")
    elif today == 2:
        MESSAGE_SUFFIX = os.getenv("MESSAGE_SUFFIX_WED")
        if even == 0 and os.getenv("MESSAGE_SUFFIX_WED_EVEN") is not None:
            MESSAGE_SUFFIX = os.getenv("MESSAGE_SUFFIX_WED_EVEN")
        elif even == 1 and os.getenv("MESSAGE_SUFFIX_WED_ODD") is not None:
            MESSAGE_SUFFIX = os.getenv("MESSAGE_SUFFIX_WED_ODD")
    elif today == 3:
        MESSAGE_SUFFIX = os.getenv("MESSAGE_SUFFIX_THU")
        if even == 0 and os.getenv("MESSAGE_SUFFIX_THU_EVEN") is not None:
            MESSAGE_SUFFIX = os.getenv("MESSAGE_SUFFIX_THU_EVEN")
        elif even == 1 and os.getenv("MESSAGE_SUFFIX_THU_ODD") is not None:
            MESSAGE_SUFFIX = os.getenv("MESSAGE_SUFFIX_THU_ODD")
    elif today == 4:
        MESSAGE_SUFFIX = os.getenv("MESSAGE_SUFFIX_FRI")
        if even == 0 and os.getenv("MESSAGE_SUFFIX_FRI_EVEN") is not None:
            MESSAGE_SUFFIX = os.getenv("MESSAGE_SUFFIX_FRI_EVEN")
        elif even == 1 and os.getenv("MESSAGE_SUFFIX_FRI_ODD") is not None:
            MESSAGE_SUFFIX = os.getenv("MESSAGE_SUFFIX_FRI_ODD")
    elif today == 5:
        MESSAGE_SUFFIX = os.getenv("MESSAGE_SUFFIX_SAT")
        if even == 0 and os.getenv("MESSAGE_SUFFIX_SAT_EVEN") is not None:
            MESSAGE_SUFFIX = os.getenv("MESSAGE_SUFFIX_SAT_EVEN")
        elif even == 1 and os.getenv("MESSAGE_SUFFIX_SAT_ODD") is not None:
            MESSAGE_SUFFIX = os.getenv("MESSAGE_SUFFIX_SAT_ODD")
    elif today == 6:
        MESSAGE_SUFFIX = os.getenv("MESSAGE_SUFFIX_SUN")
        if even == 0 and os.getenv("MESSAGE_SUFFIX_SUN_EVEN") is not None:
            MESSAGE_SUFFIX = os.getenv("MESSAGE_SUFFIX_SUN_EVEN")
        elif even == 1 and os.getenv("MESSAGE_SUFFIX_SUN_ODD") is not None:
            MESSAGE_SUFFIX = os.getenv("MESSAGE_SUFFIX_SUN_ODD")
    else:
        MESSAGE_SUFFIX = ""

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
    list_of_dishes = alsterfood_scraping.fetch_todays_lunch_menu(ALSTERFOOD_WEBSITE_URL)

    try:
        list_of_dishes += cfel_scraping.fetch_todays_lunch_menu(CFEL_WEBSITE_URL)
    except Exception as e:
        logger.error(f"An error occurred while fetching CFEL lunch menu: {str(e)}")

    logger.info("The following dishes were found:")
    for i, dish_name in enumerate(list_of_dishes):
        logger.info(f"  {i+1})  {dish_name}")

    # -------------------------------------------------------------------------
    # Generate an image for each meal
    # ---
    logger.info(50 * "-")
    logger.info("Generating images for the meals...")

    for dish in list_of_dishes:
        dish_name = dish["name"]
        meal_hash = dish["hash"]

        logger.debug(f"Meal: {dish_name}")
        logger.debug(f"Hash: {meal_hash}")

        dish["image_url"] = f"{IMAGE_CLOUD_DOWNLOAD_URL}{meal_hash}.png"

        # check if image already exists - if it does, skip image generation
        # and just use the existing image
        if requests.get(dish["image_url"]).status_code == 200:
            logger.info(
                f"Image with hash {color_text(meal_hash, 'yellow')} for "
                f"'{color_text(dish_name, 'yellow')}' already exists. "
                "Skipping image generation."
            )
            dish["generation_info_tag"] = "Already generated"
            continue
        logger.info(f"Generating image with hash {meal_hash} for '{dish_name}'")

        if API_TO_USE == "openai":
            # generate the image using the OpenAI API
            generated_image_url = generate_image_openai(prompt=dish_name)
            # log the URL of the generated image
            logger.info(f"Generated Image URL: {generated_image_url}")

            # download the image from the openAI url and save in images/image_hash.png
            # (openAI urls are only valid for one hour, then they expire)
            # command = f"curl --output images/asdf{i}.png {image_url}"
            request.urlretrieve(generated_image_url, f"images/{meal_hash}.png")
            dish["generation_info_tag"] = "Generated with OpenAI API"
        elif API_TO_USE == "huggingface":
            try:
                # try generating image using huggingface
                generate_image_huggingface(
                    prompt=dish_name,
                    api_url=HUGGINGFACE_API_URL,
                    api_token=HUGGINGFACE_API_TOKEN,
                    save_path=f"images/{meal_hash}.png",
                )
                dish["generation_info_tag"] = "Generated with Huggingface API"
            except Exception as e:
                # if an error occurs, use the OpenAI API to generate the image
                # (for some reason Huggingface API sometimes fails to generate images)
                logger.error(f"An error occurred while generating image: {e}")
                logger.info("Trying to generate image with OpenAI API")
                generated_image_url = generate_image_openai(prompt=dish_name)
                # log the URL of the generated image
                logger.info(f"Generated Image URL: {generated_image_url}")

                # download the image from the openAI url and save in images/image_hash.png
                # (openAI urls are only valid for one hour, then they expire)
                # command = f"curl --output images/asdf{i}.png {image_url}"
                request.urlretrieve(generated_image_url, f"images/{meal_hash}.png")  # nosec
                dish["generation_info_tag"] = "Generated with OpenAI API"
            else:
                # this error should be raised already, but just in case
                raise ValueError("API_TO_USE must be either 'huggingface' or 'openai'")

        # --- upload the image to the cloud ---
        # the image will be available for unlimited time / until we delete it in the
        # cloud, so we don't have to worry about the image link expiring after some time)
        upload_command = [
            "curl",
            "-u",
            f"'{IMAGE_CLOUD_UPLOAD_TOKEN}'",
            "-T",
            f"images/{meal_hash}.png",
            f"{IMAGE_CLOUD_UPLOAD_URL}{meal_hash}.png",
        ]
        run(" ".join(upload_command), shell=True)  # nosec

        # check if the image was uploaded successfully
        if requests.get(dish["image_url"]).status_code == 200:
            logger.info(f"Image uploaded successfully to {dish['image_url']}")
        else:
            raise ValueError(f"Image upload failed for {dish['image_url']}")

    # if there are price/info/canteen elements that are None, set them to "N/A"
    for dish in list_of_dishes:
        if dish["price"] is None:
            dish["price"] = "N/A"
        if dish["info"] is None:
            dish["info"] = "N/A"
        if dish["canteen"] is None:
            dish["canteen"] = "N/A"

    # printout the information which helps with debugging in case something goes wrong
    for dish in list_of_dishes:
        logger.info(f"Dish: {dish['name']}")
        logger.info(f"\tImage URL: {dish['image_url']}")
        logger.info(f"\tGeneration info tag: {dish['generation_info_tag']}")
        logger.info(f"\tHash: {dish['hash']}")
        logger.info(f"\tPrice: {dish['price']}")
        logger.info(f"\tInfo: {dish['info']}")
        logger.info(f"\tCanteen: {dish['canteen']}")


    # -------------------------------------------------------------------------
    # Put the message together and send to Mattermost
    # ---

    # this table includes both DESY cantine and CFEL cafe menus
    # fmt: off
    table_dish_columns_merged = (
        "\n| " + " | ".join([dish["name"].replace("|", "-") for dish in list_of_dishes]) + " |\n"
        + "|" + " --- |" * len([dish["name"] for dish in list_of_dishes]) + "\n"
        # add the price
        + "|" + " | ".join([dish["price"] for dish in list_of_dishes]) + " |\n"
        # add the info
        + "|" + " | ".join([dish["info"] for dish in list_of_dishes]) + " |\n"
        # add which canteen
        + "|" + " | ".join([dish["canteen"] for dish in list_of_dishes]) + " |\n"
        # add the images
        + "|" + " | ".join([f" ![preview {dish['generation_info_tag']}]({dish['image_url']} =200)" 
                            for dish in list_of_dishes]) + " |\n"
    )
    # fmt: on

    # add hyperlinks pointing to the official menus (where the information was scraped from)
    table_dish_columns_merged = table_dish_columns_merged.replace(
        "DESY Canteen", f"**[DESY Canteen]({ALSTERFOOD_WEBSITE_URL})** :alsterfood:"
    )
    table_dish_columns_merged = table_dish_columns_merged.replace(
        "Cafe CFEL", f"**[Cafe CFEL]({CFEL_WEBSITE_URL})** :cfel:"
    )

    # add prefix and suffix to the message
    message = (
        MESSAGE_PREFIX
        + "\n"
        + table_dish_columns_merged
        + "\n\n"
        + "\n"
        + MESSAGE_SUFFIX
    )

    logger.info("Posting the following message on Mattermost:")
    logger.info(color_text(message, 'green'))

    n_attempts = 10

    for n in range(n_attempts):
        try:
            send_message_via_webhook(
                webhook_url=MATTERMOST_WEBHOOK_URL,
                message=message,
                username=MATTERMOST_USERNAME,
            )
            break
        except Exception as e:
            logger.error(f"An error occurred while posting message: {e}")
            if n < n_attempts - 1:
                logger.info(f"Retrying... (attempt {n+2}/{n_attempts})")
            else:
                raise e
    logger.info("Message posted successfully!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        MATTERMOST_WEBHOOK_URL_ALERT = os.getenv("MATTERMOST_WEBHOOK_URL_ALERT")
        ALERT_PREFIX = os.getenv("ALERT_PREFIX")
        send_message_via_webhook(
            webhook_url=MATTERMOST_WEBHOOK_URL_ALERT,
            message=f"{ALERT_PREFIX}An error occurred: {e}",
            username="Lunchbot",
        )
