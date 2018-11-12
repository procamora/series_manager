#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
# Como ha dejado de funcionar el feed de torrentlocura he creado uno nuevo haciendo scraping web de la pagina de ultimos capitulos

"""
import os
import re
import time

import feedparser
import requests
from bs4 import BeautifulSoup

from modulos import funciones
from modulos.connect_sqlite import conectionSQLite, ejecutaScriptSqlite
from modulos.mail2 import ML2
from modulos.pushbullet2 import PB2
from modulos.settings import modo_debug, directorio_trabajo, ruta_db
from modulos.telegram2 import TG2


SERIE_DEBUG="The Flashd"

# https://gist.github.com/kaotika/e8ca5c340ec94f599fb2

class feed:
    def __init__(self, title, link):
        self.title = title
        self.link = link

        epiList = re.findall('Temporada \d+ Capitulo \d+', title)
        lista = re.findall('\d+', epiList[0])

        self.name = title.split('-')[0]
        self.temp = lista[0]
        self.epi = lista[1]
        self.cap = "{}x{}".format(self.temp, self.epi)


class feedparserPropio:
    def __init__(self):
        self.entries = list()

    def add(self, title, link):
        f = feed(title.strip(), link)
        self.entries.append(f)

    @staticmethod
    def parse(url='http://torrentlocura.com/ultimas-descargas/', category='1469', dat='Semana'):
        """
        category='1469' series en hd
        """
        formdata = {'categoryIDR': category, 'date': dat }
        req_headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0', 'Content-Type': 'application/x-www-form-urlencoded' }

        session = requests.session()
        login = session.post(url, data=formdata, headers=req_headers, verify=False)

        sopa = BeautifulSoup(login.text, 'html.parser')
        #sopa = BeautifulSoup(fichero, 'html.parser')
        result = sopa.findAll('ul', {"class": "noticias-series"})


        f = feedparserPropio()
        for ul in result:
            for li in ul.findAll('li'):
                f.add(li.a['title'], li.a['href'])

        #for i in f.entries:
        #    print(i.title)
        #    print(i.cap)
        #    print()

        return f


class DescargaAutomaticaCli():
    def __init__(self, dbSeries=None):
        if funciones.internetOn():
            if dbSeries is None:  # en herencia no mando ruta
                self.db = ruta_db
            else:
                self.db = dbSeries

            self.notificaciones = self.muestraNotificaciones()  # variable publica

            self.query = """SELECT Nombre, Temporada, Capitulo, VOSE FROM Series WHERE Siguiendo = "Si"
                          ORDER BY Nombre ASC"""
            self.series = conectionSQLite(self.db, self.query, True)

            self.listaNotificaciones = str()
            self.actualizaDia = str()
            self.conf = funciones.dbConfiguarion()

            urlNew = self.conf['UrlFeedNewpct']
            urlShow = self.conf['UrlFeedShowrss']

            # Diccionario con las series y capitulos para actualizar la bd el capitulo descargado
            self.capDescargado = dict()
            self.consultaUpdate = str()
            self.rutlog = str()

            self.feedNew = feedparserPropio.parse()
            """
            try:
                self.feedNew = feedparser.parse(urlNew)
            except TypeError:  # Para el fallo en fedora
                self.feedNew = funciones.feedParser(urlNew)
            """

            try:
                self.feedShow = feedparser.parse(urlShow)
            except TypeError:  # Para el fallo en fedora
                self.feedShow = funciones.feedParser(urlShow)

            self.consultaSeries = conectionSQLite(self.db, self.query, True)

    def run(self):
        SerieActualNew = str()
        SerieActualShow = str()
        SerieActualTemp = str()

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

        for i in self.consultaSeries:
            try:
                print(('Revisa: {}'.format(funciones.eliminaTildes(i['Nombre']))))
                SerieActualTemp = self.parseaFeed(
                    i['Nombre'], i['Temporada'], i['Capitulo'], i['VOSE'])
                if i['VOSE'] == 'Si':
                    SerieActualShow = SerieActualTemp
                else:
                    SerieActualNew = SerieActualTemp
            except Exception as e:
                print('################' ,i['Nombre'], ' FALLO: ', e)

        if len(self.ultimaSerieNew) != 0:  # or len(self.ultimaSerieShow) != 0:
            #print(self.actualizaDia)
            # actualiza los dias en los que sale el capitulo
            ejecutaScriptSqlite(self.db, self.actualizaDia)

            for notif in self.notificaciones:
                if notif['Activo'] == 'True':
                    if notif['Nombre'] == 'Telegram':
                        tg3.sendTg(self.listaNotificaciones)
                    elif notif['Nombre'] == 'Pushbullet':
                        pb3.sendTextPb('Gestor series', self.listaNotificaciones)

        # capitulos que descargo
        for i in self.capDescargado.items():
            query = 'UPDATE Series SET Capitulo_Descargado={} WHERE Nombre LIKE "{}";\n'.format(str(i[1]), i[0])
            self.consultaUpdate += query

        print(self.consultaUpdate)
        # actualiza el ultimo capitulo que he descargado
        ejecutaScriptSqlite(self.db, self.consultaUpdate)

        # Guardar ultima serie del feed
        if SerieActualShow is not None and SerieActualNew is not None:
            with open('{}/{}'.format(self.rutlog, fichNewpct), 'w') as f:
                f.write(funciones.eliminaTildes(SerieActualNew))
            with open('{}/{}'.format(self.rutlog, fichShowrss), 'w') as f:
                f.write(funciones.eliminaTildes(SerieActualShow))
        else:
            print('PROBLEMA CON if SerieActualShow is not None and SerieActualNew is not None:')

    def parseaFeed(self, serie, tem, cap, vose):
        """Solo funciona con series de 2 digitos por la expresion regular"""
        cap = str(cap)
        ruta = str(self.conf['RutaDescargas'])  # es unicode
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
            self.titleSerie = funciones.eliminaTildes(i.title)
            # cuando llegamos al ultimo capitulo pasamos a la siguiente serie
            #print(self.titleSerie, ".........", ultimaSerie, ".FIN")
            if self.titleSerie == ultimaSerie:
                # retornamos el valor que luego usaremos en ultima serie para guardarlo en el fichero
                return funciones.eliminaTildes(d.entries[0].title) #FIXME DESCOMENTAR

            regex_vose = '(?i){} ({}|{}|{}).*'.format(funciones.escapaParentesis(serie.lower()), tem, tem+1, tem+2)
            #regex_cast = '(?i){}( \(Proper\))?( )*- Temporada( )?\d+ \[HDTV 720p?\]\[Cap\.({}|{}|{})\d+(_\d+)?\]\[A.*'.format(
            regex_cast = '(?i){}.*Temporada( )?({}|{}|{}).*Capitulo( )?\d+.*'.format(
                funciones.escapaParentesis(serie.lower()), tem, tem+1, tem+2)

            if serie.lower() == SERIE_DEBUG.lower():
                print(regex_cast, self.titleSerie)
                print(i.link)

            estado = False
            if vose == 'Si':
                if re.search(regex_vose, self.titleSerie):
                    estado = True
            else:
                if re.search(regex_cast, self.titleSerie):
                    estado = True

            if estado:
                titleSerie = self.titleSerie # conversion necesaria para usar como str
                if vose == 'Si':
                    torrent = i.link
                else:
                    torrent = funciones.descargaUrlTorrent(i.link)

                try: # arreglar problema codificacion de algunas series
                    print(titleSerie)
                except:
                    titleSerie = titleSerie.replace(u"\uFFFD", "?")

                if not os.path.exists(u'{}{}.torrent'.format(ruta, titleSerie)):
                    ficheroDescargas = self.conf['FicheroDescargas']
                    with open('{}/{}'.format(self.rutlog, ficheroDescargas), 'a') as f:
                        f.write('{} {}\n'.format(time.strftime('%Y%m%d'), titleSerie))

                    if vose == 'Si':
                        self.accionExtra(titleSerie)
                        # creo un string para solo mandar una notificacion
                        self.listaNotificaciones += '{}\n'.format(titleSerie)
                    else:
                        self.accionExtra('{} {}'.format(i.name, i.cap))
                        # creo un string para solo mandar una notificacion
                        self.listaNotificaciones += '{} {}\n'.format(i.name, i.cap)

                    funciones.descargaFichero(torrent, r'{}/{}.torrent'.format(ruta, str(titleSerie)))
                    # Diccionario con todos los capitulos descargados, para actualizar la bd con los capitulos por
                    # donde voy regex para coger el capitulo unicamente
                    self.actualizaDia += """\nUPDATE series SET Dia="{}" WHERE Nombre LIKE "{}";""".format(
                        funciones.calculaDiaSemana(), serie)

                    self.capDescargado[serie] = i.epi
                   
                print(('DESCARGANDO: {}'.format(serie)))

        return funciones.eliminaTildes(d.entries[0].title)

    def accionExtra(self, serie):
        """
        Metodo que no hace nada en esta clase pero que en herencia es
        usado para usar el entorno ggrafico que QT
        :return:
        """
        pass

    def getSeries(self):
        return self.consultaSeries

    def getSerieActual(self):
        return self.titleSerie

    @staticmethod
    def muestraNotificaciones():
        """
        poner las api de la base de datos
        """
        queryN = 'SELECT * FROM notificaciones'
        Datos = conectionSQLite(ruta_db, queryN, True)

        global tg3, pb3, ml3, api_ml3
        print(Datos)
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




def main():
    DescargaAutomaticaCli(dbSeries=ruta_db).run()
    #feedparserPropio.parse()


if __name__ == '__main__':
    main()
