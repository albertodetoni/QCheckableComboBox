import PyQt6
from PyQt6.QtWidgets import QComboBox
from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItem
from PyQt6.QtWidgets import QFrame
from typing import Sequence, Union


class QCheckableComboBox(QComboBox):
    currentListChanged = QtCore.pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.closeOnLineEditClicked = False

        self.lineEdit().installEventFilter(self)

        self.view().viewport().installEventFilter(self)

        self.model().dataChanged.connect(self.updateLineEditField)

    def eventFilter(self, widget, event):
        if widget == self.lineEdit():
            if event.type() == QFrame.mouseReleaseEvent:
                if self.closedOnLineEditClick:
                    self.hidePopup()  # TODO
                else:
                    self.showPopup()
                return True
            return super().eventFilter(widget, event)
        if widget == self.view().viewport():
            if event.type() == QFrame.mouseReleaseEvent:
                indx = self.view().indexAt(event.pos())
                item = self.model().item(indx.row())

                if item.checkState() == Qt.CheckState.Checked:
                    item.setCheckState(Qt.CheckState.Unchecked)
                else:
                    item.setCheckState(Qt.CheckState.Checked)
                return True
            return super().eventFilter(widget, event)

    def hidePopup(self):
        super().hidePopup()
        self.startTimer(100)

    def addItems(self, items, itemList=None):
        for indx, text in enumerate(items):
            if itemList != None:
                data = itemList[indx]
            else:
                data = None
            self.addItem(text, data)

    def addItem(self, text: str, userData=None):
        item = QStandardItem()
        item.setText(text)
        if not userData is None:
            item.setData(userData)

        # enable checkbox setting
        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
        item.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
        self.model().appendRow(item)

    def setItemCheckState(self, value: Union[str, int, Sequence[Union[str, int]]], state: bool):
        '''
            Set item check-state by text(str) or index(int) or set a list of items check-states by list of text(str) or list of indices(int).\n
            Args:
                - value: str, int, list
                - state: bool
        '''
        if not isinstance(state, bool) or not isinstance(value, (str, int, list)):
            raise TypeError('Wrong data type passed to QCheckableComboBox.setItemCheckState')

        if isinstance(value, int):
            if value < 0 or value >= len(self.count()):
                raise ValueError('Index exceeding bounds in QCheckableComboBox.setItemCheckState')
            item = self.model().item(value)
            if state == False:
                item.setCheckState(Qt.CheckState.Unchecked)
            else:
                item.setCheckState(Qt.CheckState.Checked)
        elif isinstance(value, str):
            item_texts = [self.itemText(i) for i in range(self.count())]
            index = -1
            for i in range(len(item_texts)):
                if value == item_texts[i]:
                    index = i
                    break
            if index < 0 or index >= self.count():
                raise ValueError('ItemText not found in QCheckableComboBox.setItemCheckState')
            item = self.model().item(index)
            if state == False:
                item.setCheckState(Qt.CheckState.Unchecked)
            else:
                item.setCheckState(Qt.CheckState.Checked)
        elif isinstance(value, list):
            for val in value:
                self.setItemCheckState(val, state)

    def updateLineEditField(self):
        text_container = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.CheckState.Checked:
                text_container.append(self.model().item(i).text())
        text_string = ','.join(text_container)
        self.lineEdit().setText(text_string)
        self.currentListChanged.emit()
