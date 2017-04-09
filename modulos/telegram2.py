#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

import requests

try:  # Ejecucion desde Series.py
    from .settings import modo_debug, ruta_db, directorio_local, sync_sqlite
    from .connect_sqlite import conectionSQLite, ejecutaScriptSqlite
except:  # Ejecucion local
    from settings import modo_debug, ruta_db, directorio_local, sync_sqlite
    from connect_sqlite import conectionSQLite, ejecutaScriptSqlite


class TG2():
    def __init__(self, chat_id):
        datosIniciales = self.datosIniciales()
        if datosIniciales is not None:
            self.api = datosIniciales['api_telegram']
        else:
            return

        self.url = 'https://api.telegram.org/bot{0}/{1}'
        self.chat_id = chat_id
        # Esto hace que no salga la advertencia por fallo al verificar el certificado
        requests.packages.urllib3.disable_warnings()

    @staticmethod
    def datosIniciales():
        with open(r'{}/{}'.format(directorio_local, sync_sqlite), 'r') as f:
            id_fich = f.readline().replace('/n', '')

        query = 'SELECT * FROM Credenciales'.format(id_fich)
        consulta = conectionSQLite(ruta_db, query, True)
        if len(consulta) > 0:
            return consulta[0]
        return None

    def makeRequest(self, method_name, method='post', params=None, files=None):
        """
        Makes a request to the Telegram API.
        :param method_name: Name of the API method to be called. (E.g. 'getUpdates')
        :param method: HTTP method to be used. Defaults to 'get'.
        :param params: Optional parameters. Should be a dictionary with key-value pairs.
        :param files: Optional files.
        :return: The result parsed to a JSON dictionary.
        """

        CONNECT_TIMEOUT = 3.5
        READ_TIMEOUT = 9999

        request_url = self.url.format(self.api, method_name)
        read_timeout = READ_TIMEOUT
        connect_timeout = CONNECT_TIMEOUT
        if params:
            if 'timeout' in params:
                read_timeout = params['timeout'] + 10
            if 'connect-timeout' in params:
                connect_timeout = params['connect-timeout'] + 10

        result = requests.request(method, request_url, params=params, files=files, timeout=(
            connect_timeout, read_timeout))

        return json.loads(result.text)['ok']

    @staticmethod
    def getMethodType(data_type):
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
        # print(dic[data_type])
        return dic[data_type]

    def sendTg(self, texto='ola k ase'):  # funciona en python 3
        payload = {'chat_id': self.chat_id,
                   'text': texto}

        method_url = self.getMethodType(texto)

        return self.makeRequest(method_url, params=payload, method='post')

    def sendFile(self, url_file):

        payload = {'chat_id': self.chat_id}
        files = None

        data = open(url_file, 'rb')
        method_url = self.getMethodType(data)

        if str(type(data)) == "<class '_io.BufferedReader'>":
            files = {'document': data}

            return self.makeRequest(method_url, params=payload, files=files, method='post')

    def recibeTg(self):  # no funciona de momento por la codificacion
        URL = 'https://api.telegram.org/bot{}/getUpdates'.format(self.api)
        req_headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        session = requests.session()
        login = session.post(URL, headers=req_headers)  # Authenticate

        print((type(login.text)))

        # print(str(login.text.strip().decode('utf-8')))
        # print( json.loads( str(login.text.strip())))

        dat = json.loads(str(login.text.strip()))

        print(dat)


if __name__ == '__main__':
    a = TG2('33063767')
    print(a.sendTg('Test desde modulo de python'))
    # print(a.sendFile('connect_sqlite.py'))
    # a.recibeTg()
