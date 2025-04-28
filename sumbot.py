import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import os

load_dotenv()
# Need to create .evn file with TOKEN
bot_token = os.getenv("TOKEN")

# Path to the JSON file where user data will be saved
DATA_FILE = "user_data.json"

# Function to load data from the JSON file
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Return an empty dictionary if file doesn't exist or is corrupted
        return {}

# Function to save data to the JSON file
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# Function to get the current sum for a user
def get_user_sum(user_id, data):
    return data.get(str(user_id), 0)

# Function to set the current sum for a user
def set_user_sum(user_id, sum_value, data):
    data[str(user_id)] = sum_value
    save_data(data)

# Load user data at the start
user_data = load_data()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome! Send me a number, and I'll keep a running total for you. "
        "Use /reset to reset your total."
    )

async def add_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_sum = get_user_sum(user_id, user_data)

    try:
        # Try to parse the message text as an integer
        number = int(update.message.text)
        user_sum += number

        # Update the user's sum in the data and save
        set_user_sum(user_id, user_sum, user_data)

        # Send the updated sum back to the user
        await update.message.reply_text(f"The new sum for you is: {user_sum}")
    except ValueError:
        await update.message.reply_text("Please send a valid number.")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    set_user_sum(user_id, 0, user_data)

    await update.message.reply_text("Your sum has been reset to 0.")

def main():
    # Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual bot token
    application = ApplicationBuilder().token(bot_token).build()

    # Command handler for /start
    application.add_handler(CommandHandler("start", start))

    # Command handler for /reset
    application.add_handler(CommandHandler("reset", reset))

    # Message handler for any text message containing a number
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_number))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
