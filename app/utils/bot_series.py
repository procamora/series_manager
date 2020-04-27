#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# https://geekytheory.com/telegram-programando-un-bot-en-python/
# https://bitbucket.org/master_groosha/telegram-proxy-bot/src/07a6b57372603acae7bdb78f771be132d063b899/proxy_bot.py?at=master&fileviewer=file-view-default
# https://github.com/eternnoir/pyTelegramBotAPI/blob/master/telebot/types.py

"""commands
Name:
Series Manager

Username:
procamora_series_manager_bot

Description:
This is a bot to manage the series you are currently following, it also allows you to download new series.

About:
This bot has been developed by @procamora

Botpic:
<imagen del bot>

Commands:
cron - run cron series manager
empty_log - empty system log
mount - execute command mount -a
unzip - run script to decompress files
reboot_system - reboot the system
reboot_transmission - restart the transmission service
ip - obtain the public IP
info - get information about system resources
df_h - execute command df -h
show_torrent - show active torrent
help - Show help
start - Start the bot
exit - exit
"""

import json
import os
import re
import subprocess
import sys
from http import HTTPStatus
from pathlib import PurePath, Path  # nueva forma de trabajar con rutas
from typing import NoReturn, List, Tuple, Text, AnyStr

import requests
from telebot import TeleBot, types, apihelper

# Confirmamos que tenemos en el path la ruta de la aplicacion, para poder lanzarlo desde cualquier ruta
absolut_path: PurePath = PurePath(os.path.realpath(__file__))  # Ruta absoluta del fichero
new_path: Text = f'{absolut_path.parent}/../../'
if new_path not in sys.path:
    sys.path.append(new_path)

from app import logger
from app.utils.settings import CLIENT_TORRENT, BOT_DEBUG, BOT_TOK_DEBUG, BOT_TOK, BOT_ADMIN
from app.utils.settings import FILE_LOG_FEED
import app.controller.Controller as Controller
from app.utils.descarga_automatica_cli import DescargaAutomaticaCli
from app.models.model_query import Query
from app.models.model_preferences import Preferences
from app.models.model_t_grantorrent import GranTorrent
from app.utils import descomprime_rar

response_query_preferences: Query = Controller.get_preferences_id()
preferences: Preferences
if not response_query_preferences.is_empty():
    preferences = response_query_preferences.response[0]
else:
    logger.critical("No se han obtenido las preferencias")
    sys.exit(1)

users_permitted: List[int] = [BOT_ADMIN]

if BOT_DEBUG:
    bot: TeleBot = TeleBot(BOT_TOK_DEBUG)
else:
    bot = TeleBot(BOT_TOK)

my_commands: Tuple[Text, ...] = (
    '/cron',  # 0
    '/empty_log',  # 1
    '/mount',  # 2
    '/unzip',  # 3
    '/reboot_system',  # 4
    '/reboot_transmission',  # 5
    '/ip',  # 6
    '/info',  # 7
    '/df_h',  # 8
    '/show_torrent',  # 9

    '/start',  # -3
    '/help',  # -2
    '/exit',  # -1 (SIEMPRE TIENE QUE SER EL ULTIMO, ACCEDO CON -1)
)


def get_markup_cmd() -> types.ReplyKeyboardMarkup:
    markup: types.ReplyKeyboardMarkup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row(my_commands[0], my_commands[1])
    markup.row(my_commands[9], my_commands[3], my_commands[4])
    markup.row(my_commands[7], my_commands[6], my_commands[-1])
    # markup.row(my_commands[4])
    return markup


def check_error(codigo: subprocess.Popen, stderr: Text) -> bool:
    if codigo.returncode and stderr:
        logger.debug("Error:")
        return True
    return False


def download_file(url: Text, destino: Text) -> NoReturn:
    r: requests.Response = requests.get(url)
    with open(destino, "wb") as code:
        code.write(r.content)


