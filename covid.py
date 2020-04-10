#!/bin/env python
# -*- coding: utf-8 -*-
import string
import configparser
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os
import re
import asyncio
from pyrogram import Client
from pyrogram import Filters, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, ReplyKeyboardMarkup
from pyrogram.errors import BadRequest
from covid19plot import COVID19Plot
from config.getdata import pull_datasets, pull_global
from config.countries import countries
from config.settings import DBHandler
import gettext


config_file = "conf.ini"
config = configparser.ConfigParser()
config.read(config_file, encoding="utf-8")

me = int(config["USER"]["admin"])
app = Client(
    "covid19bot",
    bot_token=config["API"]["api_token"],
    api_id=config["API"]["API_ID"],
    api_hash=config["API"]["API_HASH"]
)
cplt = COVID19Plot()
tot = cplt.get_regions("world")
world = cplt.get_regions("world")
comunitat = cplt.get_regions("spain")
comunitat.sort()
tot.extend(comunitat)
tot.sort()
translations = {}
dbhd = DBHandler()

for language in cplt.LANGUAGES:
    translation = gettext.translation('messages', localedir='locales', languages=[language])
    translation.install()
    translations[language] = translation


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
    )
    for a, b in replacements:
        s = s.replace(a, b).replace(a.upper(), b.upper())
    return s


def cerca(paraula, language="en"):
    _ = translations[language].gettext
    cerca = normal(paraula).lower()
    resultats = []
    for r in tot:
        if normal(_(r)).lower().find(cerca) > -1:
            resultats.append(r)
    return resultats


def get_label(region='Global', language='en'):
    _ = translations[language].gettext
    label = '\n' + _('__Generated by [COVID19gram](t.me/COVID19gram_bot)__') + '\n'
    if region in world:
        label += _('__Data source from__') + ' __[CSSEGISandData/COVID-19](https://github.com/CSSEGISandData/COVID-19)__'
    else:
        label += _('__Data source from__') + ' __[Datadista](https://github.com/datadista/datasets/)__'
    return label


def get_caption(region, plot_type="daily_cases", language="en"):
    _ = translations[language].gettext
    flaged_region = region
    if region in countries:
        flaged_region = countries[region]['flag'] + _(region)
    else:
        flaged_region = _(region)
    title = ""
    if plot_type == "daily_cases":
        title = _('Cases increase at {region}').format(region=flaged_region)
    elif plot_type == "active_recovered_deceased":
        title = _('Active cases, recovered and deceased at {region}').format(region=flaged_region)
    elif plot_type == "active":
        title = _('Active cases at {region}').format(region=flaged_region)
    elif plot_type == "recovered":
        title = _('Recovered cases at {region}').format(region=flaged_region)
    elif plot_type == "daily_deceased":
        title = _('Deaths evolution at {region}').format(region=flaged_region)
    return title + "\n" + cplt.get_plot_caption(plot_type=plot_type, region=region, language=language)


