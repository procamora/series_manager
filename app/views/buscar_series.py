#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from typing import NoReturn

from PyQt5 import QtWidgets
from app.views.ui.buscar_series_ui import Ui_Dialog

from app import logger
from app.modulos.connect_sqlite import conectionSQLite
from app.modulos.settings import ruta_db
from app.views.actualizar_insertar import ActualizarInsertar


class BuscarSeries(QtWidgets.QDialog):
    def __init__(self, parent: object = None, database: str = None) -> NoReturn:
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.EstadoI = 'Ok'  # estado inicial
        self.EstadoF = 'Cancelado'  # final
        self.EstadoA = self.EstadoI  # actual
        self.db = database

        self.setWindowTitle('Buscador de series')

        self.ui.pushButtonBuscar.clicked.connect(self.operacionesIniciales)
        self.ui.pushButtonAplicar.clicked.connect(self.actualizaSerie)
        self.ui.pushButtonCerrar.clicked.connect(self.cancela)

    def operacionesIniciales(self) -> NoReturn:
        """
        Busca todas las series que haya con el patron buscado y crea una lista
        para seleccionar posteriormente una %% es para escapar el tanto por ciento
        y que funcione en el string
        """

        self.ui.listWidget.clear()

        query = 'SELECT Nombre FROM Series WHERE Nombre LIKE "%%{}%%"'.format(
            self.ui.lineEdit.text())
        seriesTest = conectionSQLite(self.db, query, True)

        if len(seriesTest) == 0:
            item = QtWidgets.QListWidgetItem()
            item.setText('Serie no encontrada')
            self.ui.listWidget.addItem(item)

        else:
            for i in seriesTest:
                item = QtWidgets.QListWidgetItem()
                item.setText(i['Nombre'])
                self.ui.listWidget.addItem(item)

    def actualizaSerie(self) -> NoReturn:
        """
        cojo la serie escogida, saco todos sus datos y se los mando a la libreria
        de actualizar_insertar serie
        """

        for i in self.ui.listWidget.selectedItems():
            logger.debug((i.text()))

            query = 'SELECT * FROM Series WHERE Nombre LIKE "{}"'.format(
                i.text())
            ser = conectionSQLite(self.db, query, True)[0]

            ActualizarInsertar.get_data(
                data_serie=ser, database=self.db)

    def cancela(self) -> NoReturn:
        """
        Establece el estado actual en cancelado para retornar None y ejecuta reject
        """

        self.EstadoA = self.EstadoF
        self.reject()

    @staticmethod
    def get_data(parent: object = None, database: str = None) -> NoReturn:
        dialog = BuscarSeries(parent, database)
        dialog.exec_()


def main():
    app = QtWidgets.QApplication(sys.argv)
    BuscarSeries.get_data(database=ruta_db)
    return app


if __name__ == '__main__':
    main()
