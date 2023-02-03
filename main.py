import logging, random

import os

import pytz

from datetime import datetime

from telegram.ext import (
    Application,
    ContextTypes,
    CommandHandler, 
    ConversationHandler,
    MessageHandler,
    filters
)

from telegram.constants import ChatAction
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

import asyncio

from functools import wraps

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define bot token
TOKEN = os.environ["BOT_TOKEN"]

# Define stages
PAX, FORMAT, DENOMINATION, PLAYER1, PLAYER2, PLAYER3, PLAYER4 = range(7)
WINNER_PAYOUT, TYPE_PAYOUT, SHOOTER_PAYOUT = range(3)
WINNER_WIN, TAI_WIN, TYPE_WIN, SHOOTER_WIN = range(4)

# Define constants
pax_list = ["3", "4"]
format_list = ["Shooter", "Non-shooter"]
denomination_list = ["$0.05/$0.10","$0.10/$0.20", "$0.20/$0.40", "$0.50/$1.00", "$1/$2", "三六半"]
payout_type_list = ["暗咬", "明咬", "暗杠", "明杠"]
tai_list_four = ["1", "2", "3", "4", "5"]
tai_list_three = ["5", "6", "7", "8", "9", "满", "双满", "三满", "四满"]
win_type_list = ["自摸", "Shoot", "Shoot 包自摸", "Shoot 包"]

# Define 三六半 payout
sanliu_list = [1, 2, 3, 5, 10, 20]

# Define typing decorator function
def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        async def command_func(update, context, *args, **kwargs):
            if update.message == None:
                return
            await context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return await func(update, context,  *args, **kwargs)
        return command_func
    
    return decorator


# Define command handlers
@send_action(ChatAction.TYPING) 
async def start(update, context):
    """Send a message when the command /start is issued."""
    if update.message.chat_id == 824514778:
        await update.message.reply_text('🀄 Hiiii amazing person <3. May you 發! HUAT AH 🀄')
    elif update.message.chat_id == 1005287463:
        await update.message.reply_text('🀄 Hi boss! May you 發! HUAT AH. MAY I HAVE NO BUGS AND NO CRASHES 🀄')
    else:
        await update.message.reply_text('🀄 Hi! Use /help to understand more about the bot! 🀄')

@send_action(ChatAction.TYPING) 
async def help(update, context):
    """Send a message when the command /help is issued."""
    text_file = open("help.txt", encoding="utf8" , mode="r")
    data = text_file.read()
    text_file.close()
    await update.message.reply_text(data)
    
@send_action(ChatAction.TYPING) 
async def threemanrules(update, context):
    """Send a message when the command /threemanrules is issued."""
    text_file = open("threemanrules.txt", encoding="utf8" , mode="r")
    data = text_file.read()
    text_file.close()
    await update.message.reply_text(data)
    
@send_action(ChatAction.TYPING) 
async def dice(update, context):
    """Send a message when the command /dice is issued."""
    random1 = random.randint(1, 6)
    random2 = random.randint(1, 6)
    random3 = random.randint(1, 6)
    await update.message.reply_text(f'Random dice roll: {random1+random2+random3}')
    
@send_action(ChatAction.TYPING) 
async def support(update, context):
    """Send a message when the command /support is issued."""
    await update.message.reply_photo(open("paylahqr.jfif", "rb"))
    await update.message.reply_text('Thanks for the support! Much appreciated 🫶')

@send_action(ChatAction.TYPING) 
async def feedback(update, context):
    """Send a message when the command /feedback is issued."""
    await update.message.reply_text('For any general feedback, just send a normal chat message to the bot!')

@send_action(ChatAction.TYPING) 
def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

