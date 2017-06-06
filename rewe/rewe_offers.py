from typing import Dict

from .offers import OffersWebsite
from .wanted import WantedProducts


def get_acceptable_offers(*, market_id: str, wanted_filename: str, log_level: str = "INFO") -> Dict[str, float]:
    wanted_products = WantedProducts(wanted_filename, log_level=log_level)
    offers_website = OffersWebsite(market_id, log_level=log_level)

    acceptable_offers_mappings = wanted_products.get_all_mappings()
    offers = offers_website.get_offers()
    products = set()
    for offer in offers:
        for mapping in acceptable_offers_mappings:
            if mapping.lower() in offer.get_name().lower():
                products.add(offer)

    return products


def get(*, market_id, wanted_filename, log_level: str = "INFO"):
    # noinspection PyTypeChecker
    return get_acceptable_offers(market_id=market_id, wanted_filename=wanted_filename, log_level=log_level)
