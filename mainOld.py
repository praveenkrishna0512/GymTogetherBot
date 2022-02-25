from calendar import weekday
import logging
import this
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from click import option
from env import get_api_key, get_port
import telebot
from telebot import types
import telegram
from telegram import CallbackQuery, ParseMode
import ast

PORT = get_port()
API_KEY = get_api_key()
if API_KEY == None:
    raise Exception("Please update API Key")

weekList = {
    "1" : "This Week",
    "2" : "Next Week"
    }

dayList = {
    "1" : "Mon",
    "2" : "Tue",
    "3" : "Wed",
    "4" : "Thu",
    "5" : "Fri",
    "6" : "Sat",
    "7" : "Sun"
}

timeList = {
    "1" : "7am",
    "2" : "9am",
    "3" : "11am",
    "4" : "1pm",
    "5" : "3pm",
    "6" : "5pm",
    "7" : "7pm",
    "8" : "9pm",
    "done" : "Done!"
}
# -----------------------------------------------------------------------------------------------------
# Initialise bot
bot = telebot.TeleBot(API_KEY, parse_mode = None)

# Makes Inline Keyboard
def makeInlineKeyboard(lst, optionID):
    markup = types.InlineKeyboardMarkup()
    for key, value in lst.items():
        markup.add(types.InlineKeyboardButton(text = value,
                                            callback_data = "['optionID', '" + optionID + "', 'value', '" + value + "', 'key', '" + key + "']"))
    return markup

# EVENT HANDLERS -----------------------------------------------------------------

def askDay(msg, week):
    txt1 = "You are scheduling for <b>{week}</b>\n\n".format(week = week)
    txt2 = "Pick the day you wish to schedule for below"
    fullText = txt1 + txt2
    bot.edit_message_text(chat_id = msg.chat.id,
                     text = fullText,
                     reply_markup = makeInlineKeyboard(dayList, 'DAY'),
                     message_id=msg.message_id,
                     parse_mode = 'HTML')

def askTime(msg, day):
    txt1 = "You are scheduling for <b>{day}</b>\n\n".format(day = day)
    txt2 = "Pick the times you are free\n"
    txt3 = "<b>Hit Done</b> once all slots available are picked"
    fullText = txt1 + txt2 + txt3
    bot.edit_message_text(chat_id = msg.chat.id,
                     text = fullText,
                     reply_markup = makeInlineKeyboard(timeList, 'TIME'),
                     message_id=msg.message_id,
                     parse_mode = 'HTML')

# BOT HANDLERS ---------------------------------------------------------------------

# Asks the user which week to schedule
@bot.message_handler(commands=["schedule"])
def askWeek(msg):
    bot.send_message(chat_id = msg.chat.id,
                     text = "Do you want to schedule for this week or next week?\n\n<em>(Note: A Week starts on Monday and ends on Sunday)</em>",
                     reply_markup = makeInlineKeyboard(weekList, 'WEEK'),
                     parse_mode = 'HTML')
    
# Prints out the schedule
@bot.message_handler(commands=["see"])
def printSchedule(msg):
    print(msg.from_user.username)
    bot.reply_to(msg, "see cmd")

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    print(f"call.data : {call.data} , type : {type(call.data)}")
    print(f"ast.literal_eval(call.data) : {ast.literal_eval(call.data)} , type : {type(ast.literal_eval(call.data))}")
    optionIDFromCallBack = ast.literal_eval(call.data)[1]
    if optionIDFromCallBack == 'WEEK':
        weekPicked = ast.literal_eval(call.data)[3]
        askDay(call.message, weekPicked)
    if optionIDFromCallBack == 'DAY':
        dayPicked = ast.literal_eval(call.data)[3]
        askTime(call.message, dayPicked)

    # keyFromCallBack = ast.literal_eval(call.data)[1]
    # del weekList[keyFromCallBack]
    # bot.edit_message_text(chat_id=call.message.chat.id,
    #                         text="Here are the values of stringList",
    #                         message_id=call.message.message_id,
    #                         reply_markup=makeInlineKeyboard(weekList),
    #                         parse_mode='HTML')

# Listen to messages
bot.polling()