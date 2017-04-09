#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

"""
import sys
import time
import re
import os

import feedparser
from PyQt5 import QtWidgets, QtCore

from ui.descarga_automatica_ui import Ui_Dialog
import msgbox
from modulos.connect_sqlite import conectionSQLite, ejecutaScriptSqlite
from modulos.pushbullet2 import PB2
from modulos.telegram2 import TG2
from modulos.settings import modo_debug, directorio_trabajo, ruta_db
import funciones


# https://gist.github.com/kaotika/e8ca5c340ec94f599fb2


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

        # Diccionario de series y capitulos para actualizar la bd con el capitulo descargado
        self.capDescargado = dict()
        self.consultaUpdate = str()
        self.rutlog = str()

        try:
            self.feedNew = feedparser.parse(urlNew)
        except TypeError:  # Para el fallo en fedora
            self.feedNew = funciones.feedParser(urlNew)

        try:
            self.feedShow = feedparser.parse(urlShow)
        except TypeError:  # Para el fallo en fedora
            self.feedShow = funciones.feedParser(urlShow)

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

        # para saber cuantas series tiene en la barra de progreso (ajustarla y que marque bien los porcentajes)
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
                SerieActualTemp = self.parseaFeed(i['Nombre'], i['Temporada'], i['Capitulo'], i['VOSE'])
                if i['VOSE'] == 'Si':
                    SerieActualShow = SerieActualTemp
                else:
                    SerieActualNew = SerieActualTemp
            except Exception as e:
                print('FALLO: {}'.format(i['Nombre']), e)

        if len(self.ultimaSerieNew) != 0:  # or len(self.ultimaSerieShow) != 0:
            print(self.actualizaDia)
            # actualiza los dias en los que sale el capitulo
            ejecutaScriptSqlite(self.db, self.actualizaDia)

            for notif in DescargaAutomatica.notificaciones:
                if notif['Activo'] == 'True':
                    if notif['Nombre'] == 'Telegram':
                        DescargaAutomatica.tg3.sendTg(self.listaNotificaciones)
                    elif notif['Nombre'] == 'Pushbullet':
                        DescargaAutomatica.pb3.sendTextPb('Gestor series', self.listaNotificaciones)

        # capitulos que descargo
        for i in self.capDescargado.items():
            # print (i)
            query = 'UPDATE Series SET Capitulo_Descargado={} WHERE Nombre LIKE "{}";\n'.format(str(i[1]), i[0])
            self.consultaUpdate += query

        print(self.consultaUpdate)
        # actualiza el ultimo capitulo que he descargado
        ejecutaScriptSqlite(self.db, self.consultaUpdate)

        # Guardar ultima serie del feed
        if SerieActualShow is not None and SerieActualNew is not None:
            with open('{}/{}'.format(self.rutlog, fichNewpct), 'w') as f:
                f.write(SerieActualNew)
            with open('{}/{}'.format(self.rutlog, fichShowrss), 'w') as f:
                f.write(SerieActualShow)
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
            # cuando llegamos al ultimo capitulo pasamos a la siguiente serie
            if i.title == ultimaSerie:
                # retornamos el valor que luego usaremos en ultima serie para guardarlo en el fichero
                return d.entries[0].title

            regex_vose = '(?i){} {}.*'.format(funciones.escapaParentesis(serie.lower()), tem)
            regex_cast = '(?i){}( \(Proper\))? - Temporada( )?\d+ \[HDTV 720p?\]\[Cap\.{}\d+(_\d+)?\]\[A.*'.format(
                funciones.escapaParentesis(serie.lower()), tem)

            if modo_debug:
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
                    torrent = funciones.descargaUrlTorrent(i.link)

                if not os.path.exists('{}{}.torrent'.format(ruta, i.title)):
                    ficheroDescargas = self.conf['FicheroDescargas']

                    with open('{}/{}'.format(self.rutlog, ficheroDescargas), 'a') as f:
                        f.write('{} {}\n'.format(time.strftime('%Y%m%d'), i.title))

                    if vose == 'Si':
                        self.objDescargas.append(i.title)
                        # creo un string para solo mandar una notificacion
                        self.listaNotificaciones += '\n{}'.format(i.title)
                    else:
                        # En pelis que son VOSE no se si da fallo, esto solo es para no VOSE
                        varNom = i.title.split('-')[0]
                        varEpi = i.title.split('][')[1]
                        self.objDescargas.append('{} {}'.format(varNom, varEpi))
                        # creo un string para solo mandar una notificacion
                        self.listaNotificaciones += '\n{} {}'.format(varNom, varEpi)

                    funciones.descargaFichero(torrent, r'{}/{}.torrent'.format(ruta, i.title))
                    # Diccionario con todos los capitulos descargados, para actualizar la bd con los capitulos por
                    # donde voy regex para coger el capitulo unicamente
                    self.actualizaDia += """\nUPDATE series SET Dia="{}" WHERE Nombre LIKE "{}";""".format(
                        funciones.calculaDiaSemana(), serie)

                    capituloActual = varEpi[-2:]  # mas eficiente, el otro metodo falla con multiples series: 206_209
                    # capituloActual = int(re.sub('Cap\.{}'.format(tem), '', varEpi))
                    if serie not in self.capDescargado:
                        self.capDescargado[serie] = capituloActual
                    else:
                        # REVISAR, CREO QUE ESTA MAL NO ES 4X05 ES 405
                        if self.capDescargado[serie] < capituloActual:
                            self.capDescargado[serie] = capituloActual

        return d.entries[0].title


class DescargaAutomatica(QtWidgets.QDialog):
    def __init__(self, parent=None, dbSeries=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.otra = 'otra'  # campo otra del formulario
        self.estadoI = 'Ok'  # estado inicial
        self.n = 0
        self.db = dbSeries
        self.setWindowTitle('Descarga automatica de newpct1')
        self.ui.progressBar.setValue(self.n)

        # variable de acceso compartido, no se como hacerlo de otra forma
        DescargaAutomatica.notificaciones = self.muestraNotificaciones()

        query = """SELECT Nombre, Temporada, Capitulo, VOSE FROM Series WHERE Siguiendo = "Si" ORDER BY Nombre ASC"""
        self.series = conectionSQLite(self.db, query, True)

        # si le doy a ok cierro la ventana
        self.ui.pushButtonCerrar.clicked.connect(self.close)

        self.thread = mythread(self.ui.progressBar, self.ui.textEditVistas, self.ui.textEditDescargadas, self.db, query)
        self.thread.total.connect(self.ui.progressBar.setMaximum)
        self.thread.update.connect(self.update)
        self.thread.finished.connect(self.close)
        self.thread.start()

    def update(self):
        self.ui.textEditVistas.append(str(self.series[self.n]['Nombre']))
        self.n += 1
        if modo_debug:
            print(self.n)
        self.ui.progressBar.setValue(self.n)

    def muestraNotificaciones(self):
        """
        poner las api de la base de datos
        """
        queryN = 'SELECT * FROM Notificaciones'
        Datos = conectionSQLite(ruta_db, queryN, True)

        global tg3, pb3, ml3, api_ml3

        for i in Datos:
            if i['Activo'] == 'True':
                if i['Nombre'] == 'Telegram':
                    DescargaAutomatica.tg3 = TG2(i['API'])

                elif i['Nombre'] == 'Pushbullet':
                    DescargaAutomatica.pb3 = PB2(i['API'])

        return Datos

    @staticmethod
    def getDatos(parent=None, dbSeries=None):
        if funciones.internetOn():
            dialog = DescargaAutomatica(parent, dbSeries)
            dialog.exec_()
        else:
            dat = {'title': 'Error de internet', 'text': 'No hay internet'}
            msgbox.MsgBox.getData(datos=dat)


def main():
    app = QtWidgets.QApplication(sys.argv)
    DescargaAutomatica.getDatos(dbSeries=ruta_db)
    return app


if __name__ == '__main__':
    main()
