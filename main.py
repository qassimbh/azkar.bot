import json, random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "6288532598:AAEf-5FT5mCBr6D5Pv1iHap3mp9CtB7FE10"

def load_azkar():
    try:
        with open("azkar.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def load_users():
    try:
        with open("rshq.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_user(uid):
    users = load_users()
    if uid not in users:
        users.append(uid)
        with open("rshq.json", "w", encoding="utf-8") as f:
            json.dump(users, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    uid = u.id
    name = f"@{u.username}" if u.username else u.first_name
    users = load_users()
    if uid not in users:
        await update.message.reply_text(f"أهلاً بك يا {name} في بوت الأذكار 😊")
        save_user(uid)
    azkar = load_azkar()
    if azkar:
        await update.message.reply_text(random.choice(azkar))

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot is live (polling)...")
    app.run_polling()
