#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# https://geekytheory.com/telegram-programando-un-bot-en-python/
# https://bitbucket.org/master_groosha/telegram-proxy-bot/src/07a6b57372603acae7bdb78f771be132d063b899/proxy_bot.py?at=master&fileviewer=file-view-default
# https://github.com/eternnoir/pyTelegramBotAPI/blob/master/telebot/types.py

import json
import os
import re
import sys
from http import HTTPStatus
from pathlib import PurePath, Path  # nueva forma de trabajar con rutas
from typing import NoReturn, Union

import requests
from telebot import TeleBot, types  # Importamos la librería Y los tipos especiales de esta

# Confirmamos que tenemos en el path la ruta de la aplicacion, para poder lanzarlo desde cualquier ruta
absolut_path: PurePath = PurePath(os.path.realpath(__file__))  # Ruta absoluta del fichero
new_path: str = f'{absolut_path.parent}/../../'
if new_path not in sys.path:
    sys.path.append(new_path)

from app import logger
from app.utils.settings import PASSWORD_CLIENT_TORRENT, CLIENT_TORRENT
from app.utils.settings import FILE_LOG_FEED
import app.controller.Controller as Controller
from app.utils.descarga_automatica_cli import DescargaAutomaticaCli
from app.models.model_query import Query
from app.models.model_credentials import Credentials
from app.models.model_preferences import Preferences
from app.models.model_t_grantorrent import GranTorrent
from app.utils import descomprime_rar

response_query_credentials: Query = Controller.get_credentials()
response_query_preferences: Query = Controller.get_preferences_id()

credentials: Credentials
if not response_query_credentials.is_empty():
    credentials = response_query_credentials.response[0]
else:
    logger.critical("No se han obtenido las credenciales")
    sys.exit(1)

preferences: Preferences
if not response_query_preferences.is_empty():
    preferences = response_query_preferences.response[0]
else:
    logger.critical("No se han obtenido las preferencias")
    sys.exit(1)

administrador = 33063767
users_permitted = [33063767, 40522670]

bot = TeleBot(credentials.api_telegram)
bot.send_message(administrador, "El bot se ha iniciado")

dicc_botones = {
    'cgs': '/cron_Gestor_Series',
    'log': '/empty_log',
    'mount': '/mount',
    'rar': '/descomprime',
    'sys': '/reboot_system',
    'ts': '/reboot_transmission',
    'exit': '/exit',
    'ip': '/ip',
}


def check_error(codigo, stderr) -> bool:
    if codigo.returncode and stderr:
        logger.debug("Error:")
        return True
    return False


def download_file(url: str, destino: str) -> NoReturn:
    r = requests.get(url)
    with open(destino, "wb") as code:
        code.write(r.content)


# Handle always first "/start" message when new chat with your bot is created


@bot.message_handler(commands=["start"])
def command_start(message) -> NoReturn:
    bot.send_message(message.chat.id, f"Bienvenido al bot\nTu id es: {message.chat.id}")
    command_system(message)
    return  # solo esta puesto para que no falle la inspeccion de codigo


@bot.message_handler(commands=["help"])
def command_help(message) -> NoReturn:
    bot.send_message(message.chat.id, "Aqui pondre todas las opciones")
    markup = types.InlineKeyboardMarkup()
    itembtna = types.InlineKeyboardButton('Github', url="https://github.com/procamora/Gestor-Series")
    itembtnv = types.InlineKeyboardButton('Documentacion',
                                          url="https://github.com/procamora/Gestor-Series/blob/master/README.md")
    markup.row(itembtna, itembtnv)
    bot.send_message(message.chat.id, "Aqui pondre todas las opciones", reply_markup=markup)
    return  # solo esta puesto para que no falle la inspeccion de codigo


@bot.message_handler(commands=["system"])
def command_system(message) -> NoReturn:
    bot.send_message(message.chat.id, "Lista de comandos disponibles")

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row(dicc_botones['cgs'], dicc_botones['log'], dicc_botones['mount'])
    markup.row(dicc_botones['rar'], dicc_botones['ts'], dicc_botones['sys'])
    markup.row(dicc_botones['exit'])

    bot.send_message(message.chat.id, "Escoge una opcion: ", reply_markup=markup)
    return  # solo esta puesto para que no falle la inspeccion de codigo


