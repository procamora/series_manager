#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""

import sys
import time
from typing import NoReturn

from PyQt5 import QtWidgets, QtCore
from app.views.ui.descarga_completa_ui import Ui_Dialog

import app.controller.Controller as Controller
from app import logger
from app.models.model_preferences import Preferences
from app.models.model_query import Query
from app.utils import funciones
from app.utils.telegram2 import Telegram


# https://gist.github.com/kaotika/e8ca5c340ec94f599fb2

class Mythread(QtCore.QThread):
    total = QtCore.pyqtSignal(object)
    update = QtCore.pyqtSignal()

    def __init__(self, parent: QtWidgets.QProgressBar, serie: str, capitulo: int, temporada: int,
                 text_edit: QtWidgets.QTextEdit, send_tg: bool) -> NoReturn:
        super(Mythread, self).__init__(parent)

        preferences: Query = Controller.get_database_configuration(self.db)
        self.preferences: Preferences = preferences.response[0]
        self.serie = serie.replace(' ', '-')  # ruta correcta
        self.cap = capitulo
        self.temp = temporada
        self.textEdit = text_edit
        self.sendTg = send_tg
        if send_tg:
            self.telegram = Telegram('33063767')

        self.url = 'http://torrentlocura.com/descargar-seriehd/{}/capitulo-{}{}/hdtv-720p-ac3-5-1/'
        self.url2 = 'http://torrentlocura.com/serie/{}/capitulo-{}{}/hdtv-720p-ac3-5-1/'

    def run(self) -> NoReturn:
        self.total.emit(int(self.cap))
        for i in range(1, self.cap + 1):
            self.update.emit()
            # if len(str(i)) != 2:
            #    i = '0{}'.format(i)
            # else:
            i = str(i)
            time.sleep(0.2)
            try:
                fichero = f'{self.preferences.path_download}/{self.serie}_{self.temp}x{i}.torrent'
                # al ser un or si la primera retorna true no comprueba la segunda
                if self.try_get_url(self.url, i, fichero) or self.try_get_url(self.url2, i, fichero):
                    if self.sendTg:
                        self.telegram.send_file(fichero)
                        # fichero = '{}/{}x{}.torrent'.format(ruta, self.serie, i)
                    self.textEdit.append(f'{self.serie} {self.temp}x{i}')
                else:
                    self.textEdit.append(f'No encontrada: {self.serie} {self.temp}x{i}')
            except Exception as e:
                logger.error('FALLO DESCONOCIDO!!', e)
                self.textEdit.append(f"Error:{str(e)}")
                raise

        logger.info("fin")

    def try_get_url(self, url: str, capitulo: str, fichero: str) -> bool:
        url_format = url.format(self.serie, self.temp, capitulo)
        logger.debug(url_format)
        try:
            # FIXME ARREGLAR Y PONER UNA FUNCION VALIDA
            url_torrent = funciones.get_url_torrent_dontorrent(url_format)
            logger.debug(url_format)
            logger.debug(capitulo, "Bien: ", url_torrent)

            if url_torrent is None:
                return False

            funciones.download_file(url_torrent, fichero)
            return True

        except Exception as e:
            logger.error("fallo: ", url_format, e, file=sys.stderr)
            return False


