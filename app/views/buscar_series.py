#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from typing import NoReturn

from PyQt5 import QtWidgets
from app.views.ui.buscar_series_ui import Ui_Dialog

import app.controller.Controller as Controller
from app import logger
from app.models.model_query import Query
from app.views.actualizar_insertar import ActualizarInsertar


class BuscarSeries(QtWidgets.QDialog):
    def __init__(self, parent: object = None) -> NoReturn:
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.state_ok = 'Ok'  # estado inicial
        self.state_cancel = 'Cancelado'  # final
        self.state_current = self.state_ok  # actual

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
        response_query: Query = Controller.get_series_name(self.ui.lineEdit.text())

        if response_query.is_empty():
            item = QtWidgets.QListWidgetItem()
            item.setText('Serie no encontrada')
            self.ui.listWidget.addItem(item)

        else:
            for i in response_query.response:
                item = QtWidgets.QListWidgetItem()
                item.setText(i.title)
                self.ui.listWidget.addItem(item)

    def update_serie(self) -> NoReturn:
        """
        cojo la serie escogida, saco todos sus datos y se los mando a la libreria
        de actualizar_insertar serie
        """

        for i in self.ui.listWidget.selectedItems():
            logger.debug((i.text()))

            response_query: Query = Controller.get_series_name(i.text())
            ActualizarInsertar.get_data(data_serie=response_query.response[0])

    def cancel(self) -> NoReturn:
        """
        Establece el estado actual en cancelado para retornar None y ejecuta reject
        """

        self.state_current = self.state_cancel
        self.reject()

    @staticmethod
    def get_data(parent: object = None) -> NoReturn:
        dialog = BuscarSeries(parent)
        dialog.exec_()


def main():
    app = QtWidgets.QApplication(sys.argv)
    BuscarSeries.get_data()
    return app


if __name__ == '__main__':
    main()
