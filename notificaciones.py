#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

from PyQt5 import QtWidgets

from ui.notificaciones_ui import Ui_Dialog
from modulos.connect_sqlite import conectionSQLite, ejecutaScriptSqlite
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
        self.setWindowTitle('Notificaciones de la aplicacion')

        self.__operacionesIniciales()

        self.ui.checkBox_Telegram.clicked.connect(lambda
            x=self.ui.checkBox_Telegram,
            y=self.ui.lineEdit_Telegram: self.__compruebaCheck(x, y))

        self.ui.checkBox_PushBullet.clicked.connect(lambda
            x=self.ui.checkBox_PushBullet,
            y=self.ui.lineEdit_PushBullet: self.__compruebaCheck(x, y))

        self.ui.checkBox_Email.clicked.connect(lambda
            x=self.ui.checkBox_Email,
            y=self.ui.lineEdit_Email: self.__compruebaCheck(x, y))

        self.ui.checkBox_Hangouts.clicked.connect(lambda
            x=self.ui.checkBox_Hangouts,
            y=self.ui.lineEdit_Hangouts: self.__compruebaCheck(x, y))

        self.ui.pushButtonAplicar.clicked.connect(self.__aplicaDatos)
        self.ui.pushButtonCerrar.clicked.connect(self.__cancela)
        self.ui.pushButtonAceptar.clicked.connect(self.__aceptaDatos)


    def __compruebaCheck(self, a, b):
        '''
        Compruueba se hay un check en el campo a y si lo hay desabilita el campo de texto b
        '''

        if a:
            b.setDisabled(False)
        else:
            b.setDisabled(True)


    def __operacionesIniciales(self):
        '''
        Ejecuta las 2 funciones necesarias para que funcione el programa,
        sacar los datos e introducirlos a la gui
        '''
        self.__sacaDatos()
        self.__averiguaConf()


    def __sacaDatos(self):
        '''
        Ejecuta la consulta
        '''

        query = 'SELECT * FROM Notificaciones'
        self.DatodDb = conectionSQLite(self.db, query, True)


    def __averiguaConf(self):
        '''
        Con la lista de la bd pone los datos en la gui
        '''

        for i in self.DatodDb:

            if modo_debug:
                print(i)

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
                    #self.lineEdit_PushBullet.setDisabled(False)
                else:
                    #self.checkBox_PushBullet.setChecked(False)
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


    def __aplicaDatos(self):
        '''
        Creo un diccionario con todos los datos y voy ejecutando los updates,
        si el campo de la api es None o NULL hago que ponfga el campo NULL en la bd
        '''

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
                query += '''\nUPDATE Notificaciones SET API=NULL, Activo="{}"
                WHERE Nombre LIKE "{}";'''.format(i['Activo'], i['Nombre'])
            else:
                query += '''\nUPDATE Notificaciones SET API="{}", Activo="{}"
                WHERE Nombre LIKE "{}";'''.format(i['API'], i['Activo'], i['Nombre'])

        if modo_debug:
            print(query)

        ejecutaScriptSqlite(self.db, query)
        return True


    def __cancela(self):
        '''
        Establece el estado actual en cancelado para retornar None y ejecuta reject
        '''

        self.EstadoA = self.EstadoF
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

# revisar cuando pongo Otra, poner insetar en vez de otra
if __name__ == '__main__':
    main()
