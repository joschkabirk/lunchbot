import logging

import requests
import yaml
from bs4 import BeautifulSoup

from lunchbot.utils import generate_hash, translate_german_food_description_to_english

logger = logging.getLogger(__name__)


def fetch_todays_lunch_menu(url: str):
    """Fetch the lunch menu from the CFEL menu website.

    Parameters
    ----------
    url : str
        URL of the cfel menu website.

    Returns
    -------
    list
        List of dictionaries with the dishes, prices and info.
        Example: [{"name": "Dish 1", "price": "€4.50", "info": "vegan"}, ...]
    """
    dishes_list = []

    # Get the page source
    page_source = requests.get(url, timeout=20).text
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(page_source, "html.parser")

    # find all the different cards (corresponding to different days)
    card_divs = soup.find_all("div", class_="aw-meal row no-margin-xs")

    for hit in card_divs:
        dish_name = None
        for d in hit.find_all("p", class_="aw-meal-description"):
            if dish_name is None:
                dish_name = d.text
            else:
                raise ValueError("Multiple meal descriptions found")

        # check if the dish is vegetarian or vegan
        vegetarian = None
        vegan = None
        for d in hit.find_all("p", class_="small aw-meal-attributes"):
            if vegetarian is None:
                vegetarian = "vegetarian" in d.text.lower()
            if vegan is None:
                vegan = "vegan" in d.text.lower()

        dish_price = None
        for d in hit.find_all("div", class_="col-sm-2 no-padding-xs aw-meal-price"):
            if dish_price is None:
                dish_price = d.text.replace(",", ".")
            else:
                raise ValueError("Multiple meal prices found")

        logger.info(20 * "-")
        logger.info(dish_name)
        logger.info(f"vegetarian {vegetarian}")
        logger.info(f"vegan: {vegan}")
        logger.info(20 * "-")

        if vegan:
            dish_info = "vegan"
        elif vegetarian:
            dish_info = "vegetarian"
        else:
            dish_info = ""

        # Translate the dish description to English
        dish_name_translated = translate_german_food_description_to_english(dish_name)

        dishes_list.append(
            {
                "name": dish_name_translated,
                "info": dish_info,
                "price": dish_price,
                "canteen": "Cafe CFEL",
                "hash": generate_hash(dish_name),
            }
        )

    logger.info(80 * "-")

    print()
    print(yaml.dump(dishes_list, allow_unicode=True))
    print()

    return dishes_list


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    url = "https://www.imensa.de/hamburg/cafe-cfel/index.html"
    todays_menu = fetch_todays_lunch_menu(url)
    print(todays_menu)
