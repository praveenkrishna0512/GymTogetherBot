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
    "7" : "Sun",
    "done" : "Done!"
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
    "back" : "Back"
}

# Creates user database
# ------------------------------------------------
# TODO: TO BE REPLACED WITH SERVER SIDE
# ------------------------------------------------
usersList = ["praveeeenk"]
def makeUserDataBase(users):
    timeDict = {}
    for time in timeList.values():
        if time == "Done!":
            break
        timeDict[time] = False

    dayDict = {}
    for day in dayList.values():
        dayDict[day] = timeDict.copy()

    userDict = {}
    for user in users:
        userDict[user] = dayDict.copy()

    return userDict
userDataBase = makeUserDataBase(usersList)

# -----------------------------------------------------------------------------------------------------
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Initialise bot
bot = telebot.TeleBot(API_KEY, parse_mode = None)

# Makes Inline Keyboard
def makeInlineKeyboard(lst, optionID):
    markup = types.InlineKeyboardMarkup()
    for key, value in lst.items():
        markup.add(types.InlineKeyboardButton(text = value,
                                            callback_data = "['optionID', '" + optionID + "', 'value', '" + value + "']"))
    return markup

# Specific Inline Keyboard for showing time slots
def makeTimeInlineKeyboard(lst, optionID, dayPicked):
    markup = types.InlineKeyboardMarkup()
    for key, value in lst.items():
        markup.add(types.InlineKeyboardButton(text = value,
                                            callback_data = "['optionID', '" + optionID + "', 'value', '" + value + "', 'day', '" + dayPicked + "']"))
    return markup

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    txt1 = "Hi! Welcome to GymTogether\n\n"
    txt2 = "Type <b>/help</b> for more info\n"
    fullText = txt1 + txt2
    update.message.reply_text(text = fullText, parse_mode = ParseMode.HTML)

def help(update, context):
    """Send a message when the command /help is issued."""
    txt1 = "Here are the suppported individual commands:\n"
    txt2 = "<b>/schedule</b> - Begin scheduling your gym slots for this/next week\n\n"
    txt3 = "Here are the support group commands:\n"
    txt4 = "<b>/see</b> - See the current schedule"
    fullText = txt1 + txt2 + txt3 + txt4
    update.message.reply_text(text = fullText, parse_mode = ParseMode.HTML)

def askWeek(update, context):
    bot.send_message(chat_id = update.message.chat.id,
                     text = "Do you want to schedule for this week or next week?\n\n<em>(Note: A Week starts on Monday and ends on Sunday)</em>",
                     reply_markup = makeInlineKeyboard(weekList, 'WEEK'),
                     parse_mode = 'HTML')

def askDay(update, context, weekPicked):
    user = update.callback_query.message.chat.username
    txt1 = "You are scheduling for <b>{week}</b>\n".format(week = weekPicked)
    txt2 = printTimeslots(user)
    txt3 = "Pick the day you wish to schedule for below"
    if txt2 != "":
        txt2 += "\n" 
    fullText = txt1 + txt2 + txt3
    bot.edit_message_text(chat_id = update.callback_query.message.chat.id,
                     text = fullText,
                     reply_markup = makeInlineKeyboard(dayList, 'DAY'),
                     message_id = update.callback_query.message.message_id,
                     parse_mode = 'HTML')

def handleDay(update, context, dayPicked, weekPicked):
    user = update.callback_query.message.chat.username
    if dayPicked == "Done!":
        txt1 = "Done scheduling for <em><b>{week}</b></em>!\n".format(week = weekPicked)
        txt2 = printTimeslots(user)
        txt3 = "\n<b>See you at the gym :)</b>"
        fullText = txt1 + txt2 + txt3
        bot.edit_message_text(chat_id = update.callback_query.message.chat.id,
                     text = fullText,
                     message_id = update.callback_query.message.message_id,
                     parse_mode = 'HTML')
    else:
        askTime(update, context, dayPicked)

def printTimeslots(user):
    txt2 = "\n<b>Timeslots picked:</b>\n"
    fulltxt = ""
    for day, timeDict in userDataBase[user].items():
        tempStr = ""
        for time, status in timeDict.items():
            if status:
                tempStr = tempStr + "\n" + time
        if tempStr != "":
            fulltxt += "\n<u>" + day + "</u>" + tempStr + "\n"
    if fulltxt != "":
        fulltxt = txt2 + fulltxt
    return fulltxt
    

def askTime(update, context, dayPicked):
    txt1 = "You are scheduling for <b>{day}</b>\n\n".format(day = dayPicked)
    txt2 = "Pick the times you are free\n"
    txt3 = "<b>Hit Done</b> once all slots available are picked\n\n"
    txt4 = "Timeslots picked:\n"
    txt5 = ""
    user = update.callback_query.message.chat.username
    timeDict = userDataBase[user][dayPicked]
    for time, status in timeDict.items():
        if status:
            txt5 = txt5 + "\n" + time
    fullText = txt1 + txt2 + txt3 + txt4 + txt5
    bot.edit_message_text(chat_id = update.callback_query.message.chat.id,
                     text = fullText,
                     reply_markup = makeTimeInlineKeyboard(timeList, 'TIME', dayPicked),
                     message_id = update.callback_query.message.message_id,
                     parse_mode = 'HTML')

def handleTime(update, context, dayPicked, timePicked):
    user = update.callback_query.message.chat.username
    if timePicked == "Back":
        # ------------------------------------------------
        # TODO CHANGE THE THIS WEEK
        # ------------------------------------------------
        askDay(update, context, "This Week")
    else:
        currentState = userDataBase[user][dayPicked][timePicked]
        userDataBase[user][dayPicked][timePicked] = (not currentState)
        askTime(update, context, dayPicked)


def mainCallBackHandler(update, context):
    dataClicked = ast.literal_eval(update.callback_query.data)
    optionID = dataClicked[1]
    value = dataClicked[3]
    if optionID == 'WEEK':
        askDay(update, context, value)
    if optionID == 'DAY':
        handleDay(update, context, value, "This Week")
    if optionID == 'TIME':
        day = dataClicked[5]
        handleTime(update, context, day, value)

def stop(update, context):
    """Stops"""
    update.message.reply_text(update.message.text)

def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    # Start the bot.
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(API_KEY, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("schedule", askWeek))

    # Handle all callback
    dp.add_handler(CallbackQueryHandler(callback=mainCallBackHandler, pattern=str))


    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    #  updater.start_webhook(listen="0.0.0.0",
    #                       port=int(PORT),
    #                       url_path=str(API_KEY))
    #  updater.bot.setWebhook('https://yourherokuappname.herokuapp.com/' + str(API_KEY))

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    # updater.idle()
    updater.start_polling()

if __name__ == '__main__':
    main()