import json
from telegram.bot import Bot
from telegram.ext import CommandHandler, Updater
from .rewe_offers import get
from .wanted import WantedProducts


def get_token(filename: str = "secrets.json"):
    with open(filename, "r+") as secrets:
        return json.load(secrets)['token']


def offers(bot: Bot, update):
    # TODO: Add markdown
    def _get_product_printable(name: str, price: float):
        bold_price = "**{}**".format(price)
        return "[{}] {}".format(bold_price, name)

    products = []

    market_id = "1487799323156"
    wanted_filename = "wanted.json"
    for name, price in get(market_id=market_id, wanted_filename=wanted_filename).items():
        products.append(_get_product_printable(name, price))

    bot.send_message(chat_id=update.message.chat_id, text="\n".join(products))


def list_wanted(bot: Bot, update):
    wanted_filename = "wanted.json"
    wanted_products = WantedProducts(wanted_filename).get_products()

    bot.send_message(chat_id=update.message.chat_id,
                     text="\n".join([product.get_name() for product in wanted_products]))


def run(token: str):
    updater = Updater(token=token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("list", offers))
    dispatcher.add_handler(CommandHandler("list_wanted", list_wanted))

    updater.start_polling()


if __name__ == "__main__":
    run(get_token())
