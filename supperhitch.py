import asyncio
import nest_asyncio
from typing import Final
from telegram import (Update, InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          MessageHandler, filters, ContextTypes)
from telegram.constants import ParseMode
import requests

nest_asyncio.apply()

TOKEN: Final = '7239673940:AAFNjd09l_lAM-mMDott9YziiQBgIYJzR9E' # NEVER SHARE THIS PUBLICLY
BOT_USER: Final = 'SupperHitch_Bot'

# List of Food Stores
STORES_LIST: Final = ["Fong Seng", "AL Amaans"]

#commands
async def start(update: Update, context : ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(text=f"Hello {user.mention_markdown_v2()}\!"
                                        f"\n What would you like to eat today?",
                                    parse_mode=ParseMode.MARKDOWN_V2)
    
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(text=f'This shows the list of commands'
                                         f' this bot has.')

async def viewcart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass

async def stores(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [   
            InlineKeyboardButton(text="Al Amaans", callback_data="Al Amaans"),
            InlineKeyboardButton(text="Ban Mian", callback_data="Ban Mian"),
            InlineKeyboardButton(text="Niggas", callback_data="Nikkis"),
        ],
        [
            InlineKeyboardButton(text="Ban Mian", callback_data="Ban Mian"),
            InlineKeyboardButton(text="Nana Thai", callback_data="Nana Thai"),
            InlineKeyboardButton(text="Formosa", callback_data="Formosa"),
        ],
        [   
            InlineKeyboardButton(text="Fong Seng", callback_data="Fong Seng"),
            InlineKeyboardButton(text="Hong Kong", callback_data="Hong Kong"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text="Which menu would you like to view?", reply_markup=reply_markup)

#helper functions
penis penis penis


#running the shit
if __name__ == '__main__':
    # Initializes your bot with the token!
    app = Application.builder().token(TOKEN).build()

    # Commands 
    # Left side is name of command user needs to type in, right side is name of function
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help))
    app.add_handler(CommandHandler('stores', stores))


    # Message Handlers
    #app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Callback - we'll come back to this!
    #app.add_handler(CallbackQueryHandler(display_focus_area))

    # Error Handlers
    #app.add_error_handler(error)

    # Polls the bot
    print('Polling...')
    asyncio.run(app.run_polling())
