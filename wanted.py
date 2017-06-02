import codecs
import json
from typing import Dict, List, Union


class WantedProducts:
    def __init__(self, filename: str):
        with codecs.open(filename, "r+", "utf-8") as wanted:
            self.wanted = json.load(wanted)

    def get_products(self) -> List[WantedProduct]:
        return [WantedProduct(item) for item in self.wanted]

    def get_all_mappings(self) -> List[str]:
        complete_list = [product.get_mappings() for product in self.get_products()]

        return [element for sublist in complete_list for element in sublist]


class WantedProduct:
    def __init__(self, item: Dict):
        for name, value in item.items():
            self.name = name
            self.mappings = value['mapping']

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
