#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

import requests

try: #Ejecucion desde Series.py
    from .settings import api_telegram
except: #Ejecucion local
    from settings import api_telegram


class TG2():
    def __init__(self, chat_id):
        self.api = api_telegram
        self.url = 'https://api.telegram.org/bot{0}/{1}'
        self.chat_id = chat_id
        requests.packages.urllib3.disable_warnings()		## Esto hace que no salga la advertencia por fallo al verificar el certificado


    def __makeRequest(self, method_name, method='post', params=None, files=None):
        """
        Makes a request to the Telegram API.
        :param token: The bot's API token. (Created with @BotFather)
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
            if 'timeout' in params: read_timeout = params['timeout'] + 10
            if 'connect-timeout' in params: connect_timeout = params['connect-timeout'] + 10

        result = requests.request(method, request_url, params=params, files=files, timeout=(connect_timeout, read_timeout))

        return json.loads(result.text)['ok']



    def __get_method_by_type(self, data_type):
        data_type = str(type(data_type))
        dic = {
            "<class 'str'>": 'sendMessage',
            "<class '_io.BufferedReader'>": "sendDocument"
        }
        '''
        if data_type == 'document':
            return r'sendDocument'
        if data_type == 'sticker':
            return r'sendSticker'''
        #print(dic[data_type])
        return dic[data_type]


    def sendTg(self, texto='ola k ase'):   #funciona en python 3
        payload = {'chat_id': self.chat_id,
                    'text': texto}

        method_url = self.__get_method_by_type(texto)

        return self.__makeRequest(method_url, params=payload, method='post')


    def sendFile(self, url_file):

        payload = {'chat_id': self.chat_id}
        files = None

        data = open(url_file, 'rb')
        method_url = self.__get_method_by_type(data)

        if str(type(data)) == "<class '_io.BufferedReader'>":
            files = {'document': data}

            return self.__makeRequest(method_url, params=payload, files=files, method='post')


    def recibeTg(self): # no funciona de momento por la codificacion
        URL  = 'https://api.telegram.org/bot{}/getUpdates'.format(self.api)
        req_headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        session = requests.session()
        login = session.post(URL, headers=req_headers)			# Authenticate

        print((type(login.text)))


        #print(str(login.text.strip().decode('utf-8')))
        #print( json.loads( str(login.text.strip())))

        dat = json.loads(str(login.text.strip()))

        print(dat)




if __name__ == '__main__':
    a = TG2('33063767')
    print(a.sendTg('Test desde modulo de python'))
    #print(a.sendFile('connect_sqlite.py'))
    #a.recibeTg()
