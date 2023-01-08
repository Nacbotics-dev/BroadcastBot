from telebot.types import *


def available_channels(channels):
    keyboard = InlineKeyboardMarkup()

    for channel in channels:
        keyboard.add(InlineKeyboardButton(channel.chat_name,callback_data=f"to:{int(channel.ChannelId.time_low)}"))
    
    
    return(keyboard)


def confirmBroadcast():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Confirm ✅',callback_data="confirm"))
    return(keyboard)


def urlKeyboard(name,url):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(name,url=str(url).strip(' ')))
    return(keyboard)