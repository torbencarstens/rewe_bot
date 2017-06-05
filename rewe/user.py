import json
import os
from typing import List, Dict

from . import wanted
from .s3 import S3
from .wanted import WantedProduct, WantedProducts


class User:
    base = "resources"
    market_id = None

    def __init__(self, id: int):
        """
        :param id: int
        """
        self.id = id
        self.products = self.get_wanted_products()
        self.s3 = S3(self)
        self.filename = self.s3.get_local_filepath(directory=self.base)
        self.market_id = self.get_market_id()

    def get_market_id(self):
        if self.market_id:
            return self.market_id
        return self._read()['market_id']

    def get_wanted_products(self) -> List[WantedProduct]:
        if os.path.exists(self.filename):
            self.products = WantedProducts(self.filename).get_products()
            return self.products
        else:
            return []

    def add_offer(self, product: WantedProduct):
        self.products.append(product)

    def _write(self) -> None:
        with open(self.filename, "w") as resource:
            json.dump(wanted.to_json(self.products), resource)

    def _upload(self, *, base_directory: str = None):
        self.s3.upload(directory=base_directory)

    def _download(self, *, base_directory: str = None):
        self.s3.download(directory=base_directory)

    def _read(self) -> Dict:
        if not os.path.exists(self.filename):
            self.s3.exists()

        with open(self.filename, "r") as resource:
            return json.load(resource)
