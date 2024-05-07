import telebot
import qrcode

# Initialize your Telegram bot using the API token
bot = telebot.TeleBot('6877821362:AAHqjfOSBnpvmORuhR40u8JYZ6gh9gWH2hM')

# Default colors
default_foreground_color = "black"
default_background_color = "white"

# Dictionary to store user names, IDs, and color preferences
user_data = {}

# Command to start the bot or get help
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    if message.from_user.last_name:
        user_name += " " + message.from_user.last_name

    if user_id not in user_data:
        user_data[user_id] = {
            "display_name": user_name,
            "user_name": message.from_user.username,
            "foreground_color": default_foreground_color,
            "background_color": default_background_color
        }

    bot.reply_to(message, f"Welcome to the QR Code Bot, {user_name}! Here's how to use it:\n\n"
                          "To generate a QR code, send '/qr [text]'.\n"
                          "For example, '/qr Hello' will generate a QR code with the default colors.\n\n"
                          "You can also customize the colors by including them in the command, e.g., '/qr [text] [foreground_color] [background_color]'.")

# Function to save user data to a text file
def save_user_data():
    with open("user.txt", "w") as file:
        for user_id, user_info in user_data.items():
            file.write(f"User ID: {user_id}, Display Name: {user_info['display_name']}, "
                       f"User Name: {user_info['user_name']}, "
                       f"Foreground Color: {user_info['foreground_color']}, "
                       f"Background Color: {user_info['background_color']}\n")

# Load user data from the text file (if available)
try:
    with open("user.txt", "r") as file:
        for line in file:
            parts = line.strip().split(", ")
            if len(parts) == 5:
                user_id = int(parts[0].split(": ")[1])
                display_name = parts[1].split(": ")[1]
                user_name = parts[2].split(": ")[1]
                foreground_color = parts[3].split(": ")[1]
                background_color = parts[4].split(": ")[1]
                user_data[user_id] = {
                    "display_name": display_name,
                    "user_name": user_name,
                    "foreground_color": foreground_color,
                    "background_color": background_color
                }
except FileNotFoundError:
    pass
except Exception as e:
    print(f"Error loading user data: {str(e)}")

# Command to handle regular messages
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    if message.from_user.last_name:
        user_name += " " + message.from_user.last_name

    if user_id not in user_data:
        user_data[user_id] = {
            "display_name": user_name,
            "user_name": message.from_user.username,
            "foreground_color": default_foreground_color,
            "background_color": default_background_color
        }

    if text.lower() == "hello" or text.lower() == "hi":
        bot.reply_to(message, f"Hey there! 👋, {user_name}! See the instructions with /help?")
    elif text.startswith("/qr"):
        try:
            parts = text.split()
            if len(parts) < 2:
                bot.reply_to(message, "Please provide the text for the QR code.")
                return
            text_to_encode = ' '.join(parts[1:])

            # Generate a QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(text_to_encode)
            qr.make(fit=True)

            # Use default colors or user-specified colors
            foreground_color = user_data[user_id]["foreground_color"]
            background_color = user_data[user_id]["background_color"]
            if len(parts) >= 4:
                foreground_color = parts[2]
                background_color = parts[3]

            img = qr.make_image(fill_color=foreground_color, back_color=background_color)

            # Save the QR code as a file
            img.save("qrcode.png")

            # Send the QR code to the user
            bot.send_photo(message.chat.id, open("qrcode.png", "rb"))

        except Exception as e:
            bot.reply_to(message, f"An error occurred: {str(e)}")
    else:
        bot.reply_to(message, "I'm not sure what you mean. Send '/help' to see how to use this bot.")

# Start the bot
bot.polling()
