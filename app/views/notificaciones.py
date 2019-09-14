#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from typing import NoReturn

from PyQt5 import QtWidgets
from app.views.ui.notificaciones_ui import Ui_Dialog

from app import logger
from app.modulos.connect_sqlite import conectionSQLite, ejecutaScriptSqlite
from app.modulos.settings import ruta_db


class Notificaciones(QtWidgets.QDialog):
    def __init__(self, parent: object = None, database: str = None) -> NoReturn:
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.otra = 'otra'  # campo otra del formulario
        self.estadoI = 'Ok'  # estado inicial
        self.estadoF = 'Cancelado'  # final
        self.estadoA = self.estadoI  # actual
        self.db = database
        self.setWindowTitle('Notificaciones de la aplicacion')

        self.datodDb = list(dict())
        self.operacionesIniciales()

        self.ui.checkBox_Telegram.clicked.connect(lambda
                                                      x=self.ui.checkBox_Telegram,
                                                      y=self.ui.lineEdit_Telegram: self.compruebaCheck(x, y))

        self.ui.checkBox_PushBullet.clicked.connect(lambda
                                                        x=self.ui.checkBox_PushBullet,
                                                        y=self.ui.lineEdit_PushBullet: self.compruebaCheck(x, y))

        self.ui.checkBox_Email.clicked.connect(lambda
                                                   x=self.ui.checkBox_Email,
                                                   y=self.ui.lineEdit_Email: self.compruebaCheck(x, y))

        self.ui.checkBox_Hangouts.clicked.connect(lambda
                                                      x=self.ui.checkBox_Hangouts,
                                                      y=self.ui.lineEdit_Hangouts: self.compruebaCheck(x, y))

        self.ui.pushButtonAplicar.clicked.connect(self.aplicaDatos)
        self.ui.pushButtonCerrar.clicked.connect(self.cancela)
        self.ui.pushButtonAceptar.clicked.connect(self.aceptaDatos)

    @staticmethod
    def compruebaCheck(a: QtWidgets.QCheckBox, b: QtWidgets.QCheckBox) -> NoReturn:
        """
        Compruueba se hay un check en el campo a y si lo hay desabilita el campo de texto b
        """

        if a:
            b.setDisabled(False)
        else:
            b.setDisabled(True)

    def operacionesIniciales(self) -> NoReturn:
        """
        Ejecuta las 2 funciones necesarias para que funcione el programa,
        sacar los datos e introducirlos a la views
        """
        self.sacaDatos()
        self.averiguaConf()

    def sacaDatos(self) -> NoReturn:
        """
        Ejecuta la consulta
        """

        query = 'SELECT * FROM Notificaciones'
        self.datodDb = conectionSQLite(self.db, query, True)

    def averiguaConf(self) -> NoReturn:
        """
        Con la lista de la bd pone los datos en la views
        """

        for i in self.datodDb:
            logger.debug(i)

            if len(str(i['API'])) != 'None':
                api = str(i['API'])
            else:
                api = ''

            if i['Nombre'] == 'Telegram':
                self.ui.lineEdit_Telegram.setText(api)
                if i['Activo'] == 'True':
                    self.ui.checkBox_Telegram.setChecked(True)
                else:
                    self.ui.lineEdit_Telegram.setDisabled(True)

            elif i['Nombre'] == 'Pushbullet':
                self.ui.lineEdit_PushBullet.setText(api)
                if i['Activo'] == 'True':
                    self.ui.checkBox_PushBullet.setChecked(True)
                    # self.lineEdit_PushBullet.setDisabled(False)
                else:
                    # self.checkBox_PushBullet.setChecked(False)
                    self.ui.lineEdit_PushBullet.setDisabled(True)

            elif i['Nombre'] == 'Email':
                self.ui.lineEdit_Email.setText(api)
                if i['Activo'] == 'True':
                    self.ui.checkBox_Email.setChecked(True)
                else:
                    self.ui.lineEdit_Email.setDisabled(True)

            elif i['Nombre'] == 'Hangouts':
                self.ui.lineEdit_Hangouts.setText(api)
                if i['Activo'] == 'True':
                    self.ui.checkBox_Hangouts.setChecked(True)
                else:
                    self.ui.lineEdit_Hangouts.setDisabled(True)

    def aplicaDatos(self) -> bool:
        """
        Creo un diccionario con todos los datos y voy ejecutando los updates,
        si el campo de la api es None o NULL hago que ponfga el campo NULL en la bd
        """

        datos = [
            {'Nombre': 'Telegram', 'API': str(self.ui.lineEdit_Telegram.text()),
             'Activo': str(self.ui.checkBox_Telegram.isChecked())},
            {'Nombre': 'Pushbullet', 'API': str(self.ui.lineEdit_PushBullet.text()),
             'Activo': str(self.ui.checkBox_PushBullet.isChecked())},
            {'Nombre': 'Email', 'API': str(self.ui.lineEdit_Email.text()),
             'Activo': str(self.ui.checkBox_Email.isChecked())},
            {'Nombre': 'Hangouts', 'API': str(self.ui.lineEdit_Hangouts.text()),
             'Activo': str(self.ui.checkBox_Hangouts.isChecked())}
        ]
        query = str()
        for i in datos:
            if i['API'] == 'NULL' or i['API'] == 'None':
                query += """\nUPDATE Notificaciones SET API=NULL, Activo="{}" WHERE Nombre LIKE "{}";""".format(
                    i['Activo'], i['Nombre'])
            else:
                query += """\nUPDATE Notificaciones SET API="{}", Activo="{}" WHERE Nombre LIKE "{}";""".format(
                    i['API'], i['Activo'], i['Nombre'])

        logger.debug(query)
        ejecutaScriptSqlite(self.db, query)
        return True

    def cancela(self) -> NoReturn:
        """
        Establece el estado actual en cancelado para retornar None y ejecuta reject
        """

        self.estadoA = self.estadoF
        self.reject()

    def aceptaDatos(self) -> NoReturn:
        """
        Boton Aceptar, primero aplicas los datos, si retorna True, cierra la ventana
        """

        if self.aplicaDatos():
            self.accept()

    @staticmethod
    def get_data(parent: object = None, database: str = None) -> NoReturn:
        dialog = Notificaciones(parent, database)
        dialog.exec_()


def main():
    app = QtWidgets.QApplication(sys.argv)
    Notificaciones.get_data(database=ruta_db)
    return app


# revisar cuando pongo otra, poner insetar en vez de otra
if __name__ == '__main__':
    main()