async def record(update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Records the user's message."""
    user = update.message.from_user
    message = update.message.text
    logger.info(f"User {user.first_name} said {message}", )

# Define cancel command to end conversations
@send_action(ChatAction.TYPING)     
async def cancel(update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Operation cancelled succesfully!", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# Define game start function
@send_action(ChatAction.TYPING) 
async def game(update, context):
    """Asks for number of pax."""
    if context.user_data.get("game_state", 'Not found') == 1:
        await update.message.reply_text("Game ongoing, please end with /endgame before starting new game")
        return ConversationHandler.END
    else:
        reply_keyboard = [["3","4"]]
        await update.message.reply_text(
            "Please select the number of players.",
            reply_markup = ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="Number of players"
            ),
        )
        return PAX

@send_action(ChatAction.TYPING) 
async def pax(update, context):
    """Asks for format."""
    update.message.text
    if update.message.text in pax_list:
        context.user_data["pax"] = update.message.text
    else:
        await update.message.reply_text("Please use the reply keyboard")
        return PAX
    reply_keyboard = [["Shooter","Non-shooter"]]
    await update.message.reply_text(
        "Please select the format.",
        reply_markup = ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Format"
        ),
    )
    return FORMAT

@send_action(ChatAction.TYPING) 
async def format(update, context):
    """Asks for denomination."""
    if update.message.text in format_list:
        context.user_data["format"] = update.message.text
    else:
        await update.message.reply_text("Please use the reply keyboard")
        return FORMAT
    # 3 man
    if context.user_data["pax"] == "3":
        reply_keyboard = [["$0.05/$0.10","$0.10/$0.20"], ["$0.20/$0.40","$0.50/$1.00"]]
        await update.message.reply_text(
            "Please select the denomination.",
            reply_markup = ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="Format"
            ),
        )  
    # 4 man
    else:
        reply_keyboard = [["三六半"], ["$0.10/$0.20", "$0.20/$0.40"], ["$0.50/$1.00", "$1/$2"]]
        await update.message.reply_text(
            "Please select the denomination.",
            reply_markup = ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="Format"
            ),
        )  
    return DENOMINATION

@send_action(ChatAction.TYPING) 
async def denomination(update, context):
    """Asks for player 1."""
    if update.message.text in denomination_list:
        if update.message.text == "三六半":
            context.user_data["denomination"] = "三六半"
        elif update.message.text == "$0.05/$0.10":
            context.user_data["denomination"] = 0.1
        elif update.message.text == "$0.10/$0.20":
            context.user_data["denomination"] = 0.2
        elif update.message.text == "$0.20/$0.40":
            context.user_data["denomination"] = 0.4
        elif update.message.text == "$0.50/$1.00":
            context.user_data["denomination"] = 1
        elif update.message.text == "$1/$2":
            context.user_data["denomination"] = 2
        else:
            await update.message.reply_text("Error code 101! Please contact the admin.")
    else:
        await update.message.reply_text("Please use the reply keyboard")
        return DENOMINATION
    await update.message.reply_text(
        "Please enter the name of player 1",
        reply_markup=ReplyKeyboardRemove(),
    )
    return PLAYER1

@send_action(ChatAction.TYPING) 
async def player1(update, context):
    """Asks for player 2."""
    context.user_data["p1name"] = update.message.text
    await update.message.reply_text("Please enter the name of player 2")
    return PLAYER2

@send_action(ChatAction.TYPING) 
async def player2(update, context):
    """Asks for player 3."""
    context.user_data["p2name"] = update.message.text
    await update.message.reply_text("Please enter the name of player 3")
    return PLAYER3
    
@send_action(ChatAction.TYPING) 
async def player3(update, context):
    """Asks for player 4."""
    context.user_data["p3name"] = update.message.text
    if context.user_data["pax"] == "4":
        await update.message.reply_text("Please enter the name of player 4")
        return PLAYER4
    else:
        cardinal = ["東", "南", "西"]
        random.shuffle(cardinal)
        name1 = context.user_data["p1name"]
        name2 = context.user_data["p2name"]
        name3 = context.user_data["p3name"]
        context.user_data["player_list"] = [name1, name2, name3]
        context.user_data["p1wallet"] = 0
        context.user_data["p2wallet"] = 0
        context.user_data["p3wallet"] = 0
        context.user_data["startdate"] = datetime.now().astimezone(pytz.timezone('Asia/Singapore'))
        await update.message.reply_text(f"Player 1: {name1}. {cardinal[0]}\nPlayer 2: {name2}. {cardinal[1]}\nPlayer 3: {name3}. {cardinal[2]}")
        context.user_data["game_state"] = 1
        return ConversationHandler.END

