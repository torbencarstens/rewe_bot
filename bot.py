import json
import telegram
from telegram.ext import CommandHandler, Updater
from rewe_angebote import get


def get_token(filename: str = "secrets.json"):
    with open(filename, "r+") as secrets:
        return json.load(secrets)['token']


def offers(bot, update):
    l = []
    for offer in get():
        l.append("[{}] {}".format(*offer.values()))

    bot.sendMessage(chat_id=update.message.chat_id, text="\n".join(l))


def start(token: str):
    bot = telegram.Bot(token)

    updater = Updater(token=token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("list", offers))

    updater.start_polling()

if __name__ == "__main__":
    start(get_token())
