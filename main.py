import dotenv
import os
import telebot
import nc_py_api
import requests
import threading
import validators
import time
from io import BytesIO

dotenv.load_dotenv()
BOT_TOKEN = os.environ.get('BOT_TOKEN')
URL = os.environ.get('URL')
AUTH_USER = os.environ.get('AUTH_USER')
AUTH_PASS = os.environ.get('AUTH_PASS')
nc = nc_py_api.Nextcloud(nextcloud_url=URL,
                         nc_auth_user=AUTH_USER,
                         nc_auth_pass=AUTH_PASS)
os.chdir(os.path.dirname(__file__))

threads = list()
bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    text = 'Hi Dani.'
    bot.send_message(message.chat.id, text)


def threaded_dani(message: str):
    filename = message.text.split('/')[-1].split('?')[0]
    try:
        result = requests.get(message.text, stream=True)
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        bot.send_message(message.chat.id, text=err.args)
        return
    total_length = result.headers['Content-length']
    length = int(total_length) / 1024 / 1024
    bot.send_message(message.chat.id,
                     text=f'Downloading {filename}{"|||size:%.2fMB"}.' % length)
    file = open(filename, 'wb')
    t0 = time.time()
    for chunk in result.iter_content(chunk_size=100 * 1024 * 1024):
        file.write(chunk)
        length -= 100
        t1 = time.time()
        t = int(t1 - t0)
        if t != 0:
            speed = 100 / t
        else:
            speed = 1
        bot.send_message(
            message.chat.id,
            text=f'{filename}{"remaining size:%.2fMB||||speed:%.2fMB/s"}' %
            (length, speed))
        t0 = t1
    file.close()
    buffer = BytesIO()
    buffer = open(filename, 'rb')
    buffer.seek(0)
    bot.send_message(message.chat.id, text=f'Uploading {filename}.')
    nc.files.upload_stream(filename, buffer)
    buffer.close()
    os.remove(filename)
    bot.send_message(message.chat.id,
                     text=f'Finished Uploading {filename} to the server')


@bot.message_handler(func=lambda message: validators.url(message.text),
                     content_types=['text'])
def handle_links(message):
    x = threading.Thread(target=threaded_dani, args=(message,))
    threads.append(x)
    x.start()


def threaded_file(message: str):
    filename = "adasd"


@bot.message_handler(func=lambda message: True, content_types=['document'])
def handle_files(message):
    bot.send_message(message.chat.id, text=message.document)


# x = threading.Thread(target=threaded_file, args=(message,))
# threads.append(x)
# x.start()


@bot.message_handler(func=lambda message: True, content_types=['video'])
def handle_video(message):
    bot.send_message(message.chat.id, text=message.video)


@bot.message_handler(func=lambda message: True)
def defult(message):
    text = message.text
    bot.send_message(message.chat.id, text)


bot.infinity_polling()
