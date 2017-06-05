import json

import telegram
from telegram.bot import Bot
from telegram.ext import CommandHandler, Updater

from .logger import Logger
from .offers import OffersWebsite
from .rewe_offers import get
from .user import User
from .wanted import WantedProducts

users = []
log = Logger("bot")


def get_token(filename: str = "secrets.json"):
    global log
    log.debug("get_token")
    with open(filename, "r+") as secrets:
        token = json.load(secrets)['token']

    log.debug("Token length: {}".format(len(token)))
    return token


def get_user(bot, update) -> User:
    global log
    log.debug("get_user")
    global users
    chat_id = update.message.chat_id
    user = None
    for i_user in users:
        if i_user.id == chat_id:
            user = i_user
            log.debug("Found existing user")
            break

    if not user:
        log.debug("Creating new user: {}".format(chat_id))
        user = User(chat_id)
        users.append(user)
        log.debug("Created user: {}".format(chat_id))

    return user


# TODO: Add markdown
def _get_product_printable(name: str, price: float):
    bold_price = "*{}*".format(price)
    return "\[{}] {}".format(bold_price, name)


def offers(bot: Bot, update):
    global log
    log.debug("list")
    user = get_user(bot, update)
    products = []

    wanted_filename = user.filename
    market_id = user.market_id
    for name, price in get(market_id=market_id, wanted_filename=wanted_filename).items():
        products.append(_get_product_printable(name, price))

    log.debug("Send: {}".format(user.id))
    bot.send_message(chat_id=update.message.chat_id, text="\n".join(products), parse_mode=telegram.ParseMode.MARKDOWN)


def list_all(bot: Bot, update):
    global log
    log.debug("list_all")
    print("list_all")
    user = get_user(bot, update)
    products = []

    market_id = user.market_id
    offers = OffersWebsite(market_id).get_offers()
    for offer in offers:
        name, price = offer.get().values()
        products.append(_get_product_printable(name, price))

    log.debug("Send: {}".format(user.id))
    bot.send_message(chat_id=update.message.chat_id, text="\n".join(products), parse_mode=telegram.ParseMode.MARKDOWN)


def is_offer(bot: Bot, update):
    global log
    log.debug("is_offer")
    user = get_user(bot, update)
    wanted_product = " ".join(update.message.text.split()[1:])
    if not wanted_product:
        bot.send_message(chat_id=update.message.chat_id, text="How about specifying a product?",
                         parse_mode=telegram.ParseMode.MARKDOWN)
        return
    market_id = user.market_id

    found = False
    for offer in OffersWebsite(market_id).get_offers():
        name, price = offer.get().values()
        if wanted_product in name.lower():
            found = True
            bot.send_message(chat_id=update.message.chat_id, text=_get_product_printable(name, price),
                             parse_mode=telegram.ParseMode.MARKDOWN)
            break

    if not found:
        log.debug("Send: {}".format(user.id))
        bot.send_message(chat_id=update.message.chat_id, text="No",
                         parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        log.debug("Not found offer({}): {}".format(wanted_product, user.id))


def list_wanted(bot: Bot, update):
    global log
    log.debug("list_wanted")
    user: User = get_user(bot, update)
    wanted_filename = user.filename
    wanted_products = WantedProducts(wanted_filename).get_products()

    log.debug("Send: {}".format(user.id))
    bot.send_message(chat_id=update.message.chat_id,
                     text="\n".join([product.get_name() for product in wanted_products]),
                     parse_mode=telegram.ParseMode.MARKDOWN)


def set_market_id(bot: Bot, update):
    global log
    log.debug("set_market_id")
    market_id = " ".join(update.message.text.split()[1:])
    user = get_user(bot, update)
    if user:
        log.debug("Assign market_id: {}".format(user.id))
        user.add_market_id(market_id)
        log.debug("Assigned market_id: {}".format(user.id))


def status(bot: Bot, update):
    log.debug("status")
    bot.send_message(chat_id=update.message.chat_id, text="[{}] Functional".format(update.message.chat_id))


def run(token: str):
    global log
    log.debug("Start bot")
    updater = Updater(token=token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("list", offers))
    dispatcher.add_handler(CommandHandler("list_all", list_all))
    dispatcher.add_handler(CommandHandler("list_wanted", list_wanted))
    dispatcher.add_handler(CommandHandler("is_offer", is_offer))
    dispatcher.add_handler(CommandHandler("set_market_id", set_market_id))
    dispatcher.add_handler(CommandHandler("status", status))

    log.debug("Start polling")
    updater.start_polling()


def start():
    run(get_token())
