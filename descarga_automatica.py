#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

"""
import sys

from PyQt5 import QtWidgets, QtCore

from modulos.connect_sqlite import conectionSQLite, ejecutaScriptSqlite
from ui.descarga_automatica_ui import Ui_Dialog
import msgbox
import descarga_automatica_cli
from modulos.settings import modo_debug, directorio_trabajo, ruta_db
import funciones


# https://gist.github.com/kaotika/e8ca5c340ec94f599fb2


class mythread(QtCore.QThread, descarga_automatica_cli.DescargaAutomaticaCli):
    total = QtCore.pyqtSignal(object)
    update = QtCore.pyqtSignal()

    def __init__(self, parent, objVistas, objDescargas, dbSeries=None, query=None):
        super(mythread, self).__init__(parent)
        self.objVistas = objVistas
        self.objDescargas = objDescargas
        self.db = dbSeries
        self.query = query

    def run(self):
        # para saber cuantas series tiene en la barra de progreso (ajustarla y que marque bien los porcentajes)
        self.total.emit(len(self.getSeries()))
        descarga_automatica_cli.DescargaAutomaticaCli.run(self)

    def accionExtra(self, serie):
        self.objDescargas.append(serie)

    def parseaFeed(self, serie, tem, cap, vose):
        """Solo funciona con series de 2 digitos por la expresion regular"""

        self.update.emit()
        serie = descarga_automatica_cli.DescargaAutomaticaCli.parseaFeed(self, serie, tem, cap, vose)

        return serie


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
        DescargaAutomatica.notificaciones = descarga_automatica_cli.DescargaAutomaticaCli.muestraNotificaciones()

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
        self.ui.progressBar.setValue(self.n)

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
