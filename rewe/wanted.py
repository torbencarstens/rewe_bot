import codecs
import json
from typing import Dict, List, Union

from .product import Product


class WantedProduct(Product):
    def __init__(self, item: Dict):
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
        return self.get()


class WantedProducts:
    def __init__(self, filename: str):
        with codecs.open(filename, "r+", "utf-8") as wanted:
            self.wanted = json.load(wanted)['products']

    def get_products(self) -> List[WantedProduct]:
        products = [WantedProduct(item) for item in self.wanted]
        return products

    def get_all_mappings(self) -> List[str]:
        complete_list = [product.get_mappings() for product in self.get_products()]

        return [element for sublist in complete_list for element in sublist]


def to_json(products: List[WantedProduct]) -> Dict[str, Union[str, List[str]]]:
    json_products = {'products': []}

    for product in products:
        json_products['products'].append(product.to_json())

    return json_products
