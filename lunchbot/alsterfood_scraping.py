import logging
import re
from datetime import datetime, timedelta

import requests
import yaml
from bs4 import BeautifulSoup

from lunchbot.utils import generate_hash

logger = logging.getLogger(__name__)


def fetch_todays_lunch_menu(url: str):
    """Fetch the lunch menu from the Alsterfood website.

    Parameters
    ----------
    url : str
        URL of the Alsterfood website.

    Returns
    -------
    list
        List of dictionaries with the dishes, prices and info.
        Example: [{"name": "Dish 1", "price": "€4.50", "info": "vegan"}, ...]
    """

    dishes_list = []
    # Get the page source
    page_source = requests.get(url + "/en", timeout=20).text
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(page_source, "html.parser")

    # find all the different cards (corresponding to different days)
    card_divs = soup.find_all("div", class_="card-content black-text")

    # ----------- Find today's card -----------
    # Get today's date and select the corresponding card from the menu
    today_date_datetime = datetime.now()
    # today_date_datetime = datetime(2023, 12, 12)  # set a specific date for debugging
    today_date = today_date_datetime.strftime("%d.%m.%Y")

    todays_card = None
    # Iterate through each card div
    for card_div in card_divs:
        # Check if today's date is in the card-title primary-text
        title_div = card_div.find("div", class_="card-title primary-text")
        if title_div and today_date in title_div.text:
            # Print the original card div
            todays_card = card_div

    # if no card was found, try to find the next possible date
    if todays_card is None:
        logger.warning(f"Could not find today's card for date {today_date}")
        logger.warning("Trying to find the next possible date...")

        # iterate through the upcoming next 7 days - for the first match, take the card
        for i in range(1, 8):
            next_date = (today_date_datetime + timedelta(days=i)).strftime("%d.%m.%Y")
            logger.info(f"Looking for date {next_date}")
            for card_div in card_divs:
                # Check if today's date is in the card-title primary-text
                title_div = card_div.find("div", class_="card-title primary-text")
                if title_div and next_date in title_div.text:
                    # Print the original card div
                    todays_card = card_div
                    logger.info(f"Found date {next_date}")
                    break
            if todays_card is not None:
                break

    regex = re.compile("entry entry-item *")
    menu_entries_table = todays_card.find_all("table", {"class": regex})

    # check which of the charts has the actual means (and not the soups)
    for i, entry_list in enumerate(menu_entries_table):
        print(entry_list.text)
        if "soup" in entry_list.text.lower():
            print("Skipping soup entries")
            continue
        entries_list = entry_list

        # debugging (if website structure is changed once again)
        # for j, entry in enumerate(entries_list.find_all("tr")):
        #     logger.info(80 * "-")
        #     logger.info(f"Entry: {j}")
        #     logger.info(entry.text)
        #     logger.info(80 * "-")

        n_entries = len(entries_list.find_all("tr")) - 1
        logger.info(f"Found {n_entries} entries in the menu for date {today_date}")

        # ----------- Find different dishes -----------
        # entries are alternating: dish name, dish info + price etc
        for i in range(1, n_entries, 2):
            logger.info(80 * "-")
            logger.info(f"--- Entry {i} ---")
            dish_name = entries_list.find_all("tr")[i].text
            logger.info(f"Dish name: '{dish_name}'")
            dish_info = entries_list.find_all("tr")[i + 1].text
            logger.info(f"Dish info: '{dish_info}'")
            # find the div with class "price-text" inside dish_info
            dish_price = entries_list.find_all("tr")[i + 1].find(
                "div", class_="price-text"
            )
            if dish_price:
                dish_price = dish_price.text.split(" ")[-1].strip() + " €"
            else:
                dish_price = "N/A"

            dish_veg_label = None

            if "vegan" in dish_info.lower():
                dish_veg_label = "vegan"
            elif "vegetarisch" in dish_info.lower():
                dish_veg_label = "vegetarian"
            else:
                dish_veg_label = "meat"
            logger.info(f"Veg label: '{dish_veg_label}'")
            logger.info(f"Dish price: '{dish_price}'")

            dishes_list.append(
                {
                    "name": dish_name,
                    "info": dish_veg_label,
                    "price": dish_price,
                    "canteen": "DESY Canteen",
                    "hash": generate_hash(dish_name),
                }
            )

    print()
    print(yaml.dump(dishes_list, allow_unicode=True))
    print()

    return dishes_list


if __name__ == "__main__":
    # setup logger
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    url = "https://desy.myalsterfood.de/"
    todays_menu = fetch_todays_lunch_menu(url)
