import json

import telegram
from telegram.bot import Bot
from telegram.ext import CommandHandler, Updater

from .logger import Logger
from .offers import OffersWebsite
from .product import TelegramProduct
from .rewe_offers import get
from .user import User
from .wanted import WantedProducts

users = []
log = Logger("bot", level="DEBUG")


def get_token(filename: str = "secrets.json"):
    global log
    log.debug("get_token")
    with open(filename, "r+") as secrets:
        token = json.load(secrets)['token']

    log.debug("Token length: %d", len(token))
    return token


def get_user(update) -> User:
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
        log.debug("Creating new user: %s", chat_id)
        user = User(chat_id, log_level=log.getEffectiveLevel())
        log.debug("Created user: %s", chat_id)
        users.append(user)

    return user


def _split_messages(products):
    message_length = 4096
    messages = []
    current_length = 0
    current_message = 0
    for product in products:
        if len(messages) <= current_message:
            messages.append([])

        product_length = len(product)
        if current_length + product_length < message_length:
            current_length += product_length
            messages[current_message].append(product)
        else:
            current_length = 0
            current_message += 1

    return messages


def _get_product_printable_np(name: str, price: float):
    bold_price = "*{}*".format(price)
    return "\[{}] {}".format(bold_price, name)


def _get_product_printable(offer):
    return TelegramProduct.from_offer(offer).get()


def offers(bot: Bot, update):
    global log
    log.debug("list")
    user = get_user(update)
    products = []

    wanted_filename = user.filename
    market_id = user.market_id
    log.debug("Filename: %s | MarketID: %s", wanted_filename, market_id)
    offers = get(market_id=market_id, wanted_filename=wanted_filename)
    log.debug("Found %d offers", len(offers))
    for offer in offers:
        products.append(_get_product_printable(offer))

    messages = _split_messages(products)

    log.debug("Send %d messages: %s", len(messages), user.id)
    first = True
    for message in messages:
        sendable = "\n".join(message)
        bot.send_message(chat_id=update.message.chat_id, text=sendable, parse_mode=telegram.ParseMode.MARKDOWN,
                         disable_web_page_preview=True, disable_notification=not first)
        first = False


def list_all(bot: Bot, update):
    global log
    log.debug("list_all")
    user = get_user(update)
    products = []

    market_id = user.market_id
    log.debug("MarketID: %s", market_id)
    offers = OffersWebsite(market_id, log_level=log.getEffectiveLevel()).get_offers()
    log.debug("Found %d offers", len(offers))
    for offer in offers:
        products.append(_get_product_printable(offer))

    messages = _split_messages(products)

    log.debug("Send %d messages: %s", len(messages), user.id)
    first = True
    for message in messages:
        sendable = "\n".join(message)
        bot.send_message(chat_id=update.message.chat_id, text=sendable, parse_mode=telegram.ParseMode.MARKDOWN,
                         disable_web_page_preview=True, disable_notification=not first)
        first = False


def is_offer(bot: Bot, update):
    global log
    log.debug("is_offer")
    user = get_user(update)
    wanted_product = " ".join(update.message.text.split()[1:])
    log.debug("Wanted product: %s", wanted_product)
    if not wanted_product:
        bot.send_message(chat_id=update.message.chat_id, text="How about specifying a product?",
                         parse_mode=telegram.ParseMode.MARKDOWN)
        return
    market_id = user.market_id
    log.debug("MarketID: %s", market_id)
    found = False
    offers = OffersWebsite(market_id, log_level=log.getEffectiveLevel()).get_offers()
    log.debug("Found %d offers", len(offers))
    for offer in offers:
        name = offer.get_name()
        price = offer.get_price()
        if wanted_product in name.lower():
            found = True
            bot.send_message(chat_id=update.message.chat_id, text=_get_product_printable_np(name, price),
                             parse_mode=telegram.ParseMode.MARKDOWN)
            break

    if not found:
        log.debug("Not found | Send: %s", user.id)
        bot.send_message(chat_id=update.message.chat_id, text="No", parse_mode=telegram.ParseMode.MARKDOWN)


def list_wanted(bot: Bot, update):
    global log
    log.debug("list_wanted")
    user: User = get_user(update)
    wanted_filename = user.filename
    wanted_products = WantedProducts(wanted_filename).get_products()

    log.debug("Send: {}".format(user.id))
    bot.send_message(chat_id=update.message.chat_id,
                     text="\n".join([product.get_name() for product in wanted_products]),
                     parse_mode=telegram.ParseMode.MARKDOWN)


def add_offer(bot: Bot, update):
    global log
    user = get_user(update)
    log.debug("%s", user.id)


def set_market_id(bot: Bot, update):
    global log
    log.debug("set_market_id")
    market_id = " ".join(update.message.text.split()[1:])
    user = get_user(update)
    if user:
        log.debug("Assign market_id: %s", user.id)
        user.add_market_id(market_id)
        log.debug("Assigned market_id: %s", user.id)


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
    dispatcher.add_handler(CommandHandler("add_offer", add_offer))

    log.debug("Start polling")
    updater.start_polling()


def start():
    run(get_token())
