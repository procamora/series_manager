#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''

'''
import re
import os
import time

import requests
import feedparser
from bs4 import BeautifulSoup

from modulos.connect_sqlite import conectionSQLite, ejecutaScriptSqlite
from modulos.pushbullet2 import PB2
from modulos.telegram2 import TG2
from modulos.mail2 import ML2
from modulos.settings import modo_debug, directorio_trabajo, ruta_db
import funciones


def MuestraNotificaciones():
    '''
    poner las api de la base de datos
    '''
    queryN = 'SELECT * FROM notificaciones'
    Datos = conectionSQLite(ruta_db, queryN, True)

    global tg3, pb3, ml3, api_ml3

    for i in Datos:
        if i['Activo'] == 'True':
            if i['Nombre'] == 'Telegram':
                tg3 = TG2(i['API'])

            elif i['Nombre'] == 'Pushbullet':
                pb3 = PB2(i['API'])

            elif i['Nombre'] == 'Email':
                ml3 = ML2('test1notificaciones@gmail.com', 'i(!f!Boz_A&YLY]q')
                api_ml3 = api_ml3

    return Datos

global notificaciones
notificaciones = MuestraNotificaciones()

# https://gist.github.com/kaotika/e8ca5c340ec94f599fb2


class MiFormulario():

    def __init__(self, dbSeries=None):
        if funciones.internetOn():
            self.Otra = 'Otra'  # campo otra del formulario
            self.EstadoI = 'Ok'  # estado inicial
            self.db = dbSeries

            #query = 'SELECT Nombre, Temporada, Capitulo, VOSE FROM Series WHERE Siguiendo = "Si" AND ((VOSE = "No" AND Estado="Activa" AND Capitulo <> 0) OR (VOSE = "Si")) ORDER BY Nombre'
            #self.query = 'SELECT Nombre, Temporada, Capitulo, VOSE FROM Series WHERE Siguiendo = "Si" AND ((VOSE = "No" AND Estado="Activa" AND Capitulo <> 0) OR (VOSE = "Si" AND Capitulo <> 0)) ORDER BY Nombre ASC'
            self.query = '''SELECT Nombre, Temporada, Capitulo, VOSE FROM Series WHERE Siguiendo = "Si" ORDER BY Nombre ASC'''
            self.series = conectionSQLite(self.db, self.query, True)

            self.listaNotificaciones = str()
            self.actualizaDia = str()
            self.conf = funciones.dbConfiguarion()
            urlNew = self.conf['UrlFeedNewpct']
            urlShow = self.conf['UrlFeedShowrss']

            # Diccionario con las series y capitulos para actualizar la bd con
            # el capitulo descargado
            self.capDescargado = dict()
            self.consultaUpdate = str()

            try:
                self.feedNew = feedparser.parse(urlNew)
            except:  # Para el fallo en fedora
                self.feedNew = self.__feedparser_parse(urlNew)

            try:
                self.feedShow = feedparser.parse(urlShow)
            except:  # Para el fallo en fedora
                self.feedShow = self.__feedparser_parse(urlShow)

            self.run()

    def run(self):
        fichNewpct = self.conf['FicheroFeedNewpct']
        fichShowrss = self.conf['FicheroFeedShowrss']
        self.rutlog = r'{}/log'.format(directorio_trabajo)

        if not os.path.exists(self.rutlog):
            os.mkdir(self.rutlog)

        if not os.path.exists('{}/{}'.format(self.rutlog, fichNewpct)):
            funciones.crearFichero('{}/{}'.format(self.rutlog, fichNewpct))

        if not os.path.exists('{}/{}'.format(self.rutlog, fichShowrss)):
            funciones.crearFichero('{}/{}'.format(self.rutlog, fichShowrss))

        with open('{}/{}'.format(self.rutlog, fichNewpct), 'r') as f:
            self.ultimaSerieNew = f.readline()

        with open('{}/{}'.format(self.rutlog, fichShowrss), 'r') as f:
            self.ultimaSerieShow = f.readline()

        series = conectionSQLite(self.db, self.query, True)

        SerieActualNew = str()
        SerieActualShow = str()
        SerieActualTemp = str()

        for i in series:
            try:
                print(('Revisa: {}'.format(i['Nombre'])))
                SerieActualTemp = self.ParseaFeed(
                    i['Nombre'], i['Temporada'], i['Capitulo'], i['VOSE'])
                if i['VOSE'] == 'Si':
                    SerieActualShow = SerieActualTemp
                else:
                    SerieActualNew = SerieActualTemp
            except Exception as e:
                print('FALLO: ', e)

        if len(self.ultimaSerieNew) != 0:  # or len(self.ultimaSerieShow) != 0:
            print(self.actualizaDia)
            # actualiza los dias en los que sale el capitulo
            ejecutaScriptSqlite(self.db, self.actualizaDia)

            for notif in notificaciones:
                if notif['Activo'] == 'True':
                    if notif['Nombre'] == 'Telegram':
                        tg3.sendTg(self.listaNotificaciones)
                    elif notif['Nombre'] == 'Pushbullet':
                        pb3.sendTextPb(
                            'Gestor series', self.listaNotificaciones)
                    elif notif['Nombre'] == 'Email':
                        ml3.sendMail(api_ml3, self.listaNotificaciones)

        # capitulos que descargo
        for i in self.capDescargado.items():
            #print (i)
            query = 'UPDATE Series SET Capitulo_Descargado={} WHERE Nombre LIKE "{}";\n'.format(
                str(i[1]), i[0])
            self.consultaUpdate += query

        print(self.consultaUpdate)
        # actualiza el ultimo capitulo que he descargado
        ejecutaScriptSqlite(self.db, self.consultaUpdate)

        # Guardar ultima serie del feed
        if SerieActualShow is not None and SerieActualNew is not None:
            with open('{}/{}'.format(self.rutlog, fichNewpct), 'w') as f:
                pass
                f.write(SerieActualNew)
            with open('{}/{}'.format(self.rutlog, fichShowrss), 'w') as f:
                pass
                f.write(SerieActualShow)
        else:
            print(
                'PROBLEMA CON if SerieActualShow is not None and SerieActualNew is not None:')

    def ParseaFeed(self, serie, tem, cap, vose):
        '''Solo funciona con series de 2 digitos por la expresion regular'''

        cap = str(cap)
        ruta = str(self.conf['RutaDescargas'])   # es unicode
        if vose == 'Si':
            ultimaSerie = self.ultimaSerieShow
            d = self.feedShow
        else:
            ultimaSerie = self.ultimaSerieNew
            d = self.feedNew

        if not os.path.exists(ruta):
            os.mkdir(ruta)

        if len(str(cap)) == 1:
            cap = '0' + str(cap)

        for i in d.entries:
            # cuando llegamos al ultimo capitulo pasamos a la siguiente serie
            if i.title == ultimaSerie:
                # retornamos el valor que luego usaremos en ultima serie para
                # guardarlo en el fichero
                return d.entries[0].title
            regex_vose = '(?i){} {}.*'.format(
                self.__escapaParentesis(serie.lower()), tem)
            regex_cast = '(?i){}( \(Proper\))? - Temporada( )?\d+ \[HDTV 720p?\]\[Cap\.{}\d+(_\d+)?\]\[A.*'.format(
                self.__escapaParentesis(serie.lower()), tem)

            if modo_debug:
                # print(i.title)
                print(regex_cast, i.title)

            estado = False
            if vose == 'Si':
                if re.search(regex_vose, i.title):
                    estado = True
            else:
                if re.search(regex_cast, i.title):
                    estado = True

            if estado:
                if vose == 'Si':
                    torrent = i.link
                else:
                    torrent = self.buscaTorrent(i.link)

                if not os.path.exists('{}{}.torrent'.format(ruta, i.title)):
                    ficheroDescargas = self.conf['FicheroDescargas']

                    with open('{}/{}'.format(self.rutlog, ficheroDescargas), 'a') as f:
                        f.write(
                            '{} {}\n'.format(time.strftime('%Y%m%d'), i.title))

                    # En pelis que son VOSE no se si da fallo, esto solo es
                    # para no VOSE
                    varNom = i.title.split('-')[0]
                    varEpi = i.title.split('][')[1]
                    if vose == 'Si':
                        # creo un string para solo mandar una notificacion
                        self.listaNotificaciones += '{}\n'.format(i.title)
                    else:
                        # creo un string para solo mandar una notificacion
                        self.listaNotificaciones += '{} {}\n'.format(
                            varNom, varEpi)

                    funciones.descargaFichero(
                        torrent, r'{}/{}.torrent'.format(ruta, i.title))
                    self.actualizaDia += '''UPDATE series SET Dia="{}" WHERE Nombre LIKE "{}";\n'''.format(
                        funciones.calculaDiaSemana(), serie)

                    # Diccionario con todos los capitulos descargados, para
                    # actualizar la bd con los capitulos por donde voy
                    # regex para coger el capitulo unicamente
                    capituloActual = int(
                        re.sub('Cap\.{}'.format(tem), '', varEpi))
                    if serie not in self.capDescargado:
                        self.capDescargado[serie] = capituloActual
                    else:
                        # REVISAR, CREO QUE ESTA MAL NO ES 4X05 ES 405
                        if self.capDescargado[serie] < capituloActual:
                            self.capDescargado[serie] = capituloActual

                print(('DESCARGANDO: {}'.format(serie)))

        return d.entries[0].title

    def __escapaParentesis(self, texto):
        '''
        No he probado si funciona con series como powers
        '''
        return texto.replace('(', '\\(').replace(')', '\\)')

    def __feedparser_parse(self, url):
        '''
        Da un fallo en fedora 23, por eso hace falta esta funcion
        https://github.com/kurtmckee/feedparser/issues/30
        '''

        try:
            return feedparser.parse(url)
        except TypeError:
            if 'drv_libxml2' in feedparser.PREFERRED_XML_PARSERS:
                feedparser.PREFERRED_XML_PARSERS.remove('drv_libxml2')
                return feedparser.parse(url)
            else:
                raise

    def buscaTorrent(self, direcc):  # PARA NEWPCT1
        '''
        Funcion que obtiene la url torrent del la dirreccion que recibe,
        hay que tener en cuenta que la url que recibe es la del feed
        y que no es la apgina que contiene el torrent, pero como todas tienen
        la misma forma se modifica la url poniendole descarga-torrent

        :param str direcc: Dirreccion de la pagina web que contiene el torrent

        :return str: Nos devuelve el string con la url del torrent
        '''

        session = requests.session()
        page = session.get(direcc.replace(
            'newpct1.com/', 'newpct1.com/descarga-torrent/'), verify=False).text
        sopa = BeautifulSoup(page, 'html.parser')

        return sopa.find('div', {"id": "tab1"}).a['href']

    def buscaTorrentAntiguo(self, direcc):  # para newpct
        '''
        Funcion que obtiene la url torrent del la dirreccion que recibe

        :param str direcc: Dirreccion de la pagina web que contiene el torrent

        :return str: Nos devuelve el string con la url del torrent
        '''

        session = requests.session()
        page = session.get(direcc, verify=False).text
        sopa = BeautifulSoup(page, 'html.parser')

        return sopa.find('span', id="content-torrent").a['href']


def main():
    MiFormulario(dbSeries=ruta_db)


if __name__ == '__main__':
    main()
