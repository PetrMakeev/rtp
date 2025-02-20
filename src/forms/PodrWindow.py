
from PyQt6.QtWidgets import (QMainWindow,
                             QTableView, 
                             QMenu, QMessageBox, QFileDialog)
from PyQt6 import (QtCore, 
                   QtGui, 
                   QtWidgets)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QCursor, QAction, QIcon

from os import path, getcwd, remove
from datetime import datetime

from src.ui.ui_podr import Ui_frmPodr
from src.modules.db_local import DB_Local
from src.forms.tableview_podr import PodrTableModel
from src.forms.widget_manager import set_widget_background, check_widget
from src.modules.resource_image import resource_path


class PodrWindow(QMainWindow, Ui_frmPodr):
    def __init__(self, parent=None, *args, obj=None, **kwargs):
        super(PodrWindow, self).__init__(parent, *args, **kwargs) 
        self.setupUi(self)
        
        self.parent = parent
        
        self.curr_podr_id = -1
        self.curr_podr_ord = -1
        
        
        self.mode_edit = None
        self.mode_podr = None
        
        ###################################################
        #  панель грида
        ###################################################
        # настраиваем и заполняем грид
        self.db = DB_Local()
        self.refresh_grid()


        # привязываем контекстное меню к гриду
        self.table.customContextMenuRequested.connect(self.contextMenuEvent)


        ###################################################
        #  панель редактирования
        ###################################################
        # сигнал изменения полей вызывает перекраску полей по условию
        self.txt_podr.textChanged.connect(lambda: check_widget(self.txt_podr, len(self.txt_podr.text().strip()) == 0))

        # кнопка сохранить
        self.btn_save.clicked.connect(self.save_podr)        
        
        # кнопка отмена
        self.btn_cancel.clicked.connect(self.saveno_podr)


    ##############################################################################
    # popup меню грида  с функционалом
    #############################################################################
    # настройка вызова контекстного меню
    def contextMenuEvent(self, point):
        # проверяем чтобы был клик в области строк грида
        if  (type(point) == QtCore.QPoint):
            context_menu = QMenu(self)
            
            if len(self.data_podr) > 0:
                pop_sel = QAction(QIcon(resource_path("icons\\sel.png")), "Выбрать подразделение", self)
                context_menu.addAction(pop_sel)
                pop_sel.triggered.connect(lambda: self.select_podr(self.table.currentIndex().row()))

                context_menu.addSeparator()
            
            
            pop_add = QAction(QIcon(resource_path("icons\\add.png")), "Новое подразделение", self)
            context_menu.addAction(pop_add)
            pop_add.triggered.connect(self.popup_add)
            
            if len(self.data_podr) > 0:
                pop_edit = QAction(QIcon(resource_path("icons\\edit.png")), "Редактировать подразделение", self)
                context_menu.addAction(pop_edit)
                pop_edit.triggered.connect(self.popup_edit)
                
                pop_del = QAction(QIcon(resource_path("icons\\del.png")), "Удалить подразделение", self)
                context_menu.addAction(pop_del)
                pop_del.triggered.connect(self.popup_del)
                
                context_menu.addSeparator()

                kol_row = self.model.rowCount()
                # настраиваем в зависимости от количества записей
                if kol_row > 1 :
                    
                    if self.table.currentIndex().row() > 0 :
                        pop_move_up = QAction(QIcon(resource_path("icons\\up.png")), "Переместить вверх", self)
                        context_menu.addAction(pop_move_up)
                        pop_move_up.triggered.connect(self.popup_move_up)
                
                    if self.table.currentIndex().row() + 1  < kol_row:
                        pop_move_down = QAction(QIcon(resource_path("icons\\down.png")), "Переместить вниз", self)
                        context_menu.addAction(pop_move_down)
                        pop_move_down.triggered.connect(self.popup_move_down)
                    
            
            # context_menu.addSeparator()


            
            context_menu.popup(QCursor.pos())
            
            
    # пункт контекстного меню - добавить
    def popup_add(self, event):
        # очищаем поля
        self.txt_podr.setText("")
        self.curr_podr_id = -1
        self.curr_podr_ord = -1

        # подкрашиваем обязательные поля
        check_widget(self.txt_podr, len(self.txt_podr.text().strip()) == 0)
          
        # переводим в режим добавления
        self.mode_edit = 'ADD'
        self.frm_grid.setVisible(False)            
            
            
    # пункт контекстного меню - изменить
    def popup_edit(self, event):
        curr_row = self.table.currentIndex().row()   
        
        self.curr_podr_id = self.data_podr[curr_row][0]        
        self.txt_podr.setText(self.data_podr[curr_row][1])
        self.curr_podr_ord = self.data_podr[curr_row][2]        
        

        # подкрашиваем обязательные поля
        check_widget(self.txt_podr, len(self.txt_podr.text().strip()) == 0)
          
        # переводим в режим добавления
        self.mode_edit = 'EDIT'
        self.frm_grid.setVisible(False)            
                 
            
    # пункт контекстного меню - удалить
    def popup_del(self, event):
        
        confirmation_dialog = QMessageBox(self)
        confirmation_dialog.setIcon(QMessageBox.Icon.Warning)
        confirmation_dialog.setWindowTitle("Подтверждение")
        confirmation_dialog.setText("Вы уверены, что хотите удалить запись?")
        confirmation_dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        confirmation_dialog.setDefaultButton(QMessageBox.StandardButton.No)

        # Получение ответа пользователя
        user_response = confirmation_dialog.exec()

        if user_response == QMessageBox.StandardButton.Yes:
        # id выбранной строки
            curr_row = self.table.currentIndex().row()
            self.curr_prikaz_id = self.data_podr[curr_row][0] 
            # id выбранной строки после удаления
            curr_row_post_del = (curr_row - 1) if curr_row > 0 else 0 
            curr_id_post_del = self.data_podr[curr_row_post_del][0]  
            self.del_podr(self.curr_prikaz_id, curr_id_post_del)     
            

            
    # пункт контекстного меню - переместить вверх
    def popup_move_up(self, event):
        curr_row = self.table.currentIndex().row()           
        curr_podr_id = self.data_podr[curr_row][0]
        curr_row_up = curr_row - 1
        self.db.ordPodr_swap(self.data_podr[curr_row][0], 
                             self.data_podr[curr_row][2], 
                             self.data_podr[curr_row_up][0], 
                             self.data_podr[curr_row_up][2]
                             )
        self.refresh_grid()
        # Проходим по всем строкам модели для поиска новой позиции отредактированной строки
        for row in range(self.table.model().rowCount(QtCore.QModelIndex())):
            index = self.model.index(row, 0)  # Предполагаем, что id находится в первом столбце
            if self.model.data(index, Qt.ItemDataRole.DisplayRole) == curr_podr_id:
                self.table.setCurrentIndex(index)
                self.table.scrollTo(index)  # Прокрутить до выделенной строки        
          
    # пункт контекстного меню - переместить вниз
    def popup_move_down(self, event):
        curr_row = self.table.currentIndex().row()           
        curr_podr_id = self.data_podr[curr_row][0]
        curr_row_down = curr_row + 1
        self.db.ordPodr_swap(self.data_podr[curr_row][0], 
                             self.data_podr[curr_row][2], 
                             self.data_podr[curr_row_down][0], 
                             self.data_podr[curr_row_down][2]
                             )
        self.refresh_grid()
        # Проходим по всем строкам модели для поиска новой позиции отредактированной строки
        for row in range(self.table.model().rowCount(QtCore.QModelIndex())):
            index = self.model.index(row, 0)  # Предполагаем, что id находится в первом столбце
            if self.model.data(index, Qt.ItemDataRole.DisplayRole) == curr_podr_id:
                self.table.setCurrentIndex(index)
                self.table.scrollTo(index)  # Прокрутить до выделенной строки  
            

    ##############################################################################
    # добавление, сохранение, удаление записей
    #############################################################################
    # сохранение сведение о приказе  
    def save_podr(self):
        
        podr_dubplicate = False
        # проверка на дубликат
        for row in self.data_podr:
            if str(row[1]).upper().strip() == self.txt_podr.text().upper().strip():
                podr_dubplicate = True
                
            if podr_dubplicate and self.mode_edit == "ADD":
                info_dialog = QMessageBox(self)
                info_dialog.setIcon(QMessageBox.Icon.Information)
                info_dialog.setWindowTitle("Сохранение отменено!")
                info_dialog.setText(f"Подразделение {self.txt_podr.text()} есть в базе данных.")
                info_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
                info_dialog.exec()
                return
        
        # проверяем заполнение полей
        if len(self.txt_podr.text().strip()) == 0:
            self.txt_podr.setFocus()
            return
 

        # сохраняем данные                        
        if self.mode_edit == 'ADD':
            podr = {
                "id"          : -1,
                "podr"  : self.txt_podr.text(),
                "ord"   : -1
            }  
            
        elif self.mode_edit == 'EDIT':
            podr = {
                "id"          : self.curr_podr_id,
                "podr"  : self.txt_podr.text(),
                "ord"   : self.curr_podr_ord
            }    
        else:
            return

        # обновляем грид
        self.db.podr_save(podr=podr)
        self.refresh_grid()

        
        # Восстанавливаем текущую позицию
        if self.mode_edit == "ADD":
            # определяем новый id приказа после добавления
            self.curr_podr_id = max(row[0] for row in self.data_podr)
        
        # Проходим по всем строкам модели для поиска новой позиции отредактированной строки
        for row in range(self.table.model().rowCount(QtCore.QModelIndex())):
            index = self.model.index(row, 0)  # Предполагаем, что id находится в первом столбце
            if self.model.data(index, Qt.ItemDataRole.DisplayRole) == self.curr_podr_id:
                self.table.setCurrentIndex(index)
                self.table.scrollTo(index)  # Прокрутить до выделенной строки
            
        # выключаем режим редактирования
        self.mode_edit = 'NONE'
        self.frm_grid.setVisible(True)
        self.table.setFocus()




    # удаление подразделения  
    def del_podr(self, curr_id, curr_id_post):
        # проверяем подразделения связанные с сотрудниками
        if len(self.db.check_rtp_on_podr(curr_id))>0:
            info_dialog = QMessageBox(self)
            info_dialog.setIcon(QMessageBox.Icon.Information)
            info_dialog.setWindowTitle("Удаление отменено!")
            info_dialog.setText("Данное подразделение используется.")
            info_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
            info_dialog.exec()
            return
        
        # обновляем грид
        self.db.podr_del(curr_id)
        self.refresh_grid()
        
        
        # Проходим по всем строкам модели для поиска новой позиции отредактированной строки
        for row in range(self.table.model().rowCount(QtCore.QModelIndex())):
            index = self.model.index(row, 0)  # Предполагаем, что id находится в первом столбце
            if self.model.data(index, Qt.ItemDataRole.DisplayRole) == curr_id_post:
                #self.table.setCurrentIndex(index)
                self.table.scrollTo(index)  # Прокрутить до выделенной строки
            
        # выключаем режим редактирования
        self.mode_edit = 'NONE'
        self.frm_grid.setVisible(True)
        self.table.setFocus()
            
        
        
    # отмена  сохранения
    def saveno_podr(self):
        self.mode_edit = "NONE"
        self.frm_grid.setVisible(True)     






    ##############################################################################
    # выбор подразделения и передача сведений о нем в основную форму  
    #############################################################################      
    def select_podr(self, row):
        if not (self.mode_podr == "FILTER"):
            # передаем сведения о подразделении в основное окно
            if self.parent:
                self.parent.update_edit_from_podr(self.data_podr[row][0], 
                                                    self.data_podr[row][1])
        else:
            # передаем сведения о подразделении в фильтры
            if self.parent:
                self.parent.update_filter_from_podr(self.data_podr[row][0], 
                                                      self.data_podr[row][1])
        self.hide()
        




    ########################################################################################
    # обновляем грид
    ######################################################################################   
    def refresh_grid(self):
        # обновляем данные        
        self.data_podr = self.db.read_podr()
        self.model = PodrTableModel(self.data_podr, ["id", "Подразделение", " "])
        self.table.setModel(self.model)
        # ширина столбцов
        self.table.setColumnWidth(0, 0)
        self.table.setColumnWidth(1, 300)
        self.table.setColumnWidth(2, 0)

        
        # режим выделения = строка целиком
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)  
        self.model.layoutChanged.emit()                



    ########################################################################################
    # событие перед закрытием приложения
    ######################################################################################   

    def closeEvent(self, event):
        

        if self.mode_edit == "NONE":
            event.accept()
        else:
            self.saveno_podr()
