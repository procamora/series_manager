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
        self.estadoI = 'Ok'  # estado inicial
        self.estadoF = 'Cancelado'  # final
        self.estadoA = self.estadoI  # actual
        self.db = dbSeries

        # lista de consultas que se ejecutaran al final
        self.queryCompleta = str()

        self.setWindowTitle('Modificaciones en masa')
        # esto permite selecionar multiples
        self.ui.listWidget.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)

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

    def sacaSeries(self):
        """
        Saca todas las series de la bd y las mete en una lista de diccionarios accesible en todo el objeto
        """
        query = 'SELECT * FROM Series ORDER BY Nombre'
        self.seriesTest = conectionSQLite(self.db, query, True)
        self.ui.radioButtonAct.setChecked(True)
        # lo ejecuto al principio ya que es el activado por defecto
        self.seriesActuales()

    def seriesActuales(self):
        """
        Creo una lista con todas las series que estoy siguiendo
        """

        self.ui.listWidget.clear()
        for i in self.seriesTest:
            if i['Siguiendo'] == 'Si' and i['Capitulo'] != 0 and i['Estado'] == 'Activa':
                item = QtWidgets.QListWidgetItem()
                item.setText(i['Nombre'])
                self.ui.listWidget.addItem(item)

    def seriesTemporales(self):
        """
        Creo una lista con todas las series que han acabado temporada
        """

        self.ui.listWidget.clear()
        for i in self.seriesTest:
            if i['Capitulo'] == 0:
                item = QtWidgets.QListWidgetItem()
                item.setText(i['Nombre'])
                self.ui.listWidget.addItem(item)

    def seriesPausadas(self):
        """
        Creo una lista con todas las series que han acabado temporada
        """

        self.ui.listWidget.clear()
        for i in self.seriesTest:
            if i['Estado'] == 'Pausada':
                item = QtWidgets.QListWidgetItem()
                item.setText(i['Nombre'])
                self.ui.listWidget.addItem(item)

    def seriesTodas(self):
        """
        Creo una lista con todas las series
        """

        self.ui.listWidget.clear()
        for i in self.seriesTest:
            item = QtWidgets.QListWidgetItem()
            item.setText(i['Nombre'])
            self.ui.listWidget.addItem(item)

    def printCurrentItems(self):
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

        if modo_debug:
            print((self.queryCompleta))

    def aplicaDatos(self):
        """
        Ejecuta todas las consultas que hay en la lista
        """

        if modo_debug:
            print((self.queryCompleta))

        ejecutaScriptSqlite(self.db, self.queryCompleta)

        self.queryCompleta = str()
        return True

    def cancela(self):
        """
        Establece el estado actual en cancelado para retornar None y ejecuta reject
        """

        self.estadoA = self.estadoF
        self.reject()

    def aceptaDatos(self):
        if self.aplicaDatos():
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