@send_action(ChatAction.TYPING) 
async def player4(update, context):
    """Print players with randomised cardinal direction."""
    if context.user_data["pax"] == "4":
        context.user_data["p4name"] = update.message.text
        cardinal = ["東", "南", "西", "北"]
        random.shuffle(cardinal)
        name1 = context.user_data["p1name"]
        name2 = context.user_data["p2name"]
        name3 = context.user_data["p3name"]
        name4 = context.user_data["p4name"]
        context.user_data["player_list"] = [name1, name2, name3, name4]
        context.user_data["p1wallet"] = 0
        context.user_data["p2wallet"] = 0
        context.user_data["p3wallet"] = 0
        context.user_data["p4wallet"] = 0
        context.user_data["startdate"] = datetime.now().astimezone(pytz.timezone('Asia/Singapore'))
        await update.message.reply_text(f"Player 1: {name1}. {cardinal[0]}\nPlayer 2: {name2}. {cardinal[1]}\nPlayer 3: {name3}. {cardinal[2]}\nPlayer 4: {name4}. {cardinal[3]}")
        context.user_data["game_state"] = 1
        return ConversationHandler.END 
    else:
        await update.message.reply_text("Error code 102! Please contact the admin.")
        return ConversationHandler.END

# Define payout function
@send_action(ChatAction.TYPING) 
async def payout(update, context):
    """Asks for winner of gang/yao."""
    if context.user_data.get("game_state", 'Not found') != 1:
        await update.message.reply_text("Game not started! Start game using /game")
        return ConversationHandler.END
    reply_keyboard = [context.user_data["player_list"]]
    await update.message.reply_text(
        "Please select the winner.",
        reply_markup = ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Winner"
        ),
    )
    return WINNER_PAYOUT

@send_action(ChatAction.TYPING) 
async def winner_payout(update, context):
    """Asks for type of gang/yao."""
    if update.message.text not in context.user_data["player_list"]:
        await update.message.reply_text("Please use the reply keyboard FOR FK'S SAKE STOP TESTING ME")
        return WINNER_PAYOUT
    else:
        context.user_data["winner"] = context.user_data["player_list"].index(update.message.text) + 1
        list = context.user_data["player_list"]
        context.user_data["loser_list"] = list[:]
        context.user_data["loser_list"].pop(context.user_data["winner"] - 1)
        context.user_data["loser_list"].append("Everyone pay")
        reply_keyboard = [["暗咬", "明咬"], ["暗杠", "明杠"]]
        await update.message.reply_text(
            "Please select the type of payout.",
            reply_markup = ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="Payout type"
            ),
        )
    return TYPE_PAYOUT

@send_action(ChatAction.TYPING) 
async def type_payout(update, context):
    """Asks for shooter of gang/yao."""
    if update.message.text not in payout_type_list:
        await update.message.reply_text("Please use the reply keyboard FOR FK'S SAKE STOP TESTING ME")
        return TYPE_PAYOUT
    else:
        context.user_data["payout_type"] = update.message.text
        if context.user_data["payout_type"] == "暗杠":
            # 暗杠
            if context.user_data["pax"] == "4":
                # 4 man
                winner = context.user_data["winner"]
                winner_name = context.user_data[f"p{winner}name"]
                if context.user_data["denomination"] == "三六半":
                    # 三六半
                    loss = 2*sanliu_list[1]
                else:
                    loss = 2*context.user_data["denomination"]
                context.user_data["p1wallet"] -= loss
                context.user_data["p2wallet"] -= loss
                context.user_data["p3wallet"] -= loss
                context.user_data["p4wallet"] -= loss
                context.user_data[f"p{winner}wallet"] += 4*loss
                await update.message.reply_text(
                    f"Player {winner} {winner_name} won ${3*loss:.2f}\nEveryone else lost ${loss:.2f}",
                    reply_markup=ReplyKeyboardRemove(),
                )
            else:
                # 3 man
                winner = context.user_data["winner"]
                winner_name = context.user_data[f"p{winner}name"]
                loss = 2*context.user_data["denomination"]
                context.user_data["p1wallet"] -= loss
                context.user_data["p2wallet"] -= loss
                context.user_data["p3wallet"] -= loss
                context.user_data[f"p{winner}wallet"] += 3*loss
                await update.message.reply_text(
                    f"Player {winner} {winner_name} won ${2*loss:.2f}\nEveryone else lost ${loss:.2f}",
                    reply_markup=ReplyKeyboardRemove(),
                )
            return ConversationHandler.END
        else:
            reply_keyboard = [context.user_data["loser_list"]]
            await update.message.reply_text(
                "Please select the shooter.",
                reply_markup = ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True, input_field_placeholder="Shooter"
                ),
            )
    return SHOOTER_PAYOUT

