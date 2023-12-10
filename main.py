import os
from subprocess import run  # nosec
from urllib import request  # nosec

import yaml

from src.alsterfood_scraping import fetch_lunch_menu
from src.description_generation import get_food_description
from src.image_generation import generate_hash, generate_image
from src.mattermost_posting import send_message

DEBUG = True
ALSTERFOOD_WEBSITE_URL = os.getenv("ALSTERFOOD_WEBSITE_URL")
MATTERMOST_WEBHOOK_URL = os.getenv("MATTERMOST_WEBHOOK_URL")
IMAGE_CLOUD_UPLOAD_URL = os.getenv("IMAGE_CLOUD_UPLOAD_URL")
IMAGE_CLOUD_UPLOAD_TOKEN = os.getenv("IMAGE_CLOUD_UPLOAD_TOKEN")
IMAGE_CLOUD_DOWNLOAD_URL = os.getenv("IMAGE_CLOUD_DOWNLOAD_URL")

debug_variables = yaml.safe_load(open("debug_variables.yml"))


def main():
    # -------------------------------------------------------------------------
    # Get the list of meals and prices
    # ---
    if DEBUG:
        list_of_meals = debug_variables["debug_list_of_meals"]
    else:
        list_of_meals, list_of_prices = fetch_lunch_menu(ALSTERFOOD_WEBSITE_URL)

    print(list_of_meals)

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
            # Print the URL of the generated image
            print(f"Generated Image URL: {generated_image_url}")

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
        # Print the URL of the generated image and its hash
        print(f"Generated Image URL: {image_url}, Hash: {image_hash}")

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

    print("The following message will be posted on Mattermost:")
    print(message)

    send_message(
        url=MATTERMOST_WEBHOOK_URL,
        message=message,
        username="Lunchbot (always hungry)",
    )


if __name__ == "__main__":
    main()
