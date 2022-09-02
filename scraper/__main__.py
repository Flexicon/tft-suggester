from common.db import DB
from scraper.helpers import _trigger_webhook_if_set
from scraper.scrape_champions import _scrape_and_persist as scrape_champions
from scraper.scrape_comps import _scrape_and_persist as scrape_comps

if __name__ == '__main__':
    db = DB().connect()
    scrape_champions(db.get_champions_collection())
    scrape_comps(db.get_comps_collection())
    _trigger_webhook_if_set()
    db.disconnect()