@send_action(ChatAction.TYPING) 
async def shooter_payout(update, context):
    """Executes and prints outcome."""
    if context.user_data["payout_type"] != "暗杠":
        if update.message.text not in context.user_data["loser_list"]:
            await update.message.reply_text("Please use the reply keyboard FOR FK'S SAKE STOP TESTING ME")
            return SHOOTER_PAYOUT
        else:
            if update.message.text == "Everyone pay":
                if context.user_data["payout_type"] == "暗咬":
                    # 暗咬
                    if context.user_data["pax"] == "4":
                        # 4 man
                        winner = context.user_data["winner"]
                        winner_name = context.user_data[f"p{winner}name"]
                        if context.user_data["denomination"] == "三六半":
                            # 三六半
                            loss = 2*sanliu_list[1]
                        else:
                            loss = 2*context.user_data["denomination"]
                        context.user_data["p1wallet"] -= loss
                        context.user_data["p2wallet"] -= loss
                        context.user_data["p3wallet"] -= loss
                        context.user_data["p4wallet"] -= loss
                        context.user_data[f"p{winner}wallet"] += 4*loss
                        await update.message.reply_text(
                            f"Player {winner} {winner_name} won ${3*loss:.2f}\nEveryone else lost ${loss:.2f}",
                            reply_markup=ReplyKeyboardRemove(),
                        )
                    else:
                        # 3 man
                        winner = context.user_data["winner"]
                        winner_name = context.user_data[f"p{winner}name"]
                        loss = 2*context.user_data["denomination"]
                        context.user_data["p1wallet"] -= loss
                        context.user_data["p2wallet"] -= loss
                        context.user_data["p3wallet"] -= loss
                        context.user_data[f"p{winner}wallet"] += 3*loss
                        await update.message.reply_text(
                            f"Player {winner} {winner_name} won ${2*loss:.2f}\nEveryone else lost ${loss:.2f}",
                            reply_markup=ReplyKeyboardRemove(),
                        )
                else:
                    # 明咬, 明杠
                    if context.user_data["pax"] == "4":
                        # 4 man
                        winner = context.user_data["winner"]
                        winner_name = context.user_data[f"p{winner}name"]
                        if context.user_data["denomination"] == "三六半":
                            # 三六半
                            loss = sanliu_list[1]
                        else:
                            loss = context.user_data["denomination"]
                        context.user_data["p1wallet"] -= loss
                        context.user_data["p2wallet"] -= loss
                        context.user_data["p3wallet"] -= loss
                        context.user_data["p4wallet"] -= loss
                        context.user_data[f"p{winner}wallet"] += 4*loss
                        await update.message.reply_text(
                            f"Player {winner} {winner_name} won ${3*loss:.2f}\nEveryone else lost ${loss:.2f}",
                            reply_markup=ReplyKeyboardRemove(),
                        )
                    else:
                        # 3 man
                        winner = context.user_data["winner"]
                        winner_name = context.user_data[f"p{winner}name"]
                        loss = context.user_data["denomination"]
                        context.user_data["p1wallet"] -= loss
                        context.user_data["p2wallet"] -= loss
                        context.user_data["p3wallet"] -= loss
                        context.user_data[f"p{winner}wallet"] += 3*loss                   
                        await update.message.reply_text(
                            f"Player {winner} {winner_name} won ${2*loss:.2f}\nEveryone else lost ${loss:.2f}",
                            reply_markup=ReplyKeyboardRemove(),
                        ) 
            else:
                # shooter
                context.user_data["loser"] = context.user_data["player_list"].index(update.message.text) + 1
                winner = context.user_data["winner"]
                loser = context.user_data["loser"]
                winner_name = context.user_data[f"p{winner}name"]
                loser_name = context.user_data[f"p{loser}name"]
                if context.user_data["payout_type"] == "暗咬":
                    # 暗咬
                    if context.user_data["denomination"] == "三六半":
                        # 三六半
                        loss = 2*sanliu_list[1]
                    else:
                        loss = 2*context.user_data["denomination"]
                    context.user_data[f"p{loser}wallet"] -= loss
                    context.user_data[f"p{winner}wallet"] += loss
                    await update.message.reply_text(
                        f"Player {winner} {winner_name} won ${loss:.2f}\nPlayer {loser} {loser_name} lost ${loss:.2f}",
                        reply_markup=ReplyKeyboardRemove(),
                    )
                elif context.user_data["payout_type"] == "明咬":
                    # 明咬
                    if context.user_data["denomination"] == "三六半":
                        # 三六半
                        loss = 2*sanliu_list[0]
                    else:
                        loss = context.user_data["denomination"]
                    context.user_data[f"p{loser}wallet"] -= loss
                    context.user_data[f"p{winner}wallet"] += loss
                    await update.message.reply_text(
                        f"Player {winner} {winner_name} won ${loss:.2f}\nPlayer {loser} {loser_name} lost ${loss:.2f}",
                        reply_markup=ReplyKeyboardRemove(),
                    )
                else:
                    # 明杠
                    if context.user_data["pax"] == "4" and context.user_data["denomination"] == "三六半":
                        # 4 man 三六半
                        context.user_data[f"p{loser}wallet"] -= 3*sanliu_list[1]
                        context.user_data[f"p{winner}wallet"] += 3*sanliu_list[1]
                        await update.message.reply_text(
                            f"Player {winner} {winner_name} won ${3*sanliu_list[1]}\nPlayer {loser} {loser_name} lost ${3*sanliu_list[1]}",
                            reply_markup=ReplyKeyboardRemove(),
                        )
                    else:
                        pay_multiplier = int(context.user_data["pax"])-1
                        loss = pay_multiplier*context.user_data["denomination"]
                        context.user_data[f"p{loser}wallet"] -= loss
                        context.user_data[f"p{winner}wallet"] += loss                        
                        await update.message.reply_text(
                            f"Player {winner} {winner_name} won ${loss:.2f}\nPlayer {loser} {loser_name} lost ${loss:.2f}",
                            reply_markup=ReplyKeyboardRemove(),
                        )
    else:
        await update.message.reply_text("Error code 103! Please contact the admin.")
    return ConversationHandler.END

