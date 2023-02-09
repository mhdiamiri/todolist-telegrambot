from pyrogram import *
from pyrogram.types import *

import database_handler as db
import requests as req

import json

token = "" # @botfather

apiId = 1111 # my.telegram.org

apiHash = "" 

bot = Client(
    "todobot",
    api_hash=apiHash,
    api_id=apiId,
    bot_token=token
)

@bot.on_message(filters.command("start"))
async def start(client, message:Message):
    random_img = get_random_image()
    
    userId  = str(message.chat.id)
    
    db.setUserStatus(userId, 0)
    
    menu = ReplyKeyboardMarkup(
        [   
            ["New Task"],
            ["Show ToDo List", "Show Done Tasks"],
            
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    if random_img:
        await message.reply_photo(random_img,
                                  caption="welcome :)",
                                  reply_markup=menu)
    else:
        await message.reply_text(
            "Welcome :)",
            reply_markup=menu 
        )

@bot.on_message(filters.private & filters.text)
async def on_text_message(client, message):
    userId  = str(message.chat.id)
    stateId = int(db.getUserStatus(userId))
    
    # main menu
    if stateId == 0:
        if message.text == "Show ToDo List":
            await show_tasks(userId, message, 0, False)
        elif message.text == "New Task":
            await new_task(userId, message)
        elif message.text == "Show Done Tasks":
            await show_tasks(userId, message, 0, True)
        else:
            await message.reply_text("Wrong Command!\nclick on /start to see menu.")
    
    elif stateId == 1 or stateId == 2:
        await new_task(userId, message)
        
    
@bot.on_callback_query()
async def on_callback(client, callback_query):
    
    message = callback_query.message
    
    userId  = str(message.chat.id)
    
    data = callback_query.data.split("_")
    
    func = data[0]
    d    = data[1]
    
     # if func = task then d = taskId
    if func == "task":
        taskId = int(d)
        await show_single_task(message, taskId)
        await callback_query.answer(
            "showing task",
            show_alert = False
            
        )
    
    # if func = next then d = page
    elif func == "next": 
        page = int(data[1]) + 1
        
        if data[2] == "True":
            done = True
        else: 
            done = False
            
        await show_tasks(userId, message, page, done)
        
        await callback_query.answer(
            "next page",
            show_alert = False
            
        )
    # if func = prev then d = page
    elif func == "prev":
        page = int(data[1]) - 1
        if data[2] == "True":
            done = True
        else: 
            done = False
        
        await show_tasks(userId, message, page, done)
        
        await callback_query.answer(
            "previous page",
            show_alert = False
            
        )
        
    elif func == "del":
        taskId = int(d)
        db.hideTask(taskId)
        
        await callback_query.answer(
            "Deleted.",
            show_alert = False
        )
        
        await message.delete()
    
    elif func == "done":
        taskId = int(d)
        db.markDone(taskId)
        
        await callback_query.answer(
            "marked as done.",
            show_alert = False
            
        )
        
        await message.delete()


async def show_single_task(message, taskId):
    task = db.getSingleTask(taskId)
    if task:
        title = task[2]
        description = task[3]
        dt = task[4]
        done = task[5]
        text_message = title + '\n'
        text_message += description + '\n\n'
        text_message += "Date: " + dt + '\n'
        
        buttons = []
        
        if not done:
            
            buttons.append(
                [
                    InlineKeyboardButton("Mark As Done.", f'done_{taskId}')
                ]
            ) 
           
        buttons.append(
            [
                InlineKeyboardButton("Delete", f"del_{taskId}")
            ]
        )
        
        single_task_keyboard = InlineKeyboardMarkup(
            buttons
        )
        
        await message.reply_text(
            text_message,
            reply_markup = single_task_keyboard
        )
        await message.delete()
        
    else:
        await message.reply_text(
            "No such task found!"
        )
    
async def show_tasks(userId, message:Message, page, done):
    if done:
        tasks = db.getDoneTasks(userId)
    else:
        tasks = db.getUnderDoneTasks(userId)
    
    if len(tasks) == 0:
        await message.reply_text("empty.")
    else:
        tasks = tasks[page * 10:]
        
        has_next_page = False
        
        if len(tasks) > 10:
            tasks = tasks[:(page+1) * 10]
            has_next_page = True
        
        buttons = []
        
        for task in tasks:
            title = task[2]
            button = InlineKeyboardButton(title, 
                                     callback_data=f"task_{task[0]}")
            buttons.append( 
                [
                    button
                ]
            )
            
        if has_next_page:
            button =  InlineKeyboardButton("next",
                                    callback_data=f"next_{page}_{str(done)}"
                    )                             
            buttons.append(
                [button]
            )
        
        if page > 0:
            button = InlineKeyboardButton("previous",
                        callback_data=f"prev_{page}_{str(done)}"
                    )
            
            buttons.append(
                [button]
            )
        
        
        list_keyboard = InlineKeyboardMarkup(
            buttons
        )   
        
        await message.reply_text("choose from below:", reply_markup = list_keyboard)
        await message.delete()
    
    
async def new_task(userId, message):
    stateId = db.getUserStatus(userId)
    
    if stateId == 0:
        await message.reply_text("Please send title:\npress /start to cancel.")
        db.setUserStatus(userId, 1)
        return
        
    elif stateId == 1:
        title = message.text
        with open(userId, 'w') as f:
            f.write(title)
        db.setUserStatus(userId, 2)
        await message.reply_text("Please send description:\npress /start to cancel.")
        return 
        
    elif stateId == 2:
        description = message.text 
        title = "not set"
        
        with open(userId, 'r') as f:    
            title = f.read()
            
        db.addTask(userId, title, description, 0, 0)
        db.setUserStatus(userId, 0)
        await message.reply_text("done.\npress /start to back to main menu.")
        


def get_random_image():
    url = "https://random-d.uk/api/random"
    
    try:
        ans = req.get(url)
    except:
        return None
    
    if ans.status_code == 200:
        dictionary = json.loads(ans.text)
        return dictionary["url"]
    else:
        return None      

bot.run()
