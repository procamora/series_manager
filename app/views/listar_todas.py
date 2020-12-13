#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from typing import NoReturn, List

from PyQt5 import QtWidgets
from app.views.ui.listar_todas_ui import Ui_Dialog

import app.controller.Controller as Controller
from app.models.model_query import Query
from app.models.model_serie import Serie


class ListarTodas(QtWidgets.QDialog):
    def __init__(self, parent: object = None) -> NoReturn:
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.state_ok = 'Ok'  # estado inicial
        self.state_cancel = 'Cancelado'  # final
        self.state_current = self.state_ok  # actual

        # lista de consultas que se ejecutaran al final
        self.queryCompleta: str = str()

        self.setWindowTitle('Modificaciones en masa')
        # esto permite selecionar multiples
        self.ui.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.series: List[Serie] = list()
        self.get_all_series()

        self.ui.radioButtonAct.clicked.connect(self.series_actuals)
        self.ui.radioButtonTemp.clicked.connect(self.series_finished_season)
        self.ui.radioButtonPausada.clicked.connect(self.series_stopped)
        self.ui.radioButtonTodas.clicked.connect(self.series_all)
        self.ui.pushButtonRefresh.clicked.connect(self.get_all_series)

        self.ui.pushButtonAnadir.clicked.connect(self.print_current_items)

        self.ui.pushButtonAplicar.clicked.connect(self.apply_data)
        self.ui.pushButtonCerrar.clicked.connect(self.cancel)
        self.ui.pushButtonAceptar.clicked.connect(self.accept_data)

    def get_all_series(self) -> NoReturn:
        """
        Saca todas las series de la bd y las mete en una lista de diccionarios accesible en todo el objeto
        """
        response_query: Query = Controller.get_series_all('ORDER BY Nombre')
        self.series = response_query.response

        self.ui.radioButtonAct.setChecked(True)
        # lo ejecuto al principio ya que es el activado por defecto
        self.series_actuals()

    def series_actuals(self) -> NoReturn:
        """
        Creo una lista con todas las series que estoy siguiendo
        """

        self.ui.listWidget.clear()
        for serie in self.series:
            if serie.following and serie.chapter != 0 and serie.state == 'Activa':
                item = QtWidgets.QListWidgetItem()
                item.setText(serie.title)
                self.ui.listWidget.addItem(item)

    def series_finished_season(self) -> NoReturn:
        """
        Creo una lista con todas las series que han acabado temporada
        """

        self.ui.listWidget.clear()
        for serie in self.series:
            if serie.chapter == 0:
                item = QtWidgets.QListWidgetItem()
                item.setText(serie.title)
                self.ui.listWidget.addItem(item)

    def series_stopped(self) -> NoReturn:
        """
        Creo una lista con todas las series que han acabado temporada
        """

        self.ui.listWidget.clear()
        for serie in self.series:
            if serie.state == 'Pausada':
                item = QtWidgets.QListWidgetItem()
                item.setText(serie.title)
                self.ui.listWidget.addItem(item)

    def series_all(self) -> NoReturn:
        """
        Creo una lista con todas las series
        """

        self.ui.listWidget.clear()
        for serie in self.series:
            item = QtWidgets.QListWidgetItem()
            item.setText(serie.title)
            self.ui.listWidget.addItem(item)

    def print_current_items(self) -> NoReturn:
        """
        Coge todas las series seleccionadas y las mete en una lista con su respectiva consulta para despues ejecutarlas
        """
        test = [title.text() for title in self.ui.listWidget.selectedItems()]
        self.queryCompleta += Controller.update_list_series(test, self.ui.radioButtonAcabaT.isChecked(),
                                                            self.ui.radioButtonEmpieza.isChecked(),
                                                            self.ui.radioButtonEspera.isChecked(),
                                                            self.ui.radioButtonFinalizada.isChecked())

    def apply_data(self) -> bool:
        """
        Ejecuta todas las consultas que hay en la lista
        """
        Controller.execute_query_script_sqlite(self.queryCompleta)
        self.queryCompleta = str()
        return True

    def cancel(self) -> NoReturn:
        """
        Establece el estado actual en cancelado para retornar None y ejecuta reject
        """

        self.state_current = self.state_cancel
        self.reject()

    def accept_data(self) -> NoReturn:
        if self.apply_data():
            self.accept()

    @staticmethod
    def get_data(parent: object = None) -> NoReturn:
        dialog = ListarTodas(parent)
        dialog.exec_()


def main():
    app = QtWidgets.QApplication(sys.argv)
    ListarTodas.get_data()
    return app


if __name__ == '__main__':
    main()
# hacer boton actualizar_insertar series
# cuando haga un cabio actualizar_insertar series
