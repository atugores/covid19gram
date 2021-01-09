#!/bin/env python
# -*- coding: utf-8 -*-
import configparser
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os
# import re
import asyncio
from pyrogram import Client, filters, idle
# from pyrogram.types import CallbackQuery
# from pyrogram.errors import BadRequest
from covid19plot import COVID19Plot
from config.getdata import update_data
from config.settings import DBHandler
import logging
import random

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

config_file = "conf.ini"
config = configparser.ConfigParser()
config.read(config_file, encoding="utf-8")

admins = list(map(int, config["USER"]["admin"].split(',')))
app = Client(
    "covid19admbot",
    bot_token=config["API"]["adm_token"],
    api_id=config["API"]["API_ID"],
    api_hash=config["API"]["API_HASH"]
)

cplt = COVID19Plot()
dbhd = DBHandler()
MAXTEXT = 3000


async def exception_handle(user, e):
    if "USER_IS_BLOCKED" in str(e):
        logging.info(str(user) + ": Blocked the bot")
        return True
    elif "INPUT_USER_DEACTIVATED" in str(e):
        logging.info(str(user) + ": deactivated account")
        return True
    return False


def separa_qlsvl(text):
    separat = []
    max = MAXTEXT
    number = (len(text) - 1) // max + 2
    j = 0
    for i in range(1, number):
        separat.append((text[j * max: i * max]).rstrip(" \n"))
        j = i
    return separat


def separa_espais(text):
    paraules = text.split(" ")
    separat = []
    info = ""
    llarg = 0
    for paraula in paraules:
        if len(paraula) >= MAXTEXT:
            aux = separa_qlsvl(info + paraula)
            separat = separat + aux[: -1]
            info = (aux[-1] + " ").lstrip(" \n")
            llarg = len(info)
        elif llarg + len(paraula) >= MAXTEXT:
            separat.append(info.rstrip(" \n"))
            llarg = len(paraula)
            info = (paraula + " ").lstrip(" \n")
        else:
            llarg = llarg + len(paraula)
            info = (info + paraula + " ").lstrip(" \n")
    separat.append(info.rstrip(" "))
    return separat


def separa(text):
    linies = text.splitlines()
    separat = []
    info = ""
    llarg = 0
    for linea in linies:
        if len(linea) >= MAXTEXT:
            aux = separa_espais(info + linea)
            separat = separat + aux[: -1]
            info = (aux[-1] + "\n").lstrip("\n")
            llarg = len(info)
        elif llarg + len(linea) >= MAXTEXT:
            separat.append(info.rstrip("\n"))
            llarg = len(linea)
            info = (linea + "\n").lstrip("\n")
        else:
            llarg = llarg + len(linea)
            info = (info + linea + "\n").lstrip("\n")

    separat.append(info.rstrip(" \n"))

    return separat


async def envia(client, chat_id, text):
    linies = []
    if len(text) >= MAXTEXT:
        linies = separa(text)
        m = ()
        for linea in linies:
            m = await client.send_message(chat_id, linea, parse_mode="markdown")
        return(m)
    else:
        return await client.send_message(chat_id, text, parse_mode="markdown")


def normal(s):
    replacements = (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
        ("à", "a"),
        ("è", "e"),
        ("ï", "i"),
        ("ò", "o"),
        ("ü", "u"),
        ("î", "i"),
    )
    for a, b in replacements:
        s = s.replace(a, b).replace(a.upper(), b.upper())
    return s


async def update_notifications():
    updated = await update_data()
    text = {
        'world': '🌐Global data updated',
        'spain': '🇪🇸Spain data updated',
        'italy': '🇮🇹Italy data updated',
        'france': '🇫🇷France data updated',
        'austria': '🇦🇹Austria data updated',
        'argentina': '🇦🇷Argentina data updated',
        'australia': '🇦🇺Australia data updated',
        'brazil': '🇧🇷Brazil data updated',
        'canada': '🇨🇦Canada data updated',
        'chile': '🇨🇱Chile data updated',
        'china': '🇨🇳China data updated',
        'colombia': '🇨🇴Colombia data updated',
        'germany': '🇩🇪Germany data updated',
        'india': '🇮🇳India data updated',
        'mexico': '🇲🇽Mexico data updated',
        'portugal': '🇵🇹Portugal data updated',
        'us': '🇺🇸US data updated',
        'unitedkingdom': '🇬🇧United Kingdom data updated',
        'balears': 'Balearic Islands data updated',
        'mallorca': 'Mallorca data updated',
        'menorca': 'Menorca data updated',
        'eivissa': 'Eivissa data updated',
        'catalunya': 'Catalonia data updated',
    }
    for scope in cplt.SCOPES:
        if updated[scope]:
            for user_id in admins:
                try:
                    await app.send_message(user_id, text[scope])
                except Exception as e:
                    await exception_handle(user_id, e)


async def DoBot(command, chat, user_id, client, **kwargs):
    comm = command.pop(0)

    if comm in ["start", "help"]:
        await client.send_message(chat, "Admin comands:\n\n/clean\n/update\n/status\n/get")

    elif comm == "clean" and user_id in admins:
        await client.send_message(chat, "Cleanig images cache.")
        filelist = [f for f in os.listdir("images") if f.endswith(".png")]
        await dbhd.clean_hashes()
        for f in filelist:
            os.remove(os.path.join("images", f))
        await client.send_message(chat, "Cleaned.")
    elif comm == "update" and user_id in admins:
        await client.send_message(chat, "Updating data.")
        await update_notifications()
        await client.send_message(chat, "Data Updated.")
    elif comm == "status" and user_id in admins:
        text = await dbhd.status_data()
        text += "\n" + await dbhd.status_users()
        text += "\n" + await dbhd.status_notifications()
        text += "\n" + await dbhd.status_files()
        await envia(client, chat, text)
    elif comm == "get":
        SCOPES = ['world', 'spain', 'italy', 'france', 'austria', 'argentina', 'australia', 'brazil', 'canada', 'chile', 'china', 'colombia', 'germany', 'india', 'mexico', 'portugal', 'us', 'unitedkingdom', 'balears', 'mallorca', 'menorca', 'eivissa', 'catalunya']
        failed = True
        for scp in command:
            if scp in SCOPES:
                filename = f'data/{scp}_covid19gram.csv'
                failed = False
                await client.send_document(chat, filename)
        if failed:
            text = "**Use a region from this list:**"
            for scp in SCOPES:
                text = text + "\n" + scp
            await client.send_message(chat, text)
    elif comm == "opendata":
        if random.randint(0, 4) == 3:
            await client.send_message(chat, "👀")


@app.on_message(filters.text)
async def g_request(client, message):
    user_id = message.from_user.id
    chat = message.chat.id
    if message.text:
        comm = message.text.split()
        comm[0] = comm[0].split('@')[0].strip('/')
        # param = ""
        # if re.match('^/' + comm + ' .+', message.text):
        #     param = re.search('^/' + comm + ' (.+)', message.text).group(1)
        # md_param = message.text.markdown.replace('/' + comm, '', 1)
        await DoBot(comm, chat, user_id, client)


async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_notifications, "interval", hours=1)
    scheduler.start()
    await app.start()
    logging.info("Started")
    await idle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
