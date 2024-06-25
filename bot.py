import asyncio
import nest_asyncio
from typing import Final
from telegram import (Update, InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          MessageHandler, filters, ContextTypes)
from telegram.constants import ParseMode
import requests

nest_asyncio.apply()

# Replace the strings with your bot's info!
TOKEN: Final = '7239673940:AAFNjd09l_lAM-mMDott9YziiQBgIYJzR9E' # NEVER SHARE THIS PUBLICLY
BOT_USER: Final = 'SupperHitch_Bot'

# List of Module Codes for CS Focus Area Primaries
PRIMARIES_LIST: Final = [
    ['CS3230', 'CS3231', 'CS3236', 'CS4231', 'CS4234'],            # Algo
    ['CS2109S', 'CS3263', 'CS3264', 'CS4243', 'CS4246', 'CS4248'], # AI
    ['CS3241', 'CS3242', 'CS3247', 'CS4247', 'CS4350'],            # Games
    ['CS2107', 'CS3235', 'CS4236', 'CS4230', 'CS4238', 'CS4239'],  # Security
    ['CS2102', 'CS3223', 'CS4221', 'CS4224', 'CS4225'],            # Database
    ['CS2108', 'CS3245', 'CS4242', 'CS4248', 'CS4347'],            # MIR
    ['CS2105', 'CS3103', 'CS4222', 'CS4226', 'CS4231'],            # Networks
    ['CS3210', 'CS3211', 'CS4231', 'CS4223'],                      # Parallel
    ['CS2104', 'CS3211', 'CS4212', 'CS4215'],                      # Languages
    ['CS2103T', 'CS3213', 'CS3219', 'CS4211', 'CS4218', 'CS4239']  # SWE
]

# THIS HAS BEEN DONE FOR YOU
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(text=f'Hello {user.mention_markdown_v2()}\!'
                                         f'\nEnter /help to see the list of '
                                         f'commands for this bot\.',
                                    parse_mode=ParseMode.MARKDOWN_V2)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f'Update {update}  caused error {context.error}')

# TODO: What should the /help command do?
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows the list of commands this bot has."""
    """We'll deal with this when we're done with everything."""
    await update.message.reply_text(text=f'This shows the list of commands'
                                         f'this bot has.')

# TODO: Let's try handling user input with something that requires a bit more
#       logic - what about the quadratic formula?

import math

async def quadratic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # This will give us all the words in the message

    # extract the message from the user input
    # e.g. /quadratic 1 2 3

    #to get the message input by the user
    message = update.message.text

    arguments = message.split("") #['/quadratic', '1', '2', '3']

    terms = arguments[1:] #['1', '2', '3']
    terms = list(map(lambda x: float(x), terms)) #[1, 2, 3]

    a = terms[0]
    b = terms[1]
    c = terms[2]

    #calculate the discriminant
    disc = b**2 - 4*a*c

    # TODO: Find Roots
    # assume 2 real solutions
    # can add conditional statements for edge cases (imaginary solution/ 1 real root)

    root1 = (-b + math.sqrt(disc)) / 2*a
    root2 = (-b - math.sqrt(disc)) / 2*a

    # TODO: Create the reply text
    reply = f"Your roots are {root1} and {root2}"

    update.message.reply_text(reply)
    #await update.message.reply_text(text=reply)

# TODO: Let's handle any user input without a command associated!
def handle_response(text: str) -> str:
    for focus_area in PRIMARIES_LIST:
      if text in focus_area:
        return display_module(requests.get(f'https://api.nusmods.com/v2/2023-2024/modules/{text}.json').json())
    return 'Sorry, I do not have information on that module...'


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_type: str = update.message.chat.type # Private? Group?
    text: str = update.message.text              # Message content

    # Logging user input on local terminal
    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    # Handle that response!
    response: str = handle_response(text)

    # Logging bot's response on local terminal
    print('Bot:', response)

    # TODO: Make the bot reply with your response!
    await update.message.reply_text(response)

def get_mod_title(module_code: str) -> str:
  endpoint = f'https://api.nusmods.com/v2/2023-2024/modules/{module_code}.json'
  response = requests.get(endpoint)
  description = response.json()
  title = description['title']
  return title

get_mod_title('EL1101E')

if __name__ == '__main__':
    # Initializes your bot with the token!
    app = Application.builder().token(TOKEN).build()

    # Commands TODO: Add Handlers for /quadratic and /focusarea (later)
    # Left side is name of command user needs to type in, right side is name of function
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help))
    app.add_handler(CommandHandler('quadratic', quadratic))
    #app.add_handler(CommandHandler('focusarea', focusarea))


    # Message Handlers
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Callback - we'll come back to this!
    #app.add_handler(CallbackQueryHandler(display_focus_area))

    # Error Handlers
    app.add_error_handler(error)

    # Polls the bot
    print('Polling...')
    asyncio.run(app.run_polling())