# Handle always first "/start" message when new chat with your bot is created
@bot.message_handler(commands=["start"])
def command_start(message: types.Message) -> NoReturn:
    bot.send_message(message.chat.id,
                     "This is a bot to manage the series you are currently following, it also allows you to download "
                     "new series.\nYour id is: {message.chat.id}",
                     reply_markup=get_markup_cmd())
    command_system(message)
    return  # solo esta puesto para que no falle la inspeccion de codigo


@bot.message_handler(commands=["help"])
def command_help(message: types.Message) -> NoReturn:
    markup: types.InlineKeyboardMarkup = types.InlineKeyboardMarkup()
    itembtna: types.InlineKeyboardButton = types.InlineKeyboardButton(
        'Github', url="https://github.com/procamora/Gestor-Series")
    itembtnv = types.InlineKeyboardButton(
        'Documentation', url="https://github.com/procamora/Gestor-Series/blob/master/README.md")

    markup.row(itembtna, itembtnv)
    bot.send_message(message.chat.id, 'You can find the source code for this bot in:', reply_markup=markup)
    command_system(message)
    return  # solo esta puesto para que no falle la inspeccion de codigo


@bot.message_handler(commands=["system"])
def command_system(message: types.Message) -> NoReturn:
    commands: Text = '\n'.join(i for i in my_commands)
    bot.send_message(message.chat.id, f"List of available commands\nChoose an option:\n{commands}",
                     reply_markup=get_markup_cmd())
    return  # solo esta puesto para que no falle la inspeccion de codigo


@bot.message_handler(commands=['exit'])
def send_exit(message: types.Message) -> NoReturn:
    bot.send_message(message.chat.id, "go to menu", reply_markup=get_markup_cmd())
    return


@bot.message_handler(func=lambda message: message.chat.id == BOT_ADMIN, commands=[my_commands[0][1:]])
def send_cgs(message: types.Message) -> NoReturn:
    bot.reply_to(message, 'run con descarga_cli', reply_markup=get_markup_cmd())

    d: DescargaAutomaticaCli = DescargaAutomaticaCli()
    response: AnyStr = d.run()
    bot.reply_to(message, response, reply_markup=get_markup_cmd())
    return


@bot.message_handler(func=lambda message: message.chat.id == BOT_ADMIN, commands=[my_commands[1][1:]])
def send_log(message: types.Message) -> NoReturn:
    FILE_LOG_FEED.write_text('')
    bot.reply_to(message, 'clean logs', reply_markup=get_markup_cmd())
    return  # solo esta puesto para que no falle la inspeccion de codigo


@bot.message_handler(func=lambda message: message.chat.id == BOT_ADMIN, commands=[my_commands[2][1:]])
def send_mount(message: types.Message) -> NoReturn:
    command: Text = 'sudo mount -a'
    stdout, stderr, execute = Controller.execute_command(command)

    if check_error(execute, stderr):
        bot.reply_to(message, f'Error: {stderr}', reply_markup=get_markup_cmd())
        return
    elif len(stdout) == 0:
        bot.reply_to(message, 'execute mount -a', reply_markup=get_markup_cmd())
    else:
        bot.reply_to(message, stdout, reply_markup=get_markup_cmd())


@bot.message_handler(func=lambda message: message.chat.id == BOT_ADMIN, commands=[my_commands[3][1:]])
def send_descomprime(message: types.Message) -> NoReturn:
    bot.reply_to(message, 'execute unrar', reply_markup=get_markup_cmd())

    descomprime_rar.main('/media/pi/640Gb/*/*.rar')
    command: Text = "cd /home/pi/Gestor-de-Series/modulos/ && /usr/bin/python3 " \
                    "/home/pi/Gestor-de-Series/modulos/descomprime_rar.py"
    stdout, stderr, execute = Controller.execute_command(command)
    # stdout = formatea(stdout) # sino stdout esta en bytes

    if check_error(execute, stderr):
        bot.reply_to(message, f'Error: {stderr}', reply_markup=get_markup_cmd())
        return
    elif len(stdout) == 0:
        bot.reply_to(message, 'Ejecutado, puede que haya fallado o sea muy largo el resultado',
                     reply_markup=get_markup_cmd())
    else:
        bot.reply_to(message, stdout, reply_markup=get_markup_cmd())


