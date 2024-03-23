import os
import telebot
import nc_py_api
import requests
import threading
import validators
import time
import my_sql
from io import BytesIO


BOT_TOKEN = my_sql.bot_token()
URL = my_sql.url()

bot = telebot.TeleBot(BOT_TOKEN)

os.chdir(os.path.dirname(__file__))
threads = list()


@bot.message_handler(commands=['start'])
def start(message):
    text = 'Hi '+message.chat.username
    bot.send_message(message.chat.id, text)


global_num = 0


def threaded_dani(message: str, nc: nc_py_api.Nextcloud):
    global global_num

    filename = message.text.split('/')[-1].split('?')[0]

    try:
        result = requests.get(message.text, stream=True)
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        bot.send_message(message.chat.id, text=err.args)
        return

    total_length = result.headers['Content-length']
    length = int(total_length) / 1024 / 1024

    try:
        sent_message = bot.send_message(
            message.chat.id,
            text=f'Downloading {filename}{"|||size:%.2fMB"}.' % length)
    except Exception as err:
        bot.send_message(message.chat.id, text=err.args)
        filename = "file.mp4"
        sent_message = bot.send_message(
            message.chat.id,
            text=f'Downloading {filename}{"|||size:%.2fMB"}.' % length)

    if os.path.exists(filename):
        global_num += 1
        ext = filename.split('.')[-1]
        ext = '.'+ext
        new_ext = str(global_num)+ext
        filename = filename.replace(ext, new_ext)

    # Download Link
    file = open(filename, 'wb')
    t0 = time.time()
    for chunk in result.iter_content(chunk_size=10 * 1024 * 1024):
        file.write(chunk)
        length -= 10
        t1 = time.time()
        t = int(t1 - t0)
        if t != 0:
            speed = 10 / t
        else:
            speed = 1000
        bot.edit_message_text(
            text=f'{filename}{"|||remaining size:%.2fMB|||speed:%.2fMB/s"}' %
            (length, speed),
            chat_id=message.chat.id,
            message_id=sent_message.message_id)
        t0 = t1
    file.close()

    # Upload Link
    buffer = BytesIO()
    buffer = open(filename, 'rb')
    buffer.seek(0)
    bot.edit_message_text(text=f'Uploading {filename}.',
                          chat_id=message.chat.id,
                          message_id=sent_message.message_id)

    try:
        nc.files.upload_stream(filename, buffer)

    except nc_py_api._exceptions.NextcloudException as err:
        bot.send_message(message.chat.id, text=err)
        return

    buffer.close()
    os.remove(filename)

    bot.send_message(message.chat.id,
                     text=f'Finished Uploading {filename} to the server')


@bot.message_handler(func=lambda message: validators.url(message.text),
                     content_types=['text'])
def handle_links(message):
    try:
        ite = my_sql.my_sql[message.chat.username]
        AUTH_USER = ite["auth_user"]
        AUTH_PASS = ite["auth_pass"]
        nc = nc_py_api.Nextcloud(nextcloud_url=URL,
                                 nc_auth_user=AUTH_USER,
                                 nc_auth_pass=AUTH_PASS)
    except Exception as err:
        bot.send_message(message.chat.id, text=err)
        return
    x = threading.Thread(target=threaded_dani, args=(message, nc,))
    threads.append(x)
    x.start()


@bot.message_handler(func=lambda message: True)
def defult(message):
    text = message.text
    bot.send_message(message.chat.id, text)


bot.infinity_polling()
