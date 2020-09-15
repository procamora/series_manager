# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/procamora/Documents/Gestor-Series/app/utils/../../app/views/ui/notificaciones.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(354, 213)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Iconos/Icons/fatcow/Principal.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.checkBox_Telegram = QtWidgets.QCheckBox(Dialog)
        self.checkBox_Telegram.setObjectName("checkBox_Telegram")
        self.gridLayout.addWidget(self.checkBox_Telegram, 0, 0, 1, 1)
        self.lineEdit_Telegram = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_Telegram.setObjectName("lineEdit_Telegram")
        self.gridLayout.addWidget(self.lineEdit_Telegram, 0, 1, 1, 1)
        self.checkBox_PushBullet = QtWidgets.QCheckBox(Dialog)
        self.checkBox_PushBullet.setObjectName("checkBox_PushBullet")
        self.gridLayout.addWidget(self.checkBox_PushBullet, 1, 0, 1, 1)
        self.lineEdit_PushBullet = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_PushBullet.setObjectName("lineEdit_PushBullet")
        self.gridLayout.addWidget(self.lineEdit_PushBullet, 1, 1, 1, 1)
        self.checkBox_Email = QtWidgets.QCheckBox(Dialog)
        self.checkBox_Email.setObjectName("checkBox_Email")
        self.gridLayout.addWidget(self.checkBox_Email, 2, 0, 1, 1)
        self.lineEdit_Email = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_Email.setObjectName("lineEdit_Email")
        self.gridLayout.addWidget(self.lineEdit_Email, 2, 1, 1, 1)
        self.checkBox_Hangouts = QtWidgets.QCheckBox(Dialog)
        self.checkBox_Hangouts.setObjectName("checkBox_Hangouts")
        self.gridLayout.addWidget(self.checkBox_Hangouts, 3, 0, 1, 1)
        self.lineEdit_Hangouts = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_Hangouts.setObjectName("lineEdit_Hangouts")
        self.gridLayout.addWidget(self.lineEdit_Hangouts, 3, 1, 1, 1)
        self.WidgetBotones = QtWidgets.QWidget(Dialog)
        self.WidgetBotones.setObjectName("WidgetBotones")
        self.LayoutBotones = QtWidgets.QHBoxLayout(self.WidgetBotones)
        self.LayoutBotones.setObjectName("LayoutBotones")
        self.label_Info = QtWidgets.QLabel(self.WidgetBotones)
        self.label_Info.setText("")
        self.label_Info.setObjectName("label_Info")
        self.LayoutBotones.addWidget(self.label_Info)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.LayoutBotones.addItem(spacerItem)
        self.pushButtonAplicar = QtWidgets.QPushButton(self.WidgetBotones)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/Iconos/Icons/fatcow/accept_button.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonAplicar.setIcon(icon1)
        self.pushButtonAplicar.setObjectName("pushButtonAplicar")
        self.LayoutBotones.addWidget(self.pushButtonAplicar)
        self.pushButtonCerrar = QtWidgets.QPushButton(self.WidgetBotones)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/Iconos/Icons/fatcow/cancel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonCerrar.setIcon(icon2)
        self.pushButtonCerrar.setObjectName("pushButtonCerrar")
        self.LayoutBotones.addWidget(self.pushButtonCerrar)
        self.pushButtonAceptar = QtWidgets.QPushButton(self.WidgetBotones)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/Iconos/Icons/fatcow/file_save_as.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonAceptar.setIcon(icon3)
        self.pushButtonAceptar.setObjectName("pushButtonAceptar")
        self.LayoutBotones.addWidget(self.pushButtonAceptar)
        self.gridLayout.addWidget(self.WidgetBotones, 4, 0, 1, 2)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Notificaciones"))
        self.checkBox_Telegram.setText(_translate("Dialog", "Telegram"))
        self.checkBox_PushBullet.setText(_translate("Dialog", "PushBullet"))
        self.checkBox_Email.setText(_translate("Dialog", "Email"))
        self.checkBox_Hangouts.setText(_translate("Dialog", "Hangouts"))
        self.pushButtonAplicar.setText(_translate("Dialog", "Aplicar"))
        self.pushButtonCerrar.setText(_translate("Dialog", "Cerrar"))
        self.pushButtonAceptar.setText(_translate("Dialog", "Aceptar"))


import fatcow_rc


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
