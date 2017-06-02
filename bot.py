import json
from telegram.ext import CommandHandler, Updater
from rewe_angebote import get


def get_token(filename: str = "secrets.json"):
    with open(filename, "r+") as secrets:
        return json.load(secrets)['token']


def offers(bot, update):
    l = []

    market_id = "1487799323156"
    wanted_filename = "wanted.json"
    for name, price in get(market_id=market_id, wanted_filename=wanted_filename).items():
        l.append("[{}] {}".format(price, name))

    bot.sendMessage(chat_id=update.message.chat_id, text="\n".join(l))


def run(token: str):
    updater = Updater(token=token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("list", offers))

    updater.start_polling()


if __name__ == "__main__":
    run(get_token())