# Define win function
@send_action(ChatAction.TYPING) 
async def win(update, context):
    """Asks for winner of game."""
    if context.user_data.get("game_state", 'Not found') != 1:
        await update.message.reply_text("Game not started! Start game using /game")
        return ConversationHandler.END
    reply_keyboard = [context.user_data["player_list"]]
    await update.message.reply_text(
        "Please select the winner.",
        reply_markup = ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Winner"
        ),
    )
    return WINNER_WIN

@send_action(ChatAction.TYPING) 
async def winner_win(update, context):
    """Asks for tai of win."""
    if update.message.text not in context.user_data["player_list"]:
        await update.message.reply_text("Please use the reply keyboard FOR FK'S SAKE STOP TESTING ME")
        return WINNER_PAYOUT
    else:
        context.user_data["winner"] = context.user_data["player_list"].index(update.message.text) + 1
        list = context.user_data["player_list"]
        context.user_data["loser_list"] = list[:]
        context.user_data["loser_list"].pop(context.user_data["winner"] - 1)
        if context.user_data["pax"] == "4":
            reply_keyboard = [["1", "2", "3"],["4", "5"]]
        else:
            reply_keyboard = [["5", "6", "7"], ["8", "9", "满"], ["双满", "三满", "四满"]]
        await update.message.reply_text(
            "Please select the tai count.",
            reply_markup = ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="Tai count"
            ),
        )
    return TAI_WIN

