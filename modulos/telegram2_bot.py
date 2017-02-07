#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#https://geekytheory.com/telegram-programando-un-bot-en-python/
#https://bitbucket.org/master_groosha/telegram-proxy-bot/src/07a6b57372603acae7bdb78f771be132d063b899/proxy_bot.py?at=master&fileviewer=file-view-default

#https://github.com/eternnoir/pyTelegramBotAPI/blob/master/telebot/types.py

import os
import re

import requests
import telebot              # Importamos la librería
from telebot import types   # Y los tipos especiales de esta

try: #Ejecucion desde Series.py
    from .settings import api_telegram
except: #Ejecucion local
    from settings import api_telegram


administrador = 33063767
usuariosPermitidos = [33063767, 40522670]
bot = telebot.TeleBot(api_telegram)    # Cambiad este Token
pass_transmission = 'PASSWORD'


dicc_botones = {
    'cgs': 'cron Gestor Series',
    'crs': 'cron Rsync Samba',
    'mount': 'mount -a',
    'sys': 'reboot system',
    'ts': 'reboot transmission',
    'exit': 'exit',
}


# Handle always first "/start" message when new chat with your bot is created
@bot.message_handler(commands=["start"])
def command_start(message):
    bot.send_message(message.chat.id, "Bienvenido al bot\nTu id es: {}".format(message.chat.id))
    command_system(message)


@bot.message_handler(commands=["help"])
def command_help(message):
    bot.send_message(message.chat.id, "Aqui pondre todas las opciones")


@bot.message_handler(commands=["system"])
def command_system(message):
    bot.send_message(message.chat.id, "Lista de comandos disponibles")

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row(dicc_botones['cgs'], dicc_botones['crs'], dicc_botones['mount'])
    markup.row(dicc_botones['ts'], dicc_botones['sys'])
    markup.row(dicc_botones['exit'])

    bot.send_message(message.chat.id, "Escoge una opcion: ", reply_markup=markup)


@bot.message_handler(func=lambda message: message.chat.id == administrador, commands=['cron_gestor_series'])
def send_cgs(message):
    bot.reply_to(message, 'Ejecutado con gs')
    f = os.popen('cd /home/pi/Gestor-de-Series/ && /usr/bin/python3 /home/pi/Gestor-de-Series/descarga_automatica_cli.py')
    now = f.read()
    if len(now) == 0:
        bot.reply_to(message, 'Ejecutado, puede que haya fallado o sea muy largo el resultado')
    else:
        bot.reply_to(message, now)


@bot.message_handler(func=lambda message: message.chat.id == administrador, commands=['cron_rsync_samba'])
def send_crs(message):
    f = os.popen('cd /home/pi/scripts && /usr/bin/python3 /home/pi/scripts/rsync_samba.py')
    now = f.read()
    if len(now) == 0:
        bot.reply_to(message, 'Ejecutado rsync')
    else:
        bot.reply_to(message, now)


@bot.message_handler(func=lambda message: message.chat.id == administrador, commands=['mount_a'])
def send_mount(message):
    f = os.popen('sudo mount -a')
    now = f.read()
    if len(now) == 0:
        bot.reply_to(message, 'Ejecutado mount')
    else:
        bot.reply_to(message, now)


@bot.message_handler(func=lambda message: message.chat.id == administrador, commands=['reboot_transmission'])
def send_ts(message):
    f = os.popen('sudo /etc/init.d/transmission-daemon restart')
    now = f.read()
    if len(now) == 0:
        bot.reply_to(message, 'Ejecutado  reboot ts')
    else:
        bot.reply_to(message, now)


@bot.message_handler(func=lambda message: message.chat.id == administrador, commands=['reboot_system'])
def send_sys(message):
    bot.reply_to(message, 'Se ejecutara en breve el reboot')
    os.popen('sudo reboot')


@bot.message_handler(func=lambda message: message.chat.id == administrador, commands=['df_h'])
def send_df(message):
    f = os.popen('df -h')
    now = f.read()
    if len(now) == 0:
        bot.reply_to(message, 'Ejecutado df -h')
    else:
        bot.reply_to(message, now)


@bot.message_handler(func=lambda message: message.chat.id == administrador, commands=['info'])
def send_info(message):
    #uptime, cpu, ram, disk, speed download/upload
    f = os.popen('pwd')
    now = f.read()
    if len(now) == 0:
        bot.reply_to(message, 'Ejecutado, pero esta en proceso')
    else:
        bot.reply_to(message, now)


@bot.message_handler(func=lambda message: message.chat.id == administrador, commands=['show_torrent'])
def send_show_torrent(message):
    #f = os.popen('transmission-remote --auth=pi:{} -l | egrep -v "Finished|Stopped|Seeding|ID|Sum:" |  awk \'{print $2}{for(i=13; i<=NF; i++) printf "%s",$i (i==NF?ORS:OFS)}\''.format(pass_transmission))
    f = os.popen('transmission-remote 127.0.0.1:9091 --auth=pi:{} -l | egrep -v "Finished|Stopped|Seeding|ID|Sum:"'.format(pass_transmission))
    now = f.read()
    if len(now) != 0:
        for line in now:
            line = re.sub('\[AC3 5\.1-Castellano-AC3 5.1 Ingles\+Subs\]|\[ES-EN\]|\[AC3 5.1 Español Castellano\]|\[HDTV 720p?\]|(\d+\.?\d+|None)( )+(MB|GB|kB|Unknown).*(Up & Down|Downloading|Queued|Idle|Uploading)( )*| - Temporada \d+ |(\d+\.\d+)( )+(\d+\.\d+)', '', now)
        bot.reply_to(message, line)
        #bot.reply_to(message, now)
    else:
        bot.reply_to(message, 'Ningun torrent activo en este momento.')


