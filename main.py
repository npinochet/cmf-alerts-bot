# coding=utf-8
import os, requests
from datetime import datetime, timedelta
from time import sleep
from cmfScrap import get_fondos, get_value, get_value_url

# Env vars
TOKEN = os.environ["token"]
chat_id = os.environ["chat_id"]
sleep_sec = int(os.environ["sleep_sec"])

# Templates
alert_template = """*ALERTA CMF*
Nombre Fondo: {}
Valor Ayer: {}
Valor Hoy: {}
[CMF Link]({})
"""

def send_message(text, markdown=True):
    url = "https://api.telegram.org/bot{}/".format(TOKEN)
    params = {
        "method": "sendMessage",
        "text": text,
        "chat_id": chat_id,
    }
    if markdown:
        params["parse_mode"] = "Markdown"
        params["disable_web_page_preview"] = "True"
    return requests.get(url, params=(params))

def parse_data(data, name, rut, now):
    data.pop(0) # remove header

    if len(data[0]) <= 1:
        print(name, "Doesn't have information")
        return "no_data"

    date = "{:02d}/{:02}/{}".format(now.day, now.month, now.year)
    if data[-1][0] != date:
        print(name, "Doesn't have updated information")
        return "no_updated"

    istr_num = len(data) // 2
    for i in range(istr_num):
        y = float(data[i][3].replace(",", "."))
        n = float(data[istr_num + i][3].replace(",", "."))

        if True:#abs(y - n) >= 0.1:
            print("ALERT TIME!!!", name)
            text = alert_template.format(name, y, n, get_value_url(rut))
            send_message(text)

    return "success"

if __name__ == "__main__":
    ruts, names = get_fondos()
    if not ruts:
        text = "Error, could not get company ruts"
        send_message(text, markdown=False)
        raise Exception(text)

    print("Checking", len(ruts), "Companies...")

    now = datetime.now()
    yest = now - timedelta(days=1)

    for i in range(len(ruts)):
        sleep(sleep_sec)

        r = ruts[i].split("-")[0]
        data = get_value(r, yest.day, yest.month, yest.year, now.day, now.month, now.year)
        if not data:
            text = "Error, could not get company data"
            send_message(text, markdown=False)
            raise Exception(text)

        parse_data(data, names[i], r, now)
