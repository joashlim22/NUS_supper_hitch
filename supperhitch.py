import asyncio
import nest_asyncio
from typing import Final
from telegram import (Update, InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler, CallbackContext,
                          MessageHandler, filters, ContextTypes)
from telegram.constants import ParseMode
import requests
import supabase
import bcrypt
import postgrest

nest_asyncio.apply()

TOKEN: Final = 
BOT_USER: Final = 'SupperHitch_Bot'
supabase_url = 'https://vsfnugzfivmidxcareah.supabase.co'
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZzZm51Z3pmaXZtaWR4Y2FyZWFoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTkzOTYzODIsImV4cCI6MjAzNDk3MjM4Mn0.F0FVjkcnDMvURNWGEgVMvx3clPNpWWavTsvJf1KU3ks"
supabase_client = supabase.create_client(supabase_url, supabase_key)

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
    
async def register_user(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 2:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please do /register (email) (password) \nIf you are already a user do /login (email) (password) instead!")
        return
    try:
        users_email = context.args[0]
        users_password = context.args[1]
        hashed_password = hash_password(users_password)
        new_user = supabase_client.auth.sign_up({ "email": users_email, "password": users_password }) #test hashed pw
    except Exception as e:
        print(e)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="error! sowwy")
        return
    else:
       await context.bot.send_message(chat_id=update.effective_chat.id, text="Successful Registration, please confirm in your email!")
       return
    
async def login_user(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 2:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please do /login (email) (password) \nIf you are not a user yet do /register (email) (password) instead!")
        return
    
    try:
        users_email = context.args[0]
        users_password = context.args[1]
        user = supabase_client.auth.sign_in_with_password({ "email": users_email, "password": users_password })
    except Exception as e:
        print(e)
        if e == "Invalid login credentials":
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid Email / Password")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="error! sowwy")
        return
    else:
       await context.bot.send_message(chat_id=update.effective_chat.id, text="Successful login YIPPIE!")
       return
    

async def viewcart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if await login_status(update, context) == False:
        return
    
    user = update.effective_user.id
    result = supabase_client.table("user_cart").select("*").eq("user_id", str(user)).execute()
    if len(result.data) == 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Cart is currently empty!")
        return False
    else:
        cart_contents = "\n".join([f"Item ID:{item['item_id']}, {item['item_qty']} {item['item_name']} - ${item['unit_price'] * item['item_qty']:.2f}" for item in result.data])
        message = f"Your Cart:\n{cart_contents}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        return True

async def addcart(update: Update, context: CallbackContext) -> None:
    if await login_status(update, context) == False:
        return
    
    args = context.args
    user = update.effective_user.id
    if len(args) != 2:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please do /add (item_id) (qty)")
        return
    
    item_id = args[0]
    item_qty = int(args[1])
    food_name = await getfoodname(item_id)
    food_price = await getfoodprice(item_id)
    if food_name == None:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid Item ID")
        return
    
    try:
        # Check if the item is already in the cart
        result = supabase_client.table("user_cart").select("*").eq("user_id", str(user)).eq("item_id", item_id).execute()
        print(result)
        if len(result.data) > 0:
            # If item exists, update the quantity
            current_qty = result.data[0]["item_qty"]
            new_qty = current_qty + item_qty
            update_result = supabase_client.table("user_cart").update({"item_qty": new_qty}).eq("user_id", str(user)).eq("item_id", item_id).execute()
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Item {food_name} updated to {new_qty} in cart!")
            await viewcart(update, context)
        else:
            # If item does not exist, insert new item
            insert_result = supabase_client.table("user_cart").insert({"user_id": user, "item_id": item_id, "item_name": food_name, "item_qty": item_qty, "unit_price": food_price}).execute()
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Item {food_name} added to cart!")
            await viewcart(update, context)
    
    except postgrest.exceptions.APIError as e:
        print(f"PostgREST APIError occurred: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error, are you logged in?")
    except Exception as e:
        print(f"Error occurred: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Error occurred while processing your request.")

async def removecart(update: Update, context: CallbackContext) -> None:
    if await login_status(update, context) == False:
        return
    
    args = context.args
    if len(args) != 2:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please do /remove (item_id) (item_qty)")
        return
    
    item_id = args[0]
    item_qty = int(args[1])
    user = update.effective_user.id

    try:
        # Check if the item exists in the cart
        result = supabase_client.table("user_cart").select("*").eq("user_id", str(user)).eq("item_id", item_id).execute()
        if len(result.data) > 0:
            current_qty = result.data[0]["item_qty"]
            new_qty = current_qty - item_qty
            if new_qty <= 0:
                delete_result = supabase_client.table("user_cart").delete().eq("user_id", str(user)).eq("item_id", item_id).execute()
            else:
                update_result = supabase_client.table("user_cart").update({"item_qty": new_qty}).eq("user_id", str(user)).eq("item_id", item_id).execute()
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Item {item_id} quantity updated to {new_qty} in cart!")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Item {item_id} is not in the cart.")
    
    except postgrest.exceptions.APIError as e:
        print(f"PostgREST APIError occurred: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Error occurred while processing your request.")
    except Exception as e:
        print(f"Error occurred: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Error occurred while processing your request.")
        
