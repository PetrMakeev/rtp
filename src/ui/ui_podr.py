# Form implementation generated from reading ui file 'ui_podr.ui'
#
# Created by: PyQt6 UI code generator 6.8.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_frmPodr(object):
    def setupUi(self, frmPodr):
        frmPodr.setObjectName("frmPodr")
        frmPodr.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        frmPodr.resize(350, 500)
        frmPodr.setMinimumSize(QtCore.QSize(350, 500))
        frmPodr.setMaximumSize(QtCore.QSize(350, 500))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        frmPodr.setFont(font)
        self.centralwidget = QtWidgets.QWidget(parent=frmPodr)
        self.centralwidget.setObjectName("centralwidget")
        self.frm_grid = QtWidgets.QFrame(parent=self.centralwidget)
        self.frm_grid.setGeometry(QtCore.QRect(5, 5, 340, 490))
        self.frm_grid.setAutoFillBackground(True)
        self.frm_grid.setFrameShape(QtWidgets.QFrame.Shape.Panel)
        self.frm_grid.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frm_grid.setObjectName("frm_grid")
        self.table = QtWidgets.QTableView(parent=self.frm_grid)
        self.table.setGeometry(QtCore.QRect(5, 5, 330, 480))
        self.table.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.setObjectName("table")
        self.frm_edit = QtWidgets.QFrame(parent=self.centralwidget)
        self.frm_edit.setGeometry(QtCore.QRect(5, 5, 340, 490))
        self.frm_edit.setAutoFillBackground(True)
        self.frm_edit.setFrameShape(QtWidgets.QFrame.Shape.Panel)
        self.frm_edit.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frm_edit.setObjectName("frm_edit")
        self.txt_podr = QtWidgets.QLineEdit(parent=self.frm_edit)
        self.txt_podr.setGeometry(QtCore.QRect(12, 160, 321, 22))
        self.txt_podr.setObjectName("txt_podr")
        self.lbl_podr = QtWidgets.QLabel(parent=self.frm_edit)
        self.lbl_podr.setGeometry(QtCore.QRect(60, 130, 221, 20))
        self.lbl_podr.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lbl_podr.setObjectName("lbl_podr")
        self.btn_save = QtWidgets.QPushButton(parent=self.frm_edit)
        self.btn_save.setGeometry(QtCore.QRect(70, 240, 93, 28))
        self.btn_save.setObjectName("btn_save")
        self.btn_cancel = QtWidgets.QPushButton(parent=self.frm_edit)
        self.btn_cancel.setGeometry(QtCore.QRect(180, 240, 93, 28))
        self.btn_cancel.setObjectName("btn_cancel")
        self.frm_edit.raise_()
        self.frm_grid.raise_()
        frmPodr.setCentralWidget(self.centralwidget)

        self.retranslateUi(frmPodr)
        QtCore.QMetaObject.connectSlotsByName(frmPodr)
        frmPodr.setTabOrder(self.table, self.txt_podr)
        frmPodr.setTabOrder(self.txt_podr, self.btn_save)
        frmPodr.setTabOrder(self.btn_save, self.btn_cancel)

    def retranslateUi(self, frmPodr):
        _translate = QtCore.QCoreApplication.translate
        frmPodr.setWindowTitle(_translate("frmPodr", "Подразделения"))
        self.lbl_podr.setText(_translate("frmPodr", "Подразделение"))
        self.btn_save.setText(_translate("frmPodr", "Сохранить"))
        self.btn_cancel.setText(_translate("frmPodr", "Отмена"))