@send_action(ChatAction.TYPING) 
async def tai_win(update, context):
    """Asks for type of win."""
    if context.user_data["pax"] == "4":
        if update.message.text not in tai_list_four:
            await update.message.reply_text("Please use the reply keyboard FOR FK'S SAKE STOP TESTING ME")
            return TAI_WIN
    elif context.user_data["pax"] == "3":
        if update.message.text not in tai_list_three:
            await update.message.reply_text("Please use the reply keyboard FOR FK'S SAKE STOP TESTING ME")
            return TAI_WIN
    if context.user_data["pax"] == "4":
        context.user_data["tai"] = int(update.message.text)
    elif update.message.text.isnumeric() == True:
        context.user_data["tai"] = int(update.message.text)
    elif update.message.text == "满":
        context.user_data["tai"] = 20
    elif update.message.text == "双满":
        context.user_data["tai"] = 40
    elif update.message.text == "三满":
        context.user_data["tai"] = 80
    elif update.message.text == "四满":
        context.user_data["tai"] = 160
    if context.user_data["format"] == "Shooter":
        reply_keyboard = [["自摸", "Shoot", "Shoot 包自摸"]]
    else:
        reply_keyboard = [["自摸", "Shoot"], ["Shoot 包自摸", "Shoot 包"]]
    await update.message.reply_text(
        "Please select the type of payout.",
        reply_markup = ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Payout type"
        ),
    )
    return TYPE_WIN

@send_action(ChatAction.TYPING) 
async def type_win(update, context):
    """Asks for shooter of win."""
    if update.message.text not in win_type_list:
        await update.message.reply_text("Please use the reply keyboard FOR FK'S SAKE STOP TESTING ME")
        return TYPE_WIN
    else:
        context.user_data["payout_type"] = update.message.text
        if context.user_data["payout_type"] == "自摸":
            # 自摸
            tai = context.user_data["tai"]
            winner = context.user_data["winner"]
            winner_name = context.user_data[f"p{winner}name"]
            if context.user_data["pax"] == "4":
                # 4 man
                if context.user_data["denomination"] == "三六半":
                    # 三六半
                    loss = sanliu_list[tai]
                else:
                    loss = context.user_data["denomination"]*(2**(tai - 1))
                context.user_data["p1wallet"] -= loss
                context.user_data["p2wallet"] -= loss
                context.user_data["p3wallet"] -= loss
                context.user_data["p4wallet"] -= loss
                context.user_data[f"p{winner}wallet"] += 4*loss
                await update.message.reply_text(
                    f"Player {winner} {winner_name} won ${3*loss:.2f}\nEveryone else lost ${loss:.2f}",
                    reply_markup=ReplyKeyboardRemove(),
                )
            else:
                # 3 man
                loss = context.user_data["denomination"]*tai
                context.user_data["p1wallet"] -= loss
                context.user_data["p2wallet"] -= loss
                context.user_data["p3wallet"] -= loss
                context.user_data[f"p{winner}wallet"] += 3*loss
                await update.message.reply_text(
                    f"Player {winner} {winner_name} won ${2*loss:.2f}\nEveryone else lost ${loss:.2f}",
                    reply_markup=ReplyKeyboardRemove(),
                )
            return ConversationHandler.END
        else:
            reply_keyboard = [context.user_data["loser_list"]]
            await update.message.reply_text(
                "Please select the shooter.",
                reply_markup = ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True, input_field_placeholder="Shooter"
                ),
            )
        return SHOOTER_WIN

