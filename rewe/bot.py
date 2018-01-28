import json
import threading

import schedule
import telegram
from telegram.bot import Bot
from telegram.ext import CommandHandler, Updater

from .logger import Logger
from .offers import OffersWebsite
from .product import TelegramProduct
from .rewe_offers import get
from .user import User
from .wanted import WantedProduct, WantedProducts

users = []
log = Logger("bot", level="DEBUG")
updater = ""


def get_token(filename: str = "secrets.json"):
    global log
    import os

    log.debug("get_token")
    try:
        with open(filename, "r+") as secrets:
            token = json.load(secrets)['token']
    except OSError:
        token = ""

    token = os.getenv("TELEGRAM_BOT_TOKEN", token)

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
    offers = get(market_id=market_id, wanted_filename=wanted_filename, log_level=log.getEffectiveLevel())
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


def why(bot: Bot, update):
    global log
    log.debug("list")
    user = get_user(update)
    product = " ".join(update.message.text.split()[1:])

    wanted_filename = user.filename
    market_id = user.market_id
    log.debug("Filename: %s | MarketID: %s", wanted_filename, market_id)
    offers = get(market_id=market_id, wanted_filename=wanted_filename, log_level=log.getEffectiveLevel(),
                 return_reason=True)
    log.debug("Offers length: %d", len(offers))
    reason = None
    used_offer = None

    for offer, wanted in offers:
        if offer.get_name() == product:
            print("is")
            used_offer = offer
            reason = wanted
            break
    if reason:
        mappings = []
        for mapping in reason.get_mappings():
            formatable = "{}"
            if mapping.lower() in used_offer.get_name().lower():
                formatable = "*{}*"

            mappings.append(formatable.format(mapping))

        mapping_text = "\[{}]".format(", ".join(mappings))
        text = "{} - {}".format(reason.get_name(), mapping_text)
        bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        bot.send_message(chat_id=update.message.chat_id, text="Couldn't find {}".format(product))


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

    if not found:
        log.debug("Not found | Send: %s", user.id)
        bot.send_message(chat_id=update.message.chat_id, text="No", parse_mode=telegram.ParseMode.MARKDOWN)


def list_wanted(bot: Bot, update):
    global log
    log.debug("list_wanted")
    user = get_user(update)
    wanted_filename = user.filename
    wanted_products = WantedProducts(wanted_filename).get_products()

    log.debug("Send: {}".format(user.id))
    bot.send_message(chat_id=update.message.chat_id,
                     text="\n".join(
                         ["{} - {}".format(product.get_name(), product.get_mappings()) for product in wanted_products]),
                     parse_mode=telegram.ParseMode.MARKDOWN)


def add_offer(bot: Bot, update):
    global log
    user = get_user(update)
    log.debug("%s", user.id)
    new_offer = " ".join(update.message.text.split()[1:])
    log.debug("New offer: %s", new_offer)

    id = WantedProducts(user.filename).last_id() + 1
    log.debug("Last id: %d", id)
    wp = WantedProduct.parse_new(id=id, input=new_offer)
    log.debug("Created new product(%d): %s", wp.id, wp.to_json())
    user.add_offer(wp)
    log.debug("Added product %s to user %s", wp.to_json(), user.id)


def remove_offer(bot: Bot, update):
    global log
    user = get_user(update)
    log.debug("%s", user.id)
    to_remove = " ".join(update.message.text.split()[1:])

    if not user.remove_offer_key(to_remove):
        text = "{} is not listed for this user. Please input the complete name of the product (retrievable via `list_wanted`".format(
            to_remove)
        bot.send_message(chat_id=update.message.chat_id, text=text)


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


def post_list_update():
    global log
    global updater
    global users
    log.debug("post_list_update")
    products = []

    for user in users:
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
            updater.bot.send_message(chat_id=user.id, text=sendable, parse_mode=telegram.ParseMode.MARKDOWN,
                                     disable_web_page_preview=True, disable_notification=not first)
            first = False


def run_scheduler():
    global updater
    try:
        schedule.every().monday.at("06:00").do(post_list_update)
        # schedule.every().minute.do(post_list_update)
        while updater is not None:
            schedule.run_pending()
    except Exception as e:
        print(e)


def run(token: str):
    global log
    global updater

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
    dispatcher.add_handler(CommandHandler("remove_offer", remove_offer))
    dispatcher.add_handler(CommandHandler("why", why))

    t = threading.Thread(target=run_scheduler)
    t.start()

    log.debug("Start polling")
    updater.start_polling()
    updater = None


def start():
    run(get_token())
