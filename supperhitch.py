import asyncio
import nest_asyncio
from typing import Final
from telegram import (Update, InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler, CallbackContext,
                          MessageHandler, filters, ContextTypes)
from telegram.constants import ParseMode
import requests

nest_asyncio.apply()

TOKEN: Final = '7239673940:AAG34wNYJ3wUmvfernb_0Bv5TzsaVvRqfTY' # NEVER SHARE THIS PUBLICLY
BOT_USER: Final = 'SupperHitch_Bot'

# List of Food Stores
STORES_LIST: Final = ["Fong Seng", "AL Amaans"]

#User Cart
cart = []

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
    if cart == []:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Cart is currently empty!")
    else:
        #cart_contents = "\n".join([f"{item['name']}: ${item['price']}" for item in cart])
        message = f"Your Cart:\n{cart}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

async def addcart(update: Update, context: CallbackContext) -> None:
    args = context.args
    if len(args) != 1:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please do /add (item_id)")
        return
    
    item_id = args[0]
    #CHANGE THIS LATER
    cart.append(item_id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Item {item_id} added to cart!")

async def removecart(update: Update, context: CallbackContext) -> None:
    args = context.args
    if len(args) != 1:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please do /add (item_id)")
        return
    remove_item = args[0]
    if remove_item in cart:
        cart.remove(remove_item)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Item {remove_item} removed from cart!")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Item {remove_item} is not in the cart.")


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
    query = update.callback_query
    callback_data = query.data
    print(f"Received callback query with data:{callback_data}")
    


#helper functions
async def store_button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if query:
        # Acknowledge the callback
        await query.answer()

        # Get the callback data
        callback_data = query.data
        print(f"Received callback query with data: {callback_data}")
        await print_menu(update, context, callback_data)
    else:
        print("No valid callback_query found.")

async def print_menu(update: Update, context: CallbackContext, store):
    if store == "Nana Thai":
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Showing Nana Thai Menu")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Deez nutz")


#running the shit
if __name__ == '__main__':
    # Initializes your bot with the token!
    app = Application.builder().token(TOKEN).build()

    # Commands 
    # Left side is name of command user needs to type in, right side is name of function
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help))
    app.add_handler(CommandHandler('stores', stores))
    app.add_handler(CommandHandler('add', addcart))
    app.add_handler(CommandHandler('remove', removecart))
    app.add_handler(CommandHandler('viewcart', viewcart))
    app.add_handler(CallbackQueryHandler(store_button_click))
    


    # Message Handlers
    #app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Callback - we'll come back to this!
    #app.add_handler(CallbackQueryHandler(display_focus_area))

    # Error Handlers
    #app.add_error_handler(error)

    # Polls the bot
    print('Polling...')
    asyncio.run(app.run_polling())
