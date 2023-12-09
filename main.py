import os

import yaml

from src.alsterfood_scraping import fetch_lunch_menu
from src.description_generation import get_food_description
from src.image_generation import generate_image
from src.mattermost_posting import send_message

DEBUG = True
ALSTERFOOD_WEBSITE_URL = os.getenv("ALSTERFOOD_WEBSITE_URL")
MATTERMOST_WEBHOOK_URL = os.getenv("MATTERMOST_WEBHOOK_URL")

debug_variables = yaml.safe_load(open("debug_variables.yml"))


if __name__ == "__main__":
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
    for meal, desc, img_url in zip(list_of_meals, descriptions, images):
        table += f"| ![preview]({img_url}) | **{meal}**  | {desc}| \n"

    message = prefix + "\n\n" + table

    print("The following message will be posted on Mattermost:")
    print(message)

    send_message(
        url=MATTERMOST_WEBHOOK_URL,
        message=message,
        username="Lunchbot (always hungry)",
    )
