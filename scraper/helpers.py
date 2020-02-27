import os

import requests
from bs4.element import Tag
from selenium import webdriver

from common.models import Champion


class ScraperWebDriver:
    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(5)

    def fetch_content_html(self, url: str, *, selector: str = '.main'):
        print('Fetching html to scrape, please wait...')
        self.driver.get(url)
        return self.driver.find_element_by_css_selector(selector).get_attribute('innerHTML')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()


def _build_champion_from_character(character: Tag) -> Champion:
    img_tag = character.find('img')
    name = img_tag['alt']
    icon = img_tag['src']
    return Champion(name, icon)


def _trigger_webhook_if_set():
    data_fetched_webhook = os.getenv('DATA_FETCHED_WEBHOOK')
    if not data_fetched_webhook:
        return

    response = requests.post(data_fetched_webhook)
    response.raise_for_status()

    print('Webhook triggered')
