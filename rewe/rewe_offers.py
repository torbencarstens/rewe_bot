import re
from typing import Set, Tuple, Union

from .logger import Logger
from .offers import Offer, OffersWebsite
from .wanted import WantedProduct, WantedProducts


def get_acceptable_offers(*, market_id: str, wanted_filename: str, log_level: str = "INFO",
                          return_reason: bool = False) -> Union[Set[Offer], Tuple[Set[Offer], WantedProduct]]:
    log = Logger("rewe_offers")
    log.debug("Get wanted")
    wanted_products = WantedProducts(wanted_filename, log_level=log_level)
    log.debug("Get offers")
    offers_website = OffersWebsite(market_id, log_level=log_level)

    log.debug("Get mappings")
    log.debug("Get offers")
    offers = offers_website.get_offers()
    products = set()
    log.debug("iterate")
    for offer in offers:
        for wanted in wanted_products.get_products():
            for mapping in wanted.get_mappings():
                try:
                    if re.search(mapping.lower(), offer.get_name().lower()):
                        if return_reason:
                            products.add((offer, wanted))
                        else:
                            products.add(offer)
                        break
                except Exception as e:
                    log.error("Regex error (%s): %s", mapping, e)

    log.debug("Found %d products.", len(products))
    result = products

    return result


def get(*, market_id, wanted_filename, log_level: str = "INFO", return_reason: bool = False):
    # noinspection PyTypeChecker
    Logger("rewe_offers", level=log_level).debug("get")
    return get_acceptable_offers(market_id=market_id, wanted_filename=wanted_filename, log_level=log_level,
                                 return_reason=return_reason)
