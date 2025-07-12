
import requests
from bs4 import BeautifulSoup
from telegram.ext import Updater, CommandHandler
import time
import os

TOKEN = '7684771448:AAHoZN7XEACNupV4RtCcW31dk1rAmPEhLN0'
USERS_FILE = 'users.txt'
CHECK_INTERVAL = 3600

sent_games = set()

def get_free_games():
    url = "https://steamdb.info/sales/?min_discount=100&max_discount=100"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    games = []
    rows = soup.select("tr.app")
    for row in rows:
        game_name = row.select_one(".b").text.strip()
        link = "https://store.steampowered.com/app/" + row['data-appid']
        cover_url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{row['data-appid']}/header.jpg"
        games.append({'name': game_name, 'link': link, 'cover': cover_url, 'appid': row['data-appid']})
    return games

def read_users():
    if not os.path.exists(USERS_FILE):
        return set()
    with open(USERS_FILE, 'r') as f:
        return set(line.strip() for line in f)

def write_user(chat_id):
    users = read_users()
    if str(chat_id) not in users:
        with open(USERS_FILE, 'a') as f:
            f.write(str(chat_id) + '\n')

def start(update, context):
    chat_id = update.effective_chat.id
    write_user(chat_id)
    context.bot.send_message(chat_id=chat_id, text="سلام! ربات بازی‌های رایگان استیم فعال شد.\nاز دستور /freegames برای دیدن بازی‌های رایگان استفاده کن.")

def freegames(update, context):
    chat_id = update.effective_chat.id
    games = get_free_games()
    if not games:
        context.bot.send_message(chat_id=chat_id, text="فعلاً بازی رایگانی نیست.")
        return

    for game in games:
        text = f"🎮 *{game['name']}*\n🔗 [مشاهده در استیم]({game['link']})"
        context.bot.send_photo(chat_id=chat_id, photo=game['cover'], caption=text, parse_mode='Markdown')

def send_updates(context):
    games = get_free_games()
    users = read_users()
    global sent_games
    new_games = [g for g in games if g['name'] not in sent_games]

    for game in new_games:
        for user in users:
            text = f"🎮 *{game['name']}* الان رایگان شده!\n🔗 [مشاهده در استیم]({game['link']})"
            context.bot.send_photo(chat_id=int(user), photo=game['cover'], caption=text, parse_mode='Markdown')
        sent_games.add(game['name'])

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("freegames", freegames))
    updater.job_queue.run_repeating(send_updates, interval=CHECK_INTERVAL, first=10)
    updater.start_polling()
    print("🤖 ربات اجرا شد.")
    updater.idle()

if __name__ == "__main__":
    main()
