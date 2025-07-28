from fastapi import FastAPI, Request
import json
import random
import asyncio
import os
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv

# تحميل التوكن
TOKEN = "6288532598:AAEf-5FT5mCBr6D5Pv1iHap3mp9CtB7FE10"

# تحميل الأذكار من ملف data/azkar.json
with open("data/azkar.json", "r", encoding="utf-8") as f:
    azkar = json.load(f)

# تحميل المستخدمين
users_file = "data/rshq.json"
if os.path.exists(users_file):
    with open(users_file, "r", encoding="utf-8") as f:
        users = json.load(f)
else:
    users = []

# تعريف البوت وFastAPI
bot = Bot(token=TOKEN)
app = FastAPI()
application = Application.builder().token(TOKEN).build()

# وظيفة لإرسال ذكر عشوائي
async def send_random_zekr(user_id):
    zekr = random.choice(azkar["random"])
    try:
        await bot.send_message(chat_id=user_id, text=zekr)
    except Exception as e:
        print(f"❌ فشل إرسال الذكر للمستخدم {user_id}: {e}")

# وظيفة تكرار الأذكار كل ساعة
async def background_task():
    while True:
        for user_id in users:
            await send_random_zekr(user_id)
        await asyncio.sleep(3600)  # كل ساعة

# رسالة ترحيب عند /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in users:
        users.append(user_id)
        with open(users_file, "w", encoding="utf-8") as f:
            json.dump(users, f)

        welcome = f"أهلاً وسهلاً أخي الكريم {update.effective_user.first_name} في بوت الأذكار، سيساعدك كثيراً ❤️"
        await update.message.reply_text(welcome)

    keyboard = [
        [InlineKeyboardButton("🌅 أذكار الصباح", callback_data="morning")],
        [InlineKeyboardButton("🌇 أذكار المساء", callback_data="evening")],
        [InlineKeyboardButton("🛏️ أذكار النوم", callback_data="sleep")],
        [InlineKeyboardButton("🙏 أذكار بعد الصلاة", callback_data="prayer")],
        [InlineKeyboardButton("🔀 ذكر عشوائي", callback_data="random")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("اختر نوع الذكر الذي تريده:", reply_markup=reply_markup)

# التعامل مع الضغط على الأزرار
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    kind = query.data
    if kind in azkar:
        text = random.choice(azkar[kind])
        await query.message.reply_text(text)
    else:
        await query.message.reply_text("❌ لم أتمكن من العثور على هذا النوع من الأذكار.")

# نقطة استقبال Webhook من تيليجرام
@app.post(f"/webhook/{TOKEN}")
async def webhook_handler(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    await application.process_update(update)
    return {"ok": True}

# إعدادات البوت
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))

# تشغيل مهمة الأذكار التلقائية
async def on_startup():
    asyncio.create_task(background_task())

# عند بدء التطبيق
@app.on_event("startup")
async def startup_event():
    await on_startup()