@bot.message_handler(func=lambda message: message.chat.id == BOT_ADMIN, commands=[my_commands[4][1:]])
def send_sys(message: types.Message) -> NoReturn:
    bot.reply_to(message, 'rebooting system...', reply_markup=get_markup_cmd())

    command: Text = 'sudo reboot'
    stdout, stderr, execute = Controller.execute_command(command)
    # stdout = formatea(stdout)  # sino stdout esta en bytes

    if check_error(execute, stderr):
        bot.reply_to(message, f'Error: {stderr}', reply_markup=get_markup_cmd())
        return


@bot.message_handler(func=lambda message: message.chat.id == BOT_ADMIN, commands=[my_commands[5][1:]])
def send_ts(message: types.Message) -> NoReturn:
    command: Text = 'sudo systemctl restart transmission-daemon.service'
    stdout, stderr, execute = Controller.execute_command(command)
    if check_error(execute, stderr):
        bot.reply_to(message, f'Error: {stderr}', reply_markup=get_markup_cmd())
        return
    elif len(stdout) == 0:
        bot.reply_to(message, 'Ejecutado  reboot ts', reply_markup=get_markup_cmd())
    else:
        bot.reply_to(message, stdout, reply_markup=get_markup_cmd())


@bot.message_handler(func=lambda message: message.chat.id == BOT_ADMIN, commands=[my_commands[6][1:]])
def send_public_ip(message: types.Message) -> NoReturn:
    response_url: requests.Response = requests.get('https://api.ipify.org/?format=json')
    if response_url.status_code == HTTPStatus.OK:
        my_ip: Text = json.loads(response_url.text)['ip']
        bot.reply_to(message, my_ip, reply_markup=get_markup_cmd())
    else:
        bot.reply_to(message, f'Error: {response_url.text}', reply_markup=get_markup_cmd())
    return  # solo esta puesto para que no falle la inspeccion de codigo


@bot.message_handler(func=lambda message: message.chat.id == BOT_ADMIN, commands=[my_commands[7][1:]])
def send_info(message: types.Message) -> NoReturn:
    # uptime, cpu, ram, disk, speed download/upload
    mem: Text = """free -m | awk 'NR==2 { printf "Total: %sMB, Used: %sMB, Free: %sMB",$2,$3,$4; }'"""
    disk: Text = """df -h ~ | awk 'NR==2 { printf "Total: %sB, Used: %sB, Free: %sB",$2,$3,$4; }'"""
    temp: Text = '/opt/vc/bin/vcgencmd measure_temp | cut -c "6-9"'
    response: Text = str()
    for cmd, info in zip([mem, disk, temp], ['Memory', 'Home space', 'Temperature']):
        stdout, stderr, execute = Controller.execute_command(cmd)
        if check_error(execute, stderr):
            bot.reply_to(message, 'Error: {stderr}', reply_markup=get_markup_cmd())
            return
        if info == 'Temperature':
            stdout = stdout.replace('\n', '')
            response += f'{info}: {stdout}ºC\n'
        else:
            response += f'{info}: {stdout}\n'

    bot.reply_to(message, response, reply_markup=get_markup_cmd())


@bot.message_handler(func=lambda message: message.chat.id == BOT_ADMIN, commands=[my_commands[8][1:]])
def send_df(message: types.Message) -> NoReturn:
    command: Text = 'df -h'
    stdout, stderr, execute = Controller.execute_command(command)

    if check_error(execute, stderr):
        bot.reply_to(message, f'Error: {stderr}', reply_markup=get_markup_cmd())
        return
    elif len(stdout) == 0:
        bot.reply_to(message, 'Ejecutado df -h', reply_markup=get_markup_cmd())
    else:
        bot.reply_to(message, stdout, reply_markup=get_markup_cmd())


