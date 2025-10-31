# Anonymous Telegram Bot

A Telegram bot that allows users to send messages anonymously to the bot owner.  
The owner can reply privately, view user information, and manage conversations easily.  

---

## 📝 Features

- Users can send messages anonymously  
- Owner receives forwarded messages  
- Inline buttons to view user info, reply, or cancel reply  
- Welcome sticker for new users  
- Lightweight and easy to deploy  

---

## ⚙️ Requirements

- Python 3.10+  
- `python-telegram-bot` library (v20+)  
- Optional `keep_alive.py` for 24/7 uptime  

Install dependencies with:

```bash
pip install python-telegram-bot --upgrade
🚀 Usage
Clone this repository:

bash
Copy code
git clone https://github.com/USERNAME/anonymous-telegram-bot.git
cd anonymous-telegram-bot
Set your bot token and owner ID in bot.py:

python
Copy code
BOT_TOKEN = "YOUR_BOT_TOKEN"
OWNER_ID = YOUR_TELEGRAM_ID
WELCOME_STICKER = "optional_sticker_url"
Run the bot:

bash
Copy code
python bot.py
📁 File structure
bot.py – main bot script

keep_alive.py – optional web server for continuous uptime

README.md – project explanation

requirements.txt – list of Python libraries
