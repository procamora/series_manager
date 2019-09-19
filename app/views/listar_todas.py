#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from typing import NoReturn

from PyQt5 import QtWidgets
from app.views.ui.listar_todas_ui import Ui_Dialog

from app import logger
from app.modulos.connect_sqlite import conection_sqlite, execute_script_sqlite
from app.modulos.settings import ruta_db


class ListarTodas(QtWidgets.QDialog):
    def __init__(self, parent: object = None, database: str = None) -> NoReturn:
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.state_ok = 'Ok'  # estado inicial
        self.state_cancel = 'Cancelado'  # final
        self.state_current = self.state_ok  # actual
        self.db = database

        # lista de consultas que se ejecutaran al final
        self.queryCompleta = str()

        self.setWindowTitle('Modificaciones en masa')
        # esto permite selecionar multiples
        self.ui.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.seriesTest = list(dict())
        self.get_all_series()

        self.ui.radioButtonAct.clicked.connect(self.series_actuals)
        self.ui.radioButtonTemp.clicked.connect(self.series_finished_season)
        self.ui.radioButtonPausada.clicked.connect(self.series_stopped)
        self.ui.radioButtonTodas.clicked.connect(self.series_all)
        self.ui.pushButtonRefresh.clicked.connect(self.get_all_series)

        self.ui.pushButtonAnadir.clicked.connect(self.print_current_items)

        self.ui.pushButtonAplicar.clicked.connect(self.apply_data)
        self.ui.pushButtonCerrar.clicked.connect(self.cancela)
        self.ui.pushButtonAceptar.clicked.connect(self.accept_data)

    def get_all_series(self) -> NoReturn:
        """
        Saca todas las series de la bd y las mete en una lista de diccionarios accesible en todo el objeto
        """
        query = 'SELECT * FROM Series ORDER BY Nombre'
        self.seriesTest = conection_sqlite(self.db, query, True)
        self.ui.radioButtonAct.setChecked(True)
        # lo ejecuto al principio ya que es el activado por defecto
        self.series_actuals()

    def series_actuals(self) -> NoReturn:
        """
        Creo una lista con todas las series que estoy siguiendo
        """

        self.ui.listWidget.clear()
        for i in self.seriesTest:
            if i['Siguiendo'] == 'Si' and i['Capitulo'] != 0 and i['Estado'] == 'Activa':
                item = QtWidgets.QListWidgetItem()
                item.setText(i['Nombre'])
                self.ui.listWidget.addItem(item)

    def series_finished_season(self) -> NoReturn:
        """
        Creo una lista con todas las series que han acabado temporada
        """

        self.ui.listWidget.clear()
        for i in self.seriesTest:
            if i['Capitulo'] == 0:
                item = QtWidgets.QListWidgetItem()
                item.setText(i['Nombre'])
                self.ui.listWidget.addItem(item)

    def series_stopped(self) -> NoReturn:
        """
        Creo una lista con todas las series que han acabado temporada
        """

        self.ui.listWidget.clear()
        for i in self.seriesTest:
            if i['Estado'] == 'Pausada':
                item = QtWidgets.QListWidgetItem()
                item.setText(i['Nombre'])
                self.ui.listWidget.addItem(item)

    def series_all(self) -> NoReturn:
        """
        Creo una lista con todas las series
        """

        self.ui.listWidget.clear()
        for i in self.seriesTest:
            item = QtWidgets.QListWidgetItem()
            item.setText(i['Nombre'])
            self.ui.listWidget.addItem(item)

    def print_current_items(self) -> NoReturn:
        """
        Coge todas las series seleccionadas y las mete en una lista con su respectiva consulta para despues ejecutarlas
        """

        for i in self.ui.listWidget.selectedItems():
            if self.ui.radioButtonAcabaT.isChecked():
                query = """UPDATE series SET Temporada=Temporada+1, Capitulo="00", Estado="En Espera" WHERE Nombre
                    LIKE "{}";\n""".format(i.text())
                self.queryCompleta += query

            elif self.ui.radioButtonEmpieza.isChecked():
                query = 'UPDATE series SET Capitulo="01", Estado="Activa" WHERE Nombre LIKE "{}";\n'.format(
                    i.text())
                self.queryCompleta += query

            elif self.ui.radioButtonEspera.isChecked():
                query = 'UPDATE series SET Estado="Pausada" WHERE Nombre LIKE "{}";\n'.format(
                    i.text())
                self.queryCompleta += query

            elif self.ui.radioButtonFinalizada.isChecked():
                query = 'UPDATE series SET Estado="Finalizada", Acabada="Si" WHERE Nombre LIKE "{}";\n'.format(
                    i.text())
                self.queryCompleta += query

        logger.debug(self.queryCompleta)

    def apply_data(self) -> bool:
        """
        Ejecuta todas las consultas que hay en la lista
        """

        logger.debug(self.queryCompleta)

        execute_script_sqlite(self.db, self.queryCompleta)

        self.queryCompleta = str()
        return True

    def cancela(self) -> NoReturn:
        """
        Establece el estado actual en cancelado para retornar None y ejecuta reject
        """

        self.state_current = self.state_cancel
        self.reject()

    def accept_data(self) -> NoReturn:
        if self.apply_data():
            self.accept()

    @staticmethod
    def get_data(parent: object = None, database: str = None) -> NoReturn:
        dialog = ListarTodas(parent, database)
        dialog.exec_()


def main():
    app = QtWidgets.QApplication(sys.argv)
    ListarTodas.get_data(database=ruta_db)
    return app


if __name__ == '__main__':
    main()
# hacer boton actualizar_insertar series
# cuando haga un cabio actualizar_insertar series
