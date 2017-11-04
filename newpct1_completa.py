#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""

import sys
import time

from PyQt5 import QtWidgets, QtCore

from modulos import funciones
from modulos.settings import modo_debug
from modulos.telegram2 import TG2
from ui.descarga_completa_ui import Ui_Dialog


# https://gist.github.com/kaotika/e8ca5c340ec94f599fb2

class mythread(QtCore.QThread):
    total = QtCore.pyqtSignal(object)
    update = QtCore.pyqtSignal()

    def __init__(self, parent, serie, capitulo, temporada, textEdit, sendTg):
        super(mythread, self).__init__(parent)

        self.conf = funciones.dbConfiguarion()
        self.serie = serie.replace(' ', '-') # ruta correcta
        self.cap = capitulo
        self.temp = temporada
        self.textEdit = textEdit
        self.sendTg = sendTg
        if sendTg:
            self.telegram = TG2('33063767')

        self.url = 'http://torrentlocura.com/descargar-seriehd/{}/capitulo-{}{}/hdtv-720p-ac3-5-1/'
        self.url2 = 'http://torrentlocura.com/serie/{}/capitulo-{}{}/hdtv-720p-ac3-5-1/'

    def run(self):
        ruta = self.conf['RutaDescargas']
        self.total.emit(int(self.cap))
        for i in range(1, self.cap + 1):
            self.update.emit()
            # if len(str(i)) != 2:
            #    i = '0{}'.format(i)
            # else:
            i = str(i)
            time.sleep(0.2)
            try:
                fichero = '{}/{}_{}x{}.torrent'.format(ruta, self.serie, self.temp, i)
                # al ser un or si la primera retorna true no comprueba la segunda
                if(self.tryGetUrl(self.url, i, fichero) or self.tryGetUrl(self.url2, i, fichero)):
                    if self.sendTg:
                        self.telegram.sendFile(fichero)
                        # fichero = '{}/{}x{}.torrent'.format(ruta, self.serie, i)
                    self.textEdit.append('{} {}x{}'.format(self.serie, self.temp, i))
                else:
                    self.textEdit.append('No encontrada: {} {}x{}'.format(self.serie, self.temp, i))
                    
                if modo_debug:
                    print()

            except Exception as e:
                print('FALLO DESCONOCIDO!!', e)
                self.textEdit.append("Error:{}".format(str(e)))
                raise

        print("fin")

    def tryGetUrl(self, url, capitulo, fichero):
        urlFormat = url.format(self.serie, self.temp, capitulo)
        if modo_debug:
            print(urlFormat)
        try:
            urlTorrent = funciones.descargaUrlTorrent(urlFormat)
            if modo_debug:
                print(urlFormat)
                print(capitulo, "Bien: ", urlTorrent)

            if (urlTorrent is None):
                return False

            funciones.descargaFichero(urlTorrent, fichero)
            return True

        except Exception as e:
            print("fallo: ", urlFormat, e, file=sys.stderr)
            return False



class torrentlocuraCompleta(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.Otra = 'otra'  # campo otra del formulario
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

        self.ui.BoxTemporada.activated.connect(self.campoTemporada)
        self.ui.BoxCapitulos.activated.connect(self.campoCapitulos)

        self.ui.pushButtonAplicar.clicked.connect(self.aplicaCambios)
        self.ui.pushButtonCerrar.clicked.connect(self.close)
        self.ui.checkBoxTg.clicked.connect(self.checkTg)

    def checkTg(self):
        if self.ui.checkBoxTg.isChecked():
            self.envioTg = True
        else:
            self.envioTg = False

    def update(self):
        self.n += 1
        if modo_debug:
            print(self.n)
        self.ui.progressBar.setValue(self.n)

    def campoTemporada(self):
        """
        Si en la lista de temporadas seleccionamos otra se abre un line edit para poner el numero de temporada que 
        no esta, si lo cambiamos se oculta
        """

        if self.ui.BoxTemporada.currentText() == self.Otra:
            self.ui.lineTemp.setEnabled(True)
            self.ui.lineTemp.setVisible(True)
            self.ui.lineTemp.setText('')
        else:
            self.ui.lineTemp.setEnabled(False)
            self.ui.lineTemp.setVisible(False)
            self.ui.lineTemp.setText(str(self.ui.BoxTemporada.currentText()))

    def campoCapitulos(self):
        """
        Si en la lista de temporadas seleccionamos otra se abre un line edit para poner el numero de temporada que 
        no esta, si lo cambiamos se oculta
        """

        if self.ui.BoxCapitulos.currentText() == self.Otra:
            self.ui.lineCap.setEnabled(True)
            self.ui.lineCap.setVisible(True)
            self.ui.lineCap.setText('')
        else:
            self.ui.lineCap.setEnabled(False)
            self.ui.lineCap.setVisible(False)
            self.ui.lineCap.setText(str(self.ui.BoxCapitulos.currentText()))

    def listaTemporadas(self, x, y):
        """
        Crea el comboBox de las temporadas, primero lo vacia y luego lo crea con los rangos que le indico
        """

        listTemp = list()
        for i in range(x, y):
            listTemp.append(str(i))

        self.ui.BoxTemporada.clear()
        self.ui.BoxTemporada.addItems(listTemp)
        self.ui.BoxTemporada.addItem(self.Otra)

    def listaCapitulos(self):
        """
        Crea el comboBox de las temporadas, primero lo vacia y luego lo crea con los rangos que le indico
        """

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

    def aplicaCambios(self):
        """
        Recoge todos los valores que necesita, crea el update y lo ejecuta
        """

        self.ui.textEdit.clear()
        self.n = 0

        if len(str(self.ui.lineTitulo.text())) != 0:
            serie = str(self.ui.lineTitulo.text()).lower().replace(' ', '-')
            capitulo = int(self.ui.lineCap.text())
            temporada = int(self.ui.lineTemp.text())

            thread = mythread(self.ui.progressBar, serie, capitulo, temporada, self.ui.textEdit, self.envioTg)
            thread.total.connect(self.ui.progressBar.setMaximum)
            thread.update.connect(self.update)
            # thread.finished.connect(self.close)
            thread.start()
            print("final thread")
        else:
            self.ui.textEdit.append('Introduce una nombre')

    @staticmethod
    def getDatos(parent=None):
        dialog = torrentlocuraCompleta(parent)
        dialog.exec_()


def main():
    app = QtWidgets.QApplication(sys.argv)
    torrentlocuraCompleta.getDatos()
    return app


# si hay internet ejecutar sino dar un aviso
if __name__ == '__main__':
    main()
