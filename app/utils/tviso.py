#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import http.cookiejar
import os
import re
import sys
from pathlib import PurePath  # nueva forma de trabajar con rutas

import requests

# Confirmamos que tenemos en el path la ruta de la aplicacion, para poder lanzarlo desde cualquier ruta
absolut_path: PurePath = PurePath(os.path.realpath(__file__))  # Ruta absoluta del fichero
new_path: str = f'{absolut_path.parent}/../../'
if new_path not in sys.path:
    sys.path.append(new_path)

from app import logger

from typing import List


# NO funciona en python 3
def conect_tviso_mechanize(username: str, password: str) -> List[str]:
    # import mechanicalsoup as mechanize
    import mechanize  # no es compatible con python3

    urllogin = 'https://es.tviso.com/login'
    urlafter = 'https://es.tviso.com/calendar?area=ES&all=true'
    loginhtml = 'user'
    loginpass = 'pass'

    # Browser
    br = mechanize.Browser()

    # Enable cookie support
    # cookiejar = http.cookiejar.LWPCookieJar()
    cookiejar = http.cookiejar.LWPCookieJar()
    br.set_cookiejar(cookiejar)

    # Broser options

    br.set_handle_equiv(True)
    # br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)

    br.addheaders = [
        ('User-agent',
         'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

    # authenticate
    br.open(urllogin)
    br.select_form(nr=1)
    # br.select_form(name = 'entrada')
    br.form[loginhtml] = username
    br.form[loginpass] = password

    # request2 = br.form.click()
    response1 = br.submit()
    logger.info(response1.read())

    # logger.info(cookiejar)
    url = br.open(urlafter)
    return_page = url.read()
    compl = re.findall('<span class="event-name full-name">.*</span>', return_page)
    series = list()

    for i in compl:
        a = i.replace('<span class="event-name full-name">', '').replace('</span>', '')
        series.append(a)

    # eliminar duplicados
    # http://blog.elcodiguero.com/python/eliminar-objetos-repetidos-de-una-lista.html
    return list(set(series))


# funciona en python 3
def conect_tviso(username: str, password: str) -> List[str]:
    urllogin = 'https://es.tviso.com/login'
    urlafter = 'https://es.tviso.com/calendar?area=ES&all=true'

    formdata = {'user': username,
                'pass': password,
                'r': 'on',
                'call': '',
                'ref': ''}

    req_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0',
        'Content-Type': 'application/x-www-form-urlencoded'}

    session = requests.session()
    login = session.post(urllogin, data=formdata, headers=req_headers, verify=True)  # Authenticate
    # Accedo a la pagina donde esta el saldo total
    series = session.get(urlafter, cookies=login.cookies, headers=req_headers, verify=True)

    compl = re.findall('<span class="event-name full-name">.*</span>', series.text)
    series = list()

    for i in compl:
        a = i.replace('<span class="event-name full-name">', '').replace('</span>', '')
        series.append(a)

    # eliminar duplicados
    # http://blog.elcodiguero.com/python/eliminar-objetos-repetidos-de-una-lista.html
    return list(set(series))


def main():
    opcion1 = conect_tviso("user", "pass")

    for i in opcion1:
        logger.info(i)


if __name__ == '__main__':
    # main()
    pass
