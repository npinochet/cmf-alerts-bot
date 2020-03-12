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
Valot hoy: {}
Valor ayer: {}
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

def check_data(data, out):
    data.pop(0) # remove header

    if len(data[0]) <= 1:
        return "no_data"

    istr_num = 1
    while data[0][0] == data[istr_num][0]:
        istr_num = istr_num + 1
        if istr_num >= len(data):
            return "not_reported"

    data = data[-istr_num*2:]

    for i in range(istr_num):
        y = float(data[i][3].replace(",", "."))
        n = float(data[istr_num + i][3].replace(",", "."))
        if y != 0 and abs(n/y) <= 0.5:
            out.append(n)
            out.append(y)
            return "alert"

    return "no_change"

if __name__ == "__main__":
    ruts, names = get_fondos()
    if not ruts:
        text = "Error, could not get company ruts"
        send_message(text, markdown=False)
        raise Exception(text)

    print("Checking", len(ruts), "Companies...")

    now = datetime.now() + timedelta(days=1)
    yest = datetime.now() - timedelta(days=3)

    for i in range(len(ruts)):
        sleep(sleep_sec)

        r = ruts[i].split("-")[0]
        data = get_value(r, yest.day, yest.month, yest.year, now.day, now.month, now.year)
        if not data:
            text = "Error, could not get company data"
            send_message(text, markdown=False)
            raise Exception(text)

        value = []
        status = check_data(data, value)

        if status == "alert":
            print("ALERT TIME!!!", names[i])
            text = alert_template.format(names[i], value[0], value[1], get_value_url(r))
            send_message(text)
        elif status == "no_change":
            print(names[i], "Has valid data")
        elif status == "no_data":
            print(names[i], "Doesn't have information")
        elif status == "not_reported":
            print(names[i], "Haven't reported today's value")
        break
