from PyQt6.QtWidgets import (QMainWindow,
                            QTableView, 
                            QMenu,
                            QComboBox, QMessageBox, QFileDialog
                             )
from PyQt6 import (QtCore, 
                   QtGui, 
                   QtWidgets)
from PyQt6.QtCore import Qt, QDate, QSize
from PyQt6.QtGui import QCursor, QFont, QAction, QIcon, QFontMetrics
from src.ui.ui_main import Ui_MainWindow
from src.modules.filters import  el_zvan, el_obrazov
from src.modules.db_local import DB_Local
from src.forms.tableview_rtp import RtpTableModel
from datetime import datetime
from src.forms.PrikazWindow import PrikazWindow
from src.forms.PodrWindow import PodrWindow
from src.modules.filters_manager import FilterManager
from src.forms.widget_manager import set_widget_background, check_widget
from src.modules.export_xls import export_xls
from src.modules.resource_image import resource_path



class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs) 
        self.setupUi(self)
        
        self.setWindowIcon(QIcon(resource_path("icons\\database.ico")))
        
        # создаем формы приказов и подразделений
        self.w_prikaz = PrikazWindow(parent = self)
        self.w_podr = PodrWindow(parent = self)
        
         # Устанавливаем изображение
        icon = QIcon(resource_path("icons\\print.png"))  # Укажите путь к изображению
        self.btn_print.setIcon(icon)
        self.btn_print.setIconSize(QSize(40 , 40))
        
        # ###################################################
        # #  панель редактирования
        # ###################################################
        # # режим редактирования
        self.mode_edit = 'NONE'
        self.curr_id_rtp = -1 
        self.curr_prikaz_id = -1 # для панели редактирования
        self.filter_prikaz_id = None # для панели грида
        self.curr_podr_id = -1 # для панели редактирования
        self.filter_podr_id = None # для панели грида
        
        
        
        # # заполняем комбобоксы
                
        self.cmb_edit_obrazov.addItems(el_obrazov)
        self.cmb_edit_obrazov.setCurrentIndex(-1)
        
        
        self.cmb_edit_zvan.addItems(el_zvan)
        self.cmb_edit_zvan.setCurrentIndex(-1)
        
        
        # # сигнал изменения полей вызывает перекраску полей по условию
        self.txt_edit_family.textChanged.connect(lambda: check_widget(self.txt_edit_family, len(self.txt_edit_family.text().strip()) == 0))
        self.txt_edit_name.textChanged.connect(lambda: check_widget(self.txt_edit_name, len(self.txt_edit_name.text().strip()) == 0))
        self.txt_edit_lastname.textChanged.connect(lambda: check_widget(self.txt_edit_lastname, len(self.txt_edit_lastname.text().strip()) == 0))
        self.txt_edit_podr.textChanged.connect(lambda: check_widget(self.txt_edit_podr, self.curr_podr_id == -1))
        self.txt_edit_dolzh.textChanged.connect(lambda: check_widget(self.txt_edit_dolzh, len(self.txt_edit_dolzh.text().strip()) == 0))
        self.cmb_edit_zvan.currentIndexChanged.connect(lambda: check_widget(self.cmb_edit_zvan, self.cmb_edit_zvan.currentIndex() < 0))
        self.cmb_edit_obrazov.currentIndexChanged.connect(lambda: check_widget(self.cmb_edit_obrazov, self.cmb_edit_obrazov.currentIndex() < 0))
        self.txt_edit_prikaz.textChanged.connect(lambda: check_widget(self.txt_edit_prikaz, self.curr_prikaz_id == -1))
        self.txt_edit_rezTeor.textChanged.connect(lambda: check_widget(self.txt_edit_rezTeor, self.txt_edit_rezTeor.value() < 1))
        self.txt_edit_rezTech.textChanged.connect(lambda: check_widget(self.txt_edit_rezTech, self.txt_edit_rezTech.value() < 1))
        self.txt_edit_rezFiz.textChanged.connect(lambda: check_widget(self.txt_edit_rezFiz, self.txt_edit_rezFiz.value() < 1))
        self.txt_edit_rezSob.textChanged.connect(lambda: check_widget(self.txt_edit_rezSob, self.txt_edit_rezSob.value() < 1))
        self.txt_edit_rtpDo.dateChanged.connect(lambda: check_widget(self.txt_edit_rtpDo, self.txt_edit_rtpDo.date() <= QDate(2000, 1, 1)))       
        
        
        # вызов формы справочника Приказов из панели редактирования
        self.btn_edit_prikaz.clicked.connect(lambda: self.open_prikaz('EDIT'))
        self.btn_edit_podr.clicked.connect(lambda: self.open_podr('EDIT'))

        # # кнопка сохранить
        self.btn_save.clicked.connect(self.save_rtp)
        
        # кнопка отмена
        self.btn_cancel.clicked.connect(self.saveno_rtp)




        # ##################################################
        #  панель грида
        # ##################################################
        # заполняем комбобоксы фильтров
        self.cmb_obrazov.addItems(el_obrazov)
        self.cmb_obrazov.setCurrentIndex(-1)
        
        self.cmb_zvan.addItems(el_zvan)
        self.cmb_zvan.setCurrentIndex(-1)
        

        # выставляем флаги фильтров
        # Настройка фильтров
        self.filters_config = {
            "podr": False,
            "obrazov": False,
            "zvan": False,
            "prikaz": False,
            "srok_tg": False,
            "srok_end": False,
        }
        self.ui_elements = {
            "btn_podr": self.btn_podr,
            "txt_podr": self.txt_podr,
            "btn_sel_podr": self.btn_sel_podr,
            "btn_obrazov": self.btn_obrazov,
            "cmb_obrazov": self.cmb_obrazov,
            "btn_zvan": self.btn_zvan,
            "cmb_zvan": self.cmb_zvan,
            "btn_prikaz": self.btn_prikaz,
            "txt_prikaz": self.txt_prikaz,
            "btn_sel_prikaz": self.btn_sel_prikaz,
            "btn_dopusk_ist": self.btn_dopusk_ist,
            "btn_dopusk_tg": self.btn_dopusk_tg,
            
        }
        self.filter_manager = FilterManager(self.filters_config, self.ui_elements)        
        
      
        # # приказ выбранной строки
        self.curr_prikaz_id = -1

        # соединяем сигналы клика кнопок флагов фильтров
        # Подключение кнопок к фильтрам
        self.btn_podr.clicked.connect(lambda: self.filter_toggled_set("podr", self.btn_podr.isChecked()))
        self.btn_obrazov.clicked.connect(lambda: self.filter_toggled_set("obrazov", self.btn_obrazov.isChecked()))
        self.btn_zvan.clicked.connect(lambda: self.filter_toggled_set("zvan", self.btn_zvan.isChecked()))
        self.btn_prikaz.clicked.connect(lambda: self.filter_toggled_set("prikaz", self.btn_prikaz.isChecked()))
        self.btn_dopusk_tg.clicked.connect(lambda: self.filter_toggled_set("dopusk_tg", self.btn_dopusk_tg.isChecked()))
        self.btn_dopusk_ist.clicked.connect(lambda: self.filter_toggled_set("dopusk_ist", self.btn_dopusk_ist.isChecked()))
        
        # изменение значений фильтров 
        self.cmb_obrazov.currentIndexChanged.connect(self.filter_set)
        self.cmb_zvan.currentIndexChanged.connect(self.filter_set)
        
        
        # # настраиваем и заполняем грид
        self.db = DB_Local()
        self.filter_set()
        
        
        
        # привязываем контекстное меню к гриду
        self.table.customContextMenuRequested.connect(self.contextMenuEvent)
        
        # вызов формы приказа из панели фильтров
        self.btn_sel_prikaz.clicked.connect(lambda: self.open_prikaz('FILTER'))

        # вызов формы подразделений из панели фильтров
        self.btn_sel_podr.clicked.connect(lambda: self.open_podr('FILTER'))
        
        # # кнопка сохранения в эксель
        self.btn_print.clicked.connect(self.export_xls)

        

    # #############################################################################
    # экспорт в эксель 
    # ############################################################################
    def export_xls(self):
        
        # подразделение
        filter_podr = f" idPodr = {self.filter_podr_id} " if self.filter_podr_id else None
        #образование 
        filter_obrazov = f" obrazov = '{self.cmb_obrazov.currentIndex()}' " if self.cmb_obrazov.currentIndex() > -1 else None
        # звание
        filter_zvan = f" zvanie = '{self.cmb_zvan.currentIndex()}' " if self.cmb_zvan.currentIndex() > -1 else None
        # приказ
        filter_prikaz = f" idPrikaz = {self.filter_prikaz_id} " if self.filter_prikaz_id else None
        # допуск истекает в текущем году
        filter_dopusk_tg = " rtpDo BETWEEN strftime('%Y-01-01', 'now') AND strftime('%Y-12-31', 'now') " if self.btn_dopusk_tg.isChecked() else None
        # сдача просрочена
        filter_dopusk_ist = " DATE(rtpDo) < DATE('now') " if self.btn_dopusk_ist.isChecked() else None

        self.data_export = self.db.read_rtp_export(
                    filter_podr=filter_podr,
                    filter_obrazov=filter_obrazov,
                    filter_zvan=filter_zvan,
                    filter_prikaz=filter_prikaz,
                    filter_dopusk_tg=filter_dopusk_tg,
                    filter_dopusk_ist=filter_dopusk_ist)
        if len(self.data_export) == 0:
            return
        save_path, _ = QFileDialog.getSaveFileName(self, "Сохранить как", "Сведения о", "Excel файл (*.xlsx)")
        if save_path:
            try:
                
                export_xls(self.data_export, save_path)
                
                QMessageBox.information(self, "Успешно", f"Файл {save_path} сохранен.")
            except FileNotFoundError as e:
                QMessageBox.critical(self, "Error", str(e))
        
                # сотрудники, военные, уволенные


        print("export xls")

        
        

    ##############################################################################
    # popup меню грида  с функционалом
    #############################################################################
    # настройка вызова контекстного меню
    def contextMenuEvent(self, point):
        # проверяем чтобы был клик в области строк грида
        if  (type(point) == QtCore.QPoint):
            context_menu = QMenu(self)
            
           
            pop_add = QAction(QIcon(resource_path("icons\\add.png")), "Новая запись", self)
            context_menu.addAction(pop_add)
            pop_add.triggered.connect(self.popup_add)
            
            # если нет записей в гриде отключаем пункты меню
            if self.data_rtp:
                pop_edit = QAction(QIcon(resource_path("icons\\edit.png")), "Изменить запись", self)
                context_menu.addAction(pop_edit)
                pop_edit.triggered.connect(self.popup_edit)
                
                pop_del = QAction(QIcon(resource_path("icons\\del.png")), "Удалить запись", self)
                context_menu.addAction(pop_del)
                pop_del.triggered.connect(self.popup_del)


            context_menu.popup(QCursor.pos())
            
            
    # пункт контекстного меню - добавить
    def popup_add(self, event):
        self.txt_edit_family.clear()
        self.txt_edit_name.clear()
        self.txt_edit_lastname.clear()
        self.curr_podr_id = -1
        self.txt_edit_podr.clear()
        self.txt_edit_dolzh.clear()
        self.cmb_edit_zvan.setCurrentIndex(-1)
        self.cmb_edit_obrazov.setCurrentIndex(-1)
        self.curr_prikaz_id = -1
        self.txt_edit_prikaz.clear()
        self.txt_edit_rezTeor.setValue(0)
        self.txt_edit_rezFiz.setValue(0)
        self.txt_edit_rezTech.setValue(0)
        self.txt_edit_rezSob.setValue(0)
        self.txt_edit_rtpDo.setDate(QDate(2000, 1 , 1))
        
        # подкрашиваем поля
        check_widget(self.txt_edit_family, len(self.txt_edit_family.text().strip()) == 0)
        check_widget(self.txt_edit_name, len(self.txt_edit_name.text().strip()) == 0)
        check_widget(self.txt_edit_lastname, len(self.txt_edit_lastname.text().strip()) == 0)
        check_widget(self.txt_edit_podr, self.curr_podr_id == -1)
        check_widget(self.txt_edit_dolzh, len(self.txt_edit_dolzh.text().strip()) == 0)
        check_widget(self.cmb_edit_zvan, self.cmb_edit_zvan.currentIndex() < 0)
        check_widget(self.cmb_edit_obrazov, self.cmb_edit_obrazov.currentIndex() < 0)
        check_widget(self.txt_edit_rezTeor, self.txt_edit_rezTeor.value() == 0)
        check_widget(self.txt_edit_rezTech, self.txt_edit_rezTech.value() == 0)
        check_widget(self.txt_edit_rezFiz, self.txt_edit_rezFiz.value() == 0)
        check_widget(self.txt_edit_rezSob, self.txt_edit_rezSob.value() == 0)
        check_widget(self.txt_edit_prikaz, self.curr_prikaz_id == -1)
        check_widget(self.txt_edit_rtpDo, self.txt_edit_rtpDo.date() <= QDate(2000, 1, 1))
          
        # переводим в режим добавления
        self.mode_edit = 'ADD'
        self.frm_grid.setVisible(False)
        
        
    # пункт контекстного меню - изменить
    def popup_edit(self, event):    
        curr_row = self.table.currentIndex().row()   
        
        self.curr_id_rtp = self.data_rtp[curr_row][0]
        data = self.db.read_rtp_to_edit(self.curr_id_rtp)
        
        self.txt_edit_family.setText(data[1])
        self.txt_edit_name.setText(data[2])
        self.txt_edit_lastname.setText(data[3])
        self.txt_edit_podr.setText(data[14])
        self.curr_podr_id = data[4]
        self.txt_edit_dolzh.setText(data[5])
        self.cmb_edit_zvan.setCurrentIndex(data[7])
        self.cmb_edit_obrazov.setCurrentIndex(data[6])
        self.txt_edit_prikaz.setText(f'№ {data[15]} от {datetime.strptime(data[16], "%Y-%m-%d").strftime("%d.%m.%Y")}')
        self.curr_prikaz_id = data[12]
        # self.curr_prikaz_dt = datetime.strptime(data[16], "%Y-%m-%d")
        self.txt_edit_rezTeor.setValue(data[8])
        self.txt_edit_rezFiz.setValue(data[10])
        self.txt_edit_rezTech.setValue(data[9])
        self.txt_edit_rezSob.setValue(data[11])
        self.txt_edit_rtpDo.setDate(datetime.strptime(data[13], "%Y-%m-%d"))

        # подкрашиваем поля
        check_widget(self.txt_edit_family, len(self.txt_edit_family.text().strip()) == 0)
        check_widget(self.txt_edit_name, len(self.txt_edit_name.text().strip()) == 0)
        check_widget(self.txt_edit_lastname, len(self.txt_edit_lastname.text().strip()) == 0)
        check_widget(self.txt_edit_podr, self.curr_podr_id == -1)
        check_widget(self.txt_edit_dolzh, len(self.txt_edit_dolzh.text().strip()) == 0)
        check_widget(self.cmb_edit_zvan, self.cmb_edit_zvan.currentIndex() < 0)
        check_widget(self.cmb_edit_obrazov, self.cmb_edit_obrazov.currentIndex() < 0)
        check_widget(self.txt_edit_rezTeor, self.txt_edit_rezTeor.value() == 0)
        check_widget(self.txt_edit_rezTech, self.txt_edit_rezTech.value() == 0)
        check_widget(self.txt_edit_rezFiz, self.txt_edit_rezFiz.value() == 0)
        check_widget(self.txt_edit_rezSob, self.txt_edit_rezSob.value() == 0)
        check_widget(self.txt_edit_prikaz, self.curr_prikaz_id == -1)
        check_widget(self.txt_edit_rtpDo, self.txt_edit_rtpDo.date() <= QDate(2000, 1, 1))
          
        #  переводим в режим редактирования
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
            self.curr_prikaz_id = self.data_rtp[curr_row][0] 
            # id выбранной строки после удаления
            curr_row_post_del = (curr_row - 1) if curr_row > 0 else 0 
            curr_id_post_del = self.data_rtp[curr_row_post_del][0]  

            self.db.rtp_del(self.curr_prikaz_id)

            # обновляем грид
            self.filter_set()

            
            
            # Проходим по всем строкам модели для поиска новой позиции отредактированной строки
            for row in range(self.table.model().rowCount(QtCore.QModelIndex())):
                index = self.model.index(row, 0)  # Предполагаем, что id находится в первом столбце
                if self.model.data(index, Qt.ItemDataRole.DisplayRole) == curr_id_post_del:
                    #self.table.setCurrentIndex(index)
                    self.table.scrollTo(index)  # Прокрутить до выделенной строки
                
            # выключаем режим редактирования
            self.mode_edit = 'NONE'
            self.frm_grid.setVisible(True)
            self.table.setFocus()


        
    # ##############################################################################
    # # получаем состояние флагов фильтров и настраиваем фильтр
    # #############################################################################
    # # управление переключателями фильтра
    def filter_toggled_set(self, filter_name, checked):
        self.filter_manager.toggle_filter(filter_name, checked)
        if not (self.btn_prikaz.isChecked()):
            self.filter_prikaz_id = None
        if not (self.btn_podr.isChecked()):
            self.filter_podr_id = None            
        self.filter_set()
        
       
    
    # # устанавливаем фильтр и выставляем указатель на первую строку
    def filter_set(self):
        # подразделение
        filter_podr = f" idPodr = {self.filter_podr_id} " if self.filter_podr_id else None
        #образование 
        filter_obrazov = f" obrazov = '{self.cmb_obrazov.currentIndex()}' " if self.cmb_obrazov.currentIndex() > -1 else None
        # звание
        filter_zvan = f" zvanie = '{self.cmb_zvan.currentIndex()}' " if self.cmb_zvan.currentIndex() > -1 else None
        # приказ
        filter_prikaz = f" idPrikaz = {self.filter_prikaz_id} " if self.filter_prikaz_id else None
        # допуск истекает в текущем году
        filter_dopusk_tg = " rtpDo BETWEEN strftime('%Y-01-01', 'now') AND strftime('%Y-12-31', 'now') " if self.btn_dopusk_tg.isChecked() else None
        # сдача просрочена
        filter_dopusk_ist = " DATE(rtpDo) < DATE('now') " if self.btn_dopusk_ist.isChecked() else None

        self.data_rtp = self.db.read_rtp_filter(
                            filter_podr=filter_podr,
                            filter_obrazov=filter_obrazov,
                            filter_zvan=filter_zvan,
                            filter_prikaz=filter_prikaz,
                            filter_dopusk_tg=filter_dopusk_tg,
                            filter_dopusk_ist=filter_dopusk_ist)
        kol_row = len(self.data_rtp)
        self.statusbar.showMessage(f"Записей - {kol_row}")
        self.refresh_grid()
        
        
        

        






    ##############################################################################
    # добавление, сохранение, удаление специалиста
    #############################################################################
    # сохранение сведение о специалисте  
    def save_rtp(self):
        

        # проверка на дубликат
        for row in self.data_rtp:
            fio = (self.txt_edit_family.text().upper().strip() + " " + 
                self.txt_edit_name.text().upper().strip() + " " + 
                self.txt_edit_lastname.text().upper().strip())
            if str(row[1]).upper().strip() == fio and self.mode_edit == "ADD":
                info_dialog = QMessageBox(self)
                info_dialog.setIcon(QMessageBox.Icon.Information)
                info_dialog.setWindowTitle("Сохранение отменено!")
                info_dialog.setText(f"Специалист есть в базе данных.")
                info_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
                info_dialog.exec()
                return
        
        # проверяем заполнение полей
        if len(self.txt_edit_family.text().strip()) == 0:
            self.txt_edit_family.setFocus()
            return
        if len(self.txt_edit_name.text().strip()) == 0:
            self.txt_edit_name.setFocus()
            return
        if len(self.txt_edit_lastname.text().strip()) == 0:
            self.txt_edit_lastname.setFocus()
            return
        if self.curr_podr_id == -1:
            self.btn_edit_podr.setFocus()
            return
        if len(self.txt_edit_dolzh.text().strip()) == 0:
            self.txt_edit_dolzh.setFocus()
            return
        if self.cmb_edit_zvan.currentIndex() < 0:
            self.cmb_edit_zvan.showPopup()
            self.cmb_edit_zvan.setFocus()
            return        
        if self.cmb_edit_obrazov.currentIndex() < 0:
            self.cmb_edit_obrazov.showPopup()
            self.cmb_edit_obrazov.setFocus()
            return 
        if self.curr_prikaz_id == -1:
            self.btn_edit_prikaz.setFocus()
            return
        if self.txt_edit_rezTeor == 0:
            self.txt_edit_rezTeor.setFocus()
            return 
        if self.txt_edit_rezTech == 0:
            self.txt_edit_rezTech.setFocus()
            return 
        if self.txt_edit_rezFiz == 0:
            self.txt_edit_rezFiz.setFocus()
            return 
        if self.txt_edit_rezSob == 0:
            self.txt_edit_rezSob.setFocus()
            return 
        if self.txt_edit_rtpDo.date() <= QDate(2000, 1, 1):
            self.txt_edit_rtpDo.setFocus()
            return

        # сохраняем данные                        
        if self.mode_edit == 'ADD':
            print('добавляем')
            rtp = {
                "id"       : -1,
                "family"   : self.txt_edit_family.text(),
                "name"     : self.txt_edit_name.text(),
                "lastname" : self.txt_edit_lastname.text(),
                "idPodr"   : self.curr_podr_id,
                "dolzh"    : self.txt_edit_dolzh.text(),
                "zvanie"   : self.cmb_edit_zvan.currentIndex(),
                "obrazov"  : self.cmb_edit_obrazov.currentIndex(),
                "idPrikaz": self.curr_prikaz_id,
                "rezTeor"  : self.txt_edit_rezTeor.value(),
                "rezFiz"  : self.txt_edit_rezFiz.value(),
                "rezTech"  : self.txt_edit_rezTech.value(),
                "rezSob"  : self.txt_edit_rezSob.value(),
                "rtpDo"   : datetime.strftime(self.txt_edit_rtpDo.date().toPyDate(), "%Y-%m-%d")
            }  
            
        elif self.mode_edit == 'EDIT':
            print('изменяем')
            rtp = {
                "id"       : self.curr_id_rtp,
                "family"   : self.txt_edit_family.text(),
                "name"     : self.txt_edit_name.text(),
                "lastname" : self.txt_edit_lastname.text(),
                "idPodr"   : self.curr_podr_id,
                "dolzh"    : self.txt_edit_dolzh.text(),
                "zvanie"     : self.cmb_edit_zvan.currentIndex(),
                "obrazov"  : self.cmb_edit_obrazov.currentIndex(),
                "idPrikaz": self.curr_prikaz_id,
                "rezTeor"  : self.txt_edit_rezTeor.value(),
                "rezFiz"  : self.txt_edit_rezFiz.value(),
                "rezTech"  : self.txt_edit_rezTech.value(),
                "rezSob"  : self.txt_edit_rezSob.value(),
                "rtpDo"   : datetime.strftime(self.txt_edit_rtpDo.date().toPyDate(), "%Y-%m-%d")
            }    
        else:
            return

        # обновляем грид
        self.db.rtp_save(rtp=rtp)
        self.filter_set()


        
        # Восстанавливаем текущую позицию
        if self.mode_edit == "ADD":
            # определяем новый id приказа после добавления
            self.curr_id_rtp = max(row[0] for row in self.data_rtp)
        
        # Проходим по всем строкам модели для поиска новой позиции отредактированной строки
        for row in range(self.table.model().rowCount(QtCore.QModelIndex())):
            index = self.model.index(row, 0)  # Предполагаем, что id находится в первом столбце
            if self.model.data(index, Qt.ItemDataRole.DisplayRole) == self.curr_id_rtp:
                self.table.setCurrentIndex(index)
                self.table.scrollTo(index)  # Прокрутить до выделенной строки
                            
        # выключаем режим редактирования
        self.mode_edit = 'NONE'
        self.frm_grid.setVisible(True)
        self.table.setFocus()
        

    # удаление сотрудника  
    def del_rtp(self, curr_id, curr_id_post):
        self.db.rtp_del(curr_id)

        # обновляем грид
        self.filter_set()

        
        
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

    
    # отмена сохранения
    def saveno_rtp(self):
        self.mode_edit = "NONE"
        self.frm_grid.setVisible(True)
        
        
        
        
    ########################################################################################
    # открытие формы с приказами
    ######################################################################################        
    def open_prikaz(self, mode):
        # настраиваем режим работы (фильтр или выбор на панели редактирования)
        self.w_prikaz.mode_prikaz = mode
        self.w_prikaz.show()    
        

    ########################################################################################
    # открытие формы с подразделениями
    ######################################################################################        
    def open_podr(self, mode):
        # настраиваем режим работы (фильтр или выбор на панели редактирования)
        self.w_podr.mode_podr = mode
        self.w_podr.show()    
    
    

    ########################################################################################
    # событие перед закрытием приложения
    ######################################################################################   

    def closeEvent(self, event):
        

        if self.mode_edit == "NONE":
            self.db.close_connection()
            event.accept()
        else:
            # Показываем диалог для подтверждения выхода
            reply = QMessageBox.question(
                self,
                "Подтверждение выхода",
                "Вы действительно хотите закрыть приложение?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
                
            if reply == QMessageBox.StandardButton.Yes:
                # Выполняем действия перед закрытием, если нужно
                #print("Сохраняем данные перед выходом...")
                # Разрешаем закрытие
                self.db.close_connection()
                event.accept()
            else:
                # Отменяем закрытие
                event.ignore()
                
                
    ########################################################################################
    # Прием сведений из формы приказов
    ###################################################################################### 
    def update_edit_from_prikaz(self, prikaz_id, prikaz_nom, prikaz_dt):
        self.curr_prikaz_id = prikaz_id
        self.curr_prikaz_dt = prikaz_dt
        self.txt_edit_prikaz.setText(f'№ {prikaz_nom} от {datetime.strftime(prikaz_dt, "%d.%m.%Y")}')
        check_widget(self.txt_edit_prikaz, prikaz_id == -1)

    def update_filter_from_prikaz(self, prikaz_id, prikaz_nom, prikaz_dt):
        if self.btn_prikaz.isChecked():
            self.filter_prikaz_id = prikaz_id
        else:
            self.filter_prikaz_id = None
        self.txt_prikaz.setText(f'№ {prikaz_nom} от {datetime.strftime(prikaz_dt, "%d.%m.%Y")}')
        self.filter_set()


    ########################################################################################
    # Прием сведений из формы подразделений
    ###################################################################################### 
    def update_edit_from_podr(self, podr_id, podr):
        self.curr_podr_id = podr_id
        self.txt_edit_podr.setText(podr)
        check_widget(self.txt_edit_podr, podr_id == -1)

    def update_filter_from_podr(self, podr_id, podr):
        if self.btn_podr.isChecked():
            self.filter_podr_id = podr_id
        else:
            self.filter_podr_id = None
        self.txt_podr.setText(podr)
        self.filter_set()



    # ########################################################################################
    # # Обновляем грид
    # ###################################################################################### 
    def refresh_grid(self):
        # настраиваем грид
        column_titles = ["id", "ФИО", "Подразделение", "Должность", "Звание", "Образование", "Теор", "Физ","Тех","Соб", "Допуск до"]
        self.model = RtpTableModel(self.data_rtp, column_titles)

        self.table.setModel(self.model)
        
        # ширина столбцов
        self.table.setColumnWidth(0, 0)
        self.table.setColumnWidth(1, 220)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 170)
        self.table.setColumnWidth(4, 180)
        self.table.setColumnWidth(5, 140)  
        self.table.setColumnWidth(6, 35)  
        self.table.setColumnWidth(7, 35)  
        self.table.setColumnWidth(8, 35)                          
        self.table.setColumnWidth(9, 35)  
        self.table.setColumnWidth(10, 80)
        
        # режим выделения = строка целиком
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)  
        self.model.layoutChanged.emit()        
        
        
        
        
        
    
