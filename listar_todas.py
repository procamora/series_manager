#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

from PyQt5 import QtWidgets

from ui.listar_todas_ui import Ui_Dialog
from modulos.connect_sqlite import conectionSQLite, ejecutaScriptSqlite
from modulos.settings import modo_debug, ruta_db


class MiFormulario(QtWidgets.QDialog):
    def __init__(self, parent=None, dbSeries=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.EstadoI = 'Ok' # estado inicial
        self.EstadoF = 'Cancelado' #final
        self.EstadoA = self.EstadoI #actual
        self.db = dbSeries

        self.QueryCompleta = str()   # lista de consultas que se ejecutaran al final

        self.setWindowTitle('Modificaciones en masa')
        # esto permite selecionar multiples
        self.ui.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.__sacaSeries()

        self.ui.radioButtonAct.clicked.connect(self.__seriesActuales)
        self.ui.radioButtonTemp.clicked.connect(self.__seriesTemporales)
        self.ui.radioButtonPausada.clicked.connect(self.__seriesPausadas)
        self.ui.radioButtonTodas.clicked.connect(self.__seriesTodas)
        self.ui.pushButtonRefresh.clicked.connect(self.__sacaSeries)

        self.ui.pushButtonAnadir.clicked.connect(self.__printCurrentItems)

        self.ui.pushButtonAplicar.clicked.connect(self.__aplicaDatos)
        self.ui.pushButtonCerrar.clicked.connect(self.__cancela)
        self.ui.pushButtonAceptar.clicked.connect(self.__aceptaDatos)


    def __sacaSeries(self):
        '''
        Saca todas las series de la bd y las mete en una lista de diccionarios accesible en todo el objeto
        '''
        query = 'SELECT * FROM Series ORDER BY Nombre'
        self.seriesTest =  conectionSQLite(self.db, query, True)
        self.ui.radioButtonAct.setChecked(True)
        self.__seriesActuales() # lo ejecuto al principio ya que es el activado por defecto


    def __seriesActuales(self):
        '''
        Creo una lista con todas las series que estoy siguiendo
        '''

        self.ui.listWidget.clear()
        for i in self.seriesTest:
            if i['Siguiendo'] == 'Si' and i['Capitulo'] != 0 and i['Estado'] == 'Activa':
                item=QtWidgets.QListWidgetItem()
                item.setText(i['Nombre'])
                self.ui.listWidget.addItem(item)


    def __seriesTemporales(self):
        '''
        Creo una lista con todas las series que han acabado temporada
        '''

        self.ui.listWidget.clear()
        for i in self.seriesTest:
            if i['Capitulo'] == 0:
                item=QtWidgets.QListWidgetItem()
                item.setText(i['Nombre'])
                self.ui.listWidget.addItem(item)

    def __seriesPausadas(self):
        '''
        Creo una lista con todas las series que han acabado temporada
        '''

        self.ui.listWidget.clear()
        for i in self.seriesTest:
            if i['Estado'] == 'Pausada':
                item=QtWidgets.QListWidgetItem()
                item.setText(i['Nombre'])
                self.ui.listWidget.addItem(item)


    def __seriesTodas(self):
        '''
        Creo una lista con todas las series
        '''

        self.ui.listWidget.clear()
        for i in self.seriesTest:
            item=QtWidgets.QListWidgetItem()
            item.setText(i['Nombre'])
            self.ui.listWidget.addItem(item)


    def __printCurrentItems(self):
        '''
        Coge todas las series seleccionadas y las mete en una lista con su respectiva consulta para despues ejecutarlas
        '''

        for i in self.ui.listWidget.selectedItems():
            if self.ui.radioButtonAcabaT.isChecked():
                query = '''UPDATE series SET Temporada=Temporada+1, Capitulo="00", Estado="En Espera" WHERE Nombre
                    LIKE "{}";\n'''.format(i.text())
                self.QueryCompleta += query

            elif self.ui.radioButtonEmpieza.isChecked():
                query = 'UPDATE series SET Capitulo="01", Estado="Activa" WHERE Nombre LIKE "{}";\n'.format(i.text())
                self.QueryCompleta += query

            elif self.ui.radioButtonEspera.isChecked():
                query = 'UPDATE series SET Estado="Pausada" WHERE Nombre LIKE "{}";\n'.format(i.text())
                self.QueryCompleta += query

            elif self.ui.radioButtonFinalizada.isChecked():
                query = 'UPDATE series SET Estado="Finalizada", Acabada="Si" WHERE Nombre LIKE "{}";\n'.format(i.text())
                self.QueryCompleta += query

        if modo_debug:
            print((self.QueryCompleta))


    def __aplicaDatos(self):
        '''
        Ejecuta todas las consultas que hay en la lista
        '''

        if modo_debug:
            print((self.QueryCompleta))

        ejecutaScriptSqlite(self.db, self.QueryCompleta)

        self.QueryCompleta = str()
        return True


    def __cancela(self):
        '''
        Establece el estado actual en cancelado para retornar None y ejecuta reject
        '''

        self.EstadoA = self.EstadoF
        self.reject()


    def __aceptaDatos(self):
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
# hacer boton actualizar_insertar series
# cuando haga un cabio actualizar_insertar series
