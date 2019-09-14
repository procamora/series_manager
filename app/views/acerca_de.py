#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from typing import NoReturn

from PyQt5 import QtGui, QtWidgets

from app.views.ui.acerca_de_ui import Ui_Dialog


class AcercaDe(QtWidgets.QDialog):
    def __init__(self, parent=None) -> NoReturn:
        # super(MiFormulario, self).__init__()
        # uic.loadUi('ui/AcercaDe.ui', self)
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.setWindowTitle('Acerca de')

        self.ui.tabWidget.setCurrentIndex(0)

        pixmap = QtGui.QPixmap('Icons/personal.png')
        self.ui.label_imagen.setPixmap(pixmap)

        texto = """
<html>
    <head>
    <head/>
    <body>
        <p>Version 2.1.0</p>
        <p>Python 3.5.3</p>
        <p>PyQt Version 5.7.4</p>
        <p>Qt Version 5.7.1</p>
        <p><br/></p>
        <p>&#169; 2019 Pablo Rocamora All Rights Reserved</p>
        <p>
            <a href="mailto:pablojoserocamora@gmail.com">pablojoserocamora@gmail.com</a>
        </p>
        <p><br/>Este es un programa para gestionar series<br/></p>
    </body>
</html>"""
        self.ui.label_info.setText(texto)

        self.ui.pushButtonClose.clicked.connect(self.close)

    @staticmethod
    def getDatos(parent=None) -> NoReturn:
        dialog = AcercaDe(parent)
        dialog.exec_()


def main():
    app = QtWidgets.QApplication(sys.argv)
    AcercaDe.getDatos()

    return app


if __name__ == '__main__':
    main()
