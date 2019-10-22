#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import sys
from pathlib import Path  # nueva forma de trabajar con rutas
from typing import NoReturn, List

from PyQt5 import QtWidgets
from app.views.ui.preferencias_ui import Ui_Dialog

import app.controller.Controller as Controller
import app.utils.settings
from app import logger
from app.models.model_preferences import Preferences
from app.models.model_query import Query
from app.utils.settings import PATH_FILE_CONFIG, write_config


class Preferencias(QtWidgets.QDialog):
    def __init__(self, parent: object = None) -> NoReturn:
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.other = 'otra'  # campo otra del formulario
        self.state_ok = 'Ok'  # estado inicial
        self.state_cancel = 'Cancelado'  # final
        self.state_current = self.state_ok  # actual

        self.setWindowTitle('Preferencias de configuracion')
        self.ui.tabWidget.setCurrentIndex(0)

        self.configuraciones: List[Preferences] = list()
        self.preferences_actual: Preferences = Preferences()
        self.initials_operations()

        # recogo todos los dias de la caja y le paso el indice del dia en el que sale
        all_items = [self.ui.BoxId.itemText(i) for i in range(self.ui.BoxId.count())]
        logger.info(all_items)
        try:
            self.ui.BoxId.setCurrentIndex(all_items.index(str(app.utils.settings.DATABASE_ID)))
        except ValueError as e:
            logger.debug(e)
            if len(all_items) == 1:  # si solo hay 1 es 'otra'
                self.ui.BoxId.setCurrentIndex(all_items.index(self.other))
            else:
                # si da error por algun motivo pongo el primero
                self.ui.BoxId.setCurrentIndex(all_items.index('1'))

        self.common_processes()

        self.ui.pushButton.clicked.connect(self.search_directory)
        self.ui.BoxId.activated.connect(self.common_processes)

        self.ui.pushButtonAplicar.clicked.connect(self.apply_data)
        self.ui.pushButtonCerrar.clicked.connect(self.cancel)
        self.ui.pushButtonAceptar.clicked.connect(self.accept_data)

    def initials_operations(self) -> NoReturn:
        self.get_all_notifications()
        self.list_id()

    def search_directory(self) -> NoReturn:
        """
        Se encarga de coger la ruta en la que vamos a guardar el fichero, en este caso solo buscamos directorios,
        y establecemos que la ruta raiz sea el escrotorio, que se establece en el init
        """
        # filenames = QtGui.QFileDialog.getOpenFileName()
        # noinspection PyArgumentList
        filenames: str = QtWidgets.QFileDialog.getExistingDirectory(
            parent=self, caption="Select Directory", directory=self.ui.lineRuta.text(),
            QFileDialog_Options=QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks)

        if filenames is not None:
            # if not (filenames.isNull()): en python 3 filenames ya no es un
            # QString sino str
            self.ui.lineRuta.setText(filenames)

    def get_all_notifications(self) -> NoReturn:
        """

        """
        response_query: Query = Controller.get_preferences()
        self.configuraciones = response_query.response
        # self.configuraciones = conection_sqlite(self.db, query, True)
        if not response_query.is_empty():
            self.preferences_actual = self.configuraciones[0]
        else:
            logger.info('Information not obtained')

    def list_id(self) -> NoReturn:
        """

        """
        lista: list = [str(i.id) for i in self.configuraciones]
        # for i in self.configuraciones:
        #    lista.append(str(i.id))
        self.ui.BoxId.clear()
        self.ui.BoxId.addItems(lista)
        self.ui.BoxId.addItem(self.other)

    def get_configuration(self) -> NoReturn:
        """
        """
        for i in self.configuraciones:
            if str(self.ui.BoxId.currentText()) == str(i.id):
                self.preferences_actual = i
        if self.ui.BoxId.currentText() == self.other:
            self.preferences_actual = Preferences()

    def common_processes(self) -> NoReturn:
        """
        """
        self.get_configuration()
        self.insert_serie()

    def apply_data(self) -> bool:
        preferences: Preferences = Preferences()
        preferences.id = int(self.ui.BoxId.currentText())
        preferences.url_feed = self.ui.lineNewpct.text()
        preferences.url_feed_vose = self.ui.lineShowrss.text()
        preferences.path_download = Path(self.ui.lineRuta.text())

        if preferences.id == self.other:
            logger.info('insert')
            Controller.insert_preferences(preferences)
            self.initials_operations()
        else:
            Controller.update_preferences(preferences)


        config = configparser.ConfigParser()
        config.read(PATH_FILE_CONFIG)
        config['CONFIGURABLE']['DATABASE_ID'] = str(preferences.id)
        write_config(config)
        app.utils.settings.DATABASE_ID = preferences.id


        return True

    def insert_serie(self) -> NoReturn:
        """
        """
        self.ui.lineNewpct.setText(self.preferences_actual.url_feed)
        self.ui.lineShowrss.setText(self.preferences_actual.url_feed_vose)
        self.ui.lineRuta.setText(str(self.preferences_actual.path_download))

    def cancel(self) -> NoReturn:
        """
        Establece el estado actual en cancelado para retornar None y ejecuta reject
        """
        self.state_current = self.state_cancel
        self.reject()

    def accept_data(self) -> NoReturn:
        """
        Boton Aceptar, primero aplicas los datos, si retorna True, cierra la ventana
        """
        if self.apply_data():
            self.accept()

    @staticmethod
    def get_data(parent: object = None) -> NoReturn:
        dialog = Preferencias(parent)
        dialog.exec_()


def main():
    app = QtWidgets.QApplication(sys.argv)
    Preferencias.get_data()
    return app


# revisar cuando pongo otra, poner insetar en vez de otra
if __name__ == '__main__':
    main()
