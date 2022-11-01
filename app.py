from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters
import requests
import urllib.parse
import os

token = os.getenv("token")
symbol = ""
updater = Updater(token, use_context=True)


def start(update: Update, context: CallbackContext):
	update.message.reply_text(
		"Enter stock symbol to get quote")

def help(update: Update, context: CallbackContext):
	update.message.reply_text("""
    Enter stock symbol to get current price.
	
	""")

def lookup(symbol):
    """Look up quote for symbol."""
    
    # Contact API
    try:
        api_key = os.getenv("API_KEY")
        url = f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        pass

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return {
            "name": "Invalid",
            "price": "Invalid",
            "symbol": "Invalid"
        }

def getQuote(update: Update, context: CallbackContext):
    global symbol
    symbol = update.message.text
    # update.message.reply_text("Sorry '%s' is not a valid command" % update.message.text)
    quote = lookup(symbol)
    price = quote["name"] +  " stock: $"+ str(quote["price"])
    update.message.reply_text(price)
        


def unknown_text(update: Update, context: CallbackContext):
	update.message.reply_text(
		"Sorry I can't recognize you , you said '%s'" % update.message.text)


updater.dispatcher.add_handler(CommandHandler('start', start))
# updater.dispatcher.add_handler(CommandHandler('tesla', stock_quote))
updater.dispatcher.add_handler(CommandHandler('help', help))

updater.dispatcher.add_handler(MessageHandler(Filters.text, getQuote))
updater.dispatcher.add_handler(MessageHandler(
	Filters.command, getQuote)) # Filters out unknown commands

# Filters out unknown messages.
updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown_text))

updater.start_polling()
