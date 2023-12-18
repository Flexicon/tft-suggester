from common.db import DB
from scraper.helpers import _trigger_webhook_if_set
from scraper.scrape_champions import scrape_and_persist as scrape_champions
from scraper.scrape_comps import scrape_and_persist as scrape_comps
from scraper.scrape_items import scrape_and_persist as scrape_items

if __name__ == '__main__':
    print("Running scraper 🕷️")
    db = DB().connect()
    scrape_champions(db.get_champions_collection())
    scrape_comps(db.get_comps_collection())
    scrape_items(db.get_items_collection())
    _trigger_webhook_if_set()
    db.disconnect()
