#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from typing import NoReturn

from PyQt5 import QtWidgets, QtSql
from app.views.ui.lista_activa_ui import Ui_Dialog

from app import logger
from app.modulos.settings import ruta_db


class ListaActiva(QtWidgets.QDialog):
    def __init__(self, parent: object = None, database: str = None) -> NoReturn:
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.otra = 'otra'  # campo otra del formulario
        self.estadoI = 'Ok'  # estado inicial
        self.estadoF = 'Cancelado'  # final
        self.estadoA = self.estadoI  # actual
        self.db = database

        self.setWindowTitle('Series Activas')

        logger.debug(self.db)

        self.database = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        self.crearConexion()

        testModel = QtSql.QSqlTableModel()
        testModel.setTable("Series")
        testModel.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        testModel.select()
        testView = self.ui.tableView
        testView.setModel(testModel)

        # self.ui.pushButtonAplicar.clicked.connect(self.__aplicaDatos)
        # #actualmente no lo uso
        self.ui.pushButtonCerrar.clicked.connect(self.cancela)
        self.ui.pushButtonAceptar.clicked.connect(self.aceptaDatos)

    def crearConexion(self) -> bool:
        """

        """

        self.database.setDatabaseName(self.db)
        if self.database.open():
            return True
        else:
            logger.info(self.database.lastError().text())
            return False

    def aplicaDatos(self) -> bool:  # actualmente sin uso
        """
        Ejecuta todas las consultas que hay en la lista
        """
        self.database.close()  # cerramos la conexion de la bd
        return True

    def cancela(self) -> NoReturn:
        """
        Establece el estado actual en cancelado para retornar None y ejecuta reject
        """

        self.estadoA = self.estadoF
        self.database.close()  # cerramos la conexion de la bd
        self.reject()

    def aceptaDatos(self) -> NoReturn:
        """
        Boton Aceptar, primero aplicas los datos, si retorna True, cierra la ventana
        """

        if self.aplicaDatos():
            self.accept()

    @staticmethod
    def get_data(parent: object = None, database: str = None) -> NoReturn:
        dialog = ListaActiva(parent, database)
        dialog.exec_()


def main():
    app = QtWidgets.QApplication(sys.argv)
    ListaActiva.get_data(database=ruta_db)
    return app


if __name__ == '__main__':
    main()