class TorrentlocuraCompleta(QtWidgets.QDialog):
    def __init__(self, parent: object = None) -> NoReturn:
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.other = 'otra'  # campo otra del formulario
        self.send_tg = False

        self.n = 0
        self.ui.progressBar.setValue(self.n)
        self.setWindowTitle('Descargar Serie Completa')

        self.list_seasons(1, 6)
        self.list_chapters()

        self.ui.lineTemp.hide()
        self.ui.lineCap.hide()

        self.ui.lineTemp.setText(str(self.ui.BoxTemporada.currentText()))
        self.ui.lineCap.setText(str(self.ui.BoxCapitulos.currentText()))

        self.ui.BoxTemporada.activated.connect(self.field_season)
        self.ui.BoxCapitulos.activated.connect(self.field_chapter)

        self.ui.pushButtonAplicar.clicked.connect(self.apply)
        self.ui.pushButtonCerrar.clicked.connect(self.close)
        self.ui.checkBoxTg.clicked.connect(self.check_tg)

    def check_tg(self) -> NoReturn:
        if self.ui.checkBoxTg.isChecked():
            self.send_tg = True
        else:
            self.send_tg = False

    def update(self) -> NoReturn:
        self.n += 1
        logger.debug(self.n)
        self.ui.progressBar.setValue(self.n)

    def field_season(self) -> NoReturn:
        """
        Si en la lista de temporadas seleccionamos otra se abre un line edit para poner el numero de temporada que 
        no esta, si lo cambiamos se oculta
        """

        if self.ui.BoxTemporada.currentText() == self.other:
            self.ui.lineTemp.setEnabled(True)
            self.ui.lineTemp.setVisible(True)
            self.ui.lineTemp.setText('')
        else:
            self.ui.lineTemp.setEnabled(False)
            self.ui.lineTemp.setVisible(False)
            self.ui.lineTemp.setText(str(self.ui.BoxTemporada.currentText()))

    def field_chapter(self) -> NoReturn:
        """
        Si en la lista de temporadas seleccionamos otra se abre un line edit para poner el numero de temporada que 
        no esta, si lo cambiamos se oculta
        """

        if self.ui.BoxCapitulos.currentText() == self.other:
            self.ui.lineCap.setEnabled(True)
            self.ui.lineCap.setVisible(True)
            self.ui.lineCap.setText('')
        else:
            self.ui.lineCap.setEnabled(False)
            self.ui.lineCap.setVisible(False)
            self.ui.lineCap.setText(str(self.ui.BoxCapitulos.currentText()))

    def list_seasons(self, x, y) -> NoReturn:
        """
        Crea el comboBox de las temporadas, primero lo vacia y luego lo crea con los rangos que le indico
        """

        list_temp = list()
        for i in range(x, y):
            list_temp.append(str(i))

        self.ui.BoxTemporada.clear()
        self.ui.BoxTemporada.addItems(list_temp)
        self.ui.BoxTemporada.addItem(self.other)

    def list_chapters(self) -> NoReturn:
        """
        Crea el comboBox de las temporadas, primero lo vacia y luego lo crea con los rangos que le indico
        """

        list_cap = list()
        list_cap.append('10')
        list_cap.append('12')
        list_cap.append('13')
        list_cap.append('22')
        list_cap.append('23')
        list_cap.append('24')

        self.ui.BoxCapitulos.clear()
        self.ui.BoxCapitulos.addItems(list_cap)
        self.ui.BoxCapitulos.addItem(self.other)

    def apply(self) -> NoReturn:
        """
        Recoge todos los valores que necesita, crea el update y lo ejecuta
        """

        self.ui.textEdit.clear()
        self.n = 0

        if len(str(self.ui.lineTitulo.text())) != 0:
            serie = str(self.ui.lineTitulo.text()).lower().replace(' ', '-')
            capitulo = int(self.ui.lineCap.text())
            temporada = int(self.ui.lineTemp.text())

            thread = Mythread(self.ui.progressBar, serie, capitulo, temporada, self.ui.textEdit, self.send_tg)
            thread.total.connect(self.ui.progressBar.setMaximum)
            thread.update.connect(self.update)
            # thread.finished.connect(self.close)
            thread.start()
            logger.info("final thread")
        else:
            self.ui.textEdit.append('Introduce una nombre')

    @staticmethod
    def get_data(parent: object = None) -> NoReturn:
        dialog = TorrentlocuraCompleta(parent)
        dialog.exec_()


def main():
    app = QtWidgets.QApplication(sys.argv)
    TorrentlocuraCompleta.get_data()
    return app


# si hay internet ejecutar sino dar un aviso
if __name__ == '__main__':
    main()
