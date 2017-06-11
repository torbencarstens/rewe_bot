from typing import Dict

from .logger import Logger
from .offers import OffersWebsite
from .wanted import WantedProducts


def get_acceptable_offers(*, market_id: str, wanted_filename: str, log_level: str = "INFO") -> Dict[str, float]:
    log = Logger("rewe_offers")
    log.debug("Get wanted")
    wanted_products = WantedProducts(wanted_filename, log_level=log_level)
    log.debug("Get offers")
    offers_website = OffersWebsite(market_id, log_level=log_level)

    log.debug("Get mappings")
    acceptable_offers_mappings = wanted_products.get_all_mappings()
    log.debug("Get offers")
    offers = offers_website.get_offers()
    products = set()
    log.debug("iterate")
    for offer in offers:
        for mapping in acceptable_offers_mappings:
            if mapping.lower() in offer.get_name().lower():
                print(offer.get_name())
                products.add(offer)

    log.debug("Found %d products.", len(products))
    return products


def get(*, market_id, wanted_filename, log_level: str = "INFO"):
    # noinspection PyTypeChecker
    Logger("rewe_offers", level=log_level).debug("get")
    return get_acceptable_offers(market_id=market_id, wanted_filename=wanted_filename, log_level=log_level)