@send_action(ChatAction.TYPING) 
async def shooter_win(update, context):
    """Executes and prints outcome."""
    if update.message.text not in context.user_data["loser_list"]:
        await update.message.reply_text("Please use the reply keyboard FOR FK'S SAKE STOP TESTING ME")
        return SHOOTER_WIN
    else:
        # shooter
        context.user_data["loser"] = context.user_data["player_list"].index(update.message.text) + 1
        winner = context.user_data["winner"]
        loser = context.user_data["loser"]
        winner_name = context.user_data[f"p{winner}name"]
        loser_name = context.user_data[f"p{loser}name"]
        tai = context.user_data["tai"]
        if ((context.user_data["format"] == "Non-shooter") and (context.user_data["payout_type"] == "Shoot")):
             # Non-shooter Shoot
            if context.user_data["pax"] == "4":
                # 4 man
                if context.user_data["denomination"] == "三六半":
                    # 三六半
                    loss1 = sanliu_list[tai]
                    loss2 = sanliu_list[tai - 1]
                else:
                    loss1 = context.user_data["denomination"]*(2**(tai - 1))
                    loss2 = context.user_data["denomination"]*(2**(tai - 2))
                context.user_data["p1wallet"] -= loss2
                context.user_data["p2wallet"] -= loss2
                context.user_data["p3wallet"] -= loss2
                context.user_data["p4wallet"] -= loss2
                context.user_data[f"p{loser}wallet"] -= loss1 - loss2
                context.user_data[f"p{winner}wallet"] += loss1 + 3*loss2
                await update.message.reply_text(
                    f"Player {winner} {winner_name} won ${loss1 + 2*loss2 :.2f}\nPlayer {loser} {loser_name} lost ${loss1:.2f}\nThe rest lost ${loss2:.2f} each",
                    reply_markup=ReplyKeyboardRemove(),
                )
            else:
                # 3 man
                loss = context.user_data["denomination"]*tai/2
                context.user_data["p1wallet"] -= loss
                context.user_data["p2wallet"] -= loss
                context.user_data["p3wallet"] -= loss
                context.user_data[f"p{loser}wallet"] -= loss
                context.user_data[f"p{winner}wallet"] += 4*loss
                await update.message.reply_text(
                    f"Player {winner} {winner_name} won ${3*loss:.2f}\nPlayer {loser} {loser_name} lost ${2*loss:.2f}\nThe rest lost ${loss:.2f}",
                    reply_markup=ReplyKeyboardRemove(),
                ) 
        elif context.user_data["payout_type"] == "Shoot" or context.user_data["payout_type"] == "Shoot 包":
            # Shooter 包
            if context.user_data["pax"] == "4":
                # 4 man
                if context.user_data["denomination"] == "三六半":
                    # 三六半
                    loss = (sanliu_list[tai] + 2*sanliu_list[tai-1])
                else:
                    loss = context.user_data["denomination"]*(2**(tai - 1))+2*context.user_data["denomination"]*(2**(tai - 2))
            else:
                # 3 man
                loss = 1.5*context.user_data["denomination"]*tai
            context.user_data[f"p{loser}wallet"] -= loss
            context.user_data[f"p{winner}wallet"] += loss                    
            await update.message.reply_text(
                f"Player {winner} {winner_name} won ${loss:.2f}\nPlayer {loser} {loser_name} lost ${loss:.2f}",
                reply_markup=ReplyKeyboardRemove(),
            )
        elif context.user_data["payout_type"] == "Shoot 包自摸":
            # Shoot 包自摸
            if context.user_data["pax"] == "4": 
                # 4 man
                if context.user_data["denomination"] == "三六半":
                    # 三六半
                    loss = 3*sanliu_list[tai]
                else:
                    loss = 3*context.user_data["denomination"]*(2**(tai - 1))
            else:
                # 3 man
                loss = 3*context.user_data["denomination"]*tai
            context.user_data[f"p{loser}wallet"] -= loss
            context.user_data[f"p{winner}wallet"] += loss
            await update.message.reply_text(
                f"Player {winner} {winner_name} won ${loss:.2f}\nPlayer {loser} {loser_name} lost ${loss:.2f}",
                reply_markup=ReplyKeyboardRemove(),
            )
        else:
            await update.message.reply_text("Error code 104! Please contact the admin.")
            return ConversationHandler.END
    return ConversationHandler.END

# Prints progress
@send_action(ChatAction.TYPING) 
async def progress(update, context):
    """Prints progress."""
    if context.user_data.get("game_state", 'Not found') != 1:
        await update.message.reply_text("Game not started! Start game using /game")
    else:
        d = {}
        pax = int(context.user_data["pax"])
        dt_string = context.user_data["startdate"].strftime("%d/%m/%Y %H:%M:%S")
        message = f"Game started at {dt_string}!\n\n"
        for i in range(1, pax+1):
            d[f"p{i}name"] = context.user_data[f"p{i}name"]
            d[f"p{i}wallet"] = context.user_data[f"p{i}wallet"]
            if d[f"p{i}wallet"] < 0:
                d[f"p{i}wallet"] = -d[f"p{i}wallet"]
                d[f"p{i}outcome"] = "lost"
            else:
                d[f"p{i}outcome"] = "won"
            name = d[f"p{i}name"]
            outcome = d[f"p{i}outcome"]
            wallet = d[f"p{i}wallet"]
            message += f"Player {i} {name} {outcome} ${wallet:.2f}\n"
        await update.message.reply_text(message)
        
