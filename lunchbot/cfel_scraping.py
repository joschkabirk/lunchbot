import logging

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService

from lunchbot.utils import translate_german_food_description_to_english

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
        logger.info("Waiting for page to be ready...")
        # wait = WebDriverWait(driver, 20)
        # wait.until(EC.presence_of_element_located((By.ID, "openings")))
        logger.info("Page is ready!")

        # Get the page source after JavaScript execution
        page_source = driver.page_source
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
                    dish_price = d.text
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
            dish_name = translate_german_food_description_to_english(dish_name)

            dishes_list.append(
                {
                    "name": dish_name,
                    "info": dish_info,
                    "price": dish_price,
                    "canteen": "Cafe CFEL",
                }
            )

        logger.info(80 * "-")

    return dishes_list


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    url = "https://www.imensa.de/hamburg/cafe-cfel/index.html"
    todays_menu = fetch_todays_lunch_menu(url)
    print(todays_menu)