@bot.message_handler(func=lambda message: message.chat.id == administrador, commands=['/cron_Gestor_Series'])
def send_cgs(message) -> NoReturn:
    bot.reply_to(message, 'Ejecutado con descarga_cli')

    d = DescargaAutomaticaCli()
    response = d.run()
    bot.reply_to(message, response)
    return


@bot.message_handler(func=lambda message: message.chat.id == administrador, commands=['/empty_log'])
def send_log(message) -> NoReturn:
    FILE_LOG_FEED.write_text('')

    bot.reply_to(message, 'Log vaciado')
    return  # solo esta puesto para que no falle la inspeccion de codigo


@bot.message_handler(func=lambda message: message.chat.id == administrador, commands=['/ip'])
def send_public_ip(message) -> NoReturn:
    response_url: requests.models.Response = requests.get('https://api.ipify.org/?format=json')
    if response_url.status_code == HTTPStatus.OK:
        my_ip: str = json.loads(response_url.text)['ip']
        bot.reply_to(message, my_ip)
    else:
        bot.reply_to(message, f'Error: {response_url.text}')
    return  # solo esta puesto para que no falle la inspeccion de codigo


@bot.message_handler(func=lambda message: message.chat.id == administrador, commands=['/mount'])
def send_mount(message) -> Union[NoReturn, None]:
    command = 'sudo mount -a'
    stdout, stderr, execute = Controller.execute_command(command)

    if check_error(execute, stderr):
        bot.reply_to(message, f'Error: {stderr}')
        return
    elif len(stdout) == 0:
        bot.reply_to(message, 'Ejecutado mount')
    else:
        bot.reply_to(message, stdout)


@bot.message_handler(func=lambda message: message.chat.id == administrador, commands=['/descomprime'])
def send_descomprime(message) -> Union[NoReturn, None]:
    bot.reply_to(message, 'Ejecutado unrar')

    descomprime_rar.main('/media/pi/640Gb/*/*.rar')
    command = "cd /home/pi/Gestor-de-Series/modulos/ && /usr/bin/python3 " \
              "/home/pi/Gestor-de-Series/modulos/descomprime_rar.py"
    stdout, stderr, execute = Controller.execute_command(command)
    # stdout = formatea(stdout) # sino stdout esta en bytes

    if check_error(execute, stderr):
        bot.reply_to(message, f'Error: {stderr}')
        return
    elif len(stdout) == 0:
        bot.reply_to(message, 'Ejecutado, puede que haya fallado o sea muy largo el resultado')
    else:
        bot.reply_to(message, stdout)


@bot.message_handler(func=lambda message: message.chat.id == administrador, commands=['reboot_transmission'])
def send_ts(message) -> Union[NoReturn, None]:
    command = 'sudo /etc/init.d/transmission-daemon restart'
    stdout, stderr, execute = Controller.execute_command(command)
    if check_error(execute, stderr):
        bot.reply_to(message, f'Error: {stderr}')
        return
    elif len(stdout) == 0:
        bot.reply_to(message, 'Ejecutado  reboot ts')
    else:
        bot.reply_to(message, stdout)


@bot.message_handler(func=lambda message: message.chat.id == administrador, commands=['reboot_system'])
def send_sys(message) -> Union[NoReturn, None]:
    bot.reply_to(message, 'Se ejecutara en breve el reboot')

    command = 'sudo reboot'
    stdout, stderr, execute = Controller.execute_command(command)
    # stdout = formatea(stdout)  # sino stdout esta en bytes

    if check_error(execute, stderr):
        bot.reply_to(message, f'Error: {stderr}')
        return


@bot.message_handler(func=lambda message: message.chat.id == administrador, commands=['df_h'])
def send_df(message) -> Union[NoReturn, None]:
    command = 'df -h'
    stdout, stderr, execute = Controller.execute_command(command)

    if check_error(execute, stderr):
        bot.reply_to(message, f'Error: {stderr}')
        return
    elif len(stdout) == 0:
        bot.reply_to(message, 'Ejecutado df -h')
    else:
        bot.reply_to(message, stdout)


