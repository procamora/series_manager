#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from typing import NoReturn, List

from PyQt5 import QtWidgets
from app.views.ui.notificaciones_ui import Ui_Dialog

import app.controller.Controller as Controller
from app.models.model_notifications import Notifications
from app.models.model_query import Query
from app.modulos.settings import PATH_DATABASE


class Notificaciones(QtWidgets.QDialog):
    def __init__(self, parent: object = None, database: str = None) -> NoReturn:
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.other = 'otra'  # campo otra del formulario
        self.state_ok = 'Ok'  # estado inicial
        self.state_cancel = 'Cancelado'  # final
        self.state_current = self.state_ok  # actual
        self.db = database
        self.setWindowTitle('Notificaciones de la aplicacion')

        self.notifications: List[Notifications] = list()
        self.initial_operations()

        self.ui.checkBox_Telegram.clicked.connect(
            lambda x=self.ui.checkBox_Telegram, y=self.ui.lineEdit_Telegram: self.check_field_check(x, y))

        self.ui.checkBox_PushBullet.clicked.connect(
            lambda x=self.ui.checkBox_PushBullet, y=self.ui.lineEdit_PushBullet: self.check_field_check(x, y))

        self.ui.checkBox_Email.clicked.connect(
            lambda x=self.ui.checkBox_Email, y=self.ui.lineEdit_Email: self.check_field_check(x, y))

        self.ui.checkBox_Hangouts.clicked.connect(
            lambda x=self.ui.checkBox_Hangouts, y=self.ui.lineEdit_Hangouts: self.check_field_check(x, y))

        self.ui.pushButtonAplicar.clicked.connect(self.apply_data)
        self.ui.pushButtonCerrar.clicked.connect(self.cancel)
        self.ui.pushButtonAceptar.clicked.connect(self.accept_data)

    @staticmethod
    def check_field_check(a: QtWidgets.QCheckBox, b: QtWidgets.QCheckBox) -> NoReturn:
        """
        Compruueba se hay un check en el campo a y si lo hay desabilita el campo de texto b
        """
        b.setDisabled(False) if a else b.setDisabled(True)
        # if a:
        #    b.setDisabled(False)
        # else:
        #    b.setDisabled(True)

    def initial_operations(self) -> NoReturn:
        """
        Ejecuta las 2 funciones necesarias para que funcione el programa,
        sacar los datos e introducirlos a la views
        """
        response_query: Query = Controller.get_notifications(self.db)
        print(response_query.response)
        self.notifications = response_query.response
        print(self.notifications)
        self.get_configuration()

    def get_configuration(self) -> NoReturn:
        """
        Con la lista de la bd pone los datos en la views
        """
        for notification in self.notifications:
            print(notification)
            if notification.api != 'None':
                api = notification.api
            else:
                api = ''

            if notification.name == 'Telegram':
                self.ui.lineEdit_Telegram.setText(api)
                if notification.active:
                    self.ui.checkBox_Telegram.setChecked(True)
                else:
                    self.ui.lineEdit_Telegram.setDisabled(True)

            elif notification.name == 'Pushbullet':
                self.ui.lineEdit_PushBullet.setText(api)
                if notification.active:
                    self.ui.checkBox_PushBullet.setChecked(True)
                    # self.lineEdit_PushBullet.setDisabled(False)
                else:
                    # self.checkBox_PushBullet.setChecked(False)
                    self.ui.lineEdit_PushBullet.setDisabled(True)

            elif notification.name == 'Email':
                self.ui.lineEdit_Email.setText(api)
                if notification.active:
                    self.ui.checkBox_Email.setChecked(True)
                else:
                    self.ui.lineEdit_Email.setDisabled(True)

            elif notification.name == 'Hangouts':
                self.ui.lineEdit_Hangouts.setText(api)
                if notification.active:
                    self.ui.checkBox_Hangouts.setChecked(True)
                else:
                    self.ui.lineEdit_Hangouts.setDisabled(True)

    def apply_data(self) -> bool:
        """
        Creo una lista con todos los datos y voy ejecutando los updates,
        si el campo de la api es None o NULL hago que ponga el campo NULL en la bd
        """
        list_notifications: List[Notifications] = list()
        notifications: Notifications = Notifications()
        notifications.name = 'Telegram'
        notifications.api = self.ui.lineEdit_Telegram.text()
        notifications.active = str(self.ui.checkBox_Telegram.isChecked())
        list_notifications.append(notifications)

        notifications: Notifications = Notifications()
        notifications.name = 'Pushbullet'
        notifications.api = self.ui.lineEdit_PushBullet.text()
        notifications.active = str(self.ui.checkBox_PushBullet.isChecked())
        list_notifications.append(notifications)

        notifications: Notifications = Notifications()
        notifications.name = 'Email'
        notifications.api = self.ui.lineEdit_Email.text()
        notifications.active = str(self.ui.checkBox_Email.isChecked())
        list_notifications.append(notifications)

        notifications: Notifications = Notifications()
        notifications.name = 'Hangouts'
        notifications.api = self.ui.lineEdit_Hangouts.text()
        notifications.active = str(self.ui.checkBox_Hangouts.isChecked())
        list_notifications.append(notifications)

        Controller.update_notifications(list_notifications, self.db)
        return True

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
        dialog = Notificaciones(parent, database)
        dialog.exec_()


def main():
    app = QtWidgets.QApplication(sys.argv)
    Notificaciones.get_data(database=PATH_DATABASE)
    return app


# revisar cuando pongo otra, poner insetar en vez de otra
if __name__ == '__main__':
    main()
