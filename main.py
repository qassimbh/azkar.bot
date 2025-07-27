import os
import json
import asyncio
import random

from fastapi import FastAPI
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)

# ✅ التوكن الكامل للبوت
TOKEN = "6288532598:AAEf-5FT5mCBr6D5Pv1iHap3mp9CtB7FE10"

# ✅ رابط Webhook الكامل للبوت على Render
WEBHOOK_URL = "https://azkar-bot.onrender.com/webhook/6288532598:AAEf-5FT5mCBr6D5Pv1iHap3mp9CtB7FE10"

# أسماء الملفات
AZKAR_FILE = "azkar.json"
USERS_FILE = "users.json"

# تهيئة FastAPI و Telegram Bot
app = FastAPI()
bot = Bot(token=TOKEN)
application = Application.builder().token(TOKEN).build()

# 📌 تحميل المستخدمين المسجلين
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# 📌 حفظ مستخدم جديد
def save_user(user_id: int):
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f)

# 📌 إرسال ذكر عشوائي كل ساعة
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
            print("❌ خطأ في إرسال الذكر:", e)
        await asyncio.sleep(3600)  # كل ساعة

# 📌 يبدأ عند تشغيل الخادم
@app.on_event("startup")
async def startup_event():
    await bot.set_webhook(WEBHOOK_URL)
    await application.initialize()
    await application.start()
    asyncio.create_task(send_random_zekr_every_hour())

# 📌 Webhook Endpoint لتلقّي التحديثات من Telegram
@app.post(f"/webhook/{TOKEN}")
async def webhook_endpoint(update: dict):
    telegram_update = Update.de_json(update, bot)
    await application.process_update(telegram_update)
    return {"ok": True}

# 📌 أمر /start
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

# 📌 عند الضغط على زر
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
        await query.message.reply_text("❌ لا توجد أذكار حالياً.")

# 📌 تسجيل الأوامر في التطبيق
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_callback))

# 📌 Healthcheck
@app.get("/")
async def healthcheck():
    return {"status": "Bot is running ✅"}

# ✅ لتشغيل السيرفر على Render
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