@bot.message_handler(func=lambda message: message.chat.id == administrador, commands=['info'])
def send_info(message) -> Union[NoReturn, None]:
    # uptime, cpu, ram, disk, speed download/upload
    mem = """free -m | awk 'NR==2 { printf "Total: %sMB, Used: %sMB, Free: %sMB",$2,$3,$4; }'"""
    disk = """df -h ~ | awk 'NR==2 { printf "Total: %sB, Used: %sB, Free: %sB",$2,$3,$4; }'"""
    temp = '/opt/vc/bin/vcgencmd measure_temp | cut -c "6-9"'
    response: str = str()
    for cmd, info in zip([mem, disk, temp], ['Memory', 'Home space', 'Temperature']):
        stdout, stderr, execute = Controller.execute_command(cmd)
        if check_error(execute, stderr):
            bot.reply_to(message, 'Error: {stderr}')
            return
        if info == 'Temperature':
            stdout = stdout.replace('\n', '')
            response += f'{info}: {stdout}ºC\n'
        else:
            response += f'{info}: {stdout}\n'

    bot.reply_to(message, response)


@bot.message_handler(func=lambda message: message.chat.id == administrador, commands=['show_torrent'])
def send_show_torrent(message) -> Union[NoReturn, None]:
    command = f'transmission-remote 127.0.0.1:9091 --auth=pi:{PASSWORD_CLIENT_TORRENT} -l | ' \
              f'egrep -v "Finished|Stopped|Seeding|ID|Sum:"'
    stdout, stderr, execute = Controller.execute_command(command)

    response: str = str()
    if check_error(execute, stderr):
        bot.reply_to(message, f'Error: {stderr}')
        return
    elif len(stdout) != 0:
        for i in stdout.split('\n'):
            # Sustituimos la columna anterior al nombre de la serie por \n
            split_lines = re.sub('Idle|Downloading|Up & Down|Queued', '\n', i)
            # Partimos por el \n puesto anteriormente y la ultima columna tiene el nombre
            name_serie = (split_lines.split('\n')[-1]).strip()
            regex = r'\[ES-EN\]|\[AC3 5.1 (Español )?Castellano\]|\[HDTV 720p?\]| - Temporada \d+( COMPLETA)? |' \
                    r'\[www.descargas2020.org\]|\[www.pctnew.org\]|\.www.DESCARGASMIX.com.mkv|' \
                    r'\[AC3 (5\.1\-DTS )?5\.1-Castellano-AC3 5\.1( |\-)Ingles\+Subs\]|\[Español Castellano\]|' \
                    r'\[wWw.EliteTorrent.IO\]|\[HDTV\]|\.WEB.x264-XLF\[rarbg\]'
            print(name_serie)
            print(regex)
            if len(name_serie) > 0:
                name_serie = re.sub(regex, '', name_serie)
                # print(name_serie)
                response += f'{name_serie}\n'

        bot.reply_to(message, response)
    else:
        bot.reply_to(message, 'Ningun torrent activo en este momento.')


@bot.message_handler(func=lambda message: message.chat.id == administrador, commands=['exit'])
def send_exit(message) -> NoReturn:
    command = 'pwd'
    stdout, stderr, execute = Controller.execute_command(command)

    if check_error(execute, stderr):
        bot.reply_to(message, f'Error: {stderr}')
        return
    elif len(stdout) == 0:
        bot.reply_to(message, 'Ejecutado, no hace nada')
    else:
        bot.reply_to(message, stdout)


@bot.message_handler(func=lambda message: message.chat.id == administrador, regexp="[Cc]md: .*")
def handle_cmd(message) -> NoReturn:
    command_dangerous = ['sudo reboot', ':(){ :|: & };:', 'sudo rm -rf /']

    command = re.sub('[Cc]md: ', '', message.text, re.IGNORECASE)
    if command not in command_dangerous:
        stdout, stderr, execute = Controller.execute_command(command)

        if check_error(execute, stderr):
            bot.reply_to(message, f'Error: {stderr}')
            return
        elif len(stdout) == 0:
            bot.reply_to(message, f'Ejecutado: {command}')
        else:
            bot.reply_to(message, stdout)
    else:
        bot.reply_to(message, 'Comando aun no implementado')


