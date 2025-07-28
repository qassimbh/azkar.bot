from fastapi import FastAPI, Request
import json
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os

TOKEN = "6288532598:AAEf-5FT5mCBr6D5Pv1iHap3mp9CtB7FE10"
app = FastAPI()
application = Application.builder().token(TOKEN).build()

# تحميل الأذكار
with open("azkar.json", "r", encoding="utf-8") as f:
    azkar_data = json.load(f)

users_file = "rshq.json"
if not os.path.exists(users_file):
    with open(users_file, "w") as f:
        json.dump([], f)

def get_random_zekr(category=None):
    if category and category in azkar_data:
        return random.choice(azkar_data[category])
    all_azkar = sum(azkar_data.values(), [])
    return random.choice(all_azkar)

def load_users():
    with open(users_file, "r") as f:
        return json.load(f)

def save_user(user_id):
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        with open(users_file, "w") as f:
            json.dump(users, f)

async def send_hourly_azkar():
    while True:
        users = load_users()
        zekr = get_random_zekr()
        for user_id in users:
            try:
                await application.bot.send_message(chat_id=user_id, text=zekr)
            except:
                pass
        await asyncio.sleep(3600)

@app.on_event("startup")
async def startup():
    asyncio.create_task(send_hourly_azkar())
    await application.initialize()
    await application.start()

@app.post(f"/webhook/{TOKEN}")
async def webhook_handler(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}

# رسالة الترحيب لمرة واحدة فقط
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)
    if context.user_data.get("started"):
        return
    context.user_data["started"] = True

    text = f"أهلاً وسهلاً أخي الكريم {update.effective_user.first_name} في بوت الأذكار، سيساعدك كثيراً في تذكيرك بذكر الله ❤️"
    keyboard = [
        [InlineKeyboardButton("🌅 أذكار الصباح", callback_data='الصباح')],
        [InlineKeyboardButton("🌇 أذكار المساء", callback_data='المساء')],
        [InlineKeyboardButton("😴 أذكار النوم", callback_data='النوم')],
        [InlineKeyboardButton("🙏 أذكار بعد الصلاة", callback_data='الصلاة')],
        [InlineKeyboardButton("🔁 ذكر عشوائي", callback_data='random')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data
    zekr = get_random_zekr(category if category != 'random' else None)
    await query.message.reply_text(zekr)

application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))
