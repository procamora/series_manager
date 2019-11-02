#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

"""
import sys
from typing import NoReturn, List

from PyQt5 import QtWidgets, QtCore
from app.views.ui.descarga_automatica_ui import Ui_Dialog

import app.controller.Controller as Controller
from app.models.model_query import Query
from app.models.model_serie import Serie
from app.utils import funciones
from app.utils.descarga_automatica_cli import DescargaAutomaticaCli
from app.views.msgbox import MsgBox


# https://gist.github.com/kaotika/e8ca5c340ec94f599fb2


class Mythread(QtCore.QThread, DescargaAutomaticaCli):
    total = QtCore.pyqtSignal(object)
    update = QtCore.pyqtSignal()

    def __init__(self, parent: QtWidgets.QProgressBar, obj_descargas: QtWidgets.QTextEdit) -> NoReturn:
        super(Mythread, self).__init__(parent)
        self.objDescargas = obj_descargas

    def run(self) -> NoReturn:
        # para saber cuantas series tiene en la barra de progreso (ajustarla y que marque bien los porcentajes)
        self.total.emit(len(self.get_series()))
        DescargaAutomaticaCli.run(self)

    def extra_action(self, serie: str) -> NoReturn:
        self.objDescargas.append(serie)

    def parser_feed(self, serie: Serie) -> str:
        """Solo funciona con series de 2 digitos por la expresion regular"""
        self.update.emit()
        serie = DescargaAutomaticaCli.parser_feed(self, serie)
        return serie


class DescargaAutomatica(QtWidgets.QDialog):
    def __init__(self, parent: object = None) -> NoReturn:
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.otra = 'otra'  # campo otra del formulario
        self.estadoI = 'Ok'  # estado inicial
        self.n: int = 0
        self.setWindowTitle('Descarga automatica de newpct1')
        self.ui.progressBar.setValue(self.n)

        # variable de acceso compartido, no se como hacerlo de otra forma
        DescargaAutomatica.notificaciones = DescargaAutomaticaCli.show_notifications()
        response_query: Query = Controller.get_series_follow()
        self.series: List[Serie] = response_query.response

        # si le doy a ok cierro la ventana
        self.ui.pushButtonCerrar.clicked.connect(self.close)

        self.thread = Mythread(self.ui.progressBar, self.ui.textEditDescargadas)
        self.thread.total.connect(self.ui.progressBar.setMaximum)
        self.thread.update.connect(self.update)
        self.thread.finished.connect(self.close)
        self.thread.start()

    def update(self) -> NoReturn:
        self.ui.textEditVistas.append(self.series[self.n].title)
        self.n += 1
        self.ui.progressBar.setValue(self.n)

    @staticmethod
    def get_data(parent: object = None) -> NoReturn:
        if funciones.internet_on():
            dialog = DescargaAutomatica(parent)
            dialog.exec_()
        else:
            dat = {'title': 'Error de internet', 'text': 'No hay internet'}
            MsgBox.get_data(datos=dat)


def main():
    app = QtWidgets.QApplication(sys.argv)
    DescargaAutomatica.get_data()
    return app


if __name__ == '__main__':
    main()
