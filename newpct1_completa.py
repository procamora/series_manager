#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''

'''

import sys
import requests
import time

from abrt_exception_handler3 import send
from bs4 import BeautifulSoup
from PyQt5 import QtWidgets, QtCore

from ui.descarga_completa_ui import Ui_Dialog
from modulos.settings import modo_debug
from modulos.telegram2 import TG2
import funciones


# https://gist.github.com/kaotika/e8ca5c340ec94f599fb2

class mythread(QtCore.QThread):
    total = QtCore.pyqtSignal(object)
    update = QtCore.pyqtSignal()

    def __init__(self, parent, serie, capitulo, temporada, textEdit, sendTg):
        super(mythread, self).__init__(parent)
        self.conf = funciones.dbConfiguarion()
        self.serie = serie
        self.cap = capitulo
        self.temp = temporada
        self.textEdit = textEdit
        self.sendTg = sendTg
        if sendTg:
            self.telegram = TG2('33063767')

        self.url = 'http://tumejortorrent.com/descargar-seriehd/{}/capitulo-{}{}/hdtv-720p-ac3-5-1/'
        self.url2 = 'http://tumejortorrent.com/serie/{}/capitulo-{}{}/hdtv-720p-ac3-5-1/'

    def run(self):
        ruta = self.conf['RutaDescargas']
        self.total.emit(int(self.cap))
        for i in range(1, self.cap + 1):
            self.update.emit()
            #if len(str(i)) != 2:
            #    i = '0{}'.format(i)
            #else:
            i = str(i)
            time.sleep(0.2)
            try:
                fichero = '{}/{}_{}x{}.torrent'.format(ruta, self.serie, self.temp, i)
                try:  # si falla la primera url probamos con la segunda
                    if modo_debug:
                        print(self.url.format(self.serie, self.temp, i))
                        print(i, "Bien: ", self.descargaTorrent(self.url.format(self.serie, self.temp, i)))
                    funciones.descargaFichero(self.descargaTorrent(self.url.format(self.serie, self.temp, i)), fichero)
                except:
                    if modo_debug:
                       print(i, "Mal: ", self.descargaTorrent(self.url2.format(self.serie, self.temp, i)))
                    funciones.descargaFichero(self.descargaTorrent(self.url2.format(self.serie,self.temp, i)), fichero)

                if self.sendTg:
                    self.telegram.sendFile(fichero)
                    # fichero = '{}/{}x{}.torrent'.format(ruta, self.serie, i)
                self.textEdit.append('{} {}x{}'.format(self.serie, self.temp, i))

            except Exception as e:
                print(e)
                self.textEdit.append(str(e))

    def descargaTorrent(self, direcc):  # PARA NEWPCT1
        '''
        Funcion que obtiene la url torrent del la dirreccion que recibe

        :param str direcc: Dirreccion de la pagina web que contiene el torrent

        :return str: Nos devuelve el string con la url del torrent
        '''

        session = requests.session()
        page = session.get(direcc, verify=False).text
        # page = urllib.urlopen(direcc).read()
        sopa = BeautifulSoup(page, 'html.parser')
        print(sopa.find_all("a", class_="btn-torrent"))
        return sopa.find_all("a", class_="btn-torrent")[0]['href']


class MiFormulario(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.Otra = 'Otra'  # campo otra del formulario
        self.envioTg = False

        self.n = 0
        self.ui.progressBar.setValue(self.n)
        self.setWindowTitle('Descargar Serie Completa')

        self.listaTemporadas(1, 6)
        self.listaCapitulos()

        self.ui.lineTemp.hide()
        self.ui.lineCap.hide()

        self.ui.lineTemp.setText(str(self.ui.BoxTemporada.currentText()))
        self.ui.lineCap.setText(str(self.ui.BoxCapitulos.currentText()))

        self.ui.BoxTemporada.activated.connect(self.CampoTemporada)
        self.ui.BoxCapitulos.activated.connect(self.CampoCapitulos)

        self.ui.pushButtonAplicar.clicked.connect(self.AplicaCambios)
        self.ui.pushButtonCerrar.clicked.connect(self.close)
        self.ui.checkBoxTg.clicked.connect(self.checkTg)

    def checkTg(self):
        if self.ui.checkBoxTg.isChecked():
            self.envioTg = True
        else:
            self.envioTg = False

    def update(self):
        # self.ui.textEdit.append('{} {}x{}'.format(str(self.ui.lineTitulo.text()).lower().replace(' ', '-'), str(self.ui.lineTemp.text()), self.n+1))
        self.n += 1
        if modo_debug:
            pass
        # sprint((self.n))
        self.ui.progressBar.setValue(self.n)

    def CampoTemporada(self):
        '''
        Si en la lista de temporadas seleccionamos Otra se abre un line edit para poner el numero de temporada que no esta, si lo cambiamos se oculta
        '''

        if self.ui.BoxTemporada.currentText() == self.Otra:
            self.ui.lineTemp.setEnabled(True)
            self.ui.lineTemp.setVisible(True)
            self.ui.lineTemp.setText('')
        else:
            self.ui.lineTemp.setEnabled(False)
            self.ui.lineTemp.setVisible(False)
            self.ui.lineTemp.setText(str(self.ui.BoxTemporada.currentText()))

    def CampoCapitulos(self):
        '''
        Si en la lista de temporadas seleccionamos Otra se abre un line edit para poner el numero de temporada que no esta, si lo cambiamos se oculta
        '''

        if self.ui.BoxCapitulos.currentText() == self.Otra:
            self.ui.lineCap.setEnabled(True)
            self.ui.lineCap.setVisible(True)
            self.ui.lineCap.setText('')
        else:
            self.ui.lineCap.setEnabled(False)
            self.ui.lineCap.setVisible(False)
            self.ui.lineCap.setText(str(self.ui.BoxCapitulos.currentText()))

    def listaTemporadas(self, x, y):
        '''
        Crea el comboBox de las temporadas, primero lo vacia y luego lo crea con los rangos que le indico
        '''

        listTemp = list()
        for i in range(x, y):
            listTemp.append(str(i))

        self.ui.BoxTemporada.clear()
        self.ui.BoxTemporada.addItems(listTemp)
        self.ui.BoxTemporada.addItem(self.Otra)

    def listaCapitulos(self):
        '''
        Crea el comboBox de las temporadas, primero lo vacia y luego lo crea con los rangos que le indico
        '''

        listCap = list()
        listCap.append('10')
        listCap.append('12')
        listCap.append('13')
        listCap.append('22')
        listCap.append('23')
        listCap.append('24')

        self.ui.BoxCapitulos.clear()
        self.ui.BoxCapitulos.addItems(listCap)
        self.ui.BoxCapitulos.addItem(self.Otra)

    def AplicaCambios(self):
        '''
        Recoge todos los valores que necesita, crea el update y lo ejecuta
        '''

        self.ui.textEdit.clear()
        self.n = 0

        if len(str(self.ui.lineTitulo.text())) != 0:
            serie = str(self.ui.lineTitulo.text()).lower().replace(' ', '-')
            capitulo = int(self.ui.lineCap.text())
            temporada = int(self.ui.lineTemp.text())

            self.thread = mythread(self.ui.progressBar, serie, capitulo, temporada, self.ui.textEdit, self.envioTg)
            self.thread.total.connect(self.ui.progressBar.setMaximum)
            self.thread.update.connect(self.update)
            # self.thread.finished.connect(self.close)
            self.thread.start()
        else:
            self.ui.textEdit.append('Introduce una nombre')

    @staticmethod
    def getDatos(parent=None):
        dialog = MiFormulario(parent)
        dialog.exec_()


def main():
    app = QtWidgets.QApplication(sys.argv)
    MiFormulario.getDatos()
    return app


# si hay internet ejecutar sino dar un aviso
if __name__ == '__main__':
    main()
