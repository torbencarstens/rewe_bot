import json
import os
from typing import List, Dict

from . import s3, wanted
from .logger import Logger
from .wanted import WantedProduct, WantedProducts


class User:
    base = "resources"
    market_id = None

    def __init__(self, id: int, log_level: str = "INFO"):
        """
        :param id: int
        """
        self.log = Logger("User", level=log_level)
        self.log.debug("Create user: %s", id)

        self.id = id
        self.s3 = s3.S3(self, log_level=log_level)
        self.filename = self.s3.get_local_filepath(directory=self.base)
        self.log.debug("Filename(%s) for user: %s", self.filename, id)
        self._read()
        self.log.debug("Successfully read from %s for user: %s", self.filename, id)
        self.products = self.get_wanted_products()
        self.log.debug("Number of relevant products %d for user: %s", len(self.products), id)
        self.market_id = self.get_market_id()
        self.log.debug("MarketID %s for user: %s", self.market_id, id)

        self.log.debug("Created user: %s", id)

    def add_market_id(self, market_id):
        self.market_id = market_id
        self._write()

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
        products = wanted.to_json(self.products)
        market_id = {"market_id": self.market_id}
        complete = {}
        complete.update(products)
        complete.update(market_id)

        with open(self.filename, "w") as resource:
            json.dump(complete, resource, indent=2)

    def _upload(self, *, base_directory: str = None) -> bool:
        if self.market_id or self.products:
            self.log.debug("Upload")
            self.s3.upload(directory=base_directory)
            self.log.debug("Uploaded")
            return True

        return False

    def _download(self, *, base_directory: str = None):
        self.s3.download(directory=base_directory)

    def _read(self) -> Dict:
        if not os.path.exists(self.filename):
            self.s3.exists()

        try:
            with open(self.filename, "r") as resource:
                return json.load(resource)
        except OSError:
            self._create_empty()
