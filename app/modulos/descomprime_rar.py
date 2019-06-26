#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
sudo apt-get install unrar-free
"""
import re
import os
import glob
import sys

import rarfile
import requests
from bs4 import BeautifulSoup

import app.modulos.telegram2 as TG2
from app import logger

def busca_pass(url):
    """
    funcion para buscar la password en la url dada, parsea todo el html
    """
    session = requests.session()
    page = session.get(url, verify=False).text
    sopa = BeautifulSoup(page, 'html.parser')

    return sopa.find('input', {"id": "txt_password"})['value']


def descomprime(fichero):
    # http://librosweb.es/libro/python/capitulo_6/metodos_de_union_y_division.html
    # partition(fichero.rar) = (antecedente, fichero.rar, consecuente), lo que
    # hago es sacar el directorio del fichero
    directory = fichero.partition(fichero.split('/')[-1])[0]
    rar = rarfile.RarFile(fichero)
    url = str()
    if rar.needs_password():
        # busco la url para descargar la pass
        # con glob no me lista los ficheros
        for i in os.listdir('{}'.format(directory)):
            if i == 'CONTRASEÑA PARA DESCOMPRIMIR.txt':
                texto = str()
                with open('{}{}'.format(directory, i), 'r', encoding="ISO-8859-1") as f:
                    texto = f.read()
                url = re.findall("((https?\:\/\/)?(\w+\.)+\w{2,3}\/?.*\/)", texto)

        if len(url) is not None:
            passwd = busca_pass(url[0][0])
            rar.setpassword(passwd)  # whatever the password is

    rar.extractall(path=directory)
    os.remove(fichero)


def main(ruta):
    a = TG2('33063767')
    for i in glob.glob(ruta):
        logger.info(i)
        try:
            a.sendTg(
                'Empieza proceos descomprimir: {}'.format(i.split('/')[-1]))
            descomprime(i)
            a.sendTg(
                'Termina proceos descomprimir: {}'.format(i.split('/')[-1]))
        except Exception as e:
            if str(e) != "Need to start from first volume":
                a.sendTg('Fallo al descomprimir: {} por: {}'.format(i.split('/')[-1], e))
            logger.info("|{}|".format(e))

            with open('/tmp/unrar.log', 'a', encoding="UTF-8") as f:
                f.write(str(sys.exc_info()[0]))


if __name__ == '__main__':
    main('/media/pi/640Gb/*/*.rar')
