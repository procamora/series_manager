#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sys
from pathlib import PurePath  # nueva forma de trabajar con rutas
from typing import NoReturn, Dict

import requests
import urllib3

# Confirmamos que tenemos en el path la ruta de la aplicacion, para poder lanzarlo desde cualquier ruta
absolut_path: PurePath = PurePath(os.path.realpath(__file__))  # Ruta absoluta del fichero
new_path: str = f'{absolut_path.parent}/../../'
if new_path not in sys.path:
    sys.path.append(new_path)

from app import logger
from app.models.model_query import Query
import app.controller.Controller as Controller
from app.utils.settings import REQ_HEADERS, BOT_DEBUG, BOT_TOK_DEBUG, BOT_TOK
from app.models.model_t_notification import Notification

# Esto hace que no salga la advertencia por fallo al verificar el certificado
urllib3.disable_warnings()


class Telegram(Notification):
    def __init__(self, chat_id: str) -> NoReturn:
        if BOT_DEBUG:
            self.api = BOT_TOK_DEBUG
        else:
            self.api = BOT_TOK

        self.url = 'https://api.telegram.org/bot{0}/{1}'
        self.chat_id = chat_id

    def make_request(self, method_name, method='post', params=None, files=None) -> Dict[str, str]:
        """
        Makes a request to the Telegram API.
        :param method_name: Name of the API method to be called. (E.g. 'getUpdates')
        :param method: HTTP method to be used. Defaults to 'get'.
        :param params: Optional parameters. Should be a dictionary with key-value pairs.
        :param files: Optional files.
        :return: The result parsed to a JSON dictionary.
        """

        connect_timeout = 3.5
        read_timeout = 9999

        request_url = self.url.format(self.api, method_name)
        connect_timeout = connect_timeout
        if params:
            if 'timeout' in params:
                read_timeout = params['timeout'] + 10
            if 'connect-timeout' in params:
                connect_timeout = params['connect-timeout'] + 10

        print(method)
        print(request_url)
        print(params)
        print(files)
        result = requests.request(method, request_url, params=params, files=files, timeout=(connect_timeout,
                                                                                            read_timeout))
        logger.debug(result)
        logger.debug(result.text)
        return json.loads(result.text)['ok']

    @staticmethod
    def get_method_type(data_type) -> str:
        data_type = str(type(data_type))
        dic = {
            "<class 'str'>": 'sendMessage',
            "<class '_io.BufferedReader'>": "sendDocument"
        }

        # logger.debug(dic[data_type])
        return dic[data_type]

    def send_tg(self, texto: str = 'ola k ase') -> Dict[str, str]:  # funciona en python 3
        payload = {
            'chat_id': self.chat_id,
            'text': texto
        }

        method_url = self.get_method_type(texto)

        return self.make_request(method_url, params=payload, method='post')

    def send_file(self, url_file: str) -> Dict[str, str]:

        payload = {'chat_id': self.chat_id}
        # files = None

        data = open(url_file, 'rb')
        method_url = self.get_method_type(data)

        if str(type(data)) == "<class '_io.BufferedReader'>":
            files = {'document': data}
            return self.make_request(method_url, params=payload, files=files, method='post')

    def receives_tg(self) -> NoReturn:  # no funciona de momento por la codificacion
        url = f'https://api.telegram.org/bot{self.api}/getUpdates'

        session = requests.session()
        login = session.post(url, headers=REQ_HEADERS)  # Authenticate

        logger.info(type(login.text))
        # logger.info(str(login.text.strip().decode('utf-8')))
        # logger.info( json.loads( str(login.text.strip())))
        dat = json.loads(str(login.text.strip()))
        logger.info(dat)


if __name__ == '__main__':
    a = Telegram('33063767')
    a.send_tg('Test desde modulo de python')
    # logger.info(a.sendFile('connect_sqlite.py'))
    # a.recibeTg()