async def clearcart(update: Update, context: CallbackContext) -> None:
    if await login_status(update, context) == False:
        return
    
    user = update.effective_user.id
    result = supabase_client.table("user_cart").select("*").eq("user_id", str(user)).execute()
    if len(result.data) > 0:
        delete_result = supabase_client.table("user_cart").delete().eq("user_id", str(user)).execute()
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Cart has been cleared!")
        

async def stores(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [   
            InlineKeyboardButton(text="Al Amaans", callback_data="Al Amaans"),
            InlineKeyboardButton(text="Ban Mian", callback_data="Ban Mian"),
            InlineKeyboardButton(text="Fong Seng", callback_data="Fong Seng"),
        ],
        [
            InlineKeyboardButton(text="Formosa", callback_data="Formosa"),
            InlineKeyboardButton(text="Hong Kong", callback_data="Hong Kong"),

        ],
        [   
            InlineKeyboardButton(text="Nana Thai", callback_data="Nana Thai"),
            InlineKeyboardButton(text="Niggas",  callback_data="Nikkis"),            
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text="Which menu would you like to view?", reply_markup=reply_markup)
    query = update.callback_query
    callback_data = query.data
    view_menu(update, context, callback_data)
    print(f"Received callback query with data:{callback_data}")
    

async def submit_order(update: Update, context: CallbackContext) -> None:
    #if user is not logged in
    if await login_status(update, context) == False:
        return
    #if cart is empty
    if viewcart(update, context) == False:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Cart is currently empty!")
        return
        
    user = update.effective_user.id
    price = 0.0
    result = supabase_client.table("user_cart").select("*").eq("user_id", str(user)).execute().data
    order = "\n".join([f"Item ID: {item['item_id']}, {item['item_name']}, Quantity: {item['item_qty']}" for item in result])

#helper functions
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

async def store_button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if query:
        # Acknowledge the callback
        await query.answer()

        # Get the callback data
        callback_data = query.data
        print(f"Received callback query with data: {callback_data}")
        await view_menu(update, context, callback_data)
    else:
        print("No valid callback_query found.")

async def view_menu(update: Update, context: CallbackContext, store):
    result = supabase_client.table(store).select("*").execute().data
    formatted_message =""
    for item in result:
        item_id = item['item_id']
        item_name = item['item_name']
        item_price = item['item_price']
        formatted_message += f"Item ID: {item_id}\nItem Name: {item_name}\nPrice: ${item_price}\n\n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=formatted_message)
    

async def login_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_session = supabase_client.auth.get_session()
    if current_session == None:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="User is not signed in!")
        return False
    return True

async def getfoodname(item_id):
    item_id = int(item_id)
    store_name = await getstorename(item_id)
    result = supabase_client.table(store_name).select("*").eq("item_id", item_id).execute()
    try:
        food_name = result.data[0]["item_name"]
    except IndexError:
        food_name =  None
    finally:
        return food_name
    
async def getfoodprice(item_id):
    item_id = int(item_id)
    store_name = await getstorename(item_id)
    result = supabase_client.table(store_name).select("*").eq("item_id", item_id).execute()
    try:
        food_price = result.data[0]["item_price"]
    except IndexError:
        food_price =  None
    finally:
        return food_price

async def getstorename(item_id):
    if item_id >= 600:
        return "Nikkis"
    elif item_id >= 500:
        return "Nana Thai"
    elif item_id >= 400:
        return "Hong Kong"
    elif item_id >= 300:
        return "Formosa"
    elif item_id >= 200:
        return "Fong Seng"
    elif item_id >= 100:
        return "Ban Mian"
    else:
        return "Al Amaans"


 
#running the shit
if __name__ == '__main__':
    # Initializes your bot with the token!
    app = Application.builder().token(TOKEN).build()

    # Commands 
    # Left side is name of command user needs to type in, right side is name of function
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('register', register_user))
    app.add_handler(CommandHandler('login', login_user))
    app.add_handler(CommandHandler('help', help))
    app.add_handler(CommandHandler('stores', stores))
    app.add_handler(CommandHandler('add', addcart))
    app.add_handler(CommandHandler('remove', removecart))
    app.add_handler(CommandHandler('viewcart', viewcart))
    app.add_handler(CommandHandler('clearcart', clearcart))
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