@bot.message_handler(func=lambda message: message.chat.id == BOT_ADMIN, commands=[my_commands[9][1:]])
def send_show_torrent(message: types.Message) -> NoReturn:
    command: Text = f'{CLIENT_TORRENT} -l | egrep -v "Finished|Stopped|Seeding|ID|Sum:"'
    stdout, stderr, execute = Controller.execute_command(command)

    response: Text = str()
    if check_error(execute, stderr):
        bot.reply_to(message, f'Error: {stderr}', reply_markup=get_markup_cmd())
        return
    elif len(stdout) != 0:
        for i in stdout.split('\n'):
            # Sustituimos la columna anterior al nombre de la serie por \n
            split_lines: Text = re.sub('Idle|Downloading|Up & Down|Queued', '\n', i)
            # Partimos por el \n puesto anteriormente y la ultima columna tiene el nombre
            name_serie: Text = (split_lines.split('\n')[-1]).strip()
            regex = r'\[ES-EN\]|\[AC3 5.1 (Español )?Castellano\]|\[HDTV 720p?\]| - Temporada \d+( COMPLETA)? |' \
                    r'\[www.descargas2020.org\]|\[www.pctnew.org\]|\.www.DESCARGASMIX.com.mkv|' \
                    r'\[AC3 (5\.1\-DTS )?5\.1-Castellano-AC3 5\.1( |\-)Ingles\+Subs\]|\[Español Castellano\]|' \
                    r'\[wWw.EliteTorrent.IO\]|\[HDTV\]|\.WEB.x264-XLF\[rarbg\]'
            logger.debug(name_serie)
            logger.debug(regex)
            if len(name_serie) > 0:
                name_serie: Text = re.sub(regex, '', name_serie)
                # print(name_serie)
                response += f'{name_serie}\n'

        bot.reply_to(message, response, reply_markup=get_markup_cmd())
    else:
        bot.reply_to(message, 'No active torrents at this time.', reply_markup=get_markup_cmd())


@bot.message_handler(func=lambda message: message.chat.id == BOT_ADMIN, regexp=r"[Cc]md: .*")
def handle_cmd(message: types.Message) -> NoReturn:
    command_dangerous: List[Text] = [':(){ :|: & };:', 'sudo rm -rf /']

    command: Text = re.sub(r'[Cc]md: ', '', message.text, re.IGNORECASE)
    if command not in command_dangerous:
        stdout, stderr, execute = Controller.execute_command(command)

        if check_error(execute, stderr):
            bot.reply_to(message, f'Error: {stderr}', reply_markup=get_markup_cmd())
            return
        elif len(stdout) == 0:
            bot.reply_to(message, f'Execute: {command}', reply_markup=get_markup_cmd())
        else:
            bot.reply_to(message, stdout, reply_markup=get_markup_cmd())
    else:
        bot.reply_to(message, 'command cmd not implement', reply_markup=get_markup_cmd())


@bot.message_handler(func=lambda message: message.chat.id == BOT_ADMIN, regexp=r"^magnet:\?xt=urn.*")
def handle_magnet(message: types.Message) -> NoReturn:
    bot.reply_to(message, 'execute add magnet torrent', reply_markup=get_markup_cmd())
    command: Text = f'{CLIENT_TORRENT} --add "{message.text}"'
    # command = f'transmission-remote 127.0.0.1:9091 --auth=pi:{pass_transmission} --add "{message.text}"'
    stdout, stderr, execute = Controller.execute_command(command)
    logger.debug(command)

    if check_error(execute, stderr):
        bot.reply_to(message, f'Error: {stderr}', reply_markup=get_markup_cmd())
        return
    else:
        bot.reply_to(message, stdout, reply_markup=get_markup_cmd())
        send_show_torrent(message)


