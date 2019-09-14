#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from typing import NoReturn

from PyQt5 import QtWidgets

from app import logger
from app.modulos.connect_sqlite import conectionSQLite, ejecutaScriptSqlite
from app.modulos.settings import ruta_db
from app.views.ui.listar_todas_ui import Ui_Dialog


class ListarTodas(QtWidgets.QDialog):
    def __init__(self, parent: object = None, dbSeries: str = None) -> NoReturn:
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.estadoI = 'Ok'  # estado inicial
        self.estadoF = 'Cancelado'  # final
        self.estadoA = self.estadoI  # actual
        self.db = dbSeries

        # lista de consultas que se ejecutaran al final
        self.queryCompleta = str()

        self.setWindowTitle('Modificaciones en masa')
        # esto permite selecionar multiples
        self.ui.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.seriesTest = list(dict())
        self.sacaSeries()

        self.ui.radioButtonAct.clicked.connect(self.seriesActuales)
        self.ui.radioButtonTemp.clicked.connect(self.seriesTemporales)
        self.ui.radioButtonPausada.clicked.connect(self.seriesPausadas)
        self.ui.radioButtonTodas.clicked.connect(self.seriesTodas)
        self.ui.pushButtonRefresh.clicked.connect(self.sacaSeries)

        self.ui.pushButtonAnadir.clicked.connect(self.printCurrentItems)

        self.ui.pushButtonAplicar.clicked.connect(self.aplicaDatos)
        self.ui.pushButtonCerrar.clicked.connect(self.cancela)
        self.ui.pushButtonAceptar.clicked.connect(self.aceptaDatos)

    def sacaSeries(self) -> NoReturn:
        """
        Saca todas las series de la bd y las mete en una lista de diccionarios accesible en todo el objeto
        """
        query = 'SELECT * FROM Series ORDER BY Nombre'
        self.seriesTest = conectionSQLite(self.db, query, True)
        self.ui.radioButtonAct.setChecked(True)
        # lo ejecuto al principio ya que es el activado por defecto
        self.seriesActuales()

    def seriesActuales(self) -> NoReturn:
        """
        Creo una lista con todas las series que estoy siguiendo
        """

        self.ui.listWidget.clear()
        for i in self.seriesTest:
            if i['Siguiendo'] == 'Si' and i['Capitulo'] != 0 and i['Estado'] == 'Activa':
                item = QtWidgets.QListWidgetItem()
                item.setText(i['Nombre'])
                self.ui.listWidget.addItem(item)

    def seriesTemporales(self) -> NoReturn:
        """
        Creo una lista con todas las series que han acabado temporada
        """

        self.ui.listWidget.clear()
        for i in self.seriesTest:
            if i['Capitulo'] == 0:
                item = QtWidgets.QListWidgetItem()
                item.setText(i['Nombre'])
                self.ui.listWidget.addItem(item)

    def seriesPausadas(self) -> NoReturn:
        """
        Creo una lista con todas las series que han acabado temporada
        """

        self.ui.listWidget.clear()
        for i in self.seriesTest:
            if i['Estado'] == 'Pausada':
                item = QtWidgets.QListWidgetItem()
                item.setText(i['Nombre'])
                self.ui.listWidget.addItem(item)

    def seriesTodas(self) -> NoReturn:
        """
        Creo una lista con todas las series
        """

        self.ui.listWidget.clear()
        for i in self.seriesTest:
            item = QtWidgets.QListWidgetItem()
            item.setText(i['Nombre'])
            self.ui.listWidget.addItem(item)

    def printCurrentItems(self) -> NoReturn:
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

    def aplicaDatos(self) -> bool:
        """
        Ejecuta todas las consultas que hay en la lista
        """

        logger.debug(self.queryCompleta)

        ejecutaScriptSqlite(self.db, self.queryCompleta)

        self.queryCompleta = str()
        return True

    def cancela(self) -> NoReturn:
        """
        Establece el estado actual en cancelado para retornar None y ejecuta reject
        """

        self.estadoA = self.estadoF
        self.reject()

    def aceptaDatos(self) -> NoReturn:
        if self.aplicaDatos():
            self.accept()

    @staticmethod
    def getDatos(parent: object = None, dbSeries: str = None) -> NoReturn:
        dialog = ListarTodas(parent, dbSeries)
        dialog.exec_()


def main():
    app = QtWidgets.QApplication(sys.argv)
    ListarTodas.getDatos(dbSeries=ruta_db)
    return app


if __name__ == '__main__':
    main()
# hacer boton actualizar_insertar series
# cuando haga un cabio actualizar_insertar series
