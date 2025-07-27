import os
import json
import asyncio
import random

from fastapi import FastAPI
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)

# ✅ توكن البوت
TOKEN = "6288532598:AAEf-5FT5mCBr6D5Pv1iHap3mp9CtB7FE10"

# ✅ رابط الويب هوك النهائي
WEBHOOK_URL = "https://azkar-bot.onrender.com/webhook/6288532598:AAEf-5FT5mCBr6D5Pv1iHap3mp9CtB7FE10"

# 📁 أسماء الملفات
AZKAR_FILE = "azkar.json"
USERS_FILE = "users.json"

# إعداد البوت والتطبيق
app = FastAPI()
bot = Bot(token=TOKEN)
application = Application.builder().token(TOKEN).build()

# ✅ تحميل المستخدمين وحفظهم
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_user(user_id: int):
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f)

# ✅ إرسال ذكر كل ساعة تلقائيًا
async def send_random_zekr_every_hour():
    while True:
        try:
            with open(AZKAR_FILE, "r", encoding="utf-8") as f:
                azkar_data = json.load(f)
            all_azkar = []
            for lst in azkar_data.values():
                all_azkar.extend(lst)
            if all_azkar:
                zekr = random.choice(all_azkar)
                for user_id in load_users():
                    try:
                        await bot.send_message(chat_id=user_id, text=f"🕒 ذكر الساعة:\n\n{zekr}")
                    except:
                        pass
        except Exception as e:
            print("❌ خطأ أثناء إرسال ذكر الساعة:", e)
        await asyncio.sleep(3600)

# ✅ تشغيل عند بدء السيرفر
@app.on_event("startup")
async def startup_event():
    await bot.set_webhook(WEBHOOK_URL)
    await application.initialize()
    await application.start()
    asyncio.create_task(send_random_zekr_every_hour())

# ✅ نقطة استقبال التحديثات من Telegram
@app.post(f"/webhook/{TOKEN}")
async def webhook_endpoint(update: dict):
    telegram_update = Update.de_json(update, bot)
    await application.process_update(telegram_update)
    return {"ok": True}

# ✅ أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id)
    text = f"أهلاً وسهلاً أخي الكريم {user.first_name} في بوت الأذكار، سيساعدك كثيراً.\nاختر نوع الذكر:"
    keyboard = [
        [InlineKeyboardButton("📿 أذكار الصباح", callback_data="azkar_sabah")],
        [InlineKeyboardButton("🌙 أذكار المساء", callback_data="azkar_masaa")],
        [InlineKeyboardButton("🛏️ أذكار النوم", callback_data="azkar_sleep")],
        [InlineKeyboardButton("🙏 أذكار الصلاة", callback_data="azkar_salah")],
        [InlineKeyboardButton("🔀 ذكر عشوائي", callback_data="azkar_random")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)

# ✅ عند ضغط المستخدم على زر
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    category_map = {
        "azkar_sabah": "الصباح",
        "azkar_masaa": "المساء",
        "azkar_sleep": "النوم",
        "azkar_salah": "الصلاة",
        "azkar_random": None
    }

    category = category_map.get(data)
    with open(AZKAR_FILE, "r", encoding="utf-8") as f:
        azkar_data = json.load(f)

    if category:
        azkar_list = azkar_data.get(category, [])
    else:
        azkar_list = [z for lst in azkar_data.values() for z in lst]

    if azkar_list:
        zekr = random.choice(azkar_list)
        await query.message.reply_text(zekr)
    else:
        await query.message.reply_text("❌ لا توجد أذكار متاحة حالياً.")

# ✅ تسجيل الأوامر
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_callback))

# ✅ صفحة فحص السيرفر
@app.get("/")
async def healthcheck():
    return {"status": "Bot is running ✅"}
