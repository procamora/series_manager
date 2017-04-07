#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

from PyQt5 import QtWidgets

from ui.estado_series_ui import Ui_Dialog
from modulos.tviso import conectTviso
from modulos.connect_sqlite import conectionSQLite, ejecutaScriptSqlite
from modulos.settings import modo_debug, ruta_db


class MiFormulario(QtWidgets.QDialog):
    def __init__(self, parent=None, dbSeries=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.EstadoI = 'Ok'  # estado inicial
        self.EstadoF = 'Cancelado'  # final
        self.EstadoA = self.EstadoI  # actual
        self.db = dbSeries

        # str de consultas que se ejecutaran al final
        self.QueryCompleta = str()

        self.setWindowTitle('Estado de series Activas')

        # esto permite selecionar multiples
        self.ui.listWidget.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)

        self.sacaSeries()

        self.ui.radioButtonEmpieza.clicked.connect(
            self.seriesEmpiezanTemporada)
        self.ui.radioButtonAcabaT.clicked.connect(self.temporadaAcabada)
        self.ui.radioButtonFinalizada.clicked.connect(self.serieFinalizada)

        self.ui.pushButtonRefresh.clicked.connect(self.sacaSeries)

        self.ui.pushButtonAnadir.clicked.connect(self.__printCurrentItems)

        self.ui.pushButtonAplicar.clicked.connect(self.aplicaDatos)
        self.ui.pushButtonCerrar.clicked.connect(self.cancela)
        self.ui.pushButtonAceptar.clicked.connect(self.aceptaDatos)

    def sacaSeries(self):
        """
        Saca todas las series de la bd y las mete en una lista de diccionarios
        accesible en todo el objeto
        """
        query = """SELECT Nombre FROM Series WHERE Estado LIKE "En Espera" AND Capitulo LIKE 0"""
        self.DatSeriesEmpiezanTemporada = conectionSQLite(self.db, query, True)

        query = """SELECT ID, Nombre, Estado, imdb_Finaliza FROM Series WHERE imdb_Finaliza <> "????" AND Capitulo LIKE imdb_Capitulos AND Estado <> 'Finalizada'"""
        self.DatSerieFinalizada = conectionSQLite(self.db, query, True)

        query = """SELECT ID, Nombre, Estado, imdb_Finaliza FROM Series WHERE imdb_Finaliza LIKE "????" AND Capitulo LIKE imdb_Capitulos"""
        self.DatTemporadaAcabada = conectionSQLite(self.db, query, True)

        query = """SELECT ID, Nombre, Temporada, Capitulo, imdb_Temporada, imdb_Capitulos FROM Series WHERE Estado LIKE "Finalizada" AND Acabada LIKE "Si" AND (Capitulo <> imdb_Capitulos OR Temporada <> imdb_Temporada)"""
        self.DatSeriesFinalizadas = conectionSQLite(self.db, query, True)

        self.ui.radioButtonFinalizada.setChecked(True)
        # lo ejecuto al principio ya que es el activado por defecto
        self.serieFinalizada()

        query = """SELECT * FROM Credenciales"""
        datos = conectionSQLite(self.db, query, True)[0]
        self.actuales = conectTviso(datos['user_tviso'], datos['pass_tviso'])

    def botonSiguiendo(self, seriesTest):
        """
        Creo una lista con todas las series que estoy siguiendo
        """

        self.ui.listWidget.clear()
        if len(seriesTest) != 0:
            for i in seriesTest:
                item = QtWidgets.QListWidgetItem()
                item.setText(i['Nombre'])
                self.ui.listWidget.addItem(item)
            self.ui.pushButtonAnadir.setVisible(True)

        else:
            item = QtWidgets.QListWidgetItem()
            item.setText('No hay ninguna serie')
            self.ui.listWidget.addItem(item)
            self.ui.pushButtonAnadir.setVisible(False)

        try:  # si no hay ninguno, da fallo
            # establezco por defecto el ultimo, que es el que tiene el valor
            # del item
            self.ui.listWidget.setCurrentItem(item)
        except:
            pass

    def aplicaDatos(self):
        """
        Ejecuta todas las consultas que hay en la lista
        """

        if modo_debug:
            print((self.QueryCompleta))

        ejecutaScriptSqlite(self.db, self.QueryCompleta)

        self.QueryCompleta = str()
        return True

    def cancela(self):
        """
        Establece el estado actual en cancelado para retornar None y ejecuta reject
        """

        self.EstadoA = self.EstadoF
        self.reject()

    def serieFinalizada(self):
        # coge las series de imdb y actualiza la table de estado
        # query = 'SELECT ID, Nombre, Estado, imdb_Finaliza FROM Series'
        # revisar porque puedo ESTAR VIENDO UNA SERIE FINALIZADA Y NO QUIERO
        # QUE CAMBIE ESTADO
        self.botonSiguiendo(self.DatSerieFinalizada)

    def temporadaAcabada(self):
        self.botonSiguiendo(self.DatTemporadaAcabada)

    def seriesFinalizadas(self):
        # busca las series finalizadas y las actualiza con el ultimo episodio si la he acabado de ver,
        # NO HAY IMPLEMENTADO BOTON PARA ELLO, solo lo ejecuto a pelo cuando lo
        # necesito

        self.botonSiguiendo(self.DatSeriesFinalizadas)

        for DatSer in self.DatSeriesFinalizadas:
            query = """UPDATE series SET Temporada=imdb_Temporada, Capitulo=imdb_Capitulos
                WHERE Nombre LIKE '{}'""".format(DatSer['Nombre'])
            print(query)
            conectionSQLite(self.db, query)

    def seriesEmpiezanTemporada(self):
        # cuidado, si lo ejecutas la misma semana que acabas la temporada se pondra en activa,
        # hay que ejecurtarlo 1 vez a la semana
        # buscar forma de hacer que haga una comprobacion con las series que
        # den positivo

        calendario = list(dict())
        for i in self.actuales:  # lista de series de tviso
            # lista de series que estan a la espera de una nueva temporada
            for j in self.DatSeriesEmpiezanTemporada:
                # http:/stackoverflow.com/questions/8214932/how-to-check-if-a-value-exists-in-a-dictionary-python
                if i in list(j.values()):
                    # hago una lista de diccionarios, porque asi la tengo
                    # deficina de __botonSiguiendo
                    calendario.append({'Nombre': str(i)})

        self.botonSiguiendo(calendario)

    def __printCurrentItems(self):
        """
        Coge todas las series seleccionadas y las mete en una lista con su
        respectiva consulta para despues ejecutarlas
        """

        for i in self.ui.listWidget.selectedItems():

            if self.ui.radioButtonAcabaT.isChecked():
                query = """UPDATE series SET Temporada=Temporada+1, Capitulo="00", Estado="En Espera" WHERE Nombre Like "{}";""".format(
                    i.text())
                self.QueryCompleta += '\n' + query

            elif self.ui.radioButtonEmpieza.isChecked():
                query = """UPDATE series SET Capitulo="01", Estado="Activa" WHERE Nombre Like "{}";""".format(i.text())
                self.QueryCompleta += '\n' + query

            elif self.ui.radioButtonFinalizada.isChecked():
                query = """UPDATE series SET Estado="Finalizada", Acabada="Si", Siguiendo="No" WHERE Nombre Like "{}";""".format(
                    i.text())
                self.QueryCompleta += '\n' + query

        if modo_debug:
            print((self.QueryCompleta))

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


# HACER FUNCION QUE COJA

# actualizar_insertar series en espera
# UPDATE series  SET Estado='En Espera' WHERE Capitulo LIKE '0'

# SERIE ACABADA
# UPDATE series SET Siguiendo='No', Acabada='Si', Estado='Finalizada'
# WHERE ID LIKE 33

# SELECT Nombre FROM Series WHERE Estado NOT LIKE "Activa" AND Estado NOT
# LIKE "En Espera" AND Estado NOT LIKE "Finalizada"
