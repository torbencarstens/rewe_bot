import json
import os
from typing import List, Dict

from wanted import WantedProduct, WantedProducts


class User:
    base = "resources"

    def __init__(self, id: int):
        """
        :param id: int
        """
        self.id = id
        self.filename = ".".join([os.pathsep.join([self.base, id]), "json"])
        self.products = self.get_wanted_products()

    def get_wanted_products(self) -> List[WantedProduct]:
        if os.path.exists(self.filename):
            self.products = WantedProducts(self.filename).get_products()
            return self.products
        else:
            return []

    def add_offer(self, product: WantedProduct):
        self.products.append(product)

    def _write(self) -> None:
        with open(self.filename, "w+") as resource:
            json.dump("", resource)

    def _read(self) -> Dict:
        with open(self.filename, "w+") as resource:
            return json.load(resource)