@bot.message_handler(func=lambda message: message.chat.id == administrador, regexp=r"^magnet:\?xt=urn.*")
def handle_magnet(message) -> NoReturn:
    bot.reply_to(message, 'Ejecutado add torrent magnet')
    command = f'{CLIENT_TORRENT} "message.text"'
    # command = f'transmission-remote 127.0.0.1:9091 --auth=pi:{pass_transmission} --add "{message.text}"'
    stdout, stderr, execute = Controller.execute_command(command)
    logger.debug(command)

    if check_error(execute, stderr):
        bot.reply_to(message, f'Error: {stderr}')
        return
    else:
        send_show_torrent(message)


@bot.message_handler(regexp=r"^(https?://)?(www.)?(grantorrent).tv\/.*")
def handle_grantorrent(message) -> Union[NoReturn, None]:
    # si no envio yo la url no continuo
    if message.chat.id != administrador:
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
        bot.reply_to(message, 'handle_grantorrent retorna None')


@bot.message_handler(func=lambda message: message.chat.id == administrador, content_types=["text"])
def my_text(message) -> NoReturn:
    if message.text in dicc_botones.values():
        if message.text == dicc_botones['cgs']:
            send_cgs(message)
        elif message.text == dicc_botones['log']:
            send_log(message)
        elif message.text == dicc_botones['mount']:
            send_mount(message)
        elif message.text == dicc_botones['ts']:
            send_ts(message)
        elif message.text == dicc_botones['sys']:
            send_sys(message)
        elif message.text == dicc_botones['exit']:
            send_exit(message)
        elif message.text == dicc_botones['ip']:
            send_public_ip(message)
    else:
        bot.send_message(message.chat.id, "Comando desconocido")
    return  # solo esta puesto para que no falle la inspeccion de codigo


@bot.message_handler(func=lambda message: message.chat.id == administrador, content_types=["photo"])
def my_photo(message) -> NoReturn:
    if message.reply_to_message:
        bot.send_photo(message.chat.id, list(message.photo)[-1].file_id)
    else:
        bot.send_message(message.chat.id, "No one to reply photo!")
    return  # solo esta puesto para que no falle la inspeccion de codigo


@bot.message_handler(func=lambda message: message.chat.id == administrador, content_types=["voice"])
def my_voice(message) -> NoReturn:
    if message.reply_to_message:
        bot.send_voice(message.chat.id, message.voice.file_id, duration=message.voice.duration)
    else:
        bot.send_message(message.chat.id, "No one to reply voice!")
    return  # solo esta puesto para que no falle la inspeccion de codigo


@bot.message_handler(func=lambda message: message.chat.id in users_permitted, content_types=["document"])
def my_document(message) -> NoReturn:
    if message.document.mime_type == 'application/x-bittorrent':
        file_info = bot.get_file(message.document.file_id)
        # bot.send_message(message.chat.id, f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}')
        file = requests.get(f'https://api.telegram.org/file/bot{credentials.api_telegram}/{file_info.file_path}')
        torrent_file: Path = Path(preferences.path_download, f'{message.document.file_id}.torrent')
        torrent_file.write_bytes(file.content)
        # with open(f'/home/pi/Downloads/{message.document.file_id}.torrent', "wb") as code:
        #    code.write(file.content)
        bot.reply_to(message, f'Descargando torrent: "{message.document.file_name}"')
        send_show_torrent(message)
    else:
        bot.reply_to(message, f'Aun no he implementado este tipo de ficheros: "{message.document.mime_type}"')
    return  # solo esta puesto para que no falle la inspeccion de codigo


@bot.message_handler(regexp=".*")
def handle_resto(message) -> NoReturn:
    texto = 'No tienes permiso para ejecutar esta accion, eso se debe a que no eres yo.\n' \
            'Por lo que ya sabes, desaparece -.-'
    bot.reply_to(message.chat.id, texto)
    return  # solo esta puesto para que no falle la inspeccion de codigo


# Con esto, le decimos al bot que siga funcionando incluso si encuentra
# algun fallo.
bot.polling(none_stop=False)
