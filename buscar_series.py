#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

from PyQt5 import QtWidgets

from ui.buscar_series_ui import Ui_Dialog
import actualizar_insertar
from modulos.connect_sqlite import conectionSQLite
from modulos.settings import modo_debug, ruta_db


class MiFormulario(QtWidgets.QDialog):

    def __init__(self, parent=None, dbSeries=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.EstadoI = 'Ok'  # estado inicial
        self.EstadoF = 'Cancelado'  # final
        self.EstadoA = self.EstadoI  # actual
        self.db = dbSeries

        self.setWindowTitle('Buscador de series')

        self.ui.pushButtonBuscar.clicked.connect(self.__operacionesIniciales)
        self.ui.pushButtonAplicar.clicked.connect(self.__actualizaSerie)
        self.ui.pushButtonCerrar.clicked.connect(self.__cancela)

    def __operacionesIniciales(self):
        '''
        Busca todas las series que haya con el patron buscado y crea una lista
        para seleccionar posteriormente una %% es para escapar el tanto por ciento
        y que funcione en el string
        '''

        self.ui.listWidget.clear()

        query = 'SELECT Nombre FROM Series WHERE Nombre LIKE "%%{}%%"'.format(
            self.ui.lineEdit.text())
        self.seriesTest = conectionSQLite(self.db, query, True)

        if len(self.seriesTest) == 0:
            item = QtWidgets.QListWidgetItem()
            item.setText('Serie no encontrada')
            self.ui.listWidget.addItem(item)

        else:
            for i in self.seriesTest:
                item = QtWidgets.QListWidgetItem()
                item.setText(i['Nombre'])
                self.ui.listWidget.addItem(item)

    def __actualizaSerie(self):
        '''
        cojo la serie escogida, saco todos sus datos y se los mando a la libreria
        de actualizar_insertar serie
        '''

        for i in self.ui.listWidget.selectedItems():
            if modo_debug:
                print((i.text()))

            query = 'SELECT * FROM Series WHERE Nombre LIKE "{}"'.format(
                i.text())
            ser = conectionSQLite(self.db, query, True)[0]

            actualizar_insertar.MiFormulario.getDatos(
                datSerie=ser, dbSeries=self.db)

    def __cancela(self):
        '''
        Establece el estado actual en cancelado para retornar None y ejecuta reject
        '''

        self.EstadoA = self.EstadoF
        self.reject()

    @staticmethod
    def getDatos(parent=None, dbSeries=None):
        dialog = MiFormulario(parent, dbSeries)
        dialog.exec_()


def main():
    app = QtWidgets.QApplication(sys.argv)
    MiFormulario.getDatos(dbSeries=ruta_db)
    return app


if __name__ == '__main__':
    main()
