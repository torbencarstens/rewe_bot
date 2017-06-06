from typing import Dict

from .offers import OffersWebsite
from .wanted import WantedProducts


def get_acceptable_offers(*, market_id: str, wanted_filename: str) -> Dict[str, float]:
    acceptable_offers_mappings = WantedProducts(wanted_filename).get_all_mappings()
    offers = OffersWebsite(market_id).get_offers()
    products = set()
    for offer in offers:
        for mapping in acceptable_offers_mappings:
            if mapping.lower() in offer.get_name().lower():
                products.add(offer)

    return products


def get(*, market_id, wanted_filename):
    # noinspection PyTypeChecker
    return get_acceptable_offers(market_id=market_id, wanted_filename=wanted_filename)
