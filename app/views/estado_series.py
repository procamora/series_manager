#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from typing import List, NoReturn

from PyQt5 import QtWidgets
from app.views.ui.estado_series_ui import Ui_Dialog

import app.controller.Controller as Controller
from app import logger
from app.models.model_query import Query
from app.models.model_serie import Serie
from app.modulos.connect_sqlite import execute_script_sqlite
from app.modulos.settings import PATH_DATABASE
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
        self.list_series_tviso = list()

        self.DatSeriesEmpiezanTemporada: List[Serie] = list()
        self.DatSerieFinalizada: List[Serie] = list()
        self.DatTemporadaAcabada: List[Serie] = list()
        self.DatSeriesFinalizadas: List[Serie] = list()

        self.setWindowTitle('Estado de series Activas')

        # esto permite selecionar multiples
        self.ui.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.get_all_series()

        self.ui.radioButtonEmpieza.clicked.connect(self.series_start_season)
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
        accesible en _todo el objeto
        """
        response_query: Query = Controller.get_series_start_season(self.db)
        self.DatSeriesEmpiezanTemporada = response_query.response

        response_query: Query = Controller.get_series_finished(self.db)
        self.DatSerieFinalizada = response_query.response

        response_query: Query = Controller.get_series_finished_season(self.db)
        self.DatTemporadaAcabada = response_query.response

        response_query: Query = Controller.get_series_finished2(self.db)
        self.DatSeriesFinalizadas = response_query.response

        self.ui.radioButtonFinalizada.setChecked(True)
        # lo ejecuto al principio ya que es el activado por defecto
        self.serie_finished()

        response_query_credentials: Query = Controller.get_credentials(self.db)
        if not response_query_credentials.is_empty():
            user_credentials = response_query_credentials.response[0]  # primer elemento
            self.list_series_tviso = conect_tviso(user_credentials.user_tviso, user_credentials.pass_tviso)

    def button_next(self, serie: List[Serie]) -> NoReturn:
        """
        Creo una lista con todas las series que estoy siguiendo
        """
        item = QtWidgets.QListWidgetItem()
        self.ui.listWidget.clear()
        if len(serie) != 0:
            for i in serie:
                item = QtWidgets.QListWidgetItem()
                item.setText(i.title)
                self.ui.listWidget.addItem(item)
            self.ui.pushButtonAnadir.setVisible(True)
        else:
            item = QtWidgets.QListWidgetItem()
            item.setText('No hay ninguna serie')
            self.ui.listWidget.addItem(item)
            self.ui.pushButtonAnadir.setVisible(False)

        try:  # si no hay ninguno, da fallo establezco por defecto el ultimo, que es el que tiene el valordel item
            self.ui.listWidget.setCurrentItem(item)
        except Exception as e:
            logger.error(e)
            logger.error('ver excepcion y poner')

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
        for serie in self.DatSeriesFinalizadas:
            Controller.update_series_finished(serie.title, self.db)

    def series_start_season(self) -> NoReturn:
        # cuidado, si lo ejecutas la misma semana que acabas la temporada se pondra en activa,
        # hay que ejecurtarlo 1 vez a la semana
        # buscar forma de hacer que haga una comprobacion con las series que
        # den positivo
        series_started: List[Serie] = list()
        for serie_tviso in self.list_series_tviso:  # lista de series de tviso
            # lista de series que estan a la espera de una nueva temporada
            for series_paused in self.DatSeriesEmpiezanTemporada:
                if serie_tviso == series_paused.title:
                    series_started.append(series_paused)

        self.button_next(series_started)

    def _print_current_items(self) -> NoReturn:
        """
        Coge todas las series seleccionadas y las mete en una lista con su
        respectiva consulta para despues ejecutarlas
        """

        for i in self.ui.listWidget.selectedItems():
            if self.ui.radioButtonAcabaT.isChecked():
                query = f"""UPDATE series SET Temporada=Temporada+1, Capitulo="00", Estado="En Espera" 
                WHERE Nombre Like "{i.text()}";"""
                self.query_complete_str += '\n' + query

            elif self.ui.radioButtonEmpieza.isChecked():
                query = f"""UPDATE series SET Capitulo="01", Estado="Activa" WHERE Nombre Like "{i.text()}";"""
                self.query_complete_str += '\n' + query

            elif self.ui.radioButtonFinalizada.isChecked():
                query = f"""UPDATE series SET Estado="Finalizada", Acabada="Si", Siguiendo="No" 
                WHERE Nombre Like "{i.text()}";"""
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
    EstadoSeries.get_data(database=PATH_DATABASE)
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
