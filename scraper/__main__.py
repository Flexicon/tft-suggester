from common.db import DB
from scraper.helpers import trigger_webhook_if_set
from scraper.scrape_champions import persist as persist_champions
from scraper.scrape_champions import scrape_champions
from scraper.scrape_comps import persist as persist_comps
from scraper.scrape_comps import scrape_comps
from scraper.scrape_items import persist as persist_items
from scraper.scrape_items import scrape_items

if __name__ == "__main__":
    print("Running scraper 🕷️")
    db = DB().connect()
    try:
        champions = scrape_champions()
        persist_champions(db.get_champions_collection(), champions)

        # Reuse the traits we just fetched instead of hitting every champion page
        # again while scraping comps.
        traits_lookup = {champion.name: champion.traits for champion in champions}
        comps = scrape_comps(traits_lookup=traits_lookup)
        persist_comps(db.get_comps_collection(), comps)

        persist_items(db.get_items_collection(), scrape_items())
        trigger_webhook_if_set()
    finally:
        db.disconnect()
