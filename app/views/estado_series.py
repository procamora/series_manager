#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from typing import List, NoReturn, Dict

from PyQt5 import QtWidgets
from app.views.ui.estado_series_ui import Ui_Dialog

from app import logger
from app.modulos.connect_sqlite import conection_sqlite, execute_script_sqlite
from app.modulos.settings import ruta_db
from app.modulos.tviso import conect_tviso


class EstadoSeries(QtWidgets.QDialog):
    def __init__(self, parent: object = None, database: str = None) -> NoReturn:
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.state_ok = 'Ok'  # estado inicial
        self.state_cancel = 'Cancelado'  # final
        self.state_current = self.state_ok  # actual
        self.db = database

        # str de consultas que se ejecutaran al final
        self.query_complete_str = str()
        self.list_actuals = list()

        self.DatSeriesEmpiezanTemporada: List[Dict] = list()
        self.DatSerieFinalizada: List[Dict] = list()
        self.DatTemporadaAcabada: List[Dict] = list()
        self.DatSeriesFinalizadas: List[Dict] = list()

        self.setWindowTitle('Estado de series Activas')

        # esto permite selecionar multiples
        self.ui.listWidget.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)

        self.get_all_series()

        self.ui.radioButtonEmpieza.clicked.connect(
            self.series_start_season)
        self.ui.radioButtonAcabaT.clicked.connect(self.session_finished)
        self.ui.radioButtonFinalizada.clicked.connect(self.serie_finished)

        self.ui.pushButtonRefresh.clicked.connect(self.get_all_series)

        self.ui.pushButtonAnadir.clicked.connect(self._print_current_items)

        self.ui.pushButtonAplicar.clicked.connect(self.apply_data)
        self.ui.pushButtonCerrar.clicked.connect(self.cancel)
        self.ui.pushButtonAceptar.clicked.connect(self.accept_data)

    def get_all_series(self) -> NoReturn:
        """
        Saca todas las series de la bd y las mete en una lista de diccionarios
        accesible en todo el objeto
        """
        query = """SELECT Nombre FROM Series WHERE Estado LIKE "En Espera" AND Capitulo LIKE 0"""
        self.DatSeriesEmpiezanTemporada = conection_sqlite(self.db, query, True)

        query = """SELECT ID, Nombre, Estado, imdb_Finaliza FROM Series WHERE imdb_Finaliza <> "????" AND Capitulo 
        LIKE imdb_Capitulos AND Estado <> 'Finalizada'"""
        self.DatSerieFinalizada = conection_sqlite(self.db, query, True)

        query = """SELECT ID, Nombre, Estado, imdb_Finaliza FROM Series WHERE imdb_Finaliza LIKE "????" AND Capitulo 
        LIKE imdb_Capitulos"""
        self.DatTemporadaAcabada = conection_sqlite(self.db, query, True)

        query = """SELECT ID, Nombre, Temporada, Capitulo, imdb_Temporada, imdb_Capitulos FROM Series WHERE Estado 
        LIKE "Finalizada" AND Acabada LIKE "Si" AND (Capitulo <> imdb_Capitulos OR Temporada <> imdb_Temporada)"""
        self.DatSeriesFinalizadas = conection_sqlite(self.db, query, True)

        self.ui.radioButtonFinalizada.setChecked(True)
        # lo ejecuto al principio ya que es el activado por defecto
        self.serie_finished()

        query = """SELECT * FROM Credenciales"""
        datos = conection_sqlite(self.db, query, True)
        if len(datos) > 0:
            self.list_actuals = conect_tviso(datos[0]['user_tviso'], datos[0]['pass_tviso'])

    def button_next(self, series_test: List) -> NoReturn:
        """
        Creo una lista con todas las series que estoy siguiendo
        """

        self.ui.listWidget.clear()
        if len(series_test) != 0:
            for i in series_test:
                item = QtWidgets.QListWidgetItem()
                item.setText(i['Nombre'])
                self.ui.listWidget.addItem(item)
            self.ui.pushButtonAnadir.setVisible(True)

        else:
            item = QtWidgets.QListWidgetItem()
            item.setText('No hay ninguna serie')
            self.ui.listWidget.addItem(item)
            self.ui.pushButtonAnadir.setVisible(False)

        try:  # si no hay ninguno, da fallo establezco por defecto el ultimo, que es el que tiene el valordel item
            self.ui.listWidget.setCurrentItem(item)
        except Exception:
            pass

    def apply_data(self) -> bool:
        """
        Ejecuta todas las consultas que hay en la lista
        """
        logger.debug(self.query_complete_str)

        execute_script_sqlite(self.db, self.query_complete_str)

        self.query_complete_str = str()
        return True

    def cancel(self) -> NoReturn:
        """
        Establece el estado actual en cancelado para retornar None y ejecuta reject
        """

        self.state_current = self.state_cancel
        self.reject()

    def serie_finished(self) -> NoReturn:
        # coge las series de imdb y actualiza la table de estado
        # query = 'SELECT ID, Nombre, Estado, imdb_Finaliza FROM Series'
        # revisar porque puedo ESTAR VIENDO UNA SERIE FINALIZADA Y NO QUIERO
        # QUE CAMBIE ESTADO
        self.button_next(self.DatSerieFinalizada)

    def session_finished(self) -> NoReturn:
        self.button_next(self.DatTemporadaAcabada)

    def series_finished(self) -> NoReturn:
        # busca las series finalizadas y las actualiza con el ultimo episodio si la he acabado de ver,
        # NO HAY IMPLEMENTADO BOTON PARA ELLO, solo lo ejecuto a pelo cuando lo
        # necesito

        self.button_next(self.DatSeriesFinalizadas)

        for DatSer in self.DatSeriesFinalizadas:
            query = """UPDATE series SET Temporada=imdb_Temporada, Capitulo=imdb_Capitulos
                WHERE Nombre LIKE '{}'""".format(DatSer['Nombre'])
            logger.info(query)
            conection_sqlite(self.db, query)

    def series_start_season(self) -> NoReturn:
        # cuidado, si lo ejecutas la misma semana que acabas la temporada se pondra en activa,
        # hay que ejecurtarlo 1 vez a la semana
        # buscar forma de hacer que haga una comprobacion con las series que
        # den positivo

        calendario = list(dict())
        for i in self.list_actuals:  # lista de series de tviso
            # lista de series que estan a la espera de una nueva temporada
            for j in self.DatSeriesEmpiezanTemporada:
                # http:/stackoverflow.com/questions/8214932/how-to-check-if-a-value-exists-in-a-dictionary-python
                if i in list(j.values()):
                    # hago una lista de diccionarios, porque asi la tengo
                    # deficina de __botonSiguiendo
                    calendario.append({'Nombre': str(i)})

        self.button_next(calendario)

    def _print_current_items(self) -> NoReturn:
        """
        Coge todas las series seleccionadas y las mete en una lista con su
        respectiva consulta para despues ejecutarlas
        """

        for i in self.ui.listWidget.selectedItems():

            if self.ui.radioButtonAcabaT.isChecked():
                query = """UPDATE series SET Temporada=Temporada+1, Capitulo="00", Estado="En Espera" 
                WHERE Nombre Like "{}";""".format(
                    i.text())
                self.query_complete_str += '\n' + query

            elif self.ui.radioButtonEmpieza.isChecked():
                query = """UPDATE series SET Capitulo="01", Estado="Activa" WHERE Nombre Like "{}";""".format(i.text())
                self.query_complete_str += '\n' + query

            elif self.ui.radioButtonFinalizada.isChecked():
                query = """UPDATE series SET Estado="Finalizada", Acabada="Si", Siguiendo="No" 
                WHERE Nombre Like "{}";""".format(
                    i.text())
                self.query_complete_str += '\n' + query

        logger.debug(self.query_complete_str)

    def accept_data(self) -> NoReturn:
        if self.apply_data():
            self.accept()

    @staticmethod
    def get_data(parent: object = None, database: str = None) -> NoReturn:
        dialog = EstadoSeries(parent, database)
        dialog.exec_()


def main():
    app = QtWidgets.QApplication(sys.argv)
    EstadoSeries.get_data(database=ruta_db)
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
