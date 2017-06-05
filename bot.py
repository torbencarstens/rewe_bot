import json

import telegram
from telegram.bot import Bot
from telegram.ext import CommandHandler, Updater

from offers import OffersWebsite
from rewe_offers import get
from wanted import WantedProducts


def get_token(filename: str = "secrets.json"):
    with open(filename, "r+") as secrets:
        return json.load(secrets)['token']


# TODO: Add markdown
def _get_product_printable(name: str, price: float):
    bold_price = "*{}*".format(price)
    return "\[{}] {}".format(bold_price, name)


def offers(bot: Bot, update):
    products = []

    market_id = "1487799323156"
    wanted_filename = "wanted.json"
    for name, price in get(market_id=market_id, wanted_filename=wanted_filename).items():
        products.append(_get_product_printable(name, price))

    bot.send_message(chat_id=update.message.chat_id, text="\n".join(products), parse_mode=telegram.ParseMode.MARKDOWN)


def list_all(bot: Bot, update):
    products = []

    market_id = "1487799323156"
    offers = OffersWebsite(market_id).get_offers()
    for offer in offers:
        name, price = offer.get().values()
        products.append(_get_product_printable(name, price))

    bot.send_message(chat_id=update.message.chat_id, text="\n".join(products), parse_mode=telegram.ParseMode.MARKDOWN)


def is_offer(bot: Bot, update):
    wanted_product = " ".join(update.message.text.split()[1:])
    if not wanted_product:
        bot.send_message(chat_id=update.message.chat_id, text="How about specifying a product?",
                         parse_mode=telegram.ParseMode.MARKDOWN)
    market_id = "1487799323156"

    found = False
    for offer in OffersWebsite(market_id).get_offers():
        name, price = offer.get().values()
        if wanted_product in name.lower():
            found = True
            bot.send_message(chat_id=update.message.chat_id, text=_get_product_printable(name, price),
                             parse_mode=telegram.ParseMode.MARKDOWN)
            break

    if not found:
        bot.send_message(chat_id=update.message.chat_id, text="No",
                         parse_mode=telegram.ParseMode.MARKDOWN)


def list_wanted(bot: Bot, update):
    wanted_filename = "wanted.json"
    wanted_products = WantedProducts(wanted_filename).get_products()
    bot.send_message(chat_id=update.message.chat_id,
                     text="\n".join([product.get_name() for product in wanted_products]),
                     parse_mode=telegram.ParseMode.MARKDOWN)


def run(token: str):
    updater = Updater(token=token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("list", offers))
    dispatcher.add_handler(CommandHandler("list_all", list_all))
    dispatcher.add_handler(CommandHandler("list_wanted", list_wanted))
    dispatcher.add_handler(CommandHandler("is_offer", is_offer))

    updater.start_polling()


if __name__ == "__main__":
    run(get_token())
