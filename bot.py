
import os
import json
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

ADMIN_USERNAME = "nookaar"
TRANSACTION_FILE = "transactions.json"
USERS_FILE = "users.json"

# بارگذاری کاربران مجاز
with open(USERS_FILE, "r") as f:
    allowed_users = json.load(f).keys()

# بارگذاری تراکنش‌ها
if os.path.exists(TRANSACTION_FILE):
    with open(TRANSACTION_FILE, "r") as f:
        transactions = json.load(f)
else:
    transactions = []

def save_transactions():
    with open(TRANSACTION_FILE, "w") as f:
        json.dump(transactions, f, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    if username not in allowed_users:
        await update.message.reply_text("دسترسی ندارید.")
        return
    with open("start_message.txt", "r", encoding="utf-8") as f:
        await update.message.reply_text(f.read())

async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    if username not in allowed_users:
        await update.message.reply_text("دسترسی ندارید.")
        return
    await update.message.reply_text("چند تتر واریزی داشتی جان🟩")
    try:
        amount = float(context.args[0])
        transaction = {
            "username": username,
            "amount": amount,
            "type": "deposit",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        transactions.append(transaction)
        save_transactions()
        await update.message.reply_text(f"واریز {amount} تتر ثبت شد.")
    except:
        await update.message.reply_text("مثال: /deposit 100")

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    if username not in allowed_users:
        await update.message.reply_text("دسترسی ندارید.")
        return
    await update.message.reply_text("چند تتر برداشت داشتی جان🟥")
    try:
        amount = float(context.args[0])
        transaction = {
            "username": username,
            "amount": amount,
            "type": "withdraw",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        transactions.append(transaction)
        save_transactions()
        await update.message.reply_text(f"برداشت {amount} تتر ثبت شد.")
    except:
        await update.message.reply_text("مثال: /withdraw 50")

async def share(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    if username not in allowed_users:
        await update.message.reply_text("دسترسی ندارید.")
        return
    deposits = {}
    for t in transactions:
        if t["type"] == "deposit":
            deposits[t["username"]] = deposits.get(t["username"], 0) + t["amount"]
    total = sum(deposits.values())
    message = "سلام جان\nشما تا این لحظه:\n"
    for u in deposits:
        percent = (deposits[u] / total) * 100 if total else 0
        message += f"@{u}: {percent:.2f}% سهم دارد\n"
    if ADMIN_USERNAME in deposits:
        message += "صد البته که سهم محمدرضا مال شماست✅️"
    await update.message.reply_text(message)

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    if username not in allowed_users:
        await update.message.reply_text("دسترسی ندارید.")
        return
    await update.message.reply_text("سلام جان\nتراکنش های شما تا این لحظه به شرح ذیل می باشد:")
    lines = []
    for t in transactions:
        if t["username"] == username or username == ADMIN_USERNAME:
            sign = "+" if t["type"] == "deposit" else "-"
            lines.append(f"{t['timestamp']} | {sign}{t['amount']} تتر")
    if lines:
        await update.message.reply_text("\n".join(lines))
    else:
        await update.message.reply_text("تراکنشی ثبت نشده است.")

if __name__ == '__main__':
    token = os.environ.get("BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("deposit", deposit))
    app.add_handler(CommandHandler("withdraw", withdraw))
    app.add_handler(CommandHandler("share", share))
    app.add_handler(CommandHandler("history", history))
    app.run_polling()
