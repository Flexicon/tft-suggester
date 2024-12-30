import os
import re

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from tenacity import (
    Retrying,
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from common.models import Champion

traits_cache = {}


class ScraperWebDriver:
    def __init__(self) -> None:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_page_load_timeout(10)
        self.driver.implicitly_wait(5)

    @retry(
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(TimeoutException),
        wait=wait_exponential(min=1, max=5),
        reraise=True,
    )
    def fetch_content_html(self, url: str, *, selector: str = ".main") -> str:
        print(f"Fetching html from: {url}")
        self.driver.get(url)
        return self.driver.find_element_by_css_selector(selector).get_attribute(
            "innerHTML"
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()


def _build_champion_from_character(
    driver: ScraperWebDriver, character: Tag
) -> Champion:
    traits = _scrape_traits_for_character(driver, character)
    img_tag = character.find("img")
    name = img_tag["alt"]
    icon = img_tag["src"]
    cost = _price_from_character_class(" ".join(character["class"]))
    return Champion(name=name, image=icon, cost=cost, traits=traits)


def _scrape_traits_for_character(driver: ScraperWebDriver, character: Tag) -> list[str]:
    href = character["href"]
    url = f"https://tftactics.gg{href}" if href.startswith("/") else href

    if url in traits_cache:
        print(f"Using cached traits for: {url}")
        return traits_cache[url]

    try:
        html = driver.fetch_content_html(url)
    except TimeoutException:
        print(f"Timeout fetching champion traits from: {url}")
        return []

    traits = traits_cache[url] = _extract_traits_from_character_html(html)
    return traits


def _extract_traits_from_character_html(html: str) -> list[str]:
    selector = ".ability-description-name"
    ability_tags = BeautifulSoup(html, "html.parser").select(selector)
    return [
        tag.find("h2").get_text()
        for tag in ability_tags
        if tag.find("h4").get_text().lower() not in ["active", "passive"]
    ]


def _price_from_character_class(classes: str) -> int:
    pattern = re.compile(r"\bc(\d+)\b")
    matches = pattern.findall(classes)
    return int(matches[0]) if matches else 0


def _trigger_webhook_if_set():
    data_fetched_webhook = os.getenv("DATA_FETCHED_WEBHOOK")
    if not data_fetched_webhook:
        return

    response = requests.post(data_fetched_webhook)
    response.raise_for_status()

    print("Webhook triggered")
