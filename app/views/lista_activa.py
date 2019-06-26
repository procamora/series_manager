#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from PyQt5 import QtWidgets, QtSql

from app.views.ui.lista_activa_ui import Ui_Dialog
from app.modulos.settings import modo_debug, ruta_db
from app import logger


class ListaActiva(QtWidgets.QDialog):
    def __init__(self, parent=None, dbSeries=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.otra = 'otra'  # campo otra del formulario
        self.estadoI = 'Ok'  # estado inicial
        self.estadoF = 'Cancelado'  # final
        self.estadoA = self.estadoI  # actual
        self.db = dbSeries

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

    def crearConexion(self):
        """

        """

        self.database.setDatabaseName(self.db)
        if self.database.open():
            return True
        else:
            logger.info(self.database.lastError().text())
            return False

    def aplicaDatos(self):  # actualmente sin uso
        """
        Ejecuta todas las consultas que hay en la lista
        """
        self.database.close()  # cerramos la conexion de la bd
        return True

    def cancela(self):
        """
        Establece el estado actual en cancelado para retornar None y ejecuta reject
        """

        self.estadoA = self.estadoF
        self.database.close()  # cerramos la conexion de la bd
        self.reject()

    def aceptaDatos(self):
        """
        Boton Aceptar, primero aplicas los datos, si retorna True, cierra la ventana
        """

        if self.aplicaDatos():
            self.accept()

    @staticmethod
    def getDatos(parent=None, dbSeries=None):
        dialog = ListaActiva(parent, dbSeries)
        dialog.exec_()


def main():
    app = QtWidgets.QApplication(sys.argv)
    ListaActiva.getDatos(dbSeries=ruta_db)
    return app


if __name__ == '__main__':
    main()
