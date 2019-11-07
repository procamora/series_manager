#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from typing import NoReturn

from PyQt5 import QtWidgets, QtSql
from app.views.ui.lista_activa_ui import Ui_Dialog

from app import logger
from app.utils.settings import PATH_DATABASE


class ListaActiva(QtWidgets.QDialog):
    def __init__(self, parent: object = None) -> NoReturn:
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.other = 'otra'  # campo otra del formulario
        self.state_ok = 'Ok'  # estado inicial
        self.state_cancel = 'Cancelado'  # final
        self.state_current = self.state_ok  # actual

        self.setWindowTitle('Series Activas')

        self.database = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        self.create_connection()

        test_model = QtSql.QSqlTableModel()
        test_model.setTable("Series")
        test_model.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        test_model.select()
        test_view = self.ui.tableView
        test_view.setModel(test_model)

        # self.ui.pushButtonAplicar.clicked.connect(self.__aplicaDatos)
        # #actualmente no lo uso
        self.ui.pushButtonCerrar.clicked.connect(self.cancel)
        self.ui.pushButtonAceptar.clicked.connect(self.accept_data)

    def create_connection(self) -> bool:
        """

        """

        self.database.setDatabaseName(str(PATH_DATABASE))
        if self.database.open():
            return True
        else:
            logger.info(self.database.lastError().text())
            return False

    def apply_data(self) -> bool:  # actualmente sin uso
        """
        Ejecuta todas las consultas que hay en la lista
        """
        self.database.close()  # cerramos la conexion de la bd
        return True

    def cancel(self) -> NoReturn:
        """
        Establece el estado actual en cancelado para retornar None y ejecuta reject
        """

        self.state_current = self.state_cancel
        self.database.close()  # cerramos la conexion de la bd
        self.reject()

    def accept_data(self) -> NoReturn:
        """
        Boton Aceptar, primero aplicas los datos, si retorna True, cierra la ventana
        """

        if self.apply_data():
            self.accept()

    @staticmethod
    def get_data(parent: object = None) -> NoReturn:
        dialog = ListaActiva(parent)
        dialog.exec_()


def main():
    app = QtWidgets.QApplication(sys.argv)
    ListaActiva.get_data()
    return app


if __name__ == '__main__':
    main()