@bot.message_handler(regexp=r"^(https?://)?(www.)?(grantorrent).tv\/.*")
def handle_grantorrent(message: types.Message) -> NoReturn:
    # si no envio yo la url no continuo
    if message.chat.id != BOT_ADMIN:
        return

    grantorrent: GranTorrent = GranTorrent('noesnecesario', message.text, preferences.path_download)
    response: bool = grantorrent.download_file_torrent()

    if response:
        # Modo para enviar con el nombre segun api
        file_data = open(str(grantorrent.path_file_torrent), 'rb')
        bot.send_document(message.chat.id, file_data)

        with open('/tmp/descarga_torrent.log', "a") as f:
            f.write(f'{message.chat.id}, {message.chat.first_name}, {message.chat.username} -> {message.text}\n')
    else:
        bot.reply_to(message, 'handle_grantorrent return None', reply_markup=get_markup_cmd())


@bot.message_handler(func=lambda message: message.chat.id == BOT_ADMIN, content_types=["photo"])
def my_photo(message: types.Message) -> NoReturn:
    if message.reply_to_message:
        bot.send_photo(message.chat.id, list(message.photo)[-1].file_id, reply_markup=get_markup_cmd())
    else:
        bot.send_message(message.chat.id, "No one to reply photo!", reply_markup=get_markup_cmd())
    return  # solo esta puesto para que no falle la inspeccion de codigo


@bot.message_handler(func=lambda message: message.chat.id == BOT_ADMIN, content_types=["voice"])
def my_voice(message: types.Message) -> NoReturn:
    if message.reply_to_message:
        bot.send_voice(message.chat.id, message.voice.file_id, duration=message.voice.duration,
                       reply_markup=get_markup_cmd())
    else:
        bot.send_message(message.chat.id, "No one to reply voice!", reply_markup=get_markup_cmd())
    return  # solo esta puesto para que no falle la inspeccion de codigo


@bot.message_handler(func=lambda message: message.chat.id in users_permitted, content_types=["document"])
def my_document(message: types.Message) -> NoReturn:
    if message.document.mime_type == 'application/x-bittorrent':
        file_info: types.File = bot.get_file(message.document.file_id)
        # bot.send_message(message.chat.id, f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}')
        file: requests.Response = requests.get(
            f'https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}')
        torrent_file: Path = Path(preferences.path_download, f'{message.document.file_id}.torrent')
        torrent_file.write_bytes(file.content)
        # with open(f'/home/pi/Downloads/{message.document.file_id}.torrent', "wb") as code:
        #    code.write(file.content)
        bot.reply_to(message, f'Download torrent: "{message.document.file_name}"', reply_markup=get_markup_cmd())
        send_show_torrent(message)
    else:
        bot.reply_to(message, f'not implemented type: "{message.document.mime_type}"',
                     reply_markup=get_markup_cmd())
    return  # solo esta puesto para que no falle la inspeccion de codigo


@bot.message_handler(regexp=".*")
def text_not_valid(message: types.Message) -> NoReturn:
    texto: Text = 'unknown command, enter a valid command :)'
    bot.reply_to(message, texto, reply_markup=get_markup_cmd())
    command_system(message)
    return


def escape_string(text: Text) -> Text:
    # In all other places characters '_‘, ’*‘, ’[‘, ’]‘, ’(‘, ’)‘, ’~‘, ’`‘, ’>‘, ’#‘, ’+‘, ’-‘, ’=‘, ’|‘, ’{‘, ’}‘,
    # ’.‘, ’!‘ must be escaped with the preceding character ’\'.
    return text.replace('=', r'\=').replace('_', r'\_').replace('(', r'\(').replace(')', r'\)').replace('-', r'\-'). \
        replace('.', r'\.').replace('>', r'\>')


def main() -> NoReturn:
    try:
        import urllib
        bot.send_message(BOT_ADMIN, 'Starting bot', reply_markup=get_markup_cmd(), disable_notification=True)
        logger.info('Starting bot')
    except (apihelper.ApiException, requests.exceptions.ReadTimeout) as e:
        logger.critical(f'Error in init bot: {e}')
        sys.exit(1)

    # Con esto, le decimos al bot que siga funcionando incluso si encuentra algun fallo.
    bot.infinity_polling(none_stop=True)


if __name__ == "__main__":
    main()