def botons(taula, plot_type="daily_cases", regio="Total", scope="spain", language="en"):
    _ = translations[language].gettext
    ibt = []
    l_botns = []
    botonets = []
    result_all = []
    for chart in list(string.ascii_lowercase):
        result = [i for i in taula if _(i)[0].lower() == chart and i != "Global"]
        result_all.extend(result)
        if len(result_all) > 7 or chart == "z":
            for item in result_all:
                flag = ""
                if item in countries:
                    flag = countries[item]['flag']
                ibt.append(InlineKeyboardButton(flag + _(item), callback_data=item + "_" + plot_type.replace('_', '-')))
            botonets = [ibt[i * 3:(i + 1) * 3] for i in range((len(ibt) // 4) + 2)]
            botonets.extend([[InlineKeyboardButton(_("⬅️Back"), callback_data="back_" + scope)]])
            btns = InlineKeyboardMarkup(botonets)
            l_botns.append(btns)
            ibt = []
            botonets = []
            result_all = []
    return l_botns


def b_alphabet(taula, plot_type="daily_cases", regio="Total", scope="spain", language="en"):
    _ = translations[language].gettext
    ibt = []
    botonets = []
    ordre = 0
    text = ""
    len_all = 0
    s_char = ""
    ibt.append(InlineKeyboardButton("🌐" + _("Global"), callback_data=_("Global") + "_" + plot_type.replace('_', '-')))
    for chart in list(string.ascii_lowercase):
        result = [i for i in taula if _(i)[0].lower() == chart and i != "Global"]
        len_all += len(result)
        if len_all > 7 or chart == "z":
            if s_char == "":
                text = chart.upper()
            else:
                text = s_char + "-" + chart.upper()
            s_char = ""
            len_all = 0
            ibt.append(InlineKeyboardButton(text, callback_data="alph_" + str(ordre) + "_" + scope))
            ordre += 1
        elif len(result) > 0:
            if s_char == "":
                s_char = chart.upper()
    botonets = [ibt[i * 3:(i + 1) * 3] for i in range((len(ibt) // 4) + 2)]
    btns = InlineKeyboardMarkup(botonets)
    return btns


def b_single(plot_type="daily_cases", region="Total", language="en"):
    _ = translations[language].gettext
    buttons = [[
        InlineKeyboardButton("🦠", callback_data="s_" + region + "_daily-cases"),
        InlineKeyboardButton("📊", callback_data="s_" + region + "_active-recovered-deceased"),
        InlineKeyboardButton("📈", callback_data="s_" + region + "_active"),
        InlineKeyboardButton("✅", callback_data="s_" + region + "_recovered"),
        InlineKeyboardButton("❌", callback_data="s_" + region + "_daily-deceased")]]
    btns = InlineKeyboardMarkup(buttons)
    return btns


def b_find(search, plot_type="daily_cases", language="en"):
    _ = translations[language].gettext
    taula = cerca(search, language)
    ibt = []
    l_botns = []
    botonets = []
    pageSize = 18
    max = len(taula) // pageSize

    if len(taula) % pageSize != 0:
        max = len(taula) // pageSize + 1

    for pag in range(max):
        for item in taula[pag * pageSize:(pag + 1) * pageSize]:
            flag = ""
            if item in countries:
                flag = countries[item]['flag']
            ibt.append(InlineKeyboardButton(flag + _(item), callback_data=item + "_" + plot_type.replace('_', '-')))
        botonets = [ibt[i * 3:(i + 1) * 3] for i in range((len(ibt) // 4) + 2)]
        if pag == 0 and pag != max - 1:
            botonets.extend([[InlineKeyboardButton(">>", callback_data="f_" + str(pag + 1) + "_" + search)]])
        elif pag == max - 1 and pag != 0:
            botonets.extend([[InlineKeyboardButton("<<", callback_data="f_" + str(pag - 1) + "_" + search)]])
        elif pag > 0 and pag < max - 1:
            botonets.extend([[
                InlineKeyboardButton("<<", callback_data="f_" + str(pag - 1) + "_" + search),
                InlineKeyboardButton(">>", callback_data="f_" + str(pag + 1) + "_" + search)]])
        btns = InlineKeyboardMarkup(botonets)
        l_botns.append(btns)
        ibt = []
        botonets = []
    return l_botns


def b_spain(taula, plot_type="daily_cases", language="en"):
    _ = translations[language].gettext
    ibt = []
    l_botns = []
    botonets = []
    for item in taula:
        ibt.append(InlineKeyboardButton(_(item), callback_data=item + "_" + plot_type.replace('_', '-')))
    botonets = [ibt[i * 3:(i + 1) * 3] for i in range((len(ibt) // 4) + 2)]
    btns = InlineKeyboardMarkup(botonets)
    l_botns.append(btns)
    return l_botns[0]


def b_lang(language="en"):
    _ = translations[language].gettext
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("English", callback_data="lang_en"),
        InlineKeyboardButton("Català", callback_data="lang_ca"),
        InlineKeyboardButton("Español", callback_data="lang_es")]])


def b_start(language="en"):
    _ = translations[language].gettext
    rep_markup = ReplyKeyboardMarkup([
        [_("🌐Global"), _("🇪🇸Spain")],
        [_("💬Language"), _("❓About")]],
        resize_keyboard=True)
    return rep_markup


async def set_language(user_id, language):
    await dbhd.set_language(user_id, language)


async def get_language(user):
    user_id = user.id
    language = await dbhd.get_language(user_id)
    if language != 'None':
        return language
    elif user.language_code and user.language_code in cplt.LANGUAGES:
        return user.language_code
    else:
        return 'en'


async def show_region(client, chat, plot_type="daily_cases", region="Total", language='en'):
    _ = translations[language].gettext
    btns = b_single(plot_type=plot_type, region=region, language=language)
    flname = cplt.generate_plot(plot_type=plot_type, region=region, language=language)
    caption = get_caption(region, plot_type, language=language)
    try:
        await client.send_photo(chat, photo=flname, caption=caption, reply_markup=btns)
    except BadRequest as e:
        if str(e).find("IMAGE_PROCESS_FAILED") > -1:
            os.remove(flname)
            flname = cplt.generate_plot(plot_type=plot_type, region=region, language=language)
            await client.send_photo(chat, photo=flname, caption=caption, reply_markup=btns)
        elif str(e).find("MESSAGE_NOT_MODIFIED") > -1:
            print("Error: " + str(e))
    except Exception as err:
        print("Unexpected error:" + type(err) + " - " + err)
        raise


async def edit_region(client, chat, mid, plot_type="daily_cases", region="Total", language="en"):
    btns = b_single(plot_type=plot_type, region=region, language=language)
    flname = cplt.generate_plot(plot_type=plot_type, region=region, language=language)
    caption = get_caption(region, plot_type=plot_type, language=language)
    try:
        await client.edit_message_media(chat, mid, InputMediaPhoto(media=flname, caption=caption), reply_markup=btns)
    except BadRequest as e:
        if str(e).find("IMAGE_PROCESS_FAILED") > -1:
            os.remove(flname)
            flname = cplt.generate_plot(plot_type=plot_type, region=region, language=language)
            await client.edit_message_media(chat, mid, InputMediaPhoto(media=flname, caption=caption), reply_markup=btns)
        elif str(e).find("MESSAGE_NOT_MODIFIED") > -1:
            print("Error: " + str(e))
    except Exception as err:
        print("Unexpected error:" + type(err) + " - " + err)
        raise


async def DoBot(comm, param, client, message, language="en", **kwargs):
    _ = translations[language].gettext
    user = message.from_user.id
    chat = message.chat.id
    if comm == "start":
        btns = b_alphabet(comunitat, language=language)
        rep_markup = b_start(language)
        await client.send_message(chat, _("⚙️Main Menu"), reply_markup=rep_markup)
    if comm == "spain":
        btns = b_spain(comunitat, language=language)
        caption = _("Choose a Region")
        await client.send_message(chat, caption, reply_markup=btns)
    if comm == "world":
        btns = b_alphabet(world, scope="world", language=language)
        caption = _("Choose a Region")
        flname = cplt.generate_scope_plot(plot_type='cases_normalized', scope="world", language=language)
        await client.send_photo(chat, photo=flname, caption=caption, reply_markup=btns)
        # await client.send_message(chat, caption, reply_markup=btns)
    elif comm == "clean" and user == me:
        filelist = [f for f in os.listdir("images") if f.endswith(".png")]
        for f in filelist:
            os.remove(os.path.join("images", f))
    elif comm == "find":
        if len(param) > 0:
            resultats = cerca(param, language=language)
            if len(resultats) == 0:
                await client.send_message(chat, _('No results for `{param}`').format(param=param))
            elif len(resultats) == 1:
                await show_region(client, chat, region=resultats[0])
            else:
                btns = b_find(param, language=language)[0]
                caption = f'Search Results for `{param}`'
                await client.send_message(chat, caption, reply_markup=btns)

    elif comm == "about":
        about = _("**Chart Buttons**") + "\n"
        about += _("🦠 - __Case increase.__") + "\n"
        about += _("📊 - __Active cases, recovered and deceased.__") + "\n"
        about += _("📈 - __Active cases.__") + " \n"
        about += _("✅ - __Recovered cases.__") + "\n"
        about += _("❌ - __Daily deaths evolution.__") + "\n\n"
        about += _("**Data Sources**") + "\n"
        about += _('__Spain data source from__') + ' __[Datadista](https://github.com/datadista/datasets/)__\n\n'
        about += _('__World data source from__') + ' __[JHU CSSE](https://github.com/CSSEGISandData/COVID-19)__, '
        about += _('__transformed to JSON by__') + ' __[github.com/pomber](https://github.com/pomber/covid19)__\n\n'
        about += _("**Contact**") + '\n'
        about += _("You can contact us using") + " [@C19G_feedbackbot](t.me/C19G_feedbackbot)"
        about += '\n\n＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿'

        await client.send_message(chat, about, disable_web_page_preview=True)


@app.on_message(Filters.text)
async def g_request(client, message):
    chat = message.chat.id
    language = await get_language(message.from_user)
    _ = translations[language].gettext
    if message.text.startswith('/'):
        comm = message.text.split()[0].strip('/')
        param = ""
        if re.match('^/' + comm + ' .+$', message.text):
            param = re.search('^/' + comm + ' (.+)$', message.text).group(1)
        await DoBot(comm, param, client, message, language)
    elif message.text == _("🌐Global"):
        await DoBot("world", "", client, message, language)
    elif message.text == _("🇪🇸Spain"):
        await DoBot("spain", "", client, message, language)
    elif message.text == _("💬Language"):
        btns = b_lang(language)
        await client.send_message(chat, _("Choose Language"), reply_markup=btns)
    elif message.text == _("❓About"):
        await DoBot("about", "", client, message, language)
    else:
        param = message.text
        resultats = cerca(param, language)
        if len(resultats) == 0:
            await client.send_message(chat, _('No results for `{param}`').format(param=param))
        elif len(resultats) == 1:
            await show_region(client, chat, region=resultats[0], language=language)
        else:
            btns = b_find(param, language=language)[0]
            caption = _('Search results for `{param}`').format(param=param)
            await client.send_message(chat, caption, reply_markup=btns)


@app.on_callback_query()
async def answer(client, callback_query):
    # cbdata = callback_query.data
    user = callback_query.from_user
    chat = callback_query.message.chat.id
    mid = callback_query.message.message_id
    params = callback_query.data.split("_")
    comm = params[0]
    language = await get_language(user)
    _ = translations[language].gettext
    if comm == "pag":
        pag = int(params[1])
        btns = botons(comunitat)[pag]
        caption = _("Choose a Region")
        await client.edit_message_text(chat, mid, caption, reply_markup=btns)

    elif comm == "back":
        font = params[1]
        if font == "world":
            btns = b_alphabet(world, scope="world", language=language)
        else:
            btns = b_alphabet(comunitat, language=language)
        text = _("Choose a Region")
        await client.edit_message_text(chat, mid, text, reply_markup=btns)

    elif comm == "s":
        region = params[1]
        plot_type = params[2].replace('-', '_')
        if region in tot:
            await edit_region(client, chat, mid, plot_type, region, language=language)

    if comm == "lang":
        language = params[1]
        _ = translations[language].gettext
        await set_language(user.id, language)
        rep_markup = b_start(language)
        await client.send_message(chat, _("Your language is now English"), reply_markup=rep_markup)

    elif comm == "alph":
        pag = int(params[1])
        font = params[2]
        btns = []
        if font == "world":
            btns = botons(world, scope="world", language=language)[pag]
        else:
            btns = botons(comunitat, language=language)[pag]
        caption = _("Choose a Region")
        await client.edit_message_text(chat, mid, caption, reply_markup=btns)

    elif comm == "f":
        pag = int(params[1])
        param = params[2]
        btns = b_find(param, language=language)[pag]
        caption = _('Search results for `{param}`').format(param=param)
        await client.edit_message_text(chat, mid, caption, reply_markup=btns)

    elif comm in tot:
        region = comm
        plot_type = params[1].replace('-', '_')
        await show_region(client, chat, plot_type, region, language=language)


async def main():
    pull_datasets()
    pull_global()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(pull_datasets, "interval", hours=1)
    scheduler.add_job(pull_global, "interval", hours=1)
    scheduler.start()
    await app.start()
    print("Started")
    await app.idle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
