# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/procamora/Documents/Gestor-Series/app/utils/../../app/views/ui/buscar_series.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(332, 349)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Iconos/Icons/fatcow/Principal.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.widget = QtWidgets.QWidget(Dialog)
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.widget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.lineEdit = QtWidgets.QLineEdit(self.widget)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.pushButtonBuscar = QtWidgets.QPushButton(self.widget)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/Iconos/Icons/fatcow/folder_search.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonBuscar.setIcon(icon1)
        self.pushButtonBuscar.setObjectName("pushButtonBuscar")
        self.horizontalLayout.addWidget(self.pushButtonBuscar)
        self.gridLayout.addWidget(self.widget, 0, 0, 1, 1)
        self.widget_2 = QtWidgets.QWidget(Dialog)
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButtonAplicar = QtWidgets.QPushButton(self.widget_2)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/Iconos/Icons/fatcow/page_edit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonAplicar.setIcon(icon2)
        self.pushButtonAplicar.setObjectName("pushButtonAplicar")
        self.horizontalLayout_2.addWidget(self.pushButtonAplicar)
        self.pushButtonCerrar = QtWidgets.QPushButton(self.widget_2)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/Iconos/Icons/fatcow/cancel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonCerrar.setIcon(icon3)
        self.pushButtonCerrar.setObjectName("pushButtonCerrar")
        self.horizontalLayout_2.addWidget(self.pushButtonCerrar)
        self.gridLayout.addWidget(self.widget_2, 2, 0, 1, 1, QtCore.Qt.AlignRight)
        self.listWidget = QtWidgets.QListWidget(Dialog)
        self.listWidget.setObjectName("listWidget")
        self.gridLayout.addWidget(self.listWidget, 1, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "Serie a buscar"))
        self.pushButtonBuscar.setText(_translate("Dialog", "Buscar"))
        self.pushButtonAplicar.setText(_translate("Dialog", "Editar"))
        self.pushButtonCerrar.setText(_translate("Dialog", "Cerrar"))


import fatcow_rc


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
