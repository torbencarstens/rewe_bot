import requests
from bs4 import BeautifulSoup, PageElement
import re
from typing import Dict, Generator, List, Union


def get_market_content(url) -> Union[bytes, str]:
    req = requests.get(url)
    return req.content


def get_soup(content) -> BeautifulSoup:
    return BeautifulSoup(content, "html.parser")


def get_products_outer(soup: BeautifulSoup) -> List[PageElement]:
    return soup.find_all(class_="controller product")


def get_product(product_outer) -> Dict[str, str]:
    product_text_raw = product_outer.find(class_='dotdot').find('div').text
    product_text_splitted = product_text_raw.split("\n")
    product_text_oneline = " ".join(product_text_splitted)
    return re.sub("\s+", " ", product_text_oneline)


def get_picture_link(product_outer) -> str:
    return product_outer.find('img')['href']


def get_picture(link) -> Union[bytes, str]:
    return requests.get(link).content


def get_price(product_outer) -> float:
    return float(re.findall(r"\d+.*", product_outer.find(class_='price').text)[0])


def get_products(raw_products) -> Generator[Dict[str, str], None, None]:
    for raw_product in raw_products:
        yield {"price": get_price(raw_product), "name": get_product(raw_product)}


def read_offers_json(filename="angebote.json"):
    import codecs
    import json

    with codecs.open(filename, "r+", "utf-8") as angebote:
        return json.load(angebote)


def get_acceptable_offers_json(d) -> List[Dict[str, List[str]]]:
    for product in d['products']:
        for product_name, value in product.items():
            product_mapping = value['mappings']
            yield {'name': product_name, 'mappings': product_mapping}


def get_acceptable_offers(products) -> Generator[Dict, None, None]:
    acceptable_offers = read_offers_json()
    acceptable_offers = list(get_acceptable_offers_json(acceptable_offers))
    for product in products:
        for acceptable_offer in acceptable_offers:
            for alias in acceptable_offer['mappings']:
                if alias.lower() in product['name'].lower():
                    yield product


def get():
    base_url = "https://www.rewe.de/angebote/?marketChosen="
    market_id = "1487799323156"
    url = base_url + market_id
    content = get_market_content(url)
    soup = get_soup(content)
    outer_products = get_products_outer(soup)

    # noinspection PyTypeChecker
    products = list(set(get_products(outer_products)))
    products.sort(key=lambda product: product["price"])
    # print(products)
    # noinspection PyTypeChecker
    return get_acceptable_offers(products)

if __name__ == "__main__":
    # noinspection PyTypeChecker
    for offer in get():
        print("[{}] {}".format(*offer.values()))
