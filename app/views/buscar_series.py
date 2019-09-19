#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from typing import NoReturn

from PyQt5 import QtWidgets
from app.views.ui.buscar_series_ui import Ui_Dialog

from app import logger
from app.modulos.connect_sqlite import conection_sqlite
from app.modulos.settings import ruta_db
from app.views.actualizar_insertar import ActualizarInsertar


class BuscarSeries(QtWidgets.QDialog):
    def __init__(self, parent: object = None, database: str = None) -> NoReturn:
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.state_ok = 'Ok'  # estado inicial
        self.state_cancel = 'Cancelado'  # final
        self.state_current = self.state_ok  # actual
        self.db = database

        self.setWindowTitle('Buscador de series')

        self.ui.pushButtonBuscar.clicked.connect(self.initial_operations)
        self.ui.pushButtonAplicar.clicked.connect(self.update_serie)
        self.ui.pushButtonCerrar.clicked.connect(self.cancel)

    def initial_operations(self) -> NoReturn:
        """
        Busca todas las series que haya con el patron buscado y crea una lista
        para seleccionar posteriormente una %% es para escapar el tanto por ciento
        y que funcione en el string
        """

        self.ui.listWidget.clear()

        query = 'SELECT Nombre FROM Series WHERE Nombre LIKE "%%{}%%"'.format(
            self.ui.lineEdit.text())
        response_query = conection_sqlite(self.db, query, True)

        if len(response_query) == 0:
            item = QtWidgets.QListWidgetItem()
            item.setText('Serie no encontrada')
            self.ui.listWidget.addItem(item)

        else:
            for i in response_query:
                item = QtWidgets.QListWidgetItem()
                item.setText(i['Nombre'])
                self.ui.listWidget.addItem(item)

    def update_serie(self) -> NoReturn:
        """
        cojo la serie escogida, saco todos sus datos y se los mando a la libreria
        de actualizar_insertar serie
        """

        for i in self.ui.listWidget.selectedItems():
            logger.debug((i.text()))

            query = 'SELECT * FROM Series WHERE Nombre LIKE "{}"'.format(
                i.text())
            response_query = conection_sqlite(self.db, query, True)[0]

            ActualizarInsertar.get_data(
                data_serie=response_query, database=self.db)

    def cancel(self) -> NoReturn:
        """
        Establece el estado actual en cancelado para retornar None y ejecuta reject
        """

        self.state_current = self.state_cancel
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
