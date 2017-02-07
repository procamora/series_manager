#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import http.cookiejar

import requests

try: #Ejecucion desde Series.py
    from .settings import modo_debug, user_tviso, pass_tviso
except: #Ejecucion local
    from settings import modo_debug, user_tviso, pass_tviso


def conectTvisoMechanize():   # NO funciona en python 3
    #import mechanicalsoup as mechanize
    import mechanize   # no es compatible con python3

    USERNAME  = user_tviso
    PASSWORD  = pass_tviso
    URLLOGIN  = 'https://es.tviso.com/login'
    URLAFTER  = 'https://es.tviso.com/calendar?area=ES&all=true'
    LOGINHTML = 'user'
    LOGINPASS = 'pass'

    # Browser
    br = mechanize.Browser()

    # Enable cookie support
    cookiejar = http.cookiejar.LWPCookieJar()              #cookiejar = http.cookiejar.LWPCookieJar()
    br.set_cookiejar(cookiejar)

    # Broser options

    br.set_handle_equiv(True)
    #br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)

    br.addheaders = [ ('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1') ]

    # authenticate
    br.open(URLLOGIN)
    br.select_form(nr = 1)
    #br.select_form(name = 'entrada')
    br.form[LOGINHTML] = USERNAME
    br.form[LOGINPASS] = PASSWORD
    #print br

    #request2 = br.form.click()
    response1 =  br.submit()
    print(response1.read())

    #print cookiejar
    url = br.open(URLAFTER)
    returnPage = url.read()
    compl = re.findall('<span class="event-name full-name">.*</span>', returnPage)
    series = list()

    for i in compl:
        a = i.replace('<span class="event-name full-name">','').replace('</span>','')
        series.append(a)

    #eliminar duplicados   http://blog.elcodiguero.com/python/eliminar-objetos-repetidos-de-una-lista.html
    return list(set(series))


def conectTviso():   #funciona en python 3

    USERNAME  = 'NotSer'
    PASSWORD  = 'i(!f!Boz_A&YLY]q'
    URLLOGIN  = 'https://es.tviso.com/login'
    URLAFTER  = 'https://es.tviso.com/calendar?area=ES&all=true'

    formdata = {'user': USERNAME,
    'pass': PASSWORD,
    'r': 'on',
    'call': '',
    'ref': ''}

    req_headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0', 'Content-Type': 'application/x-www-form-urlencoded' }

    session = requests.session()
    login = session.post(URLLOGIN, data=formdata, headers=req_headers, verify=True)			# Authenticate
    series = session.get(URLAFTER, cookies=login.cookies, headers=req_headers, verify=True)	# Accedo a la pagina donde esta el saldo total

    compl = re.findall('<span class="event-name full-name">.*</span>', series.text)
    series = list()

    for i in compl:
        a = i.replace('<span class="event-name full-name">','').replace('</span>','')
        series.append(a)

    #eliminar duplicados   http://blog.elcodiguero.com/python/eliminar-objetos-repetidos-de-una-lista.html
    return list(set(series))



def main():
    opcion1 = conectTviso()

    for i in opcion1:
        print(i)


if __name__ == '__main__':
    #main()
    pass
