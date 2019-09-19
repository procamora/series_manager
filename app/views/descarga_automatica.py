#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

"""
import sys
from typing import NoReturn

from PyQt5 import QtWidgets, QtCore
from app.views.ui.descarga_automatica_ui import Ui_Dialog

from app.modulos import funciones
from app.modulos.connect_sqlite import conection_sqlite
from app.modulos.settings import ruta_db
from app.views.descarga_automatica_cli import DescargaAutomaticaCli
from app.views.msgbox import MsgBox


# https://gist.github.com/kaotika/e8ca5c340ec94f599fb2


class Mythread(QtCore.QThread, DescargaAutomaticaCli):
    total = QtCore.pyqtSignal(object)
    update = QtCore.pyqtSignal()

    def __init__(self, parent: QtWidgets.QProgressBar, obj_vistas: QtWidgets.QTextEdit,
                 obj_descargas: QtWidgets.QTextEdit, database: str = None, query: str = None) -> NoReturn:
        super(Mythread, self).__init__(parent)
        self.objVistas = obj_vistas
        self.objDescargas = obj_descargas
        self.db = database
        self.query = query

    def run(self) -> NoReturn:
        # para saber cuantas series tiene en la barra de progreso (ajustarla y que marque bien los porcentajes)
        self.total.emit(len(self.get_series()))
        DescargaAutomaticaCli.run(self)

    def extra_action(self, serie: str) -> NoReturn:
        self.objDescargas.append(serie)

    def parser_feed(self, serie: str, tem: str, cap: str, vose: str) -> str:
        """Solo funciona con series de 2 digitos por la expresion regular"""

        self.update.emit()
        serie = DescargaAutomaticaCli.parser_feed(self, serie, tem, cap, vose)

        return serie


class DescargaAutomatica(QtWidgets.QDialog):
    def __init__(self, parent: object = None, database: str = None) -> NoReturn:
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.otra = 'otra'  # campo otra del formulario
        self.estadoI = 'Ok'  # estado inicial
        self.n = 0
        self.db = database
        self.setWindowTitle('Descarga automatica de newpct1')
        self.ui.progressBar.setValue(self.n)

        # variable de acceso compartido, no se como hacerlo de otra forma
        DescargaAutomatica.notificaciones = DescargaAutomaticaCli.show_notifications()

        query = """SELECT Nombre, Temporada, Capitulo, VOSE FROM Series WHERE Siguiendo = "Si" ORDER BY Nombre ASC"""
        self.series = conection_sqlite(self.db, query, True)

        # si le doy a ok cierro la ventana
        self.ui.pushButtonCerrar.clicked.connect(self.close)

        self.thread = Mythread(self.ui.progressBar, self.ui.textEditVistas, self.ui.textEditDescargadas, self.db, query)
        self.thread.total.connect(self.ui.progressBar.setMaximum)
        self.thread.update.connect(self.update)
        self.thread.finished.connect(self.close)
        self.thread.start()

    def update(self) -> NoReturn:
        self.ui.textEditVistas.append(str(self.series[self.n]['Nombre']))
        self.n += 1
        self.ui.progressBar.setValue(self.n)

    @staticmethod
    def get_data(parent: object = None, database: str = None) -> NoReturn:
        if funciones.internet_on():
            dialog = DescargaAutomatica(parent, database)
            dialog.exec_()
        else:
            dat = {'title': 'Error de internet', 'text': 'No hay internet'}
            MsgBox.get_data(datos=dat)


def main():
    app = QtWidgets.QApplication(sys.argv)
    DescargaAutomatica.get_data(database=ruta_db)
    return app


if __name__ == '__main__':
    main()
