#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from typing import NoReturn

from PyQt5 import QtWidgets
from app.views.ui.actualizar_insertar_ui import Ui_Dialog

import app.controller.Controller as Controller
from app import logger
from app.models.model_query import Query
from app.models.model_serie import Serie
from app.utils import funciones
from app.utils.actualiza_imdb import UpdateImdb


class ActualizarInsertar(QtWidgets.QDialog):
    def __init__(self, parent=None, data_serie: Serie = None) -> NoReturn:
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.other = 'otra'  # campo otra del formulario
        self.state_ok = 'Ok'  # estado inicial
        self.state_cancel = 'Cancelado'  # final
        self.state_current = self.state_ok  # actual
        self.serie = data_serie

        # para todos establezco esto que el estado es Activa, si actualizo lo
        # modifico en la funcion creaConf
        self.list_states()

        all_items = [self.ui.BoxEstado.itemText(i) for i in range(self.ui.BoxEstado.count())]
        if len(all_items) > 0:
            self.ui.BoxEstado.setCurrentIndex(all_items.index('Activa'))

        if self.serie is not None:  # Actualizar
            self.setWindowTitle(f'Actualizar serie: {self.serie.title}')

            # para poder modifical el nombre en el update
            self.name_original = str(self.serie.title)

            self.ui.pushButtonAplicar.setText('Actualizar')
            self.create_configuration()
        else:  # Insertar
            self.setWindowTitle('Insertar Serie')
            self.ui.pushButtonAplicar.setText('Insertar')

            # Generar checkbox
            self.list_seasons(1, 5)
            self.list_chapters(1, 13)

            # pongo la fecha de hoy para insertar por defecto
            # recogo todos los dias de la caja y le paso el indice del dia en
            # el que sale
            all_items = [self.ui.BoxEmision.itemText(i) for i in range(self.ui.BoxEmision.count())]
            if len(all_items) > 0:
                self.ui.BoxEmision.setCurrentIndex(all_items.index(funciones.calculate_day_week()))

        # Ocultar textos
        self.ui.lineTemp.hide()
        self.ui.lineCapitulo.hide()

        self.ui.lineTemp.setText(str(self.ui.BoxTemporada.currentText()))
        self.ui.lineCapitulo.setText(str(self.ui.BoxCapitulo.currentText()))

        # conectores
        self.ui.BoxTemporada.activated.connect(self.field_season)
        self.ui.BoxCapitulo.activated.connect(self.field_chapter)

        self.ui.pushButtonAplicar.clicked.connect(self.apply_data)
        self.ui.pushButtonCerrar.clicked.connect(self.cancel)
        self.ui.pushButtonAceptar.clicked.connect(self.accept_data)

    def field_season(self) -> NoReturn:
        """
        Si en la lista de temporadas seleccionamos otra se abre un line edit
        para poner el numero de temporada que no esta, si lo cambiamos se oculta
        """

        if self.ui.BoxTemporada.currentText() == self.other:
            self.ui.lineTemp.setEnabled(True)
            self.ui.lineTemp.setVisible(True)
            self.ui.lineTemp.setText('')
        else:
            self.ui.lineTemp.setEnabled(False)
            self.ui.lineTemp.setVisible(False)
            self.ui.lineTemp.setText(str(self.ui.BoxTemporada.currentText()))

    def field_chapter(self) -> NoReturn:
        """
        Si en la lista de capitulos seleccionamos otra se abre un line edit
        para poner el numero de capitulo que no esta, si lo cambiamos se oculta
        """

        if str(self.ui.BoxCapitulo.currentText()) == self.other:
            self.ui.lineCapitulo.setEnabled(True)
            self.ui.lineCapitulo.setVisible(True)
            self.ui.lineCapitulo.setText('')
        else:
            self.ui.lineCapitulo.setEnabled(False)
            self.ui.lineCapitulo.setVisible(False)
            self.ui.lineCapitulo.setText(
                str(self.ui.BoxCapitulo.currentText()))

    def list_seasons(self, x: int, y: int) -> NoReturn:
        """
        Crea el comboBox de las temporadas, primero lo vacia y
        luego lo crea con los rangos que le indico
        """

        list_temp = list()
        for i in range(x, y):
            list_temp.append(str(i))

        self.ui.BoxTemporada.clear()
        self.ui.BoxTemporada.addItems(list_temp)
        self.ui.BoxTemporada.addItem(self.other)

    def list_chapters(self, x: int, y: int) -> NoReturn:
        """
        Crea el comboBox de los capitulos, primero lo vacia y
        luego lo crea con los rangos que le indico
        """

        list_cap = list()
        for i in range(x, y):
            list_cap.append(str(i))

        self.ui.BoxCapitulo.clear()
        self.ui.BoxCapitulo.addItems(list_cap)
        self.ui.BoxCapitulo.addItem(self.other)

    def list_states(self) -> NoReturn:
        """
        Crea el comboBox de los estados, primero lo vacia y
        luego lo crea con los rangos que le indico
        """
        response_query: Query = Controller.get_states()
        list_estates: list = [states.state for states in response_query.response]
        # for i in response_query.response:
        #    list_estates.append(i.state)

        self.ui.BoxEstado.clear()
        self.ui.BoxEstado.addItems(list_estates)

    def create_configuration(self) -> NoReturn:
        """
        Establece los valores por defecto que se le indican en caso de que se indiquen
        """
        logger.debug(self.serie)

        self.ui.lineTitulo.setText(self.serie.title)

        # Generar checkbox
        self.list_seasons(self.serie.season, self.serie.season + 2)
        self.list_chapters(self.serie.chapter, self.serie.chapter + 8)

        if self.serie.following:
            self.ui.radioSeguirSi.click()
        else:
            self.ui.radioSeguirNo.click()

        # recogo todos los dias de la caja y le paso el indice del dia en el que sale
        all_items = [self.ui.BoxEmision.itemText(i) for i in range(self.ui.BoxEmision.count())]
        if len(all_items) > 0:
            print(all_items)
            print(self.serie.day)
            self.ui.BoxEmision.setCurrentIndex(all_items.index(self.serie.day))

        if self.serie.vose:
            self.ui.radioVOSE_Si.click()
        else:
            self.ui.radioVOSE_No.click()

        if self.serie.finished:
            self.ui.radioAcabadaSi.click()
        else:
            self.ui.radioAcabadaNo.click()

        all_items = [self.ui.BoxEstado.itemText(i) for i in range(self.ui.BoxEstado.count())]
        if len(all_items) > 0:
            self.ui.BoxEstado.setCurrentIndex(all_items.index(self.serie.state))

        if self.serie.imdb_id is not None:
            self.ui.lineImdb.setText(self.serie.imdb_id)

        self.ui.radioImdbNo.click()

    def apply_data(self) -> bool:
        """
        Recoge todos los valores que necesita, crea el update y lo ejecuta
        """
        self.ui.label_Info.setText('')

        serie: Serie = Serie()
        serie.title = str(self.ui.lineTitulo.text()).lstrip().rstrip()
        serie.season = int(self.ui.lineTemp.text())
        serie.chapter = int(self.ui.lineCapitulo.text())
        serie.day = str(self.ui.BoxEmision.currentText())
        serie.state = str(self.ui.BoxEstado.currentText())

        serie.vose = bool(self.ui.radioVOSE_Si.isChecked())
        serie.finished = bool(self.ui.radioAcabadaSi.isChecked())
        serie.imdb_following = bool(self.ui.radioImdbSi.isChecked())

        if len(self.ui.lineImdb.text()) == 0:  # añadido de insertar
            serie.imdb_id = 'NULL'
        else:
            # Ponemos las comillas del string usado por la query, ya que si es NULL buscamos que este sin comillas
            # para que no se añada a la BD
            serie.imdb_id = self.ui.lineImdb.text()

        if self.ui.radioSeguirSi.isChecked():
            update_imdb: bool = True
        else:
            update_imdb: bool = False

        # Nombre vacia produce errores al descargar series
        if len(str(self.ui.lineTitulo.text())) != 0:
            # HAGO ESTO PARA QUE EL UPDATE SE HAGA CON NONE EN CASO DE QUE NO LO PONGA
            if self.serie is not None:
                query_str = Controller.get_query_update_serie(serie, self.name_original)
            else:
                query_str = Controller.get_query_insert_serie(serie)

            # try:
            logger.debug(query_str)
            if update_imdb:
                imbd_test = UpdateImdb()

                if imbd_test.check_title(serie.imdb_id):
                    self.execute_imdb()
                    Controller.execute_query(query_str, self.db)
                    # Si es una inserccion despues de insertar vacio el titulo para poder hacer mas
                    if self.serie is None:
                        funciones.show_message(self.ui.label_Info, 'Insertado con imdb', True)
                        self.ui.lineTitulo.setText('')
                    else:
                        funciones.show_message(self.ui.label_Info, 'Actualizado con imdb', True)
                else:  # Si da error no quiero que borre el nombre
                    funciones.show_message(self.ui.label_Info, 'fallo en imdb', False)
            else:
                Controller.execute_query(query_str, self.db)
                # Si es una inserccion despues de insertar vacio el titulo para poder hacer mas
                if self.serie is None:
                    funciones.show_message(self.ui.label_Info, 'Insertado', True)
                    self.ui.lineTitulo.setText('')
                else:
                    funciones.show_message(self.ui.label_Info, 'Actualizado', True)
            return True

            # except Exception as e:
            #    logger.error(e)
            #    logger.error(e)
            #    dat = {'title': 'Error en bd', 'text': str(e)}
            #    MsgBox.get_data(datos=dat)
            #    return False
        else:
            funciones.show_message(self.ui.label_Info, 'Titulo vacio', False)
            return False

    def execute_imdb(self) -> NoReturn:
        """
        Actualiza los datos de la serie de imdb siempre que el id no este vacio
        """
        update_imdb = UpdateImdb()
        id_imdb = str(self.ui.lineImdb.text())
        if len(id_imdb) > 0:
            logger.debug('actualiza imdb')
            update_imdb.update_series(id_imdb)

    def accept_data(self) -> NoReturn:
        """
        Boton Aceptar, primero aplicas los datos, si retorna True, cierra la ventana
        """

        if self.apply_data():
            self.accept()

    def cancel(self) -> NoReturn:
        """
        Establece el estado actual en cancelado para retornar None y ejecuta reject
        """

        self.state_current = self.state_cancel
        self.reject()

    @staticmethod
    def get_data(parent: object = None, data_serie: Serie = None) -> NoReturn:
        dialog = ActualizarInsertar(parent, data_serie)
        dialog.exec_()


def main():
    # query = 'SELECT * FROM Series WHERE Nombre LIKE "Silicon Valley"'
    # configuracion = conectionSQLite('{}/{}'.directorio_trabajo, nombre_db), query, True)[0]
    ser = None
    app = QtWidgets.QApplication(sys.argv)
    # hay que poner la base de datos como parametro
    ActualizarInsertar.get_data(data_serie=ser)
    return app


if __name__ == '__main__':
    main()
