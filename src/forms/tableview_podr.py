from datetime import datetime
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt

class PodrTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data, columns):
        super().__init__()
        self._data = data
        self._columns = columns

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                # return f"Column {section + 1}"
                return str(self._columns[section])


    def data(self, index, role):
    
        if not index.isValid():
            return None

        value = self._data[index.row()][index.column()]
        
        # Отображение текста, исключая колонку 3
        if role == Qt.ItemDataRole.DisplayRole and index.column() != 3:
            return value
        
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter
        
        
        return None




    def rowCount(self, index=None):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        if not self._data:
            return 0
        return len(self._data[0])