class Product:
    name = None
    price = None

    def __init__(self, *, name: str, picture_link: str = None, price: float = None):
        self.name = name
        self.picture_link = picture_link
        self.price = price


class TelegramProduct(Product):
    def __init__(self, *, name: str, picture_link: str = None, price: float = None):
        super().__init__(name=name, picture_link=picture_link, price=price)

    @classmethod
    def from_offer(cls, offer):
        name = offer.name
        price = offer.price
        picture_link = offer.picture_link

        return cls(name=name, price=price, picture_link=picture_link)

    def get(self, *, markdown: bool = True, picture_link: bool = True):
        if picture_link and not markdown:
            raise AttributeError("Can't add link without markdown.")

        result = "{} {}".format(self._price(markdown), self._name(picture_link))

        return result

    def _price(self, markdown: bool = True):
        printable = "{}[{}{}{}]"
        substitution = ["", "", self.price, ""]

        if markdown:
            substitution[0] = "\\"
            substitution[1] = "*"
            substitution[3] = "*"

        return printable.format(*substitution)

    def _name(self, picture_link: bool = True):
        printable = "{}"

        if picture_link and self.picture_link:
            printable = "[{}]({})".format("{}", self.picture_link)

        return printable.format(self.name)
