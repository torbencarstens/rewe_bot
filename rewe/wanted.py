import codecs
import json
import logging
import re
from typing import Dict, List, Union

from .logger import Logger
from .product import Product


class WantedProduct(Product):
    def __init__(self, item: Dict, *, log_level: str = "INFO"):
        self.log = Logger("WantedProduct", level=log_level)
        self.id = item['id']
        name = item['name']
        self.mappings = item['mappings']

        super().__init__(name=name)

    def get_mappings(self) -> List[str]:
        return self.mappings

    def get_name(self) -> str:
        return self.name

    def get(self) -> Dict[str, Union[str, List[str]]]:
        """
        Returns a dictionary with 'name' and 'index' as keys.
        :return: Dict[{"name", "mappings"}, [...]]
        """
        return {"name": self.get_name(), "mappings": self.get_mappings()}

    def to_json(self) -> Dict[str, Union[str, List[str]]]:
        js = self.get()
        js['id'] = self.id

        return js

    @classmethod
    def parse_new(cls, *, id: int, input: str):
        regex = r"(.*?)\s*-\s*\[(.*)\]"
        result = {}

        matches = re.findall(regex, input)
        if matches:
            name, mappings_raw = matches[0]
            mappings = re.split(r"[^\\],\s*", mappings_raw)
            mappings = [mapping for mapping in mappings if mapping]

            result = {"id": id, "name": name, "mappings": mappings}

        logging.getLogger("WantedProduct").debug("Create new offer from: %s", result)
        return cls(result)


class WantedProducts:
    products = None

    def __init__(self, filename: str, *, log_level: str = "INFO"):
        self.log = Logger("WantedProducts", level=log_level)
        with codecs.open(filename, "r+", "utf-8") as wanted:
            self.wanted = json.load(wanted)['products']

    def get_products(self) -> List[WantedProduct]:
        products = [WantedProduct(item, log_level=self.log.getEffectiveLevel()) for item in self.wanted]
        return products

    def get_all_mappings(self) -> List[str]:
        complete_list = [product.get_mappings() for product in self.get_products()]

        return [element for sublist in complete_list for element in sublist]

    def last_id(self) -> int:
        try:
            return max(self.wanted, key=lambda wanted: wanted["id"])["id"]
        except (KeyError, ValueError):
            return -1


def to_json(products: List[WantedProduct]) -> Dict[str, Union[str, List[str]]]:
    json_products = {'products': []}

    for product in products:
        json_products['products'].append(product.to_json())

    return json_products
