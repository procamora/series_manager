#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from typing import NoReturn, Dict

from PyQt5 import QtWidgets
from app.views.ui.msgbox_ui import Ui_Dialog


class MsgBox(QtWidgets.QDialog):
    def __init__(self, parent: object = None, datos: str = None) -> NoReturn:
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        if datos is not None:
            self.datos = datos
        else:
            self.datos = {
                'title': 'titulo para cambiar', 'text': 'Texto a cambiar'}

        self.setWindowTitle(self.datos['title'])

        # self.plainTextEdit.appendPlainText(self.datos['text'])
        self.ui.plainTextEdit.insertPlainText(self.datos['text'])
        # self.ui.ButtonOk.clicked.connect(self.retornaDatos)

    @staticmethod
    def getData(parent: object = None, datos: Dict = None) -> NoReturn:
        dialog = MsgBox(parent, datos)
        dialog.exec_()


def main():
    app = QtWidgets.QApplication(sys.argv)
    a = """ Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam iaculis turpis eget ex bibendum, \
    et varius arcu vehicula.
Donec cursus nunc eros, quis egestas dolor faucibus eu. Vestibulum malesuada erat in ipsum aliquam, \
vel vestibulum ex sodales. 
Maecenas tristique sed lorem sit amet lacinia. Sed diam dui, vestibulum sit amet pretium vitae, convallis vitae mi. \
Nullam placerat dui ipsum, scelerisque feugiat tellus viverra non. 
Ut vel nibh suscipit risus convallis dictum. Nunc eget lacus justo. Integer feugiat erat at velit feugiat feugiat. \
Donec laoreet nibh eget tortor mattis cursus. 
Morbi consectetur, nibh a facilisis finibus, ex mauris tempus quam, quis placerat risus risus nec ipsum. Sed malesuada \
elit eget magna eleifend, non gravida ipsum mattis. Suspendisse lacinia risus id placerat eleifend.
Nunc fermentum sed quam a ullamcorper. Pellentesque posuere nec lacus nec ultricies. Nunc ornare volutpat diam \
mattis laoreet.

Sed in ante at urna luctus varius. Ut purus ipsum, sollicitudin eu facilisis vel, blandit at leo. Ut vestibulum \
tincidunt tempus.
    """

    res = {'title': 'titulo de prueba', 'text': a}
    # MiFormulario.getData(parent=None, datos=res)
    MsgBox.getData(datos=res)
    return app


if __name__ == '__main__':
    main()
