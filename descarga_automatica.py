#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''

'''
import sys
import time
import re
import os

import requests
import feedparser
from bs4 import BeautifulSoup
from PyQt5 import QtWidgets, QtCore

from ui.descarga_automatica_ui import Ui_Dialog
import msgbox
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
    queryN = 'SELECT * FROM Notificaciones'
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
                api_ml3 =	api_ml3

    return Datos

global notificaciones
notificaciones = MuestraNotificaciones()

#https://gist.github.com/kaotika/e8ca5c340ec94f599fb2

class mythread(QtCore.QThread):

    total = QtCore.pyqtSignal(object)
    update = QtCore.pyqtSignal()

    def __init__(self, parent, objVistas, objDescargas, dbSeries=None, query=None):
        super(mythread, self).__init__(parent)
        self.objVistas = objVistas
        self.objDescargas = objDescargas
        self.db = dbSeries
        self.listaNotificaciones = str()
        self.actualizaDia = str()
        self.query = query
        self.conf = funciones.dbConfiguarion()
        urlNew = self.conf['UrlFeedNewpct']
        urlShow = self.conf['UrlFeedShowrss']

        self.capDescargado = dict()	# Diccionario de series y capitulos para actualizar la bd con el capitulo descargado
        self.consultaUpdate = str()

        try:
            self.feedNew = feedparser.parse(urlNew)
        except: #Para el fallo en fedora
            self.feedNew = self.__feedparser_parse(urlNew)

        try:
            self.feedShow = feedparser.parse(urlShow)
        except: #Para el fallo en fedora
            self.feedShow = self.__feedparser_parse(urlShow)


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

        series =  conectionSQLite(self.db, self.query, True)

        # para saber cuantas series tiene en la barra de progreso
        # (ajustarla y que maque bien los porcentajes)
        self.total.emit(len(series))
        SerieActualNew = str()
        SerieActualShow = str()
        SerieActualTemp = str()

        for i in series:
            self.update.emit()
            try:
                if modo_debug:
                    print('####################################')
                    print(i['Nombre'])
                    print('####################################')
                SerieActualTemp = self.ParseaFeed(i['Nombre'], i['Temporada'], i['Capitulo'], i['VOSE'])
                if i['VOSE'] == 'Si':
                    SerieActualShow = SerieActualTemp
                else:
                    SerieActualNew = SerieActualTemp
            except Exception as e:
                print('FALLO: ', e)

        print(self.ultimaSerieNew)
        if len(self.ultimaSerieNew) != 0:# or len(self.ultimaSerieShow) != 0:
            #print self.actualizaDia
            ejecutaScriptSqlite(self.db, self.actualizaDia)  #actualiza los dias en los que sale el capitulo

            for notif in notificaciones:
                if notif['Activo'] == 'True':
                    if notif['Nombre'] == 'Telegram':
                        tg3.sendTg(self.listaNotificaciones)
                    elif notif['Nombre'] == 'Pushbullet':
                        pb3.sendTextPb('Gestor series', self.listaNotificaciones)
                    elif notif['Nombre'] == 'Email':
                        ml3.sendMail(api_ml3, self.listaNotificaciones)

        #capitulos que descargo
        for i in self.capDescargado.items():
            #print (i)
            query = 'UPDATE Series SET Capitulo_Descargado={} WHERE Nombre LIKE "{}";\n'.format(str(i[1]), i[0])
            self.consultaUpdate += query

        print (self.consultaUpdate)
        ejecutaScriptSqlite(self.db, self.consultaUpdate) #actualiza el ultimo capitulo que he descargado

        #Guardar ultima serie del feed
        if SerieActualShow is not None and SerieActualNew is not None:
            with open('{}/{}'.format(self.rutlog, fichNewpct), 'w') as f:
                pass
                f.write(SerieActualNew)
            with open('{}/{}'.format(self.rutlog, fichShowrss), 'w') as f:
                pass
                f.write(SerieActualShow)
        else:
            print('PROBLEMA CON if SerieActualShow is not None and SerieActualNew is not None:')


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
            cap = '0'+str(cap)


        for i in d.entries:
            if i.title == ultimaSerie:	#cuando llegamos al ultimo capitulo pasamos a la siguiente serie
                # retornamos el valor que luego usaremos en ultima serie para guardarlo en el fichero
                return d.entries[0].title

            regex_vose = '(?i){} {}.*'.format(self.__escapaParentesis(serie.lower()), tem)
            regex_cast = '(?i){}( \(Proper\))? - Temporada( )?\d+ \[HDTV 720p?\]\[Cap\.{}\d+(_\d+)?\]\[A.*'.format(self.__escapaParentesis(serie.lower()), tem)

            if modo_debug:
                #print(i.title)
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
                        f.write('{} {}\n'.format(time.strftime('%Y%m%d'), i.title))

                    if vose == 'Si':
                        self.objDescargas.append(i.title)
                        # creo un string para solo mandar una notificacion
                        self.listaNotificaciones += '\n{}'.format(i.title)
                    else:
                        varNom = i.title.split('-')[0]
                        varEpi = i.title.split('][')[1]
                        self.objDescargas.append('{} {}'.format(varNom, varEpi))
                        # creo un string para solo mandar una notificacion
                        self.listaNotificaciones += '\n{} {}'.format(varNom, varEpi)

                    funciones.descargaFichero(torrent, r'{}/{}.torrent'.format(ruta, i.title))
                    self.actualizaDia += '''\nUPDATE series SET Dia="{}" WHERE Nombre LIKE "{}";'''.format(funciones.calculaDiaSemana(), serie)

                    #Diccionario con todos los capitulos descargados, para actualizar la bd con los capitulos por donde voy
                    capituloActual = int(re.sub('Cap\.{}'.format(tem), '', varEpi)) # regex para coger el capitulo unicamente
                    if serie not in self.capDescargado:
                        self.capDescargado[serie] = capituloActual
                    else:
                        if self.capDescargado[serie] < capituloActual:		###########REVISAR, CREO QUE ESTA MAL NO ES 4X05 ES 405
                            self.capDescargado[serie] = capituloActual

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


    def buscaTorrent(self, direcc): #PARA NEWPCT1
        '''
        Funcion que obtiene la url torrent del la dirreccion que recibe,
        hay que tener en cuenta que la url que recibe es la del feed
        y que no es la apgina que contiene el torrent, pero como todas tienen
        la misma forma se modifica la url poniendole descarga-torrent

        :param str direcc: Dirreccion de la pagina web que contiene el torrent

        :return str: Nos devuelve el string con la url del torrent
        '''

        session = requests.session()
        page = session.get(direcc.replace('newpct1.com/', 'newpct1.com/descarga-torrent/'), verify=False).text
        sopa = BeautifulSoup(page, 'html.parser')

        return sopa.find('div', {"id": "tab1"}).a['href']


    def buscaTorrentAntiguo(self, direcc): # para newpct
        '''
        Funcion que obtiene la url torrent del la dirreccion que recibe

        :param str direcc: Dirreccion de la pagina web que contiene el torrent

        :return str: Nos devuelve el string con la url del torrent
        '''

        session = requests.session()
        page = session.get(direcc, verify=False).text
        sopa = BeautifulSoup(page, 'html.parser')

        return sopa.find('span',id="content-torrent").a['href']


class MiFormulario(QtWidgets.QDialog):
    def __init__(self, parent=None, dbSeries=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.Otra = 'Otra'  # campo otra del formulario
        self.EstadoI = 'Ok' # estado inicial
        self.n = 0
        self.db = dbSeries
        self.setWindowTitle('Descarga automatica de newpct1')
        self.ui.progressBar.setValue(self.n)

        query = '''SELECT Nombre, Temporada, Capitulo, VOSE FROM Series WHERE Siguiendo = "Si" ORDER BY Nombre ASC'''
        self.series =  conectionSQLite(self.db, query, True)

        self.ui.pushButtonCerrar.clicked.connect(self.close)    # si le doy a ok cierro la ventana

        self.thread = mythread(self.ui.progressBar, self.ui.textEditVistas, self.ui.textEditDescargadas, self.db, query)
        self.thread.total.connect(self.ui.progressBar.setMaximum)
        self.thread.update.connect(self.update)
        self.thread.finished.connect(self.close)
        self.thread.start()


    def update(self):
        self.ui.textEditVistas.append(str(self.series[self.n]['Nombre']))
        self.n += 1
        if modo_debug:
            print((self.n))
        self.ui.progressBar.setValue(self.n)


    @staticmethod
    def getDatos(parent=None, dbSeries=None):
        if funciones.internetOn():
            dialog = MiFormulario(parent, dbSeries)
            dialog.exec_()
        else:
            dat = {'title':'Error de internet', 'text': 'No hay internet'}
            msgbox.MiFormulario.getData(datos=dat)


def main():
    app = QtWidgets.QApplication(sys.argv)
    MiFormulario.getDatos(dbSeries=ruta_db)
    return app


if __name__ == '__main__':
    main()
