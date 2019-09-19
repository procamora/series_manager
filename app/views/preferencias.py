#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from typing import NoReturn

from PyQt5 import QtWidgets
from app.views.ui.preferencias_ui import Ui_Dialog

from app import logger
from app.modulos import funciones
from app.modulos.connect_sqlite import conection_sqlite
from app.modulos.settings import directorio_local, ruta_db


class Preferencias(QtWidgets.QDialog):
    def __init__(self, parent: object = None, database: str = None) -> NoReturn:
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.other = 'otra'  # campo otra del formulario
        self.state_ok = 'Ok'  # estado inicial
        self.state_cancel = 'Cancelado'  # final
        self.state_current = self.state_ok  # actual
        self.db = database
        self.ruta = directorio_local

        self.setWindowTitle('Preferencias de configuracion')
        self.ui.tabWidget.setCurrentIndex(0)

        self.configuraciones = list(dict())
        self.data_db = dict()
        self.initials_operations()

        # recogo todos los dias de la caja y le paso el indice del dia en el
        # que sale
        all_items = [self.ui.BoxId.itemText(i) for i in range(self.ui.BoxId.count())]

        logger.info(all_items)
        with open(r'{}/id.conf'.format(self.ruta), 'r') as f:
            id_fich = f.readline().replace('/n', '')

        try:
            self.ui.BoxId.setCurrentIndex(all_items.index(id_fich))
        except ValueError:
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
        filenames = QtWidgets.QFileDialog.getExistingDirectory(self, "Open Directory", str(self.ui.lineRuta.text()),
                                                               QtWidgets.QFileDialog.ShowDirsOnly |
                                                               QtWidgets.QFileDialog.DontResolveSymlinks)

        if filenames is not None:
            # if not (filenames.isNull()): en python 3 filenames ya no es un
            # QString sino str
            self.ui.lineRuta.setText(filenames)

    def get_all_notifications(self) -> NoReturn:
        """

        """

        query = 'SELECT * FROM Configuraciones'
        self.configuraciones = conection_sqlite(self.db, query, True)
        if len(self.configuraciones) > 0:
            self.data_db = self.configuraciones[0]

    def list_id(self) -> NoReturn:
        """

        """

        lista = list()
        for i in self.configuraciones:
            lista.append(str(i['id']))

        self.ui.BoxId.clear()
        self.ui.BoxId.addItems(lista)
        self.ui.BoxId.addItem(self.other)

    def get_configuration(self) -> NoReturn:
        """

        """

        for i in self.configuraciones:
            if str(self.ui.BoxId.currentText()) == str(i['id']):
                logger.debug(self.ui.BoxId.currentText())
                logger.debug(i)
                self.data_db = i
        if self.ui.BoxId.currentText() == self.other:
            self.data_db = {'UrlFeedShowrss': '',
                            'RutaDescargas': '',
                            'UrlFeedNewpct': '',
                            'id': ''}

    def common_processes(self) -> NoReturn:
        """

        """

        self.get_configuration()
        self.insert_serie()

    def apply_data(self) -> bool:
        datos = {
            'ID': str(self.ui.BoxId.currentText()),
            'Newpct': str(self.ui.lineNewpct.text()),
            'showrss': str(self.ui.lineShowrss.text()),
            'Ruta': funciones.change_bars(str(self.ui.lineRuta.text()))
        }

        if datos['ID'] == self.other:
            logger.info('insert')
            query = """INSERT INTO Configuraciones(UrlFeedNewpct, UrlFeedShowrss, RutaDescargas) VALUES ("{}", "{}", 
            "{}")""".format(datos['Newpct'], datos['showrss'], datos['Ruta'])

            logger.debug('update')
            logger.debug(query)

            conection_sqlite(self.db, query)
            self.initials_operations()
        else:
            query = """UPDATE Configuraciones SET UrlFeedNewpct="{}", UrlFeedShowrss="{}", RutaDescargas="{}"
            WHERE ID LIKE {}""".format(datos['Newpct'], datos['showrss'], datos['Ruta'], datos['ID'])

            logger.debug('update')
            logger.debug(query)

            conection_sqlite(self.db, query)

        with open(r'{}/id.conf'.format(self.ruta), 'w') as f:
            f.write(datos['ID'])

        return True

    def insert_serie(self) -> NoReturn:
        """

        """

        self.ui.lineNewpct.setText(self.data_db['UrlFeedNewpct'])
        self.ui.lineShowrss.setText(self.data_db['UrlFeedShowrss'])
        self.ui.lineRuta.setText(str(self.data_db['RutaDescargas']))

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
    def get_data(parent: object = None, database: str = None) -> NoReturn:
        dialog = Preferencias(parent, database)
        dialog.exec_()


def main():
    app = QtWidgets.QApplication(sys.argv)
    Preferencias.get_data(database=ruta_db)
    return app


# revisar cuando pongo otra, poner insetar en vez de otra
if __name__ == '__main__':
    main()
