import nc_py_api
from json import dumps
import dotenv
import os
import requests
import threading
import time
from io import BytesIO

os.chdir(os.path.dirname(__file__))

dotenv.load_dotenv()

URL = os.environ.get('URL')
AUTH_USER = os.environ.get('AUTH_USER')
AUTH_PASS = os.environ.get('AUTH_PASS')

nc = nc_py_api.Nextcloud(nextcloud_url=URL,
                         nc_auth_user=AUTH_USER,
                         nc_auth_pass=AUTH_PASS)

event = threading.Event()


def cloud(a: str, b: BytesIO):
    nc.files.upload_stream(a, b)
    event.clear()


def upload_file(filename: str):
    print('initating upload...')
    buffer = BytesIO()
    buffer = open(filename, 'rb')
    buffer.seek(0)
    t0 = time.time()
    event.set()
    x = threading.Thread(target=cloud, args=(filename, buffer))
    x.start()
    while event.is_set():
        t1 = time.time()
        if (t1 - t0) >= 20.0:
            print("Uploading...")
            t0 = t1
    # x.join()
    buffer.close()
    os.remove(filename)
    print("Done")


upload_file(input())
