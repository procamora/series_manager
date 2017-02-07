#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

from PyQt5 import QtWidgets, QtSql

from ui.lista_activa_ui import Ui_Dialog
from modulos.settings import modo_debug, ruta_db


class MiFormulario(QtWidgets.QDialog):
    def __init__(self, parent=None, dbSeries=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.Otra = 'Otra'  # campo otra del formulario
        self.EstadoI = 'Ok' # estado inicial
        self.EstadoF = 'Cancelado' #final
        self.EstadoA = self.EstadoI #actual
        self.db = dbSeries

        self.setWindowTitle('Series Activas')

        if modo_debug:
            print(self.db)
        self.__CrearConexion()

        testModel = QtSql.QSqlTableModel()
        testModel.setTable("Series")
        testModel.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        testModel.select()
        testView = self.ui.tableView
        testView.setModel(testModel)





        #self.ui.pushButtonAplicar.clicked.connect(self.__aplicaDatos) #actualmente no lo uso
        self.ui.pushButtonCerrar.clicked.connect(self.__cancela)
        self.ui.pushButtonAceptar.clicked.connect(self.__aceptaDatos)


    def __CrearConexion(self):
        '''

        '''

        self.database = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        self.database.setDatabaseName(self.db)
        if self.database.open():
            return True
        else:
            print((self.database.lastError().text()))
            return False


    def __aplicaDatos(self): #actualmente sin uso
        '''
        Ejecuta todas las consultas que hay en la lista
        '''
        self.database.close()	# cerramos la conexion de la bd
        return True


    def __cancela(self):
        '''
        Establece el estado actual en cancelado para retornar None y ejecuta reject
        '''

        self.EstadoA = self.EstadoF
        self.database.close()  # cerramos la conexion de la bd
        self.reject()


    def __aceptaDatos(self):
        """
        Boton Aceptar, primero aplicas los datos, si retorna True, cierra la ventana
        """

        if self.__aplicaDatos():
            self.accept()


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
