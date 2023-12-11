import logging
import re
from datetime import datetime, timedelta

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

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
    # Set up Chrome options (adjust as needed)
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.headless = True  # Run Chrome in headless mode (without GUI)
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-features=dbus")

    # Specify the path to your ChromeDriver executable
    # chrome_path = "/opt/homebrew/Caskroom/chromedriver/120.0.6099.71/chromedriver-mac-arm64/chromedriver"  # mac
    chrome_path = "/usr/bin/chromedriver"

    dishes_list = []

    # Initialize the Chrome driver
    with webdriver.Chrome(
        service=ChromeService(executable_path=chrome_path), options=chrome_options
    ) as driver:
        # Navigate to the URL
        driver.get(url)

        # Wait for up to 10 seconds for an element with ID 'target_element_id' to be present
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "group2-select-options-51")))

        # Get the page source after JavaScript execution
        page_source = driver.page_source
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
                next_date = (today_date_datetime + timedelta(days=i)).strftime(
                    "%d.%m.%Y"
                )
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

        logger.info(80 * "-")

        # ----------- Find different dishes -----------

        for menu_entry in menu_entries_table:
            tbody = menu_entry.find_all("tbody")

            logger.info("Entries from menu_entry:")
            # print all the different elements (for debugging)
            for i_tr, tr in enumerate(tbody):
                for i_td, td in enumerate(tr):
                    for i_p, p in enumerate(td):
                        logger.info(f"{i_tr}, {i_td}, {i_p} {p.text}")

            # skip soups
            if "soup" in menu_entry.text.lower():
                logger.info("Skipping soup.")
                continue

            # extract the dish name, info and price (check the logged output
            # in case this is messed up due to changes to the website...)
            dish_name = list(list(list(tbody)[0])[0])[0].text
            dish_info = list(list(list(tbody)[0])[1])[0].text
            dish_price = list(list(list(tbody)[0])[1])[2].text.replace(" ", "")

            logger.info(10 * "-")
            logger.info(f"--> | {dish_price} | {dish_info} | {dish_name} |")
            logger.info(80 * "-")
            dishes_list.append(
                {
                    "name": dish_name,
                    "info": dish_info,
                    "price": dish_price,
                }
            )

    return dishes_list
