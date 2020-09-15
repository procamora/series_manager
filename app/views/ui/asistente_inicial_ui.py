# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/procamora/Documents/Gestor-Series/app/utils/../../app/views/ui/asistente_inicial.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(385, 124)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Iconos/Icons/fatcow/Principal.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.WidgetBotones = QtWidgets.QWidget(Dialog)
        self.WidgetBotones.setObjectName("WidgetBotones")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.WidgetBotones)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(self.WidgetBotones)
        self.label.setText("")
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.pushButtonAplicar = QtWidgets.QPushButton(self.WidgetBotones)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/Iconos/Icons/fatcow/accept_button.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonAplicar.setIcon(icon1)
        self.pushButtonAplicar.setObjectName("pushButtonAplicar")
        self.horizontalLayout_2.addWidget(self.pushButtonAplicar)
        self.pushButtonCerrar = QtWidgets.QPushButton(self.WidgetBotones)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/Iconos/Icons/fatcow/cancel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonCerrar.setIcon(icon2)
        self.pushButtonCerrar.setObjectName("pushButtonCerrar")
        self.horizontalLayout_2.addWidget(self.pushButtonCerrar)
        self.pushButtonAceptar = QtWidgets.QPushButton(self.WidgetBotones)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/Iconos/Icons/fatcow/file_save_as.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonAceptar.setIcon(icon3)
        self.pushButtonAceptar.setObjectName("pushButtonAceptar")
        self.horizontalLayout_2.addWidget(self.pushButtonAceptar)
        self.gridLayout.addWidget(self.WidgetBotones, 2, 0, 1, 1)
        self.Widget1 = QtWidgets.QWidget(Dialog)
        self.Widget1.setObjectName("Widget1")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.Widget1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButtonRuta = QtWidgets.QPushButton(self.Widget1)
        self.pushButtonRuta.setMaximumSize(QtCore.QSize(35, 16777215))
        self.pushButtonRuta.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/Iconos/Icons/fatcow/folder_search.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonRuta.setIcon(icon4)
        self.pushButtonRuta.setObjectName("pushButtonRuta")
        self.horizontalLayout.addWidget(self.pushButtonRuta)
        self.lineRuta = QtWidgets.QLineEdit(self.Widget1)
        self.lineRuta.setEnabled(False)
        self.lineRuta.setObjectName("lineRuta")
        self.horizontalLayout.addWidget(self.lineRuta)
        self.gridLayout.addWidget(self.Widget1, 1, 0, 1, 1)
        self.WidgetDir = QtWidgets.QWidget(Dialog)
        self.WidgetDir.setObjectName("WidgetDir")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.WidgetDir)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.checkBoxSync = QtWidgets.QCheckBox(self.WidgetDir)
        self.checkBoxSync.setObjectName("checkBoxSync")
        self.horizontalLayout_3.addWidget(self.checkBoxSync)
        self.checkBoxValido = QtWidgets.QCheckBox(self.WidgetDir)
        self.checkBoxValido.setEnabled(False)
        self.checkBoxValido.setObjectName("checkBoxValido")
        self.horizontalLayout_3.addWidget(self.checkBoxValido)
        self.gridLayout.addWidget(self.WidgetDir, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.checkBoxSync, self.pushButtonRuta)
        Dialog.setTabOrder(self.pushButtonRuta, self.lineRuta)
        Dialog.setTabOrder(self.lineRuta, self.pushButtonAplicar)
        Dialog.setTabOrder(self.pushButtonAplicar, self.pushButtonCerrar)
        Dialog.setTabOrder(self.pushButtonCerrar, self.pushButtonAceptar)
        Dialog.setTabOrder(self.pushButtonAceptar, self.checkBoxValido)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.pushButtonAplicar.setText(_translate("Dialog", "Aplicar"))
        self.pushButtonCerrar.setText(_translate("Dialog", "Cerrar"))
        self.pushButtonAceptar.setText(_translate("Dialog", "Aceptar"))
        self.checkBoxSync.setText(_translate("Dialog", "Directorio instalacion personalizada"))
        self.checkBoxValido.setText(_translate("Dialog", "Valido"))


import fatcow_rc


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
