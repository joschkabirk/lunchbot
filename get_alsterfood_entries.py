from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

ALSTERFOOD_WEBSITE_URL = os.getenv('ALSTERFOOD_WEBSITE_URL')

def fetch_lunch_menu(url):
    # Set up Chrome options (adjust as needed)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.headless = True  # Run Chrome in headless mode (without GUI)

    # Specify the path to your ChromeDriver executable
    chrome_path = '/opt/homebrew/Caskroom/chromedriver/120.0.6099.71/chromedriver-mac-arm64/chromedriver'

    # Initialize the Chrome driver
    with webdriver.Chrome(service=ChromeService(executable_path=chrome_path), options=chrome_options) as driver:
        # Navigate to the URL
        driver.get(url)

        # Wait for up to 10 seconds for an element with ID 'target_element_id' to be present
        wait = WebDriverWait(driver, 3)
        wait.until(EC.presence_of_element_located((By.ID, 'group2-select-options-51')))

        # Get the page source after JavaScript execution
        page_source = driver.page_source
        # print(page_source)

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')

        # Find all elements with the specified class
        menu_entries_div_class_name = 'min-height-rem2-5'
        menu_entries = driver.find_elements(By.CLASS_NAME, menu_entries_div_class_name)

        # Get the text content of each entry
        list_of_meals = [entry.text for entry in menu_entries if entry.text != '']

    return list_of_meals

if __name__ == '__main__':
    url = ALSTERFOOD_WEBSITE_URL
    print(url)
    # Fetch the entire HTML source after rendering
    list_of_meals = fetch_lunch_menu(url)
    print(list_of_meals)