@bot.message_handler(func=lambda message: message.chat.id == administrador, commands=['exit'])
def send_exit(message):
    f = os.popen('pwd')
    now = f.read()
    if len(now) == 0:
        bot.reply_to(message, 'Ejecutado,no hace nada')
    else:
        bot.reply_to(message, now)


@bot.message_handler(func=lambda message: message.chat.id == administrador, regexp="[Cc]md: .*")
def handle_cmd(message):
    peligro = ['sudo reboot', ':(){ :|: & };:']

    msg = re.sub('[Cc]md: ', '', message.text)
    if not msg in peligro:
        f = os.popen(msg)
        now = f.read()
        if len(now) == 0:
            bot.reply_to(message, 'Ejecutado: {}'.format(msg))
        else:
            bot.reply_to(message, now)
    else:
        bot.reply_to(message, 'Comando aun no implementado')


@bot.message_handler(func=lambda message: message.chat.id == administrador, regexp="^magnet:\?xt=urn.*")
def handle_magnet(message):
    comando = 'transmission-remote 127.0.0.1:9091 --auth=pi:{} --add {}'.format(pass_transmission, message.text)
    os.popen(comando)
    #now = f.read()
    bot.reply_to(message, 'Ejecutado add torrent')
    send_show_torrent(message)


@bot.message_handler(regexp="^(http://)?www.newpct1.com/.*")
def handle_newpct1(message):

    def descargaTorrent(direcc): #PARA NEWPCT1
        '''
        Funcion que obtiene la url torrent del la dirreccion que recibe

        :param str direcc: Dirreccion de la pagina web que contiene el torrent

        :return str: Nos devuelve el string con la url del torrent
        '''

        session = requests.session()
        page = session.get(direcc, verify=False).text
        #page = urllib.urlopen(direcc).read()
        sopa = BeautifulSoup(page, 'html.parser')
        return sopa.find('div', {"id": "tab1"}).a['href']

    def descargaFichero(url, destino):
        r = requests.get(url)
        with open(destino, "wb") as code:
            code.write(r.content)

    from bs4 import BeautifulSoup

    bot.reply_to(message, 'Buscando torrent en newpct1')

    regexGenero = re.search('descarga-torrent', message.text)                   # buscamos el genero
    if regexGenero:                                                 # si hay find continua, sino retorno None el re.search
        urlPeli = message.text
    else:
        urlPeli = re.sub('(http://)?www.newpct1.com/', 'http://www.newpct1.com/descarga-torrent/', message.text)

    url = descargaTorrent(urlPeli)
    if url is not None:
        fich = '/tmp/{}.torrent'.format(message.chat.id)
        descargaFichero(url, fich)

        file_data = open(fich, 'rb')
        bot.send_document(message.chat.id,  file_data)
        if message.chat.id == administrador:
            os.rename(fich ,'/home/pi/Downloads/file.torrent')
        else:
            pass
        with open('/tmp/descarga_torrent.log', "a") as f:
            f.write('{}, {}, {} -> {}\n'.format(message.chat.id,  message.chat.first_name, message.chat.username, message.text))



@bot.message_handler(func=lambda message: message.chat.id == administrador, content_types=["text"])
def my_text(message):
    if message.text in dicc_botones.values():
        if message.text == dicc_botones['cgs']:
            send_cgs(message)
        elif message.text == dicc_botones['crs']:
            send_crs(message)
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


@bot.message_handler(func=lambda message: message.chat.id == administrador, content_types=["photo"])
def my_photo(message):
    if message.reply_to_message:
        who_to_send_id = dbhelper.get_user_id(message.reply_to_message.message_id)
        if who_to_send_id:
            # Send the largest available (last item in photos array)
            bot.send_photo(who_to_send_id, list(message.photo)[-1].file_id)
    else:
        bot.send_message(message.chat.id, "No one to reply photo!")


@bot.message_handler(func=lambda message: message.chat.id == administrador, content_types=["voice"])
def my_voice(message):
    if message.reply_to_message:
        who_to_send_id = dbhelper.get_user_id(message.reply_to_message.message_id)
        if who_to_send_id:
            # bot.send_chat_action(who_to_send_id, "record_audio")
            bot.send_voice(who_to_send_id, message.voice.file_id, duration=message.voice.duration)
    else:
        bot.send_message(message.chat.id, "No one to reply voice!")


@bot.message_handler(func=lambda message: message.chat.id in usuariosPermitidos, content_types=["document"])
def my_document(message):
    if message.document.mime_type == 'application/x-bittorrent':
        file_info = bot.get_file(message.document.file_id)
        #bot.send_message(message.chat.id, 'https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, file_info.file_path))
        file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(api_telegram, file_info.file_path))
        with open('/home/pi/Downloads/{}.torrent'.format(message.document.file_id), "wb") as code:
            code.write(file.content)
        bot.reply_to(message, 'Descargando torrent: "{}"'.format(message.document.file_name))
        send_show_torrent(message)
    else:
        bot.reply_to(message, 'Aun no he implementado este tipo de ficheros: "{}"'.format(message.document.mime_type))


@bot.message_handler(regexp=".*")
def handle_resto(message):
    texto = 'No tienes permiso para ejecutar esta accion, eso se debe a que no eres yo.\nPor lo que ya sabes, desaparece -.-'
    bot.reply_to(message.chat.id, texto)


bot.polling(none_stop=True) # Con esto, le decimos al bot que siga funcionando incluso si encuentra algun fallo.
