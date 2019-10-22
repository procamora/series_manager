#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# https://geekytheory.com/telegram-programando-un-bot-en-python/
# https://bitbucket.org/master_groosha/telegram-proxy-bot/src/07a6b57372603acae7bdb78f771be132d063b899/proxy_bot.py?at=master&fileviewer=file-view-default
# https://github.com/eternnoir/pyTelegramBotAPI/blob/master/telebot/types.py

import os
import re
import sys
import tempfile
from typing import NoReturn, Union

import requests
from telebot import TeleBot, types  # Importamos la librería Y los tipos especiales de esta

# Confirmamos que tenemos en el path la ruta de la aplicacion, para poder lanzarlo desde cualquier ruta
new_path = '{}/../../'.format(os.path.dirname(os.path.realpath(__file__)))
if new_path not in sys.path:
    sys.path.append(new_path)
from app import logger
from app.utils.settings import MODE_DEBUG, PATH_DATABASE, DIRECTORY_LOCAL, DIRECTORY_WORKING
import app.utils.funciones as funciones
import app.controller.Controller as Controller
from app.models.model_query import Query


def get_id_fileconf() -> str:
    with open(rf'{DIRECTORY_LOCAL}/id.conf', 'r') as f:
        return f.readline().replace('/n', '')


response_query: Query = Controller.get_credentials_fileconf(get_id_fileconf(), PATH_DATABASE)
credentials = response_query.response[0]
administrador = 33063767
users_permitted = [33063767, 40522670]
pass_transmission = credentials['pass_transmission']

if MODE_DEBUG:
    bot = TeleBot('694076475:AAFfiSVSnuf387hnvJOIjQOHP6w7veZbO-M')
    bot.send_message(administrador, "El bot se ha iniciado")
else:
    bot = TeleBot(credentials['api_telegram'])

dicc_botones = {
    'cgs': '/cron_Gestor_Series',
    'log': '/empty_log',
    'mount': '/mount',
    'rar': '/descomprime',
    'sys': '/reboot_system',
    'ts': '/reboot_transmission',
    'exit': '/exit',
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
def send_cgs(message) -> Union[NoReturn, None]:
    bot.reply_to(message, 'Ejecutado con gs')

    command = 'cd /home/pi/Gestor-de-Series/ && /usr/bin/python3 /home/pi/Gestor-de-Series/descarga_automatica_cli.py'
    stdout, stderr, execute = Controller.execute_command(command)
    # stdout = formatea(stdout) # sino stdout esta en bytes

    if check_error(execute, stderr):
        bot.reply_to(message, f'Error: {stderr}')
        return
    elif len(stdout) == 0:
        bot.reply_to(message, 'Ejecutado, puede que haya fallado o sea muy largo el resultado')
    else:
        bot.reply_to(message, stdout)


@bot.message_handler(func=lambda message: message.chat.id == administrador, commands=['/empty_log'])
def send_log(message) -> NoReturn:
    fichero = f'{DIRECTORY_WORKING}/log/{credentials["FicheroFeedNewpct"]}'
    with open(fichero, 'w'):
        pass

    bot.reply_to(message, 'Log vaciado')
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
    command = 'pwd'
    stdout, stderr, execute = Controller.execute_command(command)

    if check_error(execute, stderr):
        bot.reply_to(message, 'Error: {stderr}')
        return
    elif len(stderr) == 0:
        bot.reply_to(message, 'Ejecutado, pero esta en proceso')
    else:
        bot.reply_to(message, stdout)


@bot.message_handler(func=lambda message: message.chat.id == administrador, commands=['show_torrent'])
def send_show_torrent(message) -> Union[NoReturn, None]:
    command = f'transmission-remote 127.0.0.1:9091 --auth=pi:{pass_transmission} -l | egrep -v "Finished|Stopped|Seeding|ID|Sum:"'
    stdout, stderr, execute = Controller.execute_command(command)

    if check_error(execute, stderr):
        bot.reply_to(message, f'Error: {stderr}')
        return
    elif len(stdout) != 0:
        for i in stdout:
            regex = r'\[AC3 5\.1-Castellano-AC3 5.1 Ingles\+Subs\]|\[ES-EN\]|\[AC3 5.1 Español Castellano\]|' \
                    r'\[HDTV 720p?\]|(\d+\.?\d+|None)( )+(MB|GB|kB|Unknown).*(Up & Down|Downloading|Queued|' \
                    r'Idle|Uploading)( )*| - Temporada \d+ |(\d+\.\d+)( )+(\d+\.\d+)',
            line = re.sub(regex, '', i)  # fixme revisar que esta bien
            # line = re.sub(regex, '', stdout)
        bot.reply_to(message, line)
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
    bot.reply_to(message, 'Ejecutado add torrent')

    command = f'transmission-remote 127.0.0.1:9091 --auth=pi:{pass_transmission} --add "{message.text}"'
    stdout, stderr, execute = Controller.execute_command(command)
    # stdout = formatea(stdout)  # sino stdout esta en bytes

    logger.debug(command)

    if check_error(execute, stderr):
        bot.reply_to(message, f'Error: {stderr}')
        return
    else:
        send_show_torrent(message)


@bot.message_handler(regexp=r"^(https://)?(www.)?(dontorrent).com\/.*")
def handle_torrent(message) -> Union[NoReturn, None]:
    # si no envio yo la url no continuo
    if message.chat.id != administrador:
        return
    # ya no es necesario, lo implementa descargaUrlTorrent
    # buscamos el genero
    # regexGenero = re.search('descarga-torrent', message.text)
    # if regexGenero:  # si hay find continua, sino retorno None el re.search
    #    urlPeli = message.text
    # else:
    #    urlPeli = re.sub('(http://)?(www.)?newpct1.com/', 'http://www.newpct1.com/descarga-torrent/', message.text)

    url = funciones.get_url_torrent_dontorrent_direct(message.text, message)
    if url is not None:
        with tempfile.NamedTemporaryFile(mode='rb', dir=credentials['RutaDescargas'], suffix='.torrent',
                                         delete=False) as fp:
            try:
                print(url)
                download_file(url, fp.name)
                file_data = open(fp.name, 'rb')
                bot.send_document(message.chat.id, file_data)
            except Exception as e:
                print(e)
                bot.reply_to(message, 'Ha ocurrido un error al descargar')

        with open('/tmp/descarga_torrent.log', "a") as f:
            f.write(f'{message.chat.id}, {message.chat.first_name}, {message.chat.username} -> {message.text}\n')
    else:
        bot.reply_to(message, 'handle_torrent retorna None')


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
        file = requests.get(f'https://api.telegram.org/file/bot{credentials["api_telegram"]}/{file_info.file_path}')
        with open(f'/home/pi/Downloads/{message.document.file_id}.torrent', "wb") as code:
            code.write(file.content)
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
