# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/listar_todas.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(768, 458)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Iconos/Icons/fatcow/Principal.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.gridLayout_2 = QtWidgets.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        spacerItem = QtWidgets.QSpacerItem(20, 102, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 0, 1, 1, 1)
        self.widget = QtWidgets.QWidget(Dialog)
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.radioButtonEmpieza = QtWidgets.QRadioButton(self.widget)
        self.radioButtonEmpieza.setObjectName("radioButtonEmpieza")
        self.verticalLayout.addWidget(self.radioButtonEmpieza)
        self.radioButtonEspera = QtWidgets.QRadioButton(self.widget)
        self.radioButtonEspera.setObjectName("radioButtonEspera")
        self.verticalLayout.addWidget(self.radioButtonEspera)
        self.radioButtonAcabaT = QtWidgets.QRadioButton(self.widget)
        self.radioButtonAcabaT.setObjectName("radioButtonAcabaT")
        self.verticalLayout.addWidget(self.radioButtonAcabaT)
        self.radioButtonFinalizada = QtWidgets.QRadioButton(self.widget)
        self.radioButtonFinalizada.setObjectName("radioButtonFinalizada")
        self.verticalLayout.addWidget(self.radioButtonFinalizada)
        self.gridLayout_2.addWidget(self.widget, 1, 1, 1, 1)
        self.pushButtonAnadir = QtWidgets.QPushButton(Dialog)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/Iconos/Icons/fatcow/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonAnadir.setIcon(icon1)
        self.pushButtonAnadir.setObjectName("pushButtonAnadir")
        self.gridLayout_2.addWidget(self.pushButtonAnadir, 2, 1, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 158, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem1, 3, 1, 1, 1)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.widget_2 = QtWidgets.QWidget(Dialog)
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.radioButtonAct = QtWidgets.QRadioButton(self.widget_2)
        self.radioButtonAct.setChecked(True)
        self.radioButtonAct.setObjectName("radioButtonAct")
        self.horizontalLayout.addWidget(self.radioButtonAct)
        self.radioButtonTemp = QtWidgets.QRadioButton(self.widget_2)
        self.radioButtonTemp.setObjectName("radioButtonTemp")
        self.horizontalLayout.addWidget(self.radioButtonTemp)
        self.radioButtonPausada = QtWidgets.QRadioButton(self.widget_2)
        self.radioButtonPausada.setObjectName("radioButtonPausada")
        self.horizontalLayout.addWidget(self.radioButtonPausada)
        self.radioButtonTodas = QtWidgets.QRadioButton(self.widget_2)
        self.radioButtonTodas.setObjectName("radioButtonTodas")
        self.horizontalLayout.addWidget(self.radioButtonTodas)
        self.pushButtonRefresh = QtWidgets.QPushButton(self.widget_2)
        self.pushButtonRefresh.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/Iconos/Icons/fatcow/arrow_refresh.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonRefresh.setIcon(icon2)
        self.pushButtonRefresh.setObjectName("pushButtonRefresh")
        self.horizontalLayout.addWidget(self.pushButtonRefresh)
        self.gridLayout.addWidget(self.widget_2, 0, 0, 1, 1)
        self.listWidget = QtWidgets.QListWidget(Dialog)
        self.listWidget.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
        self.listWidget.setLayoutMode(QtWidgets.QListView.Batched)
        self.listWidget.setSelectionRectVisible(False)
        self.listWidget.setObjectName("listWidget")
        self.gridLayout.addWidget(self.listWidget, 1, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 4, 1)
        self.WidgetBotones = QtWidgets.QWidget(Dialog)
        self.WidgetBotones.setObjectName("WidgetBotones")
        self.LayoutBotones = QtWidgets.QHBoxLayout(self.WidgetBotones)
        self.LayoutBotones.setContentsMargins(0, 0, 0, 0)
        self.LayoutBotones.setObjectName("LayoutBotones")
        self.label_Info = QtWidgets.QLabel(self.WidgetBotones)
        self.label_Info.setText("")
        self.label_Info.setObjectName("label_Info")
        self.LayoutBotones.addWidget(self.label_Info)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.LayoutBotones.addItem(spacerItem2)
        self.pushButtonAplicar = QtWidgets.QPushButton(self.WidgetBotones)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/Iconos/Icons/fatcow/accept_button.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonAplicar.setIcon(icon3)
        self.pushButtonAplicar.setObjectName("pushButtonAplicar")
        self.LayoutBotones.addWidget(self.pushButtonAplicar)
        self.pushButtonCerrar = QtWidgets.QPushButton(self.WidgetBotones)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/Iconos/Icons/fatcow/cancel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonCerrar.setIcon(icon4)
        self.pushButtonCerrar.setObjectName("pushButtonCerrar")
        self.LayoutBotones.addWidget(self.pushButtonCerrar)
        self.pushButtonAceptar = QtWidgets.QPushButton(self.WidgetBotones)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/Iconos/Icons/fatcow/file_save_as.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonAceptar.setIcon(icon5)
        self.pushButtonAceptar.setObjectName("pushButtonAceptar")
        self.LayoutBotones.addWidget(self.pushButtonAceptar)
        self.gridLayout_2.addWidget(self.WidgetBotones, 4, 0, 1, 2)
        self.widget.raise_()
        self.pushButtonAnadir.raise_()

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.radioButtonEmpieza.setText(_translate("Dialog", "Empieza Temporada"))
        self.radioButtonEspera.setText(_translate("Dialog", "En Espera (Puasar)"))
        self.radioButtonAcabaT.setText(_translate("Dialog", "Temporada Acabada"))
        self.radioButtonFinalizada.setText(_translate("Dialog", "Serie Finalizada"))
        self.pushButtonAnadir.setText(_translate("Dialog", "Añadir"))
        self.radioButtonAct.setText(_translate("Dialog", "Activas"))
        self.radioButtonTemp.setText(_translate("Dialog", "Temporada acabada"))
        self.radioButtonPausada.setText(_translate("Dialog", "En espera(En proceso)"))
        self.radioButtonTodas.setText(_translate("Dialog", "Todas"))
        self.pushButtonAplicar.setText(_translate("Dialog", "Aplicar"))
        self.pushButtonCerrar.setText(_translate("Dialog", "Cerrar"))
        self.pushButtonAceptar.setText(_translate("Dialog", "Aceptar"))

import app.views.ui.fatcow_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

