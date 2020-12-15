#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
sudo apt-get install unrar-free
"""

import glob
import os
import re
import sys
from pathlib import Path
from typing import Text, List, NoReturn

import rarfile
import requests
from bs4 import BeautifulSoup

from app import logger
from app.utils.telegram2 import Telegram


def search_pass(url: Text) -> Text:
    """
    funcion para buscar la password en la url dada, parsea todos el html
    """
    session: requests.sessions = requests.session()
    page: Text = session.get(url, verify=False).text
    sopa: BeautifulSoup = BeautifulSoup(page, 'html.parser')

    return sopa.find('input', {"id": "txt_password"})['value']


def extract_all_parts(file_rar: Path) -> NoReturn:
    rar: rarfile.RarFile = rarfile.RarFile(file_rar)
    url: List = list()
    if rar.needs_password():
        # busco la url para descargar la pass con glob no me lista los ficheros
        for i in os.listdir(file_rar.parent):
            if i == 'CONTRASEÑA PARA DESCOMPRIMIR.txt':
                with open(f'{file_rar.parent}{i}', 'r', encoding="ISO-8859-1") as f:
                    texto = f.read()
                url = re.findall(r"((https?://)?(\w+\.)+\w{2,3}/?.*/)", texto)

        if len(url) is not None:
            passwd = search_pass(url[0][0])
            rar.setpassword(passwd)  # whatever the password is

    rar.extractall(path=str(file_rar.parent))
    name_file: Text = Path(file_rar.stem).stem  # remove .part1.rar
    all_parts: Text = str(Path(file_rar.parent, name_file))
    for i in glob.glob(f'{all_parts}*'):
        logger.debug(f"- remove {i}")
        os.remove(i)


def main(directory: Text):
    tg: Telegram = Telegram('33063767')
    for i in glob.glob(directory):
        if not re.search(r'part1.rar', i):  # skip those parts that are not part1.rar
            continue

        logger.debug(i)
        try:
            # tg.send_tg(f'Start the process of decompressing: {i.split("/")[-1]}')
            extract_all_parts(Path(i))
            # tg.send_tg(f'End the process of decompressing: {i.split("/")[-1]}')
        except Exception as e:
            tg.send_tg(f'Fallo al descomprimir: {i} por: {e}')
            logger.error(f"|{e}|")

            with open('/tmp/unrar.log', 'a', encoding="UTF-8") as f:
                f.write(str(sys.exc_info()[0]))


if __name__ == '__main__':
    main('/home/procamora/Documents/kk/*/*.rar')
