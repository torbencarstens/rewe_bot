import json
import os
from typing import List, Dict

from . import s3, wanted
from .wanted import WantedProduct, WantedProducts


class User:
    base = "resources"
    market_id = None

    def __init__(self, id: int, market_id: str = None):
        """
        :param id: int
        """
        self.id = id
        self.s3 = s3.S3(self)
        self.filename = self.s3.get_local_filepath(directory=self.base)
        self._read()
        self.products = self.get_wanted_products()
        if not os.path.exists(self.filename):
            self._create_empty()
        self.market_id = self.get_market_id()

        if not self.s3.exists():
            self._upload()

    def add_market_id(self, market_id):
        self.market_id = market_id

    def get_market_id(self):
        """
        Returns empty market_id if file has no `market_id`/is non existent
        :return: 
        """
        if self.market_id:
            return self.market_id
        try:
            return self._read()['market_id']
        except (KeyError, OSError):
            return ""

    def get_wanted_products(self) -> List[WantedProduct]:
        if os.path.exists(self.filename):
            self.products = WantedProducts(self.filename).get_products()
            return self.products
        else:
            return []

    def _create_empty(self):
        with open(self.filename, "w") as empty:
            json.dump({"market_id": "", "products": []}, empty)

    def add_offer(self, product: WantedProduct):
        self.products.append(product)
        # TODO: do this in a certain interval
        self._write()
        self._upload()

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
