#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys

import requests

# Esto hace que no salga la advertencia por fallo al verificar el certificado
requests.packages.urllib3.disable_warnings()

try:  # Ejecucion desde Series.py
    from .settings import MODE_DEBUG, PATH_DATABASE, DIRECTORY_LOCAL, SYNC_SQLITE
    from .connect_sqlite import conection_sqlite, execute_script_sqlite
    from app import logger
except ModuleNotFoundError as e:  # Ejecucion local
    new_path = '../../'
    if new_path not in sys.path:
        sys.path.append(new_path)
    from app import logger

    from app.modulos.settings import MODE_DEBUG, PATH_DATABASE, DIRECTORY_LOCAL, SYNC_SQLITE
    from app.modulos.connect_sqlite import conection_sqlite, execute_script_sqlite

from app import logger

from typing import NoReturn, Dict, Optional


class Telegram:
    def __init__(self, chat_id: str) -> NoReturn:
        initial_data = self.initial_data()
        if initial_data is not None:
            self.api = initial_data['api_telegram']
        else:
            return

        self.url = 'https://api.telegram.org/bot{0}/{1}'
        self.chat_id = chat_id

    @staticmethod
    def initial_data() -> Optional[Dict[str, str]]:
        with open(SYNC_SQLITE, 'r') as f:
            id_fich = f.readline().replace('/n', '')

        query = 'SELECT * FROM Credenciales'.format(id_fich)
        consulta = conection_sqlite(PATH_DATABASE, query, True)
        if len(consulta) > 0:
            return consulta[0]
        return None

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

        result = requests.request(method, request_url, params=params, files=files, timeout=(
            connect_timeout, read_timeout))

        logger.debug(
            requests.request(method, request_url, params=params, files=files, timeout=(connect_timeout, read_timeout)))

        return json.loads(result.text)['ok']

    @staticmethod
    def get_method_type(data_type) -> str:
        data_type = str(type(data_type))
        dic = {
            "<class 'str'>": 'sendMessage',
            "<class '_io.BufferedReader'>": "sendDocument"
        }
        """
        if data_type == 'document':
            return r'sendDocument'
        if data_type == 'sticker':
            return r'sendSticker"""
        # logger.debug(dic[data_type])
        return dic[data_type]

    def send_tg(self, texto: str = 'ola k ase') -> Dict[str, str]:  # funciona en python 3
        payload = {'chat_id': self.chat_id,
                   'text': texto}

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
        req_headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        session = requests.session()
        login = session.post(url, headers=req_headers)  # Authenticate

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