# Ends current game
@send_action(ChatAction.TYPING) 
async def endgame(update, context):
    """Prints progress."""
    if context.user_data.get("game_state", 'Not found') != 1:
        await update.message.reply_text("Game not started! Start game using /game")
    else:
        """Prints progress."""
        if context.user_data.get("game_state", 'Not found') != 1:
            await update.message.reply_text("Game not started! Start game using /game")
        else:
            d = {}
            pax = int(context.user_data["pax"])
            dt_string = context.user_data["startdate"].strftime("%d/%m/%Y %H:%M:%S")
            now = datetime.now().astimezone(pytz.timezone('Asia/Singapore')).strftime("%d/%m/%Y %H:%M:%S")
            message = f"Game started at {dt_string}!\nGame stopped at {now}!\n\n"
            for i in range(1, pax+1):
                d[f"p{i}name"] = context.user_data[f"p{i}name"]
                d[f"p{i}wallet"] = context.user_data[f"p{i}wallet"]
                if d[f"p{i}wallet"] < 0:
                    d[f"p{i}wallet"] = -d[f"p{i}wallet"]
                    d[f"p{i}outcome"] = "lost"
                else:
                    d[f"p{i}outcome"] = "won"
                name = d[f"p{i}name"]
                outcome = d[f"p{i}outcome"]
                wallet = d[f"p{i}wallet"]
                message += f"Player {i} {name} {outcome} ${wallet:.2f}\n"
            message += "\nGame successfully ended!"
            await update.message.reply_text(message)
        context.user_data.clear()
        
        
def main():
    """Start the bot."""
    app = Application.builder().token(TOKEN).build()
    
    # Start game
    game_starter = ConversationHandler(
        entry_points=[CommandHandler("game", game)],
        states={
            PAX: [MessageHandler(filters.TEXT & (~ filters.COMMAND), pax)],
            FORMAT: [MessageHandler(filters.TEXT & (~ filters.COMMAND), format)],
            DENOMINATION: [MessageHandler(filters.TEXT & (~ filters.COMMAND), denomination)],
            PLAYER1: [MessageHandler(filters.TEXT & (~ filters.COMMAND), player1)],
            PLAYER2: [MessageHandler(filters.TEXT & (~ filters.COMMAND), player2)],
            PLAYER3: [MessageHandler(filters.TEXT & (~ filters.COMMAND), player3)],
            PLAYER4: [MessageHandler(filters.TEXT & (~ filters.COMMAND), player4)],
            },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    # Payout
    payout_handler = ConversationHandler(
        entry_points=[CommandHandler("payout", payout)],
        states={
            WINNER_PAYOUT: [MessageHandler(filters.TEXT & (~ filters.COMMAND), winner_payout)],
            TYPE_PAYOUT: [MessageHandler(filters.TEXT & (~ filters.COMMAND), type_payout)],
            SHOOTER_PAYOUT: [MessageHandler(filters.TEXT & (~ filters.COMMAND), shooter_payout)],
            },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    # Win
    win_handler = ConversationHandler(
        entry_points=[CommandHandler("win", win)],
        states={
            WINNER_WIN: [MessageHandler(filters.TEXT & (~ filters.COMMAND), winner_win)],
            TAI_WIN: [MessageHandler(filters.TEXT & (~ filters.COMMAND), tai_win)],
            TYPE_WIN: [MessageHandler(filters.TEXT & (~ filters.COMMAND), type_win)],
            SHOOTER_WIN: [MessageHandler(filters.TEXT & (~ filters.COMMAND), shooter_win)],
            },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # on different commands - answer in Telegram
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(game_starter)
    app.add_handler(payout_handler)
    app.add_handler(win_handler)
    app.add_handler(CommandHandler("progress", progress))
    app.add_handler(CommandHandler("endgame", endgame))
    app.add_handler(CommandHandler("threemanrules", threemanrules))
    app.add_handler(CommandHandler("dice", dice))
    app.add_handler(CommandHandler("support", support))
    app.add_handler(CommandHandler("feedback", feedback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, record))

    # log all errors
    app.add_error_handler(error)

    # Start the Bot
    app.run_polling()
    

if __name__ == '__main__':
    main()